from controller.json_function import read_json,write_json
from flask import Blueprint, g, request,jsonify
import json


model_select_information = Blueprint('model_select_info', __name__)

@model_select_information.route('/setting', methods=['POST'])
def update_camera():
    # 使用全域變數 camera_sources
    camera_sources = g.get('camera_sources', [])
    name = request.form['name']
    index = int(request.form['index'])
    # source = request.form['source']
    models = json.loads(request.form['models'])
    # 读取当前的JSON文件
    config_data = read_json()
    config_data['cameras'][index]['models'] = models
    # config_data['cameras'][index] = {"source": source, "models": models}
    # config_data['cameras'][index] = {"name": name,"source": config_data['cameras'][index]['source'],"images": config_data['cameras'][index]['images'],"playback_speed": config_data['cameras'][index]['playback_speed'], "models": models}
    write_json(config_data)
    # 更新camera_sources
    g.camera_sources[index]['playback_speed'] = 2.0
    print("123")
    # for camera_info in camera_sources:
    #     if camera_info['name'] == name:
    #         # camera_info['safearea'] = data.get('safearea', camera_info['safearea'])
    #         camera_info['models'] = models
    #         print(camera_info)      
    return {
            'status':200,
            'method':"修改成功",
            "camera": config_data['cameras'][index]['name'],
            "models": config_data['cameras'][index]['models']
            }