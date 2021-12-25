import numpy as np
import cv2
import time
from cvzone import HandTrackingModule as htm
import screen_brightness_control as sbc

#######
wCam, hCam = 640, 480
#######

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
brightBar = 400
brightPer = 0
detector = htm.HandDetector(detectionCon=0.8)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bboxInfo = detector.findPosition(img, draw=True)

    if len(lmList) != 0:
        # Filter based on size
        bbox = list(bboxInfo['bbox'])
        area = abs((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])) // 100
        if 10 < area < 500:
            # find distance between index and thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)

            # hand range 50-300
            # brightness range - 0 - 100
            brightBar = np.interp(length, [50, 300], [400, 150])
            brightPer = np.interp(length, [50, 300], [0, 100])

            # reduce resolution to make it smoother
            smoothness = 2
            brightPer = smoothness * round(brightPer / smoothness)

            # check fingers up
            fingers = detector.fingersUp()

            # if pinky is down set brightness
            if not fingers[4]:
                sbc.set_brightness(brightPer, display=0)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)

    # Flip the image
    img = cv2.flip(img, 1)

    # Brightness bar
    cv2.rectangle(img, (550, 150), (585, 400), (0, 0, 0), 5)
    cv2.rectangle(img, (550, int(brightBar)), (585, 400), (255, 255, 0), cv2.FILLED)
    cv2.putText(img, f'Brightness: {int(brightPer)}%', (440, 450), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (120, 255, 0), 2)
    current_brightness = sbc.get_brightness()
    cv2.putText(img, f'Light set: {int(current_brightness)}', (440, 120), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (120, 255, 0), 2)

    # FPS
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow("Frame", img)
    if cv2.waitKey(1) == 27:  # Press ESC to quit
        break
