import json

# 读取 categories.json
categories_path="./categories.json"
with open(categories_path, 'r') as f:
    categories = json.load(f)

# 创建一个集合来存储已出现的颜色
color_set = set()
duplicate_colors = []

# 遍历每个类别
for category in categories:
    color_tuple = tuple(category['color'])  # 转换为元组（列表不可哈希）
    
    if color_tuple in color_set:
        duplicate_colors.append((category['id'], category['name'], color_tuple))
    else:
        color_set.add(color_tuple)

# 输出重复的颜色
if duplicate_colors:
    print("发现重复颜色：")
    for cat_id, name, color in duplicate_colors:
        print(f"类别 ID: {cat_id}, 名称: {name}, 颜色: {color}")
else:
    print("没有发现重复颜色！")
