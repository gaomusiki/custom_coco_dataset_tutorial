import json

# 读取 categories.json
with open("categories.json", "r") as f:
    categories = json.load(f)

# 初始化分类存储
stuff_class = []
thing_class = []
stuff_color = []
thing_color = []
thing_dataset_id_to_contiguous_id = {}
stuff_dataset_id_to_contiguous_id = {}

# 遍历类别
thing_counter = 0
stuff_counter = 0

for category in categories:
    cat_id = category["id"]
    cat_name = category["name"]
    cat_color = category["color"]
    is_thing = category["isthing"]

    if is_thing == 1:
        thing_class.append(cat_name)
        thing_color.append(cat_color)
        thing_dataset_id_to_contiguous_id[cat_id] = thing_counter
        thing_counter += 1
    else:
        stuff_class.append(cat_name)
        stuff_color.append(cat_color)
        stuff_dataset_id_to_contiguous_id[cat_id] = stuff_counter
        stuff_counter += 1

# 组织数据
my_custom_metadata = {
    "stuff_class": stuff_class,
    "thing_class": thing_class,
    "stuff_color": stuff_color,
    "thing_color": thing_color,
    "thing_dataset_id_to_contiguous_id": thing_dataset_id_to_contiguous_id,
    "stuff_dataset_id_to_contiguous_id": stuff_dataset_id_to_contiguous_id
}

# 保存为 my_custom_metadata.json
out_path="my_custom_metadata.json"
with open(out_path, "w") as f:
    json.dump(my_custom_metadata, f, indent=4)

print("✅ my_custom_metadata.json 生成成功！")
