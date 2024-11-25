import cv2
import numpy as np
import json
import mediapipe as mp

w, h = 640, 480  # 視窗大小
draw = np.zeros((h, w, 4), dtype='uint8')  # 用於顯示安全區的畫布

# Mediapipe 模組初始化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# 開啟攝像頭
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("../video/1.mp4")
if not cap.isOpened():
    print("Cannot open camera")
    exit()

def load_safe_area():
    # 從 config.json 加載安全區
    with open('../config.json', 'r') as f:
        data = json.load(f)
    
    # 讀取 camera1 的安全區座標
    if 'safearea' in data['cameras'][0]:
        return data['cameras'][0]['safearea']
    return []

def redraw_previous_safe_area(safearea):
    global draw
    if len(safearea) > 0:
        safe_zone_contour = np.array(safearea, dtype=np.int32)
        cv2.drawContours(draw, [safe_zone_contour], -1, (0, 0, 255, 128), cv2.FILLED)  # 繪製安全區

def is_point_in_safe_area(point, safearea):
    # 使用 cv2.pointPolygonTest 判斷點是否在多邊形內
    safe_zone_contour = np.array(safearea, dtype=np.int32)
    return cv2.pointPolygonTest(safe_zone_contour, point, False) >= 0

# 加載並顯示先前保存的安全區
safe_area = load_safe_area()
redraw_previous_safe_area(safe_area)

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

    danger = False  # 假設無危險

    # 檢測到肢體關節點後，判斷是否有任何點進入安全區
    if result.pose_landmarks:
        for landmark in result.pose_landmarks.landmark:
            # 取得肢體點的 x, y 座標
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            
            # 判斷該點是否在安全區內
            if is_point_in_safe_area((x, y), safe_area):
                danger = True
                break

    # 顯示 "danger" 在畫面右上角，如果有肢體進入安全區
    if danger:
        cv2.putText(frame, 'DANGER', (w - 150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # 顯示安全區
    for i in range(w):
        frame[:, i, 0] = frame[:, i, 0] * (1 - draw[:, i, 3] / 255) + draw[:, i, 0] * (draw[:, i, 3] / 255)
        frame[:, i, 1] = frame[:, i, 1] * (1 - draw[:, i, 3] / 255) + draw[:, i, 1] * (draw[:, i, 3] / 255)
        frame[:, i, 2] = frame[:, i, 2] * (1 - draw[:, i, 3] / 255) + draw[:, i, 2] * (draw[:, i, 3] / 255)

    cv2.imshow('safearea', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
