
# from ultralytics import YOLO
# import cv2
# import numpy as np
# import pandas as pd
# from sklearn.cluster import KMeans
# from keras.models import load_model
# from PIL import Image, ImageDraw
# from sql_feature import insert_feature
# from sql_personInformation import insert_personInformation,get_person_id
# import json
# import os

# model_cloth = YOLO("controller/model/cloth.pt", "v8")  

# # 衣物辨識
# # model_person = YOLO('../yolov8n.pt')
# model_color = load_model('controller/model/model_restNet3.h5', compile=False)  # 替换为你模型的路径
# person_num = 0
# # 在程式啟動時，從資料庫抓取已存在的 person_id
# existing_person_ids = get_person_id()  # 這是一個假設的函數，你需要實作它來抓取資料
# # 将模型移至 GPU（如果可用）
# model_cloth.to("cuda:0")
# color_dict = ['black', 'blue', 'brown', 'cyan', 'gray', 'green', 'orange', 'pink', 'purple', 'red', 'white', 'yellow']
# label_dict = {
# 0: "sunglass",
# 1: "hat",
# 2: "jacket",
# 3: "shirt",
# 4: "pants",
# 5: "shorts",
# 6: "skirt",
# 7: "dress",
# 8: "bag",
# 9: "shoe",
# }

# def color_detection(frame,person_name,camera_name,current_time):
#     global existing_person_ids,color_dict,label_dict  # 使用全局變數來儲存已存在的 person_id
#     detect_dict = []
    
#     result_cloth = model_cloth.predict(frame, verbose=False)
#     if(person_name not in existing_person_ids):
#         aa = 0
#         personId = insert_personInformation(camera_name,current_time,current_time)
#     for result in result_cloth:
#         # 将张量转换为 Python 列表
#         box_list = result.boxes.xyxy.tolist()
#         label_list = result.boxes.cls.tolist()
#         for i in range(0, len(box_list)):
#             cloth_box = box_list[i]
#             cloth_label = label_dict[int(label_list[i])]
#             # 获取检测框坐标（在整个图像上的坐标）
#             cloth_x1, cloth_y1, cloth_x2, cloth_y2 = map(int, cloth_box[:4])
#             # 提取检测框内的图像区域
#             roi_cloth = frame[cloth_y1:cloth_y2, cloth_x1:cloth_x2]
#             # 使用KMeans聚类算法获取主要颜色
#             flattened_roi = roi_cloth.reshape(-1, 3)
#             kmeans = KMeans(n_clusters=1)
#             kmeans.fit(flattened_roi)
#             main_color = kmeans.cluster_centers_[0].astype(int)

#             # 生成顏色圖片
#             # size = (224, 224)
#             size = (24, 24)
#             image = Image.new('RGB', size)
#             # 创建一个ImageDraw对象
#             draw = ImageDraw.Draw(image)
#             # 在图像上绘制一个填充有指定颜色的矩形
#             draw.rectangle([0, 0, size[0], size[1]], fill=(int(main_color[2]), int(main_color[1]), int(main_color[0])))

#             image_array = np.expand_dims(image, axis=0)

#             # 辨識顏色
#             predictions = model_color.predict(image_array)
#             # 获取预测结果
#             predicted_label_index = np.argmax(predictions)
#             predicted_class = color_dict[predicted_label_index]
            
#             cloth_color_dict = {'cloth':cloth_label ,'color_name':predicted_class , 'color':(int(main_color[0]), int(main_color[1]), int(main_color[2]))}
#             detect_dict.append(cloth_color_dict)
#             # 在原图上绘制检测框和颜色信息
#             cv2.rectangle(frame, (cloth_x1,cloth_y1), (cloth_x2,cloth_y2),
#                         (int(main_color[0]), int(main_color[1]), int(main_color[2])), 2)
#             cv2.putText(frame, f"{cloth_color_dict['cloth']},{cloth_color_dict['color_name']}", (cloth_x1, cloth_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (int(main_color[0]), int(main_color[1]), int(main_color[2])), 2)  # 添加文字
#             # print(predicted_class)
#             # 新增進資料庫
#         Feature_item = []
#         Feature_color_item = []
#         for i in detect_dict:
#             Feature_item.append(i['cloth'])
#             Feature_color_item.append(i['color_name'])
#         if(person_name not in existing_person_ids):
#             insert_feature(personId,Feature_item,Feature_color_item)
#             existing_person_ids.append(person_name)  # 新增新的 person_id 到陣列中
#             cv2.imwrite(f'images/{personId}.jpg', frame)  # 保存到文件    


#查詢影片網址:https://www.pexels.com/search/videos/people/
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18
from ultralytics import YOLO
import cv2
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
# import tensorflow as tf
# from tensorflow import keras
# from tensorflow.keras import layers
# from keras.models import load_model
from PIL import Image, ImageDraw
from model.sql_feature import insert_feature
import json
import os
import shutil
import time

output_all_person_cloth = []
# model_color = load_model('controller\\model\\model_restNet3.h5', compile=False)  
#設置顏色辨識模型
# 设置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 定义数据转换
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])
# 加载预训练模型并修改最后一层
model_color = resnet18(pretrained=False)
model_color.fc = nn.Linear(model_color.fc.in_features, 11)  # 假设你有11个颜色分类
model_color.load_state_dict(torch.load('controller/model/color_classification_model_pro4.pth'))
model_color = model_color.to(device)
model_color.eval()

# 颜色标签
color_dict = ['black', 'blue', 'brown', 'gray', 'green', 'orange', 'pink', 'purple', 'red', 'white', 'yellow']

model_cloth = YOLO("controller/model/cloth_school_pro2.pt", "v8")  
# model_color = keras.models.load_model('controller/model/model_restNet3.h5', compile=False)  

processed_images = set()  # 用来记录已处理的图片

# 尝试从文件加载已处理的图片名称
if os.path.exists("processed_images.json"):
    with open("processed_images.json", "r") as file:
        processed_images = set(json.load(file))

model_cloth.to("cuda:0")
# color_dict = ['black', 'blue', 'brown', 'cyan', 'gray', 'green', 'orange', 'pink', 'purple', 'red', 'white', 'yellow']
# label_dict = {
#     0: "sunglass",
#     1: "hat",
#     2: "jacket",
#     3: "shirt",
#     4: "pants",
#     5: "shorts",
#     6: "skirt",
#     7: "dress",
#     8: "bag",
#     9: "shoe",
# }
label_dict = {
    0:"long sleeves",
    1:"trousers",
    2:"short sleeves",
    3:"shorts",
    4:"hat",
    5:"shoe",
    6:"pretend",
    7:"skirt",
}
def color_detection(frame, person_name, image_path):
    global color_dict, label_dict, processed_images  
    detect_dict = []
    if person_name in processed_images:
        print(f"图片 {person_name} 已处理，跳过。")
        return  # 如果图片已处理，跳过处理
    result_cloth = model_cloth.predict(frame, verbose=False)
    for result in result_cloth:
        box_list = result.boxes.xyxy.tolist()
        label_list = result.boxes.cls.tolist()
        for i in range(len(box_list)):
            cloth_box = box_list[i]
            cloth_label = label_dict[int(label_list[i])]
            cloth_x1, cloth_y1, cloth_x2, cloth_y2 = map(int, cloth_box[:4])
            roi_cloth = frame[cloth_y1:cloth_y2, cloth_x1:cloth_x2]
            
            flattened_roi = roi_cloth.reshape(-1, 3)
            kmeans = KMeans(n_clusters=1)
            kmeans.fit(flattened_roi)
            main_color = kmeans.cluster_centers_[0].astype(int)

            size = (224, 224)
            image = Image.new('RGB', size)
            draw = ImageDraw.Draw(image)
            draw.rectangle([0, 0, size[0], size[1]], fill=(int(main_color[2]), int(main_color[1]), int(main_color[0])))
            #原本顏色辨識
            # image_array = np.expand_dims(image, axis=0)
            # predictions = model_color.predict(image_array)
            # predicted_label_index = np.argmax(predictions)
            # predicted_color_class = color_dict[predicted_label_index]
            # 将颜色方块转换为Tensor并传递给模型进行预测
            image_tensor = transform(image).unsqueeze(0).to(device)
            with torch.no_grad():
                output = model_color(image_tensor)
                _, predicted = torch.max(output, 1)
            
            predicted_color_class = color_dict[predicted.item()]

            cloth_color_dict = {'cloth': cloth_label, 'color_name': predicted_color_class, 'color': (int(main_color[0]), int(main_color[1]), int(main_color[2]))}
            detect_dict.append(cloth_color_dict)

            cv2.rectangle(frame, (cloth_x1, cloth_y1), (cloth_x2, cloth_y2),
                          (int(main_color[0]), int(main_color[1]), int(main_color[2])), 2)
            cv2.putText(frame, f"{cloth_color_dict['cloth']},{cloth_color_dict['color_name']}",
                        (cloth_x1, cloth_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        (int(main_color[0]), int(main_color[1]), int(main_color[2])), 2)
        cv2.imwrite(f'static/images/after-predict/{person_name}.jpg', frame)  # 保存到文件   
        # cv2.imwrite(f'static/images/after-predict/{person_name}.jpg', frame)  # 保存到文件    
        print(detect_dict)
        Feature_item = []
        Feature_color_item = []
        for i in detect_dict:
            Feature_item.append(i['cloth']) 
            Feature_color_item.append(i['color_name'])
        insert_feature(person_name, Feature_item, Feature_color_item)
        os.remove(f'static/images/non-predict/{person_name}.jpg')
    output_all_person_cloth.append([person_name, Feature_item, Feature_color_item])

    # 移動檔案
    # shutil.move(f"images/non-predict/{person_name}.jpg", f"images/after-predict/{person_name}.jpg")
    # processed_images.add(person_name)
    # # 将已处理图片名称保存到文件
    # with open("processed_images.json", "w") as file:
    #     json.dump(list(processed_images), file)

def process_images_in_folder(folder_path):
    # processed_images = set()
    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            image = cv2.imread(image_path)
            color_detection(image, filename.split(".")[0], folder_path)
            # processed_images.add(filename)

# 使用示例
while True:
    process_images_in_folder('static/images/non-predict')
    print("predict_cloth")
    time.sleep(30)  # Sleep for 30 seconds before running again
# process_images_in_folder('images/non-predict')
# print("predict_cloth")

# for i in output_all_person_cloth:
#     print(i)
