import re

# 示例字符串
text = 'Price: per night\n$780 - $4,300 +'

page_sign = r'US$'
# 正则表达式模式，用于匹配以美元为单位的金额
pattern = f'\n(.*)\d+(?:,\d+)?(?:\.\d{2})?'

# 使用findall方法找到所有匹配的金额
matches = re.findall(pattern, text)

# 打印结果
print(matches)