# import face_recognition
# import cv2
# import numpy as np
# import pickle
# import json
# RED_COLOR = (200, 58, 76)
# WHITE_COLOR = (255, 255, 255)
# tolerance = 0.6  # 比對閾值
# #載入人臉辨識模型
# def load_known_faces():
#     with open('faces.json', 'r') as f:
#         known_face_list = json.load(f)

#     for data in known_face_list:
#         img = cv2.imread(data['filename'])
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         data['encode'] = face_recognition.face_encodings(img)[0]

#     known_face_encodes = [data['encode'] for data in known_face_list]
    
#     return known_face_list, known_face_encodes
# # with open('controller/model/faces.dat', 'rb') as f:
# #     known_face_list = pickle.load(f)
    
# # known_face_encodes = [data['encode'] for data in known_face_list]
# # tolerance = 0.6  # 比對閾值
# # with open('faces.json', 'r') as f:
# #     known_face_list = json.load(f)

# # for data in known_face_list:
# #     img = cv2.imread(data['filename'])
# #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# #     data['encode'] = face_recognition.face_encodings(img)[0]

# # known_face_encodes = [data['encode'] for data in known_face_list]

# def draw_locations(img, match_results):
#     for match_result in match_results:
#         y1, x2, y2, x1 = match_result['location']
#         cv2.rectangle(img, (x1, y1), (x2, y2), RED_COLOR, 2)
#         cv2.rectangle(img, (x1, y2 + 35), (x2, y2), RED_COLOR, cv2.FILLED)
#         cv2.putText(img, match_result['name'], (x1 + 10, y2 + 25), cv2.FONT_HERSHEY_COMPLEX, 0.8, WHITE_COLOR, 2)


# def detect_face(frame):
#     # 每次检测前重新加载最新的faces.json
#     known_face_list, known_face_encodes = load_known_faces()
    
#     match_results = []
#     img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
#     # img = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
#     cur_face_locs = face_recognition.face_locations(img)
#     cur_face_encodes = face_recognition.face_encodings(img, cur_face_locs)

#     for cur_face_encode, cur_face_loc in zip(cur_face_encodes, cur_face_locs):
#         face_distance_list = face_recognition.face_distance(known_face_encodes, cur_face_encode)

#         min_distance_index = np.argmin(face_distance_list)
#         if face_distance_list[min_distance_index] < tolerance:
#             name = known_face_list[min_distance_index]['name']
#         else:
#             name = 'unknown'

#         match_results.append({
#             'name': name,
#             'location': cur_face_loc,
#         })

#     for match_result in match_results:
#         y1, x2, y2, x1 = match_result['location']
#         cv2.rectangle(img, (x1, y1), (x2, y2), RED_COLOR, 2)
#         cv2.rectangle(img, (x1, y2 + 35), (x2, y2), RED_COLOR, cv2.FILLED)
#         cv2.putText(img, match_result['name'], (x1 + 10, y2 + 25), cv2.FONT_HERSHEY_COMPLEX, 0.8, WHITE_COLOR, 2)

#     return img
#     # cur_face_locs = face_recognition.face_locations(img)
#     # cur_face_encodes = face_recognition.face_encodings(img, cur_face_locs)

#     # for cur_face_encode, cur_face_loc in zip(cur_face_encodes, cur_face_locs):
#     #     face_distance_list = face_recognition.face_distance(known_face_encodes, cur_face_encode)

#     #     min_distance_index = np.argmin(face_distance_list)
#     #     if face_distance_list[min_distance_index] < tolerance:
#     #         name = known_face_list[min_distance_index]['name']
#     #     else:
#     #         name = 'unknown'

#     #     match_results.append({
#     #         'name': name,
#     #         'location': cur_face_loc,
#     #     })

#     # for match_result in match_results:
#     #     y1, x2, y2, x1 = match_result['location']
#     #     cv2.rectangle(img, (x1, y1), (x2, y2), RED_COLOR, 2)
#     #     cv2.rectangle(img, (x1, y2 + 35), (x2, y2), RED_COLOR, cv2.FILLED)
#     #     cv2.putText(img, match_result['name'], (x1 + 10, y2 + 25), cv2.FONT_HERSHEY_COMPLEX, 0.8, WHITE_COLOR, 2)
#     # return img
import face_recognition
import cv2
import numpy as np
import json

# 常數設定
RED_COLOR = (200, 58, 76)
WHITE_COLOR = (255, 255, 255)
tolerance = 0.6  # 比對閾值

# 載入人臉資料
def load_known_faces():
    with open('faces.json', 'r') as f:
        known_face_list = json.load(f)

    for data in known_face_list:
        img = cv2.imread(data['filename'])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        data['encode'] = face_recognition.face_encodings(img)[0]

    known_face_encodes = [data['encode'] for data in known_face_list]
    return known_face_list, known_face_encodes

# 初始化已知人臉（只需執行一次）
known_face_list, known_face_encodes = load_known_faces()

# 畫出人臉框與名字
def draw_locations(img, match_results):
    for match_result in match_results:
        y1, x2, y2, x1 = match_result['location']
        cv2.rectangle(img, (x1, y1), (x2, y2), RED_COLOR, 2)
        cv2.rectangle(img, (x1, y2 + 35), (x2, y2), RED_COLOR, cv2.FILLED)
        cv2.putText(img, match_result['name'], (x1 + 10, y2 + 25), cv2.FONT_HERSHEY_COMPLEX, 0.8, WHITE_COLOR, 2)

# 偵測人臉
def detect_face(frame):
    # 降低圖片解析度，加快辨識速度
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    cur_face_locs = face_recognition.face_locations(rgb_small_frame)
    cur_face_encodes = face_recognition.face_encodings(rgb_small_frame, cur_face_locs)

    match_results = []
    for cur_face_encode, cur_face_loc in zip(cur_face_encodes, cur_face_locs):
        face_distance_list = face_recognition.face_distance(known_face_encodes, cur_face_encode)
        
        # 確保 face_distance_list 非空
        if len(face_distance_list) == 0:
            continue

        min_distance_index = np.argmin(face_distance_list)
        name = known_face_list[min_distance_index]['name'] if face_distance_list[min_distance_index] < tolerance else 'unknown'
        
        # 還原原始圖片的座標
        top, right, bottom, left = [int(v * 2) for v in cur_face_loc]
        match_results.append({
            'name': name,
            'location': (top, right, bottom, left),
        })

    draw_locations(frame, match_results)
    return frame
