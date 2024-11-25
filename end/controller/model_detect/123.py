import cv2
import face_recognition
import numpy as np
import json
from libpyvivotek import VivotekCamera
from PIL import Image
from io import BytesIO
cam = VivotekCamera(host='192.168.50.165', port=8080, usr='root', pwd='C110156108',
                    digest_auth=False, ssl=False, verify_ssl=False, sec_lvl='admin')

# known_face_list = [
#     {
#         'name': 'carlos',
#         'filename': 'train\carlos.jpg',
#         'encode': None,
#     },
#     {
#         'name': 'chaewon',
#         'filename': 'train\chaewon2.jpg',
#         'encode': None,
#     },
#     {
#         'name': 'kura',
#         'filename': 'train\kura2.jpg',
#         'encode': None,
#     },
#     {
#         'name': 'yunjin',
#         'filename': 'train\yunjin1.jpg',
#         'encode': None,
#     },
#     {
#         'name': 'zuha',
#         'filename': 'train\zuha3.jpg',
#         'encode': None,
#     },
#     {
#         'name': 'eunchae',
#         'filename': 'train\eunchae1.jpg',
#         'encode': None,
#     },   
# ]

# with open('faces.json', 'w') as f:
#     json.dump(known_face_list, f, indent=4)

with open('faces.json', 'r') as f:
    known_face_list = json.load(f)

for data in known_face_list:
    img = cv2.imread(data['filename'])
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    data['encode'] = face_recognition.face_encodings(img)[0]

known_face_encodes = [data['encode'] for data in known_face_list]
tolerance = 0.6  # 比對閾值

RED_COLOR = (200, 58, 76)
WHITE_COLOR = (255, 255, 255)

def draw_locations(img, match_results):
    for match_result in match_results:
        y1, x2, y2, x1 = match_result['location']
        cv2.rectangle(img, (x1, y1), (x2, y2), RED_COLOR, 2)
        cv2.rectangle(img, (x1, y2 + 35), (x2, y2), RED_COLOR, cv2.FILLED)
        cv2.putText(img, match_result['name'], (x1 + 10, y2 + 25), cv2.FONT_HERSHEY_COMPLEX, 0.8, WHITE_COLOR, 2)

while True:
    match_results = []
    snapshot = Image.open(BytesIO(cam.snapshot(quality=3)))
    img = cv2.cvtColor(np.array(snapshot), cv2.COLOR_RGB2BGR)
    cur_face_locs = face_recognition.face_locations(img)
    cur_face_encodes = face_recognition.face_encodings(img, cur_face_locs)

    for cur_face_encode, cur_face_loc in zip(cur_face_encodes, cur_face_locs):
        face_distance_list = face_recognition.face_distance(known_face_encodes, cur_face_encode)

        min_distance_index = np.argmin(face_distance_list)
        if face_distance_list[min_distance_index] < tolerance:
            name = known_face_list[min_distance_index]['name']
        else:
            name = 'unknown'

        match_results.append({
            'name': name,
            'location': cur_face_loc,
        })

    draw_locations(img, match_results)

    cv2.imshow('ipcam', img)
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()