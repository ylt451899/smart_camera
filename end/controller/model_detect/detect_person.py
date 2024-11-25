from ultralytics import YOLO
import cv2
from model.sql_personInformation import insert_personInformation,get_person_id,update_personInformation
import time
import shutil
from datetime import datetime
import numpy as np
from controller.model_detect.detect_fall import is_point_in_area
# 載入模型
model_person = YOLO('controller/model/yolov8n.pt',verbose=False)
# 将模型移至 GPU（如果可用）
model_person.to("cuda:0")
# 模型檢測函數 (偵測武器和人)
# 儲存每個人最大區塊尺寸和 person_id 的字典
person_max_size = {}
# 儲存每個人最後一次成功追蹤的時間
person_last_seen_time = {}
# 設定消失判斷的超時時間 (秒)
disappear_timeout = 2

def count_person(frame):
    results = model_person.predict(frame)
    person_names = model_person.names
    # 檢查是否有新的人物尚未被追蹤
    # 過濾出所有屬於 "person" 的物體
    person_boxes = [box for box in results[0].boxes.data if person_names[int(box[5])] == "person"]
    # 計算屬於 "person" 的框的數量
    num = len(person_boxes)
    for box in results[0].boxes.data:
         if person_names[int(box[5])] == "person":
            # num += 1
            # x, y, w, h
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # 紅色框
    cv2.putText(frame, f"person:{num}", (10, 30 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return frame

# def detect_person(frame, camera_info):
#     min_width = 30
#     min_height = 60
#     current_time = time.time()
    
#     results = model_person.predict(frame)
#     person_names = model_person.names

#     success, boxes = camera_info["trackers"].update(frame)
#     camera_name = camera_info["name"].split("era")[1]
    
#     persons_to_remove = []
#     tracked_persons = list(camera_info["trackers"].getObjects())  # 取得正在追蹤的物件

#     # 檢查是否有新的人物尚未被追蹤
#     for box in results[0].boxes.data:
#         if person_names[int(box[5])] == "person":
#             # 檢查該區塊是否已在追蹤器中，若未被追蹤，則新增追蹤器
#             bbox = (int(box[0]), int(box[1]), int(box[2]) - int(box[0]), int(box[3]) - int(box[1]))
#             found_existing = False
#             for tracked_box in tracked_persons:
#                 tracked_bbox = (int(tracked_box[0]), int(tracked_box[1]), 
#                                 int(tracked_box[2]), int(tracked_box[3]))
#                 if iou(tracked_bbox, bbox) > 0.05:  # 使用IoU檢查是否已經追蹤過
#                     found_existing = True
#                     break
            
#             if not found_existing:
#                 tracker = cv2.legacy.TrackerCSRT_create()
#                 camera_info["trackers"].add(tracker, frame, bbox)
#                 # 初始化人物信息，這裡也可以更新其他邏輯
#                 person_name = "person" + str(len(camera_info["trackers"].getObjects()))
#                 personId = insert_personInformation(camera_name, datetime.now().strftime("%Y-%m-%d %H:%M"), datetime.now().strftime("%Y-%m-%d %H:%M"))
#                 person_max_size[person_name] = (bbox[2], bbox[3], personId)
#                 person_last_seen_time[person_name] = current_time
#                 cv2.imwrite(f'static/images/incamera/{personId}.jpg', frame[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]])
    
#     # 遍歷追蹤器中的人物，進行處理
#     for i, newbox in enumerate(boxes):
#         x, y, w, h = map(int, newbox)
#         person_name = "person" + str(i)

#         if w >= min_width and h >= min_height:
#             person_frame = frame[y:y+h, x:x+w]
#             cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
#             # cv2.putText(frame, "person", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
#             if person_name in person_max_size:
#                 prev_w, prev_h, personId = person_max_size[person_name]
#                 if w * h > prev_w * prev_h:
#                     person_max_size[person_name] = (w, h, personId)
#                     cv2.imwrite(f'static/images/incamera/{personId}.jpg', person_frame)
#                 person_last_seen_time[person_name] = current_time
#         else:
#             if person_name in person_last_seen_time and current_time - person_last_seen_time[person_name] > disappear_timeout:
#                 persons_to_remove.append(person_name)

#     for person_name in persons_to_remove:
#         prev_w, prev_h, personId = person_max_size[person_name]
#         update_personInformation(personId, datetime.now().strftime("%Y-%m-%d %H:%M"))
#         shutil.move(f'static/images/incamera/{personId}.jpg', f'static/images/non-predict/{personId}.jpg')
#         del person_max_size[person_name]
#         del person_last_seen_time[person_name]
#         print(f"{person_name} 已離開畫面，清理相關資料。")

#     return True

# def iou(box1, box2):
#     # box1 和 box2 格式為 (x, y, w, h)
#     x1_min, y1_min = box1[0], box1[1]
#     x1_max, y1_max = box1[0] + box1[2], box1[1] + box1[3]
    
#     x2_min, y2_min = box2[0], box2[1]
#     x2_max, y2_max = box2[0] + box2[2], box2[1] + box2[3]
    
#     # 計算重疊區域的坐標
#     x_overlap_min = max(x1_min, x2_min)
#     y_overlap_min = max(y1_min, y2_min)
#     x_overlap_max = min(x1_max, x2_max)
#     y_overlap_max = min(y1_max, y2_max)
    
#     # 計算重疊區域的寬度和高度
#     overlap_width = max(0, x_overlap_max - x_overlap_min)
#     overlap_height = max(0, y_overlap_max - y_overlap_min)
    
#     # 計算重疊區域和兩個框的面積
#     overlap_area = overlap_width * overlap_height
#     box1_area = (x1_max - x1_min) * (y1_max - y1_min)
#     box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    
#     # 計算 IoU
#     total_area = box1_area + box2_area - overlap_area
#     iou_value = overlap_area / total_area if total_area > 0 else 0
    
#     return iou_value
def detect_person(frame, camera_info):
    current_time = time.time()
    
    # 使用 YOLO 模型進行偵測和追蹤
    # results = model_person.track(source=frame,show=True)
    results = model_person.track(frame, persist=True)
    # 取得所有追蹤的結果
    current_track_ids = set()  # 用於記錄當前偵測到的track_id
    # 取得所有追蹤的結果
    for result in results:
        for box in result.boxes.data:
            # 偵測到的物體類別和追蹤 ID
            # print(box)
            if len(box) > 6:
                cls = int(box[6])
                track_id = int(box[4])
                
                # 如果是 "person"
                if model_person.names[cls] == "person" and track_id is not None:
                    current_track_ids.add(track_id)  # 記錄當前追蹤的track_id
                    x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                    w, h = x2 - x1, y2 - y1
                    
                    # 繪製追蹤框
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f'Person {track_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    # 記錄/更新最大尺寸和時間
                    if track_id not in person_max_size:
                        # 如果是新的人物，初始化記錄
                        personId = insert_personInformation(camera_info["name"], datetime.now().strftime("%Y-%m-%d %H:%M"), datetime.now().strftime("%Y-%m-%d %H:%M"))
                        person_max_size[track_id] = (w, h, personId)
                        person_last_seen_time[track_id] = current_time
                        cv2.imwrite(f'static/images/incamera/{personId}.jpg', frame[y1:y2, x1:x2])
                    else:
                        # 更新追蹤到的人的資訊
                        prev_w, prev_h, personId = person_max_size[track_id]
                        if w is not None and h is not None and w * h > prev_w * prev_h:
                            person_max_size[track_id] = (w, h, personId)
                            cv2.imwrite(f'static/images/incamera/{personId}.jpg', frame[y1:y2, x1:x2])
                        person_last_seen_time[track_id] = current_time
    check_disappeared_persons(current_track_ids, current_time)
    return frame
    # 檢查是否有人物消失

def check_disappeared_persons(current_track_ids, current_time):
    disappeared_ids = []
    # 遍歷所有已追蹤的track_id
    for track_id in list(person_last_seen_time.keys()):
        if track_id not in current_track_ids:  # 如果該ID不在當前的追蹤列表中
            # 檢查最後看到該人物的時間
            last_seen_time = person_last_seen_time[track_id]
            if current_time - last_seen_time > disappear_timeout:  # 超過閾值，認為人物已消失
                prev_w, prev_h, personId = person_max_size[track_id]
                # 更新 SQL 和移動圖片
                update_personInformation(personId, datetime.now().strftime("%Y-%m-%d %H:%M"))
                shutil.move(f'static/images/incamera/{personId}.jpg', f'static/images/non-predict/{personId}.jpg')
                
                # 移除該人物的記錄
                disappeared_ids.append(track_id)
    
    # 從字典中移除消失的track_id
    for track_id in disappeared_ids:
        del person_max_size[track_id]
        del person_last_seen_time[track_id]
    # # 清理超時的追蹤對象
    # persons_to_remove = []
    # for track_id in list(person_max_size.keys()):
    #     if current_time - person_last_seen_time[track_id] > disappear_timeout:
    #         # 若人物超時，更新資料庫並移動圖片
    #         _, _, personId = person_max_size[track_id]
    #         update_personInformation(personId, datetime.now().strftime("%Y-%m-%d %H:%M"))
    #         shutil.move(f'static/images/incamera/{personId}.jpg', f'static/images/non-predict/{personId}.jpg')
    #         persons_to_remove.append(track_id)
    #         print(f"Person {track_id} 已離開畫面，清理相關資料。")
    
    # # 移除超時的追蹤對象
    # for track_id in persons_to_remove:
    #     del person_max_size[track_id]
    #     del person_last_seen_time[track_id]

    

def detect_person_in_danger_area(frame, danger_area):
    # 使用 detect_person 函數獲取檢測到的人物框
    results = model_person.predict(frame)
    person_names = model_person.names
    person_boxes = []
    for box in results[0].boxes.data:
        if person_names[int(box[5])] == "person":
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # 紅色框
            person_boxes.append((x1, y1, x2, y2))
    
    # 檢查是否有框在危險區域內
    boxes_in_danger_area = any(is_box_in_danger_area(box, danger_area) for box in person_boxes)
    
    # 根據是否有框在危險區域內決定狀態
    status = 'has_person' if boxes_in_danger_area else 'non_person'

    # 顯示狀態在畫面左上角
    color = (0, 255, 0) if status == 'non_person' else (0, 0, 255)
    cv2.putText(frame, status.upper(), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
    
    return frame

def is_box_in_danger_area(box, danger_area):
    """判斷人物框的角點是否在多邊形危險區域內"""
    x1, y1, x2, y2 = box  # 人物框的左上角和右下角
    
    # 定义人物框的四个顶点
    points = [(x1, y1), (x2, y2), (x1, y2), (x2, y1)]
    
    # 判斷是否有任意頂點在危險區域內
    for point in points:
        if is_point_in_area(point, danger_area):
            return True
    return False