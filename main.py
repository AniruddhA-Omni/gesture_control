import numpy as np
import cv2
import time
from cvzone import HandTrackingModule as htm
import screen_brightness_control as sbc
import math

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
brightBar = 400
brightPer = 0
primary_brightness = sbc.get_brightness()
print("Primary brightness:", primary_brightness)
detector = htm.HandDetector()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if lmList != ([], []):
        # print(lmList[0][4], lmList[0][8])

        x1, y1 = lmList[0][4][0], lmList[0][4][1]
        x2, y2 = lmList[0][8][0], lmList[0][8][1]
        cx, cy = (x1 + x2)//2, (y1 + y2)//2

        cv2.circle(img, (x1, y1), 7, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 7, (0, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)

        # hand range 50-300
        # brightness range - 0 - 100
        brightBar = np.interp(length, [50, 300], [400, 150])
        brightPer = np.interp(length, [50, 300], [0, 100])
        sbc.set_brightness(brightPer, display=0)
        print(length, brightPer)

    cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 0), 4)
    cv2.rectangle(img, (50, int(brightBar)), (85, 400), (0, 0, 200), cv2.FILLED)
    cv2.putText(img, f'Brightness: {int(brightPer)}%', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (120, 255, 0), 3)
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
    cv2.imshow("Frame", img)
    if cv2.waitKey(1) == 27:
        break
