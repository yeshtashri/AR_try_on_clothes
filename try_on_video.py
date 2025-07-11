from flask import Flask, Response, request
import cv2
import numpy as np
from ultralytics import YOLO
import threading
import os

app = Flask(__name__)

model = YOLO("yolov8n-pose.pt")

shirt_paths = [
    os.path.join("Resources", "Shirts", "shirt1.png"),
    os.path.join("Resources", "Shirts", "shirt2.png")
]
shirt_idx = 0
shirt_img = cv2.imread(shirt_paths[shirt_idx])
if shirt_img is None:
    raise FileNotFoundError(f"Could not load shirt image: {shirt_paths[shirt_idx]}")
shirt_aspect_ratio = shirt_img.shape[0] / shirt_img.shape[1]

color_cycle = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0), 
    'yellow': (0, 255, 255),
    'magenta': (255, 0, 255),
    'cyan': (255, 255, 0),
    'white': (255, 255, 255)
}
current_color = (255, 255, 255)  # default white

size_multiplier = 1.0
offset_x = 0
offset_y = 0

running = True
lock = threading.Lock()

def overlay_shirt(frame, shirt_resized, x, y, color_overlay):
    h, w = shirt_resized.shape[:2]
    if x < 0 or y < 0 or x + w > frame.shape[1] or y + h > frame.shape[0]:
        return frame
    roi = frame[y:y+h, x:x+w]
    # Convert shirt to HSV for better white masking
    hsv_shirt = cv2.cvtColor(shirt_resized, cv2.COLOR_BGR2HSV)
    # Define mask for white/near-white (low saturation, high value)
    lower_white = np.array([0, 0, 220], dtype=np.uint8)
    upper_white = np.array([180, 30, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv_shirt, lower_white, upper_white)
    mask_inv = cv2.bitwise_not(mask)
    color_layer = np.full(shirt_resized.shape, color_overlay, dtype=np.uint8)
    colored_shirt = cv2.bitwise_and(color_layer, color_layer, mask=mask_inv)
    bg = cv2.bitwise_and(roi, roi, mask=mask)
    dst = cv2.add(bg, colored_shirt)
    frame[y:y+h, x:x+w] = dst
    return frame

def gen_frames():
    global running, shirt_img, shirt_aspect_ratio, current_color, size_multiplier, offset_x, offset_y
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    print("Camera opened:", ret)

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, conf=0.5)
        if results and results[0].keypoints is not None:
            keypoints = results[0].keypoints.xy[0].cpu().numpy()
            try:
                left_shoulder = keypoints[5]
                right_shoulder = keypoints[6]
                shoulder_center = (left_shoulder + right_shoulder) / 2
                shoulder_width = np.linalg.norm(right_shoulder - left_shoulder)
                shirt_width = int(size_multiplier * shoulder_width)
                shirt_height = int(shirt_aspect_ratio * shirt_width)

                if shirt_width > 0 and shirt_height > 0:
                    with lock:
                        resized_shirt = cv2.resize(shirt_img, (shirt_width*2, shirt_height*2))
                    x = int(shoulder_center[0]) - shirt_width + offset_x
                    y = int(shoulder_center[1]) - int(shirt_height / 6) + offset_y

                    frame = overlay_shirt(frame, resized_shirt, x, y, current_color)
            except:
                pass

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return '''
    <html>
    <head>
    <title>AR Virtual Try-On</title>
    <style>
        body { background: #111; color: #eee; font-family: sans-serif; text-align: center; }
        h1 { color: #0ff; }
        img { border: 4px solid #0ff; border-radius: 10px; width: 80%; max-width: 640px; }
        button { margin: 5px; padding: 8px 14px; font-size: 14px; border-radius: 4px; border: none; cursor: pointer; }
        .shirt { background: #0ff; color: #111; }
        .color { background: #555; color: #eee; }
        .size { background: #f90; color: #111; }
        .pos { background: #09f; color: #111; }
    </style>
    </head>
    <body>
    <h1>👕 AR Virtual Try-On</h1>
    <img src="/video_feed">
    <div>
      <button class="shirt" onclick="fetch('/set_shirt?idx=0')">Shirt 1</button>
      <button class="shirt" onclick="fetch('/set_shirt?idx=1')">Shirt 2</button>
      <button class="color" onclick="fetch('/set_color?color=red')">Red</button>
      <button class="color" onclick="fetch('/set_color?color=green')">Green</button>
      <button class="color" onclick="fetch('/set_color?color=blue')">Blue</button>
      <button class="color" onclick="fetch('/set_color?color=yellow')">Yellow</button>
      <button class="color" onclick="fetch('/set_color?color=magenta')">Magenta</button>
      <button class="color" onclick="fetch('/set_color?color=cyan')">Cyan</button>
      <button class="color" onclick="fetch('/set_color?color=white')">White</button>
      <br>
      <button class="size" onclick="fetch('/set_size?scale=0.8')">Small</button>
      <button class="size" onclick="fetch('/set_size?scale=1.0')">Medium</button>
      <button class="size" onclick="fetch('/set_size?scale=1.2')">Large</button>
      <br>
      <button class="pos" onclick="fetch('/move?x=20&y=0')">➡️ Right</button>
      <button class="pos" onclick="fetch('/move?x=-20&y=0')">⬅️ Left</button>
      <button class="pos" onclick="fetch('/move?x=0&y=-20')">⬆️ Up</button>
      <button class="pos" onclick="fetch('/move?x=0&y=20')">⬇️ Down</button>
      <br>
      <button style="background: #f33; color: #fff;" onclick="fetch('/stop').then(()=>window.close())">Stop & Exit</button>
    </div>
    </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_shirt')
def set_shirt():
    global shirt_idx, shirt_img, shirt_aspect_ratio
    idx = int(request.args.get('idx', 0))
    with lock:
        shirt_idx = idx % len(shirt_paths)
        shirt_img = cv2.imread(shirt_paths[shirt_idx])
        if shirt_img is None:
            return f'Could not load shirt image: {shirt_paths[shirt_idx]}', 500
        shirt_aspect_ratio = shirt_img.shape[0] / shirt_img.shape[1]
    return '', 204

@app.route('/set_color')
def set_color():
    global current_color 
    color_name = request.args.get('color', 'white')
    current_color = color_cycle.get(color_name, (255, 255, 255))
    return '', 204

@app.route('/set_size')
def set_size():
    global size_multiplier
    scale = float(request.args.get('scale', 1.0))
    size_multiplier = scale
    return '', 204

@app.route('/move')
def move():
    global offset_x, offset_y
    offset_x += int(request.args.get('x', 0))
    offset_y += int(request.args.get('y', 0))
    return '', 204

@app.route('/stop')
def stop():
    global running
    running = False
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
