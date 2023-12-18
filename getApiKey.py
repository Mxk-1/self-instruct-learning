from datetime import datetime

import openai
import time
import codecs
import json


class openkey_gpt_request:
    def __init__(self, apikey="sk-y4HtX3nsqpdQtUfZ5g06U9Kz0I8mcVJTwkWpdO566E0VrOLv", retry_time=5,
                 model_name="gpt-3.5-turbo-1106") -> None:
        self.retry_time = retry_time
        # self.url = "https://op.zakix.info/v1"
        self.url = "https://giegie.green/v1"
        self.apikey = apikey
        self.model_name = model_name
        self.requstion_timeout = 60
        self.max_tokens = 500
        pass

    def get_result(self, content):
        for a in range(self.retry_time):
            rlt = self.request_gpt(content)
            if rlt:
                return rlt
            else:
                time.sleep(1)

        return None

    def request_gpt(self, prompts):
        response = None
        target_length = self.max_tokens
        retry_cnt = 0
        try:
            openai.api_key = self.apikey
            openai.api_base = self.url
            openai.proxy = "http://127.0.0.1:33210"
            messages = [{"role": "user", "content": prompts}]
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                temperature=0.01,
                request_timeout=self.requstion_timeout
            )
        except openai.error.OpenAIError as e:
            print(f"OpenAIError: {e}.")
            if "Please reduce your prompt" in str(e):
                target_length = int(target_length * 0.8)
                print(f"Reducing target length to {target_length}, retrying...")
            else:
                print(f"Retrying in {self.retry_time} seconds...")
                time.sleep(self.retry_time)
                self.retry_time *= 1.5
            retry_cnt += 1

        if isinstance(prompts, list):
            results = []
            n = 1
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

        #     result = response
        #     if "choices" in result:
        #         res = result["choices"][0]["message"]["content"].strip()
        #         return res
        # except Exception as ex:
        #     print(ex)

        # return None


if __name__ == "__main__":
    api_info = openkey_gpt_request()
    question = "你好"
    rlt = api_info.request_gpt(question)
    print("--result--")
    print(rlt)
    # 返回的response中的content包含ascii码，需要转换
    content = rlt[0]["response"]["choices"][0]["message"]["content"].encode("utf-8").decode("utf-8")
    print(content)
