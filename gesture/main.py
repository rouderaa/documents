#
# Demo usage of opencv 2 hand recognition
# Based on the excellent video : https://www.youtube.com/watch?v=vQZ4IvB07ec&t=205s
# Made by Nicholas Renotte
#

import mediapipe as mp
import cv2
import numpy as np
import uuid
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(BASE_DIR, "images")

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)
with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()

        # Detections
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # print(results)

        if results.multi_hand_landmarks:
            # draw hand framework on original image
            for num, hand in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS)

            # store a copy of the image on disk, for future reference
            # cv2.imwrite(os.path.join(
            #     image_dir,
            #     '{}.jpg'.format(uuid.uuid1())),
            #     image
            # )

        if ret == True:
            # Display the resulting frame
            cv2.imshow('Frame', image)

            # Press Q on keyboard to exit
            k = cv2.waitKey(10) & 0xFF
            # NOTE: k never gets a value while in Pycharm debugger ?
            if k == ord('q'):
                break
        # Break the loop
        else:
            break

cap.release()
cv2.destroyAllWindows()
