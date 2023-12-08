import openai
import time
import codecs
import json
class openkey_gpt_request:
    def __init__(self, apikey ="sk-y4HtX3nsqpdQtUfZ5g06U9Kz0I8mcVJTwkWpdO566E0VrOLv",retry_time=5, model_name="gpt-3.5-turbo-1106") -> None:
        self.retry_time = retry_time
        #self.url = "https://op.zakix.info/v1"
        self.url = "https://giegie.green/v1"
        self.apikey = apikey
        self.model_name = model_name
        self.requstion_timeout=60
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
            openai.api_key= self.apikey
            # openai.api_base =self.url
            messages = [{"role":"user","content": content}]
            response=openai.Completion.create(
                model=self.model_name,
                messages=messages,
                temperature=0.01,
                request_timeout=self.requstion_timeout
            )
            result = response
            if "choices" in result:
                res = result["choices"][0]["message"]["content"].strip()
                return res
        except Exception as ex:
            print(ex)

        return None
if __name__ == "__main__":
    api_info = openkey_gpt_request()
    question = "亚里士多德的哲学论点主要是什么，简单介绍下"
    rlt = api_info.request_gpt(question)
    print(rlt)
