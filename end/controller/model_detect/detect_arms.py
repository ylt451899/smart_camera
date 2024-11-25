from ultralytics import YOLO
import cv2
from controller.send_email import send_email
import time
from datetime import datetime  # 匯入 datetime 模組

# 載入模型
arms_model = YOLO('controller/model/best.pt')
# 将模型移至 GPU（如果可用）
arms_model.to("cuda:0")

# 設置間隔時間，10 分鐘 = 600 秒
EMAIL_INTERVAL = 30
# 記錄上次寄送郵件的時間（初始化為一個很早的時間）
last_email_time = time.time()-EMAIL_INTERVAL

# 模型檢測函數 (偵測武器和人)
def detect_arms(frame,camera_name):
    global last_email_time  # 使用 global 關鍵字聲明 last_email_time 為全局變數
    arms_results = arms_model.predict(frame, verbose=False)
    suspicious_detected = False
    for box in arms_results[0].boxes.data:
        x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # 紅色框
        suspicious_detected = True  # 檢測到武器或嫌疑人
        
    #如果偵測到武器且距離上次寄送時間已超過 10 分鐘
    current_time = time.time()
    if suspicious_detected and current_time - last_email_time > EMAIL_INTERVAL:
        # 將 current_time 轉換為好觀察的格式
        formatted_time = datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
        send_email(f"{camera_name}有人進入危險區域! 時間:{formatted_time}")
        last_email_time = current_time  # 更新上次寄送郵件的時間
    return frame