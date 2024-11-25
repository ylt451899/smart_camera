import cv2
import numpy as np
import mediapipe as mp

# 視窗大小
w, h = 640, 480

# Mediapipe 模組初始化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils  # 用於繪製關鍵點和骨架

# 開啟攝像頭
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

def detect_fall(pose_landmarks):
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

while True:
    ret, frame = cap.read()
    if not ret:
        print("Cannot receive frame (stream end?). Exiting ...")
        break

    # 縮放攝像頭輸出畫面
    frame = cv2.resize(frame, (w, h))

    # 將影格轉換為 RGB，並送入 Mediapipe 進行肢體檢測
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(frame_rgb)

    status = 'safe'  # 預設為安全

    # 檢測到肢體關節點後，更新跌倒檢測邏輯
    if result.pose_landmarks:
        # 繪製骨架和關鍵點
        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        if detect_fall(result.pose_landmarks):
            status = 'fall'  # 偵測到跌倒

    # 根據結果顯示 "safe" 或 "fall"
    color = (0, 255, 0) if status == 'safe' else (0, 0, 255)
    
    # 顯示 "safe" 或 "fall" 在畫面右上角
    cv2.putText(frame, status.upper(), (w - 150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

    cv2.imshow('Fall Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()