# -coding: utf-8 -*-
from libpyvivotek import VivotekCamera
from PIL import Image
from io import BytesIO
from flask import Flask, render_template, g, Response, request, send_from_directory,jsonify,url_for
from flask_cors import CORS
from flask_socketio import SocketIO
import base64
import cv2
import threading
import json
import os
from ultralytics import YOLO
from keras.models import load_model
import signal
from datetime import datetime
# import mediapipe as mp
import numpy as np
import pickle
import time
import shutil
# from controller
from controller.search.search_information import select_person_information

#model_detect
from controller.model_detect.detect_arms import detect_arms
from controller.model_detect.detect_person import count_person,detect_person,detect_person_in_danger_area
from controller.model_detect.detect_fall import detect_fall
from controller.model_detect.detect_face import detect_face
#
from controller.draw.safearea import redraw_previous_safe_area
from controller.json_function import read_json,write_json


# 初始化 VivotekCamera
cam = VivotekCamera(
    host='192.168.50.165', 
    port=8080, 
    usr='root', 
    pwd='C110156108',
    digest_auth=False, 
    ssl=False, 
    verify_ssl=False, 
    sec_lvl='admin'
)

# 載入 config.json 文件
with open('config.json', 'r') as f:
    config = json.load(f)
# 初始化每個攝像頭的模型和資源
camera_sources = []
for camera in config["cameras"]:
    cap = cv2.VideoCapture(camera["source"])
    if not cap.isOpened():
        print(f"Failed to open camera source: {camera['source']}")
    camera_sources.append({
        "name": camera["name"],
        "source": cap,
        "models": camera["models"],
        "images": camera["images"],
        "safearea": camera.get("safearea", []),
        "dangerarea": camera.get("dangerarea", []),
        "playback_speed":camera["playback_speed"],
        "frame":None
    })

app = Flask(__name__)
# 啟用 CORS，允許所有來源訪問
CORS(app)
lock = threading.Lock()
socketio = SocketIO(app, cors_allowed_origins='*')

IMAGE_DIR = 'images'  # 您存儲圖片的目錄
UPLOAD_FOLDER = 'uploads'# 設置上傳文件夾的路徑
# 確保圖片目錄存在
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)
# 配置上傳文件夾
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# @app.route("/")
# def index():
#     return render_template("index.html")


#引入# from cnn_cloth import color_detection會發生錯誤! 要分成兩個程式碼
w, h = 640, 480  # 視窗大小
draw = np.zeros((h, w, 4), dtype='uint8')  # 用於顯示安全區的畫布
# Mediapipe 模組初始化
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose()
# mp_drawing = mp.solutions.drawing_utils  # 用於繪製關鍵點和骨架
#繪製畫面變數
dots = []  # 暫存繪製過程中的座標
safe_zone_contour = None
draw = np.zeros((720, 1280, 4), dtype='uint8')  # 用於保存繪製安全區的畫布

# 載入模型
arms_model = YOLO('controller/model/best.pt')
model_person = YOLO('controller/model/yolov8n.pt',verbose=False)
model = load_model('controller/model/keras_model.h5', compile=False)
RED_COLOR = (200, 58, 76)
WHITE_COLOR = (255, 255, 255)
#載入人臉辨識模型
with open('controller/model/faces.dat', 'rb') as f:
    known_face_list = pickle.load(f)
known_face_encodes = [data['encode'] for data in known_face_list]
tolerance = 0.6  # 比對閾值



# 載入 config.json 文件
with open('config.json', 'r') as f:
    config = json.load(f)


# 處理每個攝像頭畫面的函數
def process_frame(frame, camera_info):
    redraw_previous_safe_area("safearea",camera_info["safearea"], frame)
    redraw_previous_safe_area("dangerarea",camera_info["dangerarea"], frame)
    if camera_info["dangerarea"] != []:
        detect_person_in_danger_area(frame,camera_info["dangerarea"])
    for model_choice in camera_info["models"]:
        if model_choice == '1':
            frame = detect_arms(frame,camera_info['name'])  # 偵測武器
        elif model_choice == '2':
            person_count = detect_person(frame, camera_info)  # 偵測人
        elif model_choice == '3':
            frame = detect_face(frame)  # 偵測臉
        elif model_choice == '4':
            frame = detect_fall(frame,camera_info["safearea"],camera_info['name'])  # 偵測人
        elif model_choice == '5':
            frame = count_person(frame)  # 偵測人
        
    return frame

def encode_frame(frame):
    """將影像編碼為 base64."""
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')
# 顯示多個畫面的函數 - 使用多執行緒
def process_camera_feed(camera_info, cap):
    while True:
        # if camera_info['name'] == "camera1":
        #     snapshot = Image.open(BytesIO(cam.snapshot(quality=3)))
        #     open_cv_image = cv2.cvtColor(np.array(snapshot), cv2.COLOR_RGB2BGR)
        #     camera_info['frame'] = process_frame(open_cv_image, camera_info)
        #     # cv2.imshow(f"Feed: {camera_info['name']}", frame)
        # else:
        ret , frame = cap.read()
        if not ret:
            # 如果到達影片結尾，重設幀指標到 0
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue  # 繼續迴圈而不是退出
        # camera_info['frame'] = process_frame(frame, camera_info)
        frame = process_frame(frame, camera_info)
        # 編碼影像
        frame_base64 = encode_frame(frame)
        # 傳送到對應的事件名稱
        socketio.emit(f"camera_stream_{camera_info['name']}", {'frame': frame_base64})
        socketio.sleep(0.03)  # 控制幀率
        # 根據 playback_speed 調整播放速度
        # cv2.waitKey(camera_info['playback_speed'])


def start_cameras_original():
    global camera_sources
    # 初始化每個攝影機的 trackers 和初始化狀態
    with app.app_context():  # 手動推送應用程式上下文
        for camera_info in camera_sources:
            # camera_info["trackers"] = cv2.legacy.MultiTracker_create()
            camera_info["initialized"] = False
            g.camera_sources = camera_info
            # 創建獨立的執行緒來處理每個攝像頭
            threading.Thread(target=process_camera_feed, args=(camera_info, camera_info['source'])).start()



# 生成前端請求的影像流
# def generate_frames(camera_id):
#     global camera_sources
#     # print(camera_sources[camera_id])
#     while True:
#         # cap = cv2.VideoCapture(0)
#         frame = camera_sources[camera_id]["frame"]
#         # ret, frame = cap.read()
#         if frame is not None:
#             ret, buffer = cv2.imencode('.jpg', frame)
#             if not ret:
#                 continue
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                 b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#         else:
#             continue  # 等待下一幀

# # Flask API：選擇監視器的影像流
# @app.route('/video_model_feed/<int:camera_id>')
# def video_feed(camera_id):
#     # print(camera_id)
#     return Response(generate_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')


#繪製安全區域
# 繪製安全區域的函數
# def redraw_previous_safe_area(areaname,area, frame):
#     if area:
#         for i in range(len(area) - 1):
#             start_point = tuple(area[i])
#             end_point = tuple(area[i + 1])
#             if areaname == "safearea":
#                 cv2.line(frame, start_point, end_point, (0, 255, 0), 2)  # 使用紅色繪製線段
#             else:
#                 cv2.line(frame, start_point, end_point, (0, 0, 255), 2)  # 使用紅色繪製線段
#         # 關閉多邊形的線
#         if areaname == "safearea":
#             cv2.line(frame, tuple(area[-1]), tuple(area[0]), (0, 255, 0), 2)
#         else:
#             cv2.line(frame, tuple(area[-1]), tuple(area[0]), (0, 0, 255), 2)
def redraw_previous_safe_area(areaname, area, frame):
    if area:
        for i in range(len(area) - 1):
            # 确保 start_point 和 end_point 是整数元组
            start_point = tuple(map(int, area[i]))
            end_point = tuple(map(int, area[i + 1]))
            if areaname == "safearea":
                cv2.line(frame, start_point, end_point, (0, 255, 0), 2)  # 使用绿色绘制线段
            else:
                cv2.line(frame, start_point, end_point, (0, 0, 255), 2)  # 使用红色绘制线段
        # 关闭多边形的线
        if areaname == "safearea":
            cv2.line(frame, tuple(map(int, area[-1])), tuple(map(int, area[0])), (0, 255, 0), 2)
        else:
            cv2.line(frame, tuple(map(int, area[-1])), tuple(map(int, area[0])), (0, 0, 255), 2)

# 生成前端請求的影像流
def generate_draw_frames(camera_id):
    global camera_sources
    # 讀取圖片並準備繪製框框功能
    frame = cv2.imread(camera_sources[camera_id]["images"])
    # print(camera_sources)
    # frame = cv2.resize(frame, (1280, 720))  # 調整圖片大小
    draw_resized = cv2.resize(draw, (frame.shape[1], frame.shape[0]))  # 調整 draw 大小與 frame 一致
    # print(frame.shape[1], frame.shape[0])
    # cv2.namedWindow('safearea')  # 用於顯示 OpenCV 視窗
    # cv2.setMouseCallback('safearea', show_xy)
    while True:
        display_frame = frame.copy()
        # 畫出安全區
        for i in range(display_frame.shape[1]):
            display_frame[:, i, 0] = display_frame[:, i, 0] * (1 - draw_resized[:, i, 3] / 255) + draw_resized[:, i, 0] * (draw_resized[:, i, 3] / 255)
            display_frame[:, i, 1] = display_frame[:, i, 1] * (1 - draw_resized[:, i, 3] / 255) + draw_resized[:, i, 1] * (draw_resized[:, i, 3] / 255)
            display_frame[:, i, 2] = display_frame[:, i, 2] * (1 - draw_resized[:, i, 3] / 255) + draw_resized[:, i, 2] * (draw_resized[:, i, 3] / 255)

        # 將圖片編碼為 JPG 格式並返回給前端
        ret, buffer = cv2.imencode('.jpg', display_frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
# Flask API：安全區域繪製畫面
@app.route('/images_model_feed/<int:camera_id>')
def images_feed(camera_id):
    # print(camera_id)
    return Response(generate_draw_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

# 畫布function
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

@app.route('/save_safe_area', methods=['POST'])
def save_safe_area():
    data = request.json
    camera_id = data['camera_id']
    area = data['area']
    dots = data['dots']
    # 读取当前的JSON文件
    config_data = read_json()
    config_data['cameras'][camera_id][area] = dots
    # 更新camera_sources
    global camera_sources
    for camera_info in camera_sources:
        if camera_info['name'] == config_data['cameras'][camera_id]['name']:
            camera_info[area] = dots
            # camera_info['models'] = models
            # print(camera_info)
            
    write_json(config_data)

    return jsonify({"message": "安全區已保存"})

@app.route('/delete_safe_area', methods=['POST'])
def delete_safe_area():
    data = request.json
    camera_id = data['camera_id']
    area = data['area']
    # 读取当前的JSON文件
    config_data = read_json()
    config_data['cameras'][camera_id][area] = []
    # 更新camera_sources
    global camera_sources
    for camera_info in camera_sources:
        if camera_info['name'] == config_data['cameras'][camera_id]['name']:
            camera_info[area] = dots
            # camera_info['models'] = models
            # print(camera_info)
    write_json(config_data)
    return jsonify({"message": "安全區已刪除"})

#修改json
@app.route('/setCameraSetting', methods=['POST'])
def update_camera():
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
    global camera_sources
    for camera_info in camera_sources:
        if camera_info['name'] == name:
            # camera_info['safearea'] = data.get('safearea', camera_info['safearea'])
            camera_info['models'] = models
            # print(camera_info)      
    return {
            'status':200,
            'method':"修改成功",
            "camera": config_data['cameras'][index]['name'],
            "models": config_data['cameras'][index]['models']
            }
#新增json資料s
@app.route('/newCameraSetting', methods=['POST'])
def new_camera():
    # 从请求中获取数据
    # source = "1234.mp4"
    # models = ["1",'4']
    name = request.values['name']
    source = request.values['source']
    models = request.values['models']
    name = ""
    # 读取当前的JSON文件
    data = read_json()
    data['cameras'].append({"name": name,"source": source, "models": models})
    write_json(data)
    return {
            'status':200,
            'method':"新增成功"
            }
#取的json資料
@app.route('/read_model_config', methods=['GET'])
def read_model_config():
    with open('config.json', 'r') as f:
        data = json.load(f)
    return {
            'status':200,
            'method':"查詢成功",
            'data': data
            }

# 圖片資料夾路徑
IMAGE_FOLDER = os.path.join(os.getcwd(), "static/images/after-predict")

# 路由：提供指定名稱的圖片
@app.route('/images/<filename>')
def get_image(filename):
    try:
        # 返回指定的圖片文件
        return send_from_directory(IMAGE_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    
# localhost/selectPersoninformation
# @app.route('/images/<filename>')
# def serve_image(filename):
#     filename = f"{filename}"
#     return send_from_directory('static/images', filename)  # 提供圖片

@app.route('/get_image_url/<int:person_id>', methods=['GET']) #取得圖片
def get_image_url(person_id):
    # 生成圖片名稱
    image_name = f"{person_id}.jpg"
    # 生成圖片網址
    # image_url = f"/images/after-predict/{image_name}"
    image_url = url_for('static', filename=f'images/after-predict/{image_name}')
    return jsonify(
        image_url  # 返回圖片的網址
    )
    
app.register_blueprint(select_person_information, url_prefix='/selectPersonInformation/')
# app.register_blueprint(model_select_information, url_prefix='/setCameraSetting/')
# app.register_blueprint(safearea_information, url_prefix='/safearea/')

# 處理結束信號的函數
def close_all_cameras(signum, frame): #關閉opencv畫面
    global camera_sources
    print("Closing all cameras and OpenCV windows...")
    for camera_info in camera_sources:
        if camera_info["source"].isOpened():
            camera_info["source"].release()  # 釋放攝像頭資源
    cv2.destroyAllWindows()  # 關閉所有 OpenCV 視窗
    os._exit(0)  # 確保程序完全退出


@app.route('/close_all_cameras', methods=['POST']) #取得圖片
def close_all_cameras_function(): #關閉opencv畫面
    global camera_sources
    print("Closing all cameras and OpenCV windows...")
    for camera_info in camera_sources:
        if camera_info["source"].isOpened():
            camera_info["source"].release()  # 釋放攝像頭資源
    cv2.destroyAllWindows()  # 關閉所有 OpenCV 視窗
    # 返回一個成功的響應
    return jsonify({"message": "All cameras closed"})

# def signal_handler(sig, frame): #當按下ctrl+c 關閉程式以及opencv畫面
#     print("Gracefully shutting down...")
#     # 在此关闭所有摄像头资源
#     for camera_info in camera_sources:
#         if camera_info["source"].isOpened():
#             camera_info["source"].release()
#     cv2.destroyAllWindows()  # 关闭所有 OpenCV 窗口
#     sys.exit(0)

# 新增路由來處理表單提交
@app.route("/submit_face", methods=["POST"])
def submit_data():
    # 獲取表單中的名字和圖片
    print("123")
    name = request.form.get('name')
    photo = request.files.get('photo')
    print(name)
    print(photo)
    if not name or not photo:
        return jsonify({"error": "Please provide both name and photo"}), 400

    # 保存圖片到上傳文件夾
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # 確保目錄存在
    photo.save(photo_path)

    # 創建數據結構
    data = {
        'name': name,
        'filename': "uploads\\"+photo.filename,  # 只保存圖片文件名
        'encode': None
    }

    # 寫入 JSON 文件
    json_file_path = 'faces.json'
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r+') as file:
            try:
                file_data = json.load(file)  # 讀取現有 JSON 文件內容
            except json.JSONDecodeError:
                file_data = []  # 文件為空，創建一個空列表

            file_data.append(data)  # 添加新數據
            file.seek(0)
            json.dump(file_data, file, indent=4)  # 重寫文件內容
    else:
        with open(json_file_path, 'w') as file:
            json.dump([data], file, indent=4)  # 如果文件不存在，創建文件並添加數據

    return jsonify({"message": "Data added successfully!", "data": data})



# 主程式執行
if __name__ == "__main__":
    signal.signal(signal.SIGINT, close_all_cameras)
    signal.signal(signal.SIGTERM, close_all_cameras)
    try:
        # Start periodic color detection thread
        # threading.Thread(target=run_color_detection_periodically, args=('images/non-predict',), daemon=True).start()
        start_cameras_original()  # 啟動所有攝像頭線程
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        # app.run(threaded=True)

        # websocket
        socketio.run(app, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        close_all_cameras(None, None)


# {
#     "cameras": [
#         {
#             "name": "camera1",
#             "source": 0,
#             "images": "video/start/1.jpg",
#             "playback_speed": 0,
#             "models": [
            
#             ],
#             "safearea": [],
#             "dangerarea": []
#         },
#         {
#             "name": "camera2",
#             "source": "video/business.mp4",
#             "images": "video/start/business.jpg",
#             "playback_speed": -10,
#             "models": [],
#             "safearea": [],
#             "dangerarea": []
#         },
#         {
#             "name": "camera3",
#             "source": "video/walk2_pro.mp4",
#             "images": "video/start/walk2.jpg",
#             "playback_speed": -10,
#             "models": [
            
#             ],
#             "safearea": [
                
#             ],
#             "dangerarea": [
                
#             ]
#         }
#     ]
# }
# {
#     "cameras": [
#         {
#             "name": "camera1",
#             "source": 0,
#             "images": "video/start/1.jpg",
#             "playback_speed": 0,
#             "models": [],
#             "safearea": [],
#             "dangerarea": []
#         },
#         {
#             "name": "camera2",
#             "source": "video/face_detect_fail.mp4",
#             "images": "video/start/business.jpg",
#             "playback_speed": -10,
#             "models": [
#                 "3"
#             ],
#             "safearea": [],
#             "dangerarea": []
#         },
#         {
#             "name": "camera3",
#             "source": "video/walk2_pro.mp4",
#             "images": "video/start/walk2.jpg",
#             "playback_speed": 0,
#             "models": [],
#             "safearea": [],
#             "dangerarea": []
#         }
#     ]
# }