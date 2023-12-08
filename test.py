import re

str = '2023年税务师《财务与会计》模拟题（一）'

str = re.sub(r'2023年税务师《\*》模拟题（\*）', '', str)

print(str)