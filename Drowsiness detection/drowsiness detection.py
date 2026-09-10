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
import mediapipe as mp
import requests
import json
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
sound_distracted = mixer.Sound(resource_path("distracted.wav"))
sound_yawn = mixer.Sound(resource_path("yawn.wav"))

# Initialize Mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)

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
system_running = True

# Analytics and Threat State
session_start_time = time.time()
total_alarms_prevented = 0
yawn_count = 0
distraction_score = 0
yawn_score = 0
is_yawning = False
is_distracted = False

# God-Tier Variables
is_calibrating = True
calibration_frames = 0
MAX_CALIBRATION_FRAMES = 100
baseline_mar = 0.0
baseline_brow_dist = 0.0
is_stressed = False
stress_score = 0
rppg_buffer = []
bpm = 0

# IoT Integration
iot_triggered = False
last_iot_trigger_time = 0
IOT_COOLDOWN = 10 # seconds
iot_webhook_url = "http://127.0.0.1:5000/api/smart_car"


def trigger_smart_cabin():
    global iot_triggered, last_iot_trigger_time
    # Run asynchronously to avoid blocking the video feed
    def _fire_webhook():
        try:
            payload = {
                "action": "emergency_wake",
                "windows": "down",
                "ac": "max",
                "lights": "strobe"
            }
            # Using the configurable webhook URL
            requests.post(iot_webhook_url, json=payload, timeout=2)
        except:
            pass
    
    current_time = time.time()
    if current_time - last_iot_trigger_time > IOT_COOLDOWN:
        last_iot_trigger_time = current_time
        iot_triggered = True
        threading.Thread(target=_fire_webhook, daemon=True).start()

def generate_frames():
    global score, state, r_prob, l_prob, debug_mode
    global total_alarms_prevented, yawn_count, distraction_score, yawn_score, is_yawning, is_distracted
    global is_calibrating, calibration_frames, baseline_mar, baseline_brow_dist, is_stressed, stress_score, rppg_buffer, bpm
    global iot_triggered, last_iot_trigger_time, iot_webhook_url
    cap = cv2.VideoCapture(0)
    
    while True:
        if not system_running:
            break
        ret, frame = cap.read()
        if not ret:
            break
            
        height, width = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Mediapipe Face Mesh for Head Pose & Yawning
        results = face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            is_distracted = False
            distraction_score -= 1
            if distraction_score < 0: distraction_score = 0
            
            face_landmarks = results.multi_face_landmarks[0]
            
            # --- Calibration Logic ---
            p_upper = face_landmarks.landmark[13]
            p_lower = face_landmarks.landmark[14]
            p_left = face_landmarks.landmark[78]
            p_right = face_landmarks.landmark[308]
            mar = abs(p_upper.y - p_lower.y) / (abs(p_left.x - p_right.x) + 1e-6)

            p_brow_l = face_landmarks.landmark[107]
            p_brow_r = face_landmarks.landmark[336]
            brow_dist = abs(p_brow_l.x - p_brow_r.x)

            if is_calibrating:
                baseline_mar += mar
                baseline_brow_dist += brow_dist
                calibration_frames += 1
                if calibration_frames >= MAX_CALIBRATION_FRAMES:
                    baseline_mar /= MAX_CALIBRATION_FRAMES
                    baseline_brow_dist /= MAX_CALIBRATION_FRAMES
                    is_calibrating = False
                continue # Skip threat detection while calibrating
                
            # --- Yawn Calculation (Adaptive) ---
            if mar > baseline_mar + 0.35:
                yawn_score += 1
                if yawn_score > 15: # half a second
                    is_yawning = True
                    try: sound_yawn.play()
                    except: pass
                    if yawn_score == 16: yawn_count += 1
            else:
                yawn_score -= 1
                if yawn_score < 0: yawn_score = 0
                is_yawning = False
                try: sound_yawn.stop()
                except: pass
                
            # --- Emotion / Stress Detection ---
            if brow_dist < baseline_brow_dist * 0.8: # Furrowed brows
                stress_score += 1
                if stress_score > 30: # 1 second of intense furrow
                    is_stressed = True
            else:
                stress_score -= 1
                if stress_score < 0: stress_score = 0
                is_stressed = False

            # --- rPPG Heart Rate ---
            # Extract forehead ROI points
            fh_pts = [10, 109, 67, 103, 54]
            green_sum = 0
            for pt in fh_pts:
                lm = face_landmarks.landmark[pt]
                x_px = int(lm.x * width)
                y_px = int(lm.y * height)
                if 0 <= x_px < width and 0 <= y_px < height:
                    green_sum += frame[y_px, x_px, 1] # Green channel
            
            green_avg = green_sum / len(fh_pts)
            rppg_buffer.append(green_avg)
            if len(rppg_buffer) > 150: # 5 second window at 30 FPS
                rppg_buffer.pop(0)
                # Compute FFT
                signal = np.array(rppg_buffer)
                signal = signal - np.mean(signal)
                fft_vals = np.abs(np.fft.rfft(signal))
                freqs = np.fft.rfftfreq(150, d=1.0/30.0)
                
                # Bandpass 0.75 Hz to 3.0 Hz (45 to 180 BPM)
                valid_idx = np.where((freqs >= 0.75) & (freqs <= 3.0))[0]
                if len(valid_idx) > 0:
                    peak_freq = freqs[valid_idx[np.argmax(fft_vals[valid_idx])]]
                    bpm = int(peak_freq * 60)
            
            # --- Head Pose (simplified pitch down) ---
            p_nose = face_landmarks.landmark[1]
            p_chin = face_landmarks.landmark[152]
            p_forehead = face_landmarks.landmark[10]
            face_height = p_chin.y - p_forehead.y
            nose_to_chin = p_chin.y - p_nose.y
            if nose_to_chin / (face_height + 1e-6) < 0.3:
                distraction_score += 2 # double speed if looking down
                
        else:
            # Face lost - looking away
            distraction_score += 1
            
        if distraction_score > 45: # 1.5 seconds of distraction
            is_distracted = True
            try: sound_distracted.play()
            except: pass
        else:
            is_distracted = False
            try: sound_distracted.stop()
            except: pass

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
            
        # Audio logic & Analytics
        if score > 30:
            if score == 31: 
                total_alarms_prevented += 1
            trigger_smart_cabin()
            try:
                if score < 60:
                    sound.set_volume(0.5)
                else:
                    sound.set_volume(1.0)
                if score % 15 == 0: # Play every 15 frames to prevent stuttering
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
def status():
    global score, state, r_prob, l_prob, debug_mode
    global total_alarms_prevented, yawn_count, session_start_time, distraction_score, is_yawning, is_distracted
    global is_calibrating, is_stressed, bpm, iot_triggered
    
    elapsed_time = int(time.time() - session_start_time)
    
    return jsonify({
        "score": score,
        "state": state,
        "r_prob": r_prob,
        "l_prob": l_prob,
        "debug": debug_mode,
        "alarms": total_alarms_prevented,
        "yawns": yawn_count,
        "distracted": is_distracted,
        "yawning": is_yawning,
        "time_elapsed": elapsed_time,
        "is_calibrating": is_calibrating,
        "is_stressed": is_stressed,
        "bpm": bpm,
        "iot_triggered": iot_triggered
    })

@app.route('/api/smart_car', methods=['POST'])
def mock_smart_car_api():
    # Mock IoT API that accepts the webhook from the AI logic
    return jsonify({"status": "success", "message": "Smart Cabin Emergency Protocol Activated"})

from flask import request

@app.route('/api/settings', methods=['POST'])
def update_settings():
    global iot_webhook_url
    data = request.json
    if 'iot_webhook_url' in data:
        iot_webhook_url = data['iot_webhook_url']
    return jsonify({"status": "success", "iot_webhook_url": iot_webhook_url})

@app.route('/stop_system', methods=['POST'])
def stop_system():
    global session_start_time, total_alarms_prevented, yawn_count, score
    global bpm, is_stressed, system_running
    
    system_running = False
    
    # Calculate totals
    uptime = time.time() - session_start_time
    
    # Return trip report
    return jsonify({
        'uptime_seconds': int(uptime),
        'alarms_prevented': total_alarms_prevented,
        'yawn_count': yawn_count,
        'bpm': bpm
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
