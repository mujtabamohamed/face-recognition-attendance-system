import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://faceattendencesystem-d1b02-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "12345":
        {
            "name": "PewDiePie",
            "department": "IT",
            "total attendance": "6",
            "starting year": "2020",
            "year": "TY",
            "sem": "5",
            "last_attendance_time": "2023-03-05 00:54:34"
        },

    "13579":
        {
            "name": "Elon Musk",
            "department": "IT",
            "total attendance": "8",
            "starting year": "2021",
            "year": "SY",
            "sem": "3",
            "last_attendance_time": "2023-03-05 00:54:34"
        },

    "246810":
        {
            "name": "JJ Olatunji",
            "department": "IT",
            "total attendance": "5",
            "starting year": "2021",
            "year": "SY",
            "sem": "3",
            "last_attendance_time": "2023-03-05 00:54:34"
        },

    "67890":
        {
            "name": "Mujtaba Mohamed",
            "department": "IT",
            "total attendance": "9",
            "starting year": "2021",
            "year": "SY",
            "sem": "4",
            "last_attendance_time": "2023-03-05 00:54:34"
        },

}

for key, value in data.items():
    ref.child(key).set(value)
