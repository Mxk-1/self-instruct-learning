from datetime import datetime

import openai
import time
import codecs
import json


# 自己
class openkey_gpt_request:
    def __init__(self, apikey="sk-y4HtX3nsqpdQtUfZ5g06U9Kz0I8mcVJTwkWpdO566E0VrOLv", retry_time=5,
                 model_name="gpt-3.5-turbo-1106") -> None:
        self.retry_time = retry_time
        # self.url = "https://op.zakix.info/v1"
        self.url = "https://giegie.green/v1"
        self.apikey = apikey
        self.model_name = model_name
        self.requstion_timeout = 60
        pass

    def get_result(self, content):
        for a in range(self.retry_time):
            rlt = self.request_gpt(content)
            if rlt:
                return rlt
            else:
                time.sleep(1)

        return None

    def request_gpt(self, content):
        try:
            # set proxy
            openai.proxy = "http://127.0.0.1:33210"
            openai.api_key = self.apikey
            openai.api_base = self.url
            messages = [{"role": "user", "content": content}]
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                temperature=0.01,
                request_timeout=self.requstion_timeout
            )
            result = response
            if "choices" in result:
                res = result["choices"][0]["message"]["content"].strip()
                return res
            if isinstance(content, list):
                results = []
                for j, prompt in enumerate(content):
                    data = {
                        "prompt": prompt,
                        "response": {"choices": response["choices"][j * 1: (j + 1) * 1]} if response else None,
                        "created_at": str(datetime.now()),
                    }
                    results.append(data)
                return results
        except Exception as ex:
            print(ex)

        return None


if __name__ == "__main__":
    api_info = openkey_gpt_request()
    # question = "现在需要编写linux脚本，实现调用多个shell脚本，用数字控制脚本调用顺序，比如给定数字总轮数10, 开始遍历。轮数为1时， 调用A脚本并传入参数S1，之后再调用A2脚本并传入参数S2；轮数为2时， 调用B脚本并传入参数T1，之后再调用B2脚本并传入参数T2;轮数大于2后都调用C脚本并传入参数P1，计算出剩余轮数，也就是总轮数减去2，执行后跳出循环。请帮忙写出脚本代码。"
    # question = "现在需要编写linux脚本，脚本执行时会传入3个参数，在脚本中需要写清楚怎样获取传入参数并使用。需要给出执行脚本的命令。"
    # question = "现在需要编写linux脚本，脚本执行时会传入1个参数，在脚本中需要写清楚怎样获取传入参数并使用，如果参数值为local则走A流程，否则则走B流程。需要给出执行脚本的命令。"
    question = "你好"
    rlt = api_info.request_gpt(question)
    print("--result--")
    print(rlt)

# $ python getRequest.py 
# --result--
# 1. 文本处理：包括分词、词性标注、命名实体识别等技术。
# 2. 语言模型：理解和生成自然语言的模型，如神经网络语言模型、循环神经网络等。
# 3. 信息抽取：从文本中提取结构化信息，如关键词提取、实体关系抽取等。
# 4. 语义理解：理解文本的语义，包括语义相似度计算、情感分析等。
# 5. 机器翻译：将一种语言翻译成另一种语言的技术。
# 6. 对话系统：构建能够与人类进行自然对话的系统，如聊天机器人、智能助手等。
# 7. 信息检索：从大规模文本数据中检索相关信息的技术。
# 8. 文本生成：生成自然语言文本的技术，如文本摘要、文章生成等。
# 9. 语音识别：将语音转换成文本的技术。
# 10. 情感分析：分析文本中的情感倾向，如积极情感、消极情感等。
