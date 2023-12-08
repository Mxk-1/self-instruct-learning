"""
maxinkai
irvingmxk@163.com
"""

from tika import parser
import re
import json

file_path = "./pdf/2023年税务师《税法二》考前模拟测试卷（二）_10db97fce5baae3de7075cf4afa9dfbf0dce5037.pdf"
json_file_path = "one_choice_questions.jsonl"


class ParsePdf:
    def __init__(self, filepath):
        self.file_path = filepath

    # 获取内容
    def get_content(self):
        parsed = parser.from_file(self.file_path)
        content = dict(parsed).get('content')
        return content

    # 获取元数据
    def get_metadata(self):
        parsed = parser.from_file(self.file_path)
        metadata = dict(parsed).get('metadata')
        return metadata

    # 内容处理
    def content_process(self):
        content = self.get_content()

        # 清除换行符，空格
        content = content.replace('\n', '')
        content = content.replace(' ', '')

        # 删除第几页共几页
        content = re.sub(r'第\d+页，共\d+页', '', content)
        content = re.sub(r'第\d+页共\d+页', '', content)

        # 去除无用文本 '。' '。9999' 截断条件
        content = '。' + content.replace('2023年税务师《财务与会计》模拟题（一）', '').replace(
            '咨询热线：400-678-3456微信扫码刷题免费约直播领资料扫码关注报考资讯公众号环球网校移动课堂APP环球网校侵权必究',
            '').replace('一、单项选择题（40题×1.5分，共60分），只有1个最符合题意，选错不得分。', '').replace(
            '一、单项选择题（40题×1.5分，共60分），只有1个最符合题意，选错不得分。', '').replace(
            '二、多项选择题（20题×2分，共40分），每题的备选项中（5个选项），有2个或2个以上符合题意，至少',
            '').replace('三、计算题（2小题，共16分），每题的备选项中，只有1个最符合题意。', '').replace(
            '四、综合分析题（2小题，共24分），由单项选择题和多项选择题组成。错选，本题不得分；少选，所选的每个', '').replace(
            '\u2003\u2003', '').replace('有1个错项。错选，本题不得分；少选，所选的每个选项得0.5分。', '').replace(
            '选项得0.5分。', '').replace('\t', '').replace('2023年税务师《涉税服务实务》模考试卷1', '').replace(
            '二、多选题', '').replace('2023年税务师《涉税服务实务》模考试卷2', '').replace('一、单选题', '').replace(
            '三、问答题', '').replace('四、解析题', '').replace('2023税务师《涉税服务相关法律》考前模拟（一）', '').replace(
            '一、单项选择题（共40题，每题1.5分，共60分。每题的备选项中，只有1个最符合题意。）', '').replace(
            '二、多项选择题（共20题，每题2分，共40分。每题的备选项中，有2个或2个以上符合题意，至少有1个错', '').replace(
            '三、综合分析题（共20小题，每小题2分，共40分。每题的备选项中，有1个或多个最符合题意，至少有1个', '').replace(
            '2023税务师《涉税服务相关法律》考前模拟（二）', '').replace('2023税务师《税法一》考前模拟（一）', '').replace(
            '一、单项选择题（共40题，每题1.5分，共60分。每题的备选项中，只有1个最符合题意。错选、不选均不得分。）', '').replace(
            '一、单项选择题（共40题，每题1.5分，共60分。每题的备选项中，只有1个最符合题意。错选、不选均不', '').replace(
            '三、计算分析题（共8题，每题2分，共16分。每题的备选项中，只有1个最符合题意）。', '').replace(
            '四、综合题（共12题，每题2分，共24分。', '').replace('由单项选择题和多项选择题组成。',
                                                            '').replace('错选或多选不得分；', '').replace('少选选对的',
                                                                                                         '').replace(
            '项。错选不得分；，每个选项得0.5分，多选、错选、不选均不得分。）', '').replace('2023税务师《税法一》考前模拟（二）',
                                                                                   '').replace(
            '2023税务师《税法二》考前模拟（一）', '').replace('2023税务师《税法二》考前模拟（二）', '').replace(
            '二、多项选择题（共20题，每题2分，共40分。每题的备选项中，有2个或2个以上符合题意，至少）', '') + '。9999'

        # 修改答案，解析换行，不用，控制台输出看着舒服
        # content = content.replace('【', '\n【')

        # print(content)

        # 正则解析题目

        # !!! 注意匹配规则
        question_dict = re.findall(r'。\s*(\d+)\.(.+?)\【答案】(.+?)\【解析】(.+?)(?=。\d+)', content, re.DOTALL)

        # 2023税务师《涉税服务实务》模考试卷（二） 匹配规则不同
        # question_dict = re.findall(r'。\s*(\d+)\.(.+?)\【正确答案】：(.+?)\【试题解析】：(.+?)(?=。\d+)', content, re.DOTALL)

        print(question_dict)

        # 结果集
        result_list = []

        for question in question_dict:
            question_dict = dict()
            question_dict['question_id'] = question[0]
            question_dict['question_content'] = question[1]
            question_dict['question_answer'] = question[2]
            question_dict['question_analysis'] = question[3]
            result_list.append(question_dict)

        # print(result_list)

        return result_list

    # 单选题
    # 2023税务师《涉税服务相关法律》靠前模拟（一） 单选 40道
    # 2023税务师《涉税服务实务》模考试卷（一） 单选 20道
    def one_choice_question(self):
        all_list = self.content_process()

        one_choice_list = all_list[:40]

        # for one_choice in all_list:
        #     if 40 >= int(one_choice['question_id']) >= 1 == len(one_choice['question_answer']):
        #         # print(one_choice)
        #         one_choice_list.append(one_choice)

        return one_choice_list

    # 2023税务师《涉税服务相关法律》靠前模拟（一） 多选 20道
    # 2023税务师《涉税服务实务》模考试卷（一） 多选 10道
    def many_choice_question(self):
        all_list = self.content_process()
        many_choice_list = all_list[40:60]
        return many_choice_list

    # 单选json
    def dict_to_one_choice_json(self):
        one_choice_list = self.one_choice_question()
        one_choice_json = json.dumps(one_choice_list, ensure_ascii=False)
        print(one_choice_json)

        print('\n')

        # 追加方式(a)写入文件
        # with open('one_choice.json', 'a', encoding='utf-8') as f:
        #     f.write(one_choice_json)
        #
        # with open('many_choice_questions.jsonl', 'a', encoding='utf-8') as f:
        #     f.write(many_choice_json)

        return one_choice_json

    # 多选json
    def dict_to_many_choice_json(self):
        many_choice_list = self.many_choice_question()
        many_choice_json = json.dumps(many_choice_list, ensure_ascii=False)

        print(many_choice_json)

        # 追加方式(a)写入文件
        # with open('one_choice.json', 'a', encoding='utf-8') as f:
        #     f.write(one_choice_json)
        #
        # with open('many_choice_questions.jsonl', 'a', encoding='utf-8') as f:
        #     f.write(many_choice_json)

        return many_choice_json

    # todo
    def append_to_file(self):
        # 读取原文件内容
        with open(json_file_path, 'a+', encoding='utf-8') as file:
            file.seek(0)
            original_content = file.read()

        # 单选题str
        data = self.dict_to_one_choice_json()
        # 去除首尾字符 []
        data = data[1:-1].replace('}, ', '}\n')

        #
        original_content = original_content[1:-1]

        # 新内容重写到文件
        with open(json_file_path, 'a+', encoding='utf-8') as file:
            file.write(data + '\n')


if __name__ == "__main__":
    pdf = ParsePdf(file_path)
    pdf.append_to_file()

    # pdf.dict_to_one_choice_json()

    # pdf.content_process()

    # print(pdf.dict_to_json())
    # print('\n')
    # print(pdf.many_choice_question())

    # 匹配 ’数字' '\d+\'  "\d+\"
