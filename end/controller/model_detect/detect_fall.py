import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
from controller.send_email import send_email
import time
from datetime import datetime  # 匯入 datetime 模組

model = load_model('controller/model/keras_model.h5', compile=False)
#引入# from cnn_cloth import color_detection會發生錯誤! 要分成兩個程式碼
w, h = 640, 480  # 視窗大小
draw = np.zeros((h, w, 4), dtype='uint8')  # 用於顯示安全區的畫布
# Mediapipe 模組初始化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils  # 用於繪製關鍵點和骨架
#繪製畫面變數
dots = []  # 暫存繪製過程中的座標
safe_zone_contour = None

# 設置間隔時間，10 分鐘 = 600 秒
EMAIL_INTERVAL = 30
# 記錄上次寄送郵件的時間（初始化為一個很早的時間）
last_email_time = time.time()-EMAIL_INTERVAL

def is_point_in_area(point, area):
    # 使用 cv2.pointPolygonTest 判斷點是否在多邊形內
    safe_zone_contour = np.array(area, dtype=np.int32)
    return cv2.pointPolygonTest(safe_zone_contour, point, False) >= 0

def detect_fall_func(pose_landmarks):
    if pose_landmarks:
        # 取得身體的關鍵點位置
        landmarks = pose_landmarks.landmark
        shoulder_y = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y
        hip_y = landmarks[mp_pose.PoseLandmark.LEFT_HIP].y
        head_y = landmarks[mp_pose.PoseLandmark.NOSE].y

        # 比較肩膀、臀部和頭部的高度
        if abs(shoulder_y - hip_y) < 0.3 and abs(hip_y - head_y) < 0.3:
            return True  # 可能跌倒
    return False

def count_points_in_safe_area(pose_landmarks, safe_area):
    # 計算在安全區內的點數
    count = 0
    if pose_landmarks:
        for landmark in pose_landmarks.landmark:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            if is_point_in_area((x, y), safe_area):
                count += 1
    return count

def detect_fall(frame,safe_area,camera_name):
    global last_email_time  # 使用 global 關鍵字聲明 last_email_time 為全局變數
    # 縮放攝像頭輸出畫面
    frame = cv2.resize(frame, (w, h))

    # 將影格轉換為 RGB，並送入 Mediapipe 進行肢體檢測
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(frame_rgb)

    danger = False  # 假設無危險

    # 檢測到肢體關節點後，判斷是否有任何點進入安全區
    if result.pose_landmarks:
        # 繪製骨架和關鍵點
        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # 計算在安全區內的點數
        points_in_safe_area = count_points_in_safe_area(result.pose_landmarks, safe_area)
        
        # 更新跌倒檢測邏輯
        if detect_fall_func(result.pose_landmarks):
            # 判斷是否有一半以上的點在安全區內
            total_points = len(result.pose_landmarks.landmark)
            if points_in_safe_area / total_points >= 0.5:
                status = 'safe'
            else:
                status = 'fall'
        else:
            # 沒有跌倒的情況下，根據是否有點在安全區內顯示狀態
            status = 'safe' if points_in_safe_area > 0 else 'safe'
    else:
        status = 'safe'

    # 根據結果顯示 "safe" 或 "fall"
    color = (0, 255, 0) if status == 'safe' else (0, 0, 255)
    
    #如果偵測到跌倒且距離上次寄送時間已超過 10 分鐘
    current_time = time.time()
    if(status == "fall"and current_time - last_email_time > EMAIL_INTERVAL):
        formatted_time = datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
        # send_email(f"{camera_name}有人跌倒! 時間:{formatted_time}")
        last_email_time = current_time  # 更新上次寄送郵件的時間
    # 顯示 "safe" 或 "fall" 在畫面右上角
    cv2.putText(frame, status.upper(), (w - 150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
    return frame