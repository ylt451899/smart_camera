# import cv2
# import numpy as np
# import json

# dots = []  # 暫存繪製過程中的座標
# safe_zone_contour = None
# w, h = 640, 480  # 視窗大小

# # 開啟攝像頭
# # cap = cv2.VideoCapture(0)

# # if not cap.isOpened():
# #     print("Cannot open camera")
# #     exit()
# # 讀取圖片
# image_path = '../video/start/1.png'  # 將此路徑替換為你想顯示的圖片路徑
# frame = cv2.imread(image_path)

# if frame is None:
#     print("Cannot open image")
#     exit()

# frame = cv2.resize(frame, (w, h))  # 調整圖片大小

# draw = np.zeros((h, w, 4), dtype='uint8')  # 用於保存繪製安全區的畫布

# def show_xy(event, x, y, flags, param):
#     global dots, draw
#     if event == cv2.EVENT_LBUTTONDOWN:  # 按下滑鼠左鍵
#         dots.append((x, y))
#     elif event == cv2.EVENT_LBUTTONUP:  # 放開滑鼠左鍵
#         draw_area()
#         dots = []
#     elif event == cv2.EVENT_MOUSEMOVE and flags & cv2.EVENT_FLAG_LBUTTON:  # 按住滑鼠左鍵移動
#         dots.append((x, y))
#         if len(dots) > 1:
#             cv2.line(draw, dots[-2], dots[-1], (0, 0, 255, 255), 2)  # 繪製連續的線段

# def draw_area():
#     global dots, draw, safe_zone_contour
#     if len(dots) < 3:
#         return
#     safe_zone_contour = np.array(dots, dtype=np.int32)
#     area = cv2.contourArea(safe_zone_contour)
#     if area > 100:
#         cv2.drawContours(draw, [safe_zone_contour], -1, (0, 0, 255, 128), cv2.FILLED)  # 畫出安全區
    
#     save_safe_area(dots)  # 將座標保存到 config.json

# def save_safe_area(dots):
#     # 更新 config.json 中的安全區
#     with open('../config.json', 'r') as f:
#         data = json.load(f)
    
#     # 將新的安全區座標存入 camera1
#     data['cameras'][0]['safearea'] = dots

#     with open('../config.json', 'w') as f:
#         json.dump(data, f, indent=4)

#     print("安全區已保存至 config.json")

# # 設置滑鼠回調函數
# cv2.namedWindow('safearea')
# cv2.setMouseCallback('safearea', show_xy)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Cannot receive frame (stream end?). Exiting ...")
#         break

#     # 縮放攝像頭輸出畫面
#     frame = cv2.resize(frame, (w, h))
    
#     # 顯示安全區
#     for i in range(w):
#         frame[:, i, 0] = frame[:, i, 0] * (1 - draw[:, i, 3] / 255) + draw[:, i, 0] * (draw[:, i, 3] / 255)
#         frame[:, i, 1] = frame[:, i, 1] * (1 - draw[:, i, 3] / 255) + draw[:, i, 1] * (draw[:, i, 3] / 255)
#         frame[:, i, 2] = frame[:, i, 2] * (1 - draw[:, i, 3] / 255) + draw[:, i, 2] * (draw[:, i, 3] / 255)

#     cv2.imshow('safearea', frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()

import cv2
import numpy as np
import json

dots = []  # 暫存繪製過程中的座標
safe_zone_contour = None
w, h = 640, 480  # 視窗大小

# 讀取圖片
image_path = '../video/start/1.png'  # 將此路徑替換為你想顯示的圖片路徑
frame = cv2.imread(image_path)

if frame is None:
    print("Cannot open image")
    exit()

frame = cv2.resize(frame, (w, h))  # 調整圖片大小

draw = np.zeros((h, w, 4), dtype='uint8')  # 用於保存繪製安全區的畫布

def show_xy(event, x, y, flags, param):
    global dots, draw
    if event == cv2.EVENT_LBUTTONDOWN:  # 按下滑鼠左鍵
        dots.append((x, y))
    elif event == cv2.EVENT_LBUTTONUP:  # 放開滑鼠左鍵
        draw_area()
        dots = []
    elif event == cv2.EVENT_MOUSEMOVE and flags & cv2.EVENT_FLAG_LBUTTON:  # 按住滑鼠左鍵移動
        dots.append((x, y))
        if len(dots) > 1:
            cv2.line(draw, dots[-2], dots[-1], (0, 0, 255, 255), 2)  # 繪製連續的線段

def draw_area():
    global dots, draw, safe_zone_contour
    if len(dots) < 3:
        return
    safe_zone_contour = np.array(dots, dtype=np.int32)
    area = cv2.contourArea(safe_zone_contour)
    if area > 100:
        cv2.drawContours(draw, [safe_zone_contour], -1, (0, 0, 255, 128), cv2.FILLED)  # 畫出安全區
    
    save_safe_area(dots)  # 將座標保存到 config.json

def save_safe_area(dots):
    # 更新 config.json 中的安全區
    with open('../config.json', 'r') as f:
        data = json.load(f)
    
    # 將新的安全區座標存入 camera1
    data['cameras'][0]['safearea'] = dots

    with open('../config.json', 'w') as f:
        json.dump(data, f, indent=4)

    print("安全區已保存至 config.json")

# 設置滑鼠回調函數
cv2.namedWindow('safearea')
cv2.setMouseCallback('safearea', show_xy)

while True:
    # 顯示安全區
    display_frame = frame.copy()
    
    for i in range(w):
        display_frame[:, i, 0] = display_frame[:, i, 0] * (1 - draw[:, i, 3] / 255) + draw[:, i, 0] * (draw[:, i, 3] / 255)
        display_frame[:, i, 1] = display_frame[:, i, 1] * (1 - draw[:, i, 3] / 255) + draw[:, i, 1] * (draw[:, i, 3] / 255)
        display_frame[:, i, 2] = display_frame[:, i, 2] * (1 - draw[:, i, 3] / 255) + draw[:, i, 2] * (draw[:, i, 3] / 255)

    cv2.imshow('safearea', display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
