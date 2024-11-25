import cv2
import numpy as np
from flask import Blueprint, Response, request,jsonify

#flask function 
safearea_information = Blueprint('safearea_info', __name__)

#引入# from cnn_cloth import color_detection會發生錯誤! 要分成兩個程式碼
w, h = 640, 480  # 視窗大小
draw = np.zeros((h, w, 4), dtype='uint8')  # 用於顯示安全區的畫布

# 繪製安全區域的函數
def redraw_previous_safe_area(areaname,area, frame):
    if area:
        for i in range(len(area) - 1):
            start_point = tuple(area[i])
            end_point = tuple(area[i + 1])
            if areaname == "safearea":
                cv2.line(frame, start_point, end_point, (0, 255, 0), 2)  # 使用紅色繪製線段
            else:
                cv2.line(frame, start_point, end_point, (0, 0, 255), 2)  # 使用紅色繪製線段
        # 關閉多邊形的線
        if areaname == "safearea":
            cv2.line(frame, tuple(area[-1]), tuple(area[0]), (0, 255, 0), 2)
        else:
            cv2.line(frame, tuple(area[-1]), tuple(area[0]), (0, 0, 255), 2)

# 生成前端請求的影像流
def generate_draw_frames(camera_id):
    global camera_sources
    # 讀取圖片並準備繪製框框功能
    frame = cv2.imread(camera_sources[camera_id]["images"])
    print(camera_sources)
    frame = cv2.resize(frame, (640, 480))  # 調整圖片大小
    # cv2.namedWindow('safearea')  # 用於顯示 OpenCV 視窗
    # cv2.setMouseCallback('safearea', show_xy)
    while True:
        display_frame = frame.copy()
        # 畫出安全區
        for i in range(display_frame.shape[1]):
            display_frame[:, i, 0] = display_frame[:, i, 0] * (1 - draw[:, i, 3] / 255) + draw[:, i, 0] * (draw[:, i, 3] / 255)
            display_frame[:, i, 1] = display_frame[:, i, 1] * (1 - draw[:, i, 3] / 255) + draw[:, i, 1] * (draw[:, i, 3] / 255)
            display_frame[:, i, 2] = display_frame[:, i, 2] * (1 - draw[:, i, 3] / 255) + draw[:, i, 2] * (draw[:, i, 3] / 255)

        # 將圖片編碼為 JPG 格式並返回給前端
        ret, buffer = cv2.imencode('.jpg', display_frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
@safearea_information.route('/images_model_feed/<int:camera_id>')
def images_feed(camera_id):
    print(camera_id)
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

@safearea_information.route('/save_safe_area', methods=['POST'])
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
            print(camera_info)
            
    write_json(config_data)

    return jsonify({"message": "安全區已保存"})