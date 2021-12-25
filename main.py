import numpy as np
import cv2
import time
from cvzone import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

#####
wCam, hCam = 640, 480
#####

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
vol = 0
volBar = 400
volPer = 0
area = 0
detector = htm.HandDetector(detectionCon=0.8)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    # Find Hand
    img = detector.findHands(img)
    lmList, bboxInf = detector.findPosition(img, draw=True)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])
        # Filter based on size
        bbox = list(bboxInf['bbox'])
        area = abs((bbox[2]-bbox[0]) * (bbox[3] - bbox[1]))//100
        # print(area)
        if 100 < area < 800:

            # find distance between index and thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)

            # convert volume
            # hand range 50-300
            # volume range -96 - 0
            vol = np.interp(length, [50, 300], [minVol, maxVol])
            volBar = np.interp(length, [50, 300], [400, 150])
            volPer = np.interp(length, [50, 300], [0, 100])
            # print(length, vol)

            # reduce resolution to make it smoother
            smoothness = 5
            volPer = smoothness * round(volPer/smoothness)

            # check fingers up
            fingers = detector.fingersUp()
            # print(fingers)

            # if pinky is down set volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 0), 4)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 0, 200), cv2.FILLED)
    cv2.putText(img, f'Volume: {int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 120, 10), 2)
    currentVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {int(currentVol)}', (40, 120), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 10, 10), 2)

    # Frame rate
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    cv2.imshow("Frame", img)
    if cv2.waitKey(1) == 27:
        break
