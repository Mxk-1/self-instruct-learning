import json
import tqdm
import os
import random
import openai
from datetime import datetime
import argparse
import time


# 官方的gpt3请求
def make_requests(
        prompts, max_tokens, temperature, top_p,
        frequency_penalty, presence_penalty, logprobs, n, best_of, retries=3,
        api_key=None,
        organization=None,
        model_name=None,
):
    response = None
    target_length = max_tokens
    if api_key is not None:
        openai.api_key = api_key
    if organization is not None:
        openai.organization = organization
    openai.proxy = "http://127.0.0.1:33210"
    # openai.url = "https://giegie.green/v1"
    retry_cnt = 0
    backoff_time = 5
    while retry_cnt <= retries:
        try:
            response = openai.ChatCompletion.create(
                prompt=prompts,
                max_tokens=target_length,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                logprobs=logprobs,
                n=n,
                best_of=best_of,
                model=model_name,
            )
            break
        except openai.error.OpenAIError as e:
            print(f"OpenAIError: {e}.")
            if "Please reduce your prompt" in str(e):
                target_length = int(target_length * 0.8)
                print(f"Reducing target length to {target_length}, retrying...")
            else:
                print(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
                backoff_time *= 1.5
            retry_cnt += 1

    if isinstance(prompts, list):
        results = []
        for j, prompt in enumerate(prompts):
            data = {
                "prompt": prompt,
                "response": {"choices": response["choices"][j * n: (j + 1) * n]} if response else None,
                "created_at": str(datetime.now()),
            }
            results.append(data)
        return results
    else:
        data = {
            "prompt": prompts,
            "response": response,
            "created_at": str(datetime.now()),
        }
        return [data]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_file",
        type=str,
        default="D:\\NLP\\self-instruct-learning\\data\\my_seed_tasks.jsonl",
        help="The input file that contains the prompts to GPT3.",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="data/gpt3_generations/machine_generated_instructions.jsonl",
        help="The output file to save the responses from GPT3.",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        # default="davinci",
        default="gpt-3.5-turbo-1106",
        required=False,
        # openai 模型
        help="The openai GPT3 model to use.",
    )
    parser.add_argument(
        "--max_tokens",
        default=500,
        type=int,
        required=False,
        # 每个请求的最大token数（单词或标点符号）
        help="The max_tokens parameter of GPT3.",
    )
    parser.add_argument(
        "--temperature",
        default=0.01,
        type=float,
        required=False,
        # 控制随机性的参数，值越大，结果越随机
        help="The temprature of GPT3.",
    )
    parser.add_argument(
        "--top_p",
        default=0.5,
        type=float,
        required=False,
        # 控制如何选择下一个token的参数
        help="The `top_p` parameter of GPT3.",
    )
    parser.add_argument(
        "--frequency_penalty",
        default=0,
        type=float,
        required=False,
        help="The `frequency_penalty` parameter of GPT3.",
    )
    parser.add_argument(
        "--presence_penalty",
        default=0,
        type=float,
        required=False,
        help="The `presence_penalty` parameter of GPT3.",
    )
    parser.add_argument(
        "--logprobs",
        default=5,
        type=int,
        help="The `logprobs` parameter of GPT3"
    )
    parser.add_argument(
        "--n",
        type=int,
        # 指定返回的响应数
        default=1,
        help="The `n` parameter of GPT3. The number of responses to generate."
    )
    parser.add_argument(
        "--best_of",
        type=int,
        # 指定返回的最佳结果数
        default=1,
        required=False,
        help="The `best_of` parameter of GPT3. The beam size on the GPT3 server."
    )
    parser.add_argument(
        "--use_existing_responses",
        action="store_true",
        help="Whether to use existing responses from the output file if it exists."
    )
    parser.add_argument(
        "--request_batch_size",
        default=5,
        type=int,
        help="The number of requests to send to GPT3 at a time."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        required=False,
        default="sk-y4HtX3nsqpdQtUfZ5g06U9Kz0I8mcVJTwkWpdO566E0VrOLv"
    )
    return parser.parse_args()


if __name__ == "__main__":
    result = make_requests(prompts=["你好"], model_name="gpt-3.5-turbo-1106", max_tokens=500, temperature=0.01,
                           top_p=0.5,
                           frequency_penalty=0, presence_penalty=0, logprobs=5, n=1, best_of=1,
                           api_key="sk-y4HtX3nsqpdQtUfZ5g06U9Kz0I8mcVJTwkWpdO566E0VrOLv")
    print(result)
    # random.seed(123)
    # args = parse_args()
    # os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    #
    # # read existing file if it exists
    # existing_responses = {}
    # if os.path.exists(args.output_file) and args.use_existing_responses:
    #     with open(args.output_file, "r") as fin:
    #         for line in fin:
    #             data = json.loads(line)
    #             existing_responses[data["prompt"]] = data
    #
    # # do new prompts
    # with open(args.input_file, "r") as fin:
    #     if args.input_file.endswith(".jsonl"):
    #         # all_prompts = [json.loads(line)["prompt"] for line in fin]
    #         all_prompts = [json.loads(line)["instruction"] for line in fin]
    #
    #     else:
    #         all_prompt = [line.strip().replace("\\n", "\n") for line in fin]
    #
    # with open(args.output_file, "w") as fout:
    #     for i in tqdm.tqdm(range(0, len(all_prompts), args.request_batch_size)):
    #         batch_prompts = all_prompts[i: i + args.request_batch_size]
    #         if all(p in existing_responses for p in batch_prompts):
    #             for p in batch_prompts:
    #                 fout.write(json.dumps(existing_responses[p]) + "\n")
    #         else:
    #             results = make_requests(
    #                 engine=args.engine,
    #                 prompts=batch_prompts,
    #                 max_tokens=args.max_tokens,
    #                 temperature=args.temperature,
    #                 top_p=args.top_p,
    #                 frequency_penalty=args.frequency_penalty,
    #                 presence_penalty=args.presence_penalty,
    #                 stop_sequences=args.stop_sequences,
    #                 logprobs=args.logprobs,
    #                 n=args.n,
    #                 best_of=args.best_of,
    #                 api_key=args.api_key,
    #             )
    #             for data in results:
    #                 fout.write(json.dumps(data) + "\n")
