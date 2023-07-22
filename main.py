import os
import cv2
import pickle
import cvzone
import face_recognition
import numpy as np
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, db
from firebase_admin import storage

# from flask import Flask
#
# app = Flask(__name__)
#
# @app.route('/')
# def index():

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendencesystem-d1b02-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendencesystem-d1b02.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
        imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

file = open('EncodeFile,p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:

                    # print("Known Face Detected")
                    # print(studentIds[matchIndex])

                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGR2RGB)

                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")

                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)

                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total attendance'] += 1
                    ref.child('total attendance').set(studentInfo['total attendance'])

                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total attendance']), (846, 118),
                                cv2.FONT_HERSHEY_DUPLEX, 0.65, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(id), (970, 448),
                                cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(studentInfo['department']), (985, 500),
                                cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(studentInfo['sem']), (900, 635),
                                cv2.FONT_HERSHEY_DUPLEX, 0.8, (50, 50, 50), 1)

                    cv2.putText(imgBackground, str(studentInfo['starting year']), (987, 635),
                                cv2.FONT_HERSHEY_DUPLEX, 0.7, (50, 50, 50), 1)

                    cv2.putText(imgBackground, str(studentInfo['year']), (1107, 635),
                                cv2.FONT_HERSHEY_DUPLEX, 0.7, (50, 50, 50), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_DUPLEX, 1, 1)
                    offset = (414 - w) // 2

                    cv2.putText(imgBackground, str(studentInfo['name']), (813 + offset, 400),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (50, 50, 50), 1)

                    imgBackground[147:147 + 216, 908:908 + 216] = imgStudent

                counter = counter + 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []

                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
        # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)

# if __name__ == '__main__':
#     app.run()