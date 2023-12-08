import json

# 定义你的字典数据
data = [
    {"name": "John", "age": 30, "city": "New York"},
    {"name": "Jane", "age": 25, "city": "Los Angeles"},
    {"name": "Bob", "age": 40, "city": "Chicago"}
]

# 打开一个文件用于写入
with open('data.jsonl', 'w') as f:
    # 将字典数据转化为JSON格式，并写入到文件中
    # 注意：这里我们添加了一个换行符 '\n'，使得每个JSON对象都在新的一行
    f.write(json.dumps(data) + '\n')
