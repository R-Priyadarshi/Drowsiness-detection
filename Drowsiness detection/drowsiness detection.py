import cv2
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

from keras.models import load_model
import numpy as np
from pygame import mixer
import time

mixer.init()
sound = mixer.Sound(resource_path("alarm.mp3"))

face = cv2.CascadeClassifier(resource_path(os.path.join('haar cascade files','haarcascade_frontalface_alt.xml')))
leye = cv2.CascadeClassifier(resource_path(os.path.join('haar cascade files','haarcascade_lefteye_2splits.xml')))
reye = cv2.CascadeClassifier(resource_path(os.path.join('haar cascade files','haarcascade_righteye_2splits.xml')))

lbl = ['Close', 'Open']

model = load_model(resource_path(os.path.join('models','cnnCat2.h5')))
path = os.getcwd()
cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
count = 0
score = 0
thicc = 2
rpred = None
lpred = None

while True:
    ret, frame = cap.read()
    height, width = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face.detectMultiScale(gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25))
    left_eye = leye.detectMultiScale(gray)
    right_eye = reye.detectMultiScale(gray)

    cv2.rectangle(frame, (0, height - 50), (200, height), (0, 0, 0), thickness=cv2.FILLED)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 1)

    rpred = None
    lpred = None

    for (x, y, w, h) in right_eye:
        r_eye = frame[y:y + h, x:x + w]
        r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
        r_eye = cv2.resize(r_eye, (24, 24))
        r_eye = r_eye / 255
        r_eye = r_eye.reshape(24, 24, -1)
        r_eye = np.expand_dims(r_eye, axis=0)
        rpred = model.predict(r_eye)
        break

    for (x, y, w, h) in left_eye:
        l_eye = frame[y:y + h, x:x + w]
        l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
        l_eye = cv2.resize(l_eye, (24, 24))
        l_eye = l_eye / 255
        l_eye = l_eye.reshape(24, 24, -1)
        l_eye = np.expand_dims(l_eye, axis=0)
        lpred = model.predict(l_eye)
        break
        
    r_detected = rpred is not None
    l_detected = lpred is not None

    if r_detected or l_detected:
        r_closed_prob = rpred[0][0] if r_detected else 0.0
        l_closed_prob = lpred[0][0] if l_detected else 0.0
        
        cv2.putText(frame, f"R_Close_Prob: {r_closed_prob:.2f}", (10, 30), font, 1, (255, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, f"L_Close_Prob: {l_closed_prob:.2f}", (10, 60), font, 1, (255, 255, 0), 1, cv2.LINE_AA)
        
        if (not r_detected or r_closed_prob < 0.5) and (not l_detected or l_closed_prob < 0.5):
            state = "Open"
        else:
            state = "Closed"
    else:
        if len(faces) > 0:
            state = "Closed"
        else:
            state = "No Face"

    if state == "Open":
        score -= 1
        cv2.putText(frame, "Open", (10, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
    elif state == "Closed":
        score += 1
        cv2.putText(frame, "Closed", (10, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
    else:
        score += 1 # Driver missing!
        cv2.putText(frame, "No Face", (10, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

    if score < 0:
        score = 0
    cv2.putText(frame, 'Score:' + str(score), (100, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
    
    if score > 30:
        # person is feeling sleepy so we beep the alarm
        cv2.imwrite(os.path.join(path, 'image.jpg'), frame)
        try:
            sound.play()
        except:
            pass
        if thicc < 16:
            thicc += 2
        else:
            thicc = thicc - 2
            if thicc < 2:
                thicc = 2
        cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 255), thicc)
    else:
        try:
            sound.stop()
        except:
            pass
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
