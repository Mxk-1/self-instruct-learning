# -*- coding: utf-8 -*-
# 含有中文声明utf8
import os
import json
import random
import re
import string
import tqdm
import argparse
import numpy as np
import pandas as pd
from multiprocessing import Pool
from functools import partial
from rouge_score import rouge_scorer
from getApiKey import openkey_gpt_request

random.seed(42)


def encode_prompt(prompt_instructions, classification=False):
    """Encode multiple prompt instructions into a single string."""
    if classification:
        prompt = "想出一系列分类任务。尽可能指定可能的输出标签。\n"
    else:
        prompt = "提出一系列任务：\n"
    for idx, instruction in enumerate(prompt_instructions):
        instruction = re.sub(r"\s+", " ", instruction).strip().rstrip(":")
        prompt += f"{idx + 1}. {instruction}\n"
    prompt += f"{len(prompt_instructions) + 1}."
    return prompt


def sample_machine_instructions(machine_instructions, similarities, n):
    """Sample n machine instructions from a list of machine instructions."""
    return random.sample(machine_instructions, min(n, len(machine_instructions)))


def find_word_in_string(w, s):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search(s)


def post_process_gpt3_response(response):
    if response is None or response["choices"][0]["finish_reason"] == "length":
        return []
    content = response["choices"][0]["message"]["content"].encode("utf-8").decode("utf-8")
    raw_instructions = re.split(r"\n\d+\s?\. ", content)
    instructions = []
    for inst in raw_instructions:
        inst = re.sub(r"\s+", " ", inst).strip()
        inst = inst.strip().capitalize()
        if inst == "":
            continue
        # filter out too short or too long instructions
        # 过滤较短或较长的指令
        # if len(inst.split()) <= 3 or len(inst.split()) > 150:
        #     continue
        # filter based on keywords that are not suitable for language models.
        if any(find_word_in_string(word, inst) for word in
               # ["image", "images", "graph", "graphs", "picture", "pictures", "file", "files", "map", "maps", "draw",
               #  "plot", "go to"]):
               ["图片", "文件", "地图", "绘制"]):
            continue
        # We found that the model tends to add "write a program" to some existing instructions, which lead to a lot of such instructions.
        # And it's a bit comfusing whether the model need to write a program or directly output the result. 
        # Here we filter them out.
        # Note this is not a comprehensive filtering for all programming instructions.
        if inst.startswith("Write a program"):
            continue
        # filter those starting with punctuation
        if inst[0] in string.punctuation:
            continue
        # 过滤非英语开头的指令 关闭！！！
        # if not inst[0].isascii():
        #     continue
        instructions.append(inst)
    return instructions


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--batch_dir",
        type=str,
        required=False,
        default="D:\\NLP\\self-instruct-learning\\data\\tax_data\\",
        help="The directory where the batch is stored.",
    )
    parser.add_argument(
        "--seed_tasks_path",
        type=str,
        required=False,
        default="D:\\NLP\\self-instruct-learning\\data\\tax_data\\fill_blank_seed_tasks.jsonl",
        help="The path to the human written data.",
    )
    parser.add_argument(
        "--num_instructions_to_generate",
        type=int,
        # !!! 新生成的指令数量 ！！！
        default=26,
        help="th",
    )
    parser.add_argument(
        "--use_clf_seed_tasks_only",
        action="store_true",
        help="If specified, we will only use the classification seed tasks to prompt new instructions. This will lead to more classification instructions.",
    )
    parser.add_argument(
        "--engine",
        type=str,
        default="gpt-3.5-turbo-1106",
        help="The engine to use."
    )
    parser.add_argument(
        "--num_prompt_instructions",
        type=int,
        default=8,
        help="The number of instructions to use in the prompt."
    )
    parser.add_argument(
        "--request_batch_size",
        type=int,
        # batch_inputs的数量
        default=8,
        help="The number of requests to send to GPT3 at a time."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default="sk-y4HtX3nsqpdQtUfZ5g06U9Kz0I8mcVJTwkWpdO566E0VrOLv",
        help="The API key to use. If not specified, the key will be read from the environment variable OPENAI_API_KEY."
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://giegie.green/v1",
        help="The API key to use. If not specified, the key will be read from the environment variable OPENAI_API_KEY."
    )
    parser.add_argument(
        "--organization",
        type=str,
        help="The organization to use. If not specified, the default organization id will be used."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    # utf-8编码
    seed_tasks = [json.loads(l) for l in open(args.seed_tasks_path, "r", encoding="utf-8")]
    # 筛选出分类任务为True的任务
    if args.use_clf_seed_tasks_only:
        seed_tasks = [t for t in seed_tasks if t["is_classification"]]
    seed_instructions = [t["instruction"] for t in seed_tasks]
    print(f"Loaded {len(seed_instructions)} human-written seed instructions")

    os.makedirs(args.batch_dir, exist_ok=True)
    request_idx = 0
    # load the LM-generated instructions
    machine_instructions = []
    if os.path.exists(os.path.join(args.batch_dir, "machine_generated_instructions.jsonl")):
        with open(os.path.join(args.batch_dir, "machine_generated_instructions.jsonl"), "r", encoding="gbk") as fin:
            for line in fin:
                instruction_info = json.loads(line)
                machine_instructions.append(instruction_info["instruction"])
                request_idx = instruction_info["request_idx"] + 1
        print(f"Loaded {len(machine_instructions)} machine-generated instructions")

    # similarities = {}，用来计算生成的任务instructions跟已有的相似度
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)

    # now let's generate new instructions!
    progress_bar = tqdm.tqdm(total=args.num_instructions_to_generate)
    if machine_instructions:
        progress_bar.update(len(machine_instructions))

    # 生成的指令存储在machine_generated_instructions.jsonl文件中
    with open(os.path.join(args.batch_dir, "machine_generated_instructions.jsonl"), "a", encoding="gbk") as fout:
        # 生成的指令数量小于指定数量时，继续生成
        while len(machine_instructions) < args.num_instructions_to_generate:
            batch_inputs = []
            # 每次请求的指令数量
            for _ in range(args.request_batch_size):
                # sample machine instructions from the pool
                # 从机器生成的指令中随机抽取n个指令
                prompt_instructions = sample_machine_instructions(
                    machine_instructions,
                    similarities=None,
                    n=2)
                # sample human instructions from the pool
                # 从人工生成的指令中随机抽取n个指令
                prompt_instructions += random.sample(seed_instructions,
                                                     args.num_prompt_instructions - len(prompt_instructions))
                # 打乱指令顺序
                random.shuffle(prompt_instructions)
                # 将指令转换为字符串
                prompt = encode_prompt(prompt_instructions, classification=args.use_clf_seed_tasks_only)
                batch_inputs.append(prompt)

            # 存储结果集
            results = []

            for prompt in batch_inputs:
                # print("---show info---")
                # print(prompt)
                result = openkey_gpt_request().request_gpt(prompt)
                # print("---show result---")
                # print(result)
                results.append(result)
                # print(result)

            instructions = []
            all_metadata = []
            new_instructions = []

            for result in results:
                response = result[0]["response"]
                # print(response)
                new_instructions = post_process_gpt3_response(response)
                instructions += new_instructions
                all_metadata += [result] * len(new_instructions)

            for inst, metadata in zip(instructions, all_metadata):
                with Pool(4) as p:
                    rouge_scores = p.map(partial(scorer.score, inst), seed_instructions + machine_instructions)
                rouge_scores = [score["rougeL"].fmeasure for score in rouge_scores]
                # rouge_scores = [scorer.score(inst, e_inst)["rougeL"].fmeasure for e_inst in human_instructions + machine_instructions]
                if max(rouge_scores) >= 0:
                    continue
                all_instructions = seed_instructions + machine_instructions
                most_similar_instructions = {
                    all_instructions[i]: rouge_scores[i] for i in np.argsort(rouge_scores)[-10:][::-1]
                }
                machine_instructions.append(inst)
                fout.write(json.dumps({
                    "instruction": inst,
                    "most_similar": most_similar_instructions,
                    "avg_similarity_score": float(np.mean(rouge_scores)),
                    "metadata": metadata,
                    "request_idx": request_idx
                    # ensure_ascii=False，用来解决中文乱码问题，中文不转化为ascii码
                }, ensure_ascii=False) + "\n", )
                progress_bar.update(1)
            request_idx += 1
