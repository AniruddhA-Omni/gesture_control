import numpy as np
import cv2
import time
from cvzone import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc

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
brightBar = 400
brightPer = 0
area = 0
detector = htm.HandDetector(detectionCon=0.8, maxHands=2)

while True:
    success, img = cap.read()
    # Find Hand
    img = detector.findHands(img)
    lmList, bboxInfo = detector.findPosition(img, draw=True, handNo=0)
    hType = detector.handType()

    if len(lmList) != 0:
        # print(bboxInfoV, "\t", bboxInfoB)
        # Filter based on size
        bbox = list(bboxInfo['bbox'])
        area = abs((bbox[2]-bbox[0]) * (bbox[3] - bbox[1]))//100
        print(area)
        if (10 < area < 400) and (hType == "Right"):
            # find distance between index and thumb
            lengthV, img, lineInfoV = detector.findDistance(4, 8, img)

            # convert volume
            # hand range 50-300
            # volume range -96 - 0
            vol = np.interp(lengthV, [50, 300], [minVol, maxVol])
            volBar = np.interp(lengthV, [50, 300], [400, 150])
            volPer = np.interp(lengthV, [50, 300], [0, 100])
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
                cv2.circle(img, (lineInfoV[4], lineInfoV[5]), 10, (0, 255, 0), cv2.FILLED)

        if (10 < area < 400) and (hType == "Left"):
            # find distance between index and thumb
            lengthB, img, lineInfoB = detector.findDistance(4, 8, img)
            # print(length)

            # hand range 50-300
            # brightness range - 0 - 100
            brightBar = np.interp(lengthB, [50, 300], [400, 150])
            brightPer = np.interp(lengthB, [50, 300], [0, 100])

            # reduce resolution to make it smoother
            smoothnessB = 2
            brightPer = smoothnessB * round(brightPer / smoothnessB)
            # print(length, brightPer)

            # check fingers up
            fingersB = detector.fingersUp()
            # print(fingers)

            # if pinky is down set brightness
            if not fingersB[4]:
                sbc.set_brightness(brightPer, display=0)
                cv2.circle(img, (lineInfoB[4], lineInfoB[5]), 10, (0, 255, 0), cv2.FILLED)

    img = cv2.flip(img, 1)
    cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 0), 4)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 0, 200), cv2.FILLED)
    cv2.putText(img, f'Volume: {int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 120, 10), 2)
    currentVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {int(currentVol)}', (40, 120), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 10, 10), 2)

    cv2.rectangle(img, (550, 150), (585, 400), (0, 0, 0), 4)
    cv2.rectangle(img, (550, int(brightBar)), (585, 400), (255, 255, 0), cv2.FILLED)
    cv2.putText(img, f'Brightness: {int(brightPer)}%', (440, 450), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (240, 32, 160), 2)
    current_brightness = sbc.get_brightness()
    cv2.putText(img, f'Light set: {int(current_brightness)}', (440, 120), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (240, 32, 160), 2)

    # Frame rate
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    cv2.imshow("Frame", img)
    if cv2.waitKey(1) == 27:
        break
