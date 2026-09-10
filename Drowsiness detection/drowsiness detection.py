import cv2
import os
import sys
from flask import Flask, render_template, Response, jsonify
from keras.models import load_model
import numpy as np
from pygame import mixer
import threading
import webbrowser
import time

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = Flask(__name__, template_folder=resource_path('templates'))

# Initialize Audio
mixer.init()
sound = mixer.Sound(resource_path("alarm.mp3"))

# Initialize Cascades
face_cascade = cv2.CascadeClassifier(resource_path(os.path.join('haar cascade files','haarcascade_frontalface_alt.xml')))
leye_cascade = cv2.CascadeClassifier(resource_path(os.path.join('haar cascade files','haarcascade_lefteye_2splits.xml')))
reye_cascade = cv2.CascadeClassifier(resource_path(os.path.join('haar cascade files','haarcascade_righteye_2splits.xml')))

# Initialize Model
model = load_model(resource_path(os.path.join('models','cnnCat2.h5')))

# Global state variables for the frontend to poll
score = 0
state = "Open"
r_prob = 0.0
l_prob = 0.0
debug_mode = False

def generate_frames():
    global score, state, r_prob, l_prob, debug_mode
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        height, width = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25))
        left_eye = leye_cascade.detectMultiScale(gray)
        right_eye = reye_cascade.detectMultiScale(gray)

        # Draw rects
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 1)

        rpred = None
        lpred = None
        r_eye_disp = None
        l_eye_disp = None

        for (x, y, w, h) in right_eye:
            r_eye = frame[y:y + h, x:x + w]
            r_eye_gray = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
            r_eye_24 = cv2.resize(r_eye_gray, (24, 24))
            r_eye_disp = r_eye_24.copy()
            r_eye = r_eye_24 / 255
            r_eye = r_eye.reshape(24, 24, -1)
            r_eye = np.expand_dims(r_eye, axis=0)
            rpred = model.predict(r_eye)
            if debug_mode:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cx, cy = x + w//2, y + h//2
                cv2.line(frame, (cx-10, cy), (cx+10, cy), (0, 255, 0), 1)
                cv2.line(frame, (cx, cy-10), (cx, cy+10), (0, 255, 0), 1)
                cv2.putText(frame, f"R: {float(rpred[0][0]):.2f}", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            break

        for (x, y, w, h) in left_eye:
            l_eye = frame[y:y + h, x:x + w]
            l_eye_gray = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
            l_eye_24 = cv2.resize(l_eye_gray, (24, 24))
            l_eye_disp = l_eye_24.copy()
            l_eye = l_eye_24 / 255
            l_eye = l_eye.reshape(24, 24, -1)
            l_eye = np.expand_dims(l_eye, axis=0)
            lpred = model.predict(l_eye)
            if debug_mode:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cx, cy = x + w//2, y + h//2
                cv2.line(frame, (cx-10, cy), (cx+10, cy), (0, 255, 0), 1)
                cv2.line(frame, (cx, cy-10), (cx, cy+10), (0, 255, 0), 1)
                cv2.putText(frame, f"L: {float(lpred[0][0]):.2f}", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            break
            
        r_detected = rpred is not None
        l_detected = lpred is not None

        if r_detected or l_detected:
            r_prob = float(rpred[0][0]) if r_detected else 0.0
            l_prob = float(lpred[0][0]) if l_detected else 0.0
            
            if r_detected and l_detected:
                if r_prob >= 0.90 and l_prob >= 0.90:
                    state = "Closed"
                else:
                    state = "Open"
            elif r_detected:
                if r_prob >= 0.90:
                    state = "Closed"
                else:
                    state = "Open"
            elif l_detected:
                if l_prob >= 0.90:
                    state = "Closed"
                else:
                    state = "Open"
        else:
            if len(faces) > 0:
                state = "Closed"
            else:
                state = "No Face"

        if state == "Open":
            score -= 1
        else:
            score += 1

        if score < 0:
            score = 0
            
        # Audio logic
        if score > 30:
            try:
                sound.play()
            except:
                pass
        else:
            try:
                sound.stop()
            except:
                pass
                
        # Debug Mode Overlays
        if debug_mode:
            disp_size = 120
            if r_eye_disp is not None:
                r_eye_color = cv2.cvtColor(r_eye_disp, cv2.COLOR_GRAY2BGR)
                r_eye_big = cv2.resize(r_eye_color, (disp_size, disp_size), interpolation=cv2.INTER_NEAREST)
                frame[0:disp_size, width-disp_size:width] = r_eye_big
                cv2.rectangle(frame, (width-disp_size, 0), (width, disp_size), (0,255,0), 2)
                cv2.putText(frame, "AI Input R", (width-disp_size+5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            if l_eye_disp is not None:
                l_eye_color = cv2.cvtColor(l_eye_disp, cv2.COLOR_GRAY2BGR)
                l_eye_big = cv2.resize(l_eye_color, (disp_size, disp_size), interpolation=cv2.INTER_NEAREST)
                frame[0:disp_size, 0:disp_size] = l_eye_big
                cv2.rectangle(frame, (0, 0), (disp_size, disp_size), (0,255,0), 2)
                cv2.putText(frame, "AI Input L", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # We don't use cv2.imshow anymore. Encode for web MJPEG stream.
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    global score, state, r_prob, l_prob, debug_mode
    return jsonify({
        'score': score,
        'state': state,
        'r_prob': r_prob,
        'l_prob': l_prob,
        'debug_mode': debug_mode
    })

@app.route('/toggle_debug', methods=['POST'])
def toggle_debug():
    global debug_mode
    debug_mode = not debug_mode
    return jsonify({'debug_mode': debug_mode})

def open_browser():
    # Wait a tiny bit for the server to spin up
    time.sleep(1.5)
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == '__main__':
    # Start the browser thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # In PyInstaller, running Flask requires disabling the reloader
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
