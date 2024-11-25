import json

# 读取JSON文件
def read_json():
    with open('config.json', 'r') as f:
        data = json.load(f)
    return data

# 写入JSON文件
def write_json(data):
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)