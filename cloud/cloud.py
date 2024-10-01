import cv2 
import numpy as np 
import face_recognition 
import os 
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage



cred = credentials.Certificate("attendancesystem-1b800-firebase-adminsdk-dibzn-c2824f3fb1.json")
firebase_admin.initialize_app(cred , {
    'databaseURL' : 'https://attendancesystem-1b800-default-rtdb.firebaseio.com/' ,
    'storageBucket' : "attendancesystem-1b800.appspot.com"
})

ref = db.reference("students")

data = {
    "1" : {
        "name" : "Atharv Surve" , 
        "major" : "AI&DS" , 
        "Total_attendance" : 0 , 
        "Last_attendance" : "2024-8-11 00:54:34"
    },
    "2" : {
        "name" : "Modi" , 
        "major" : "Hotel Management" , 
        "Total_attendance" : 0 , 
        "Last_attendance" : "2024-8-11 00:54:34"
    },
    "3" : {
        "name" : "Dhoni" , 
        "major" : "Hockey" , 
        "Total_attendance" : 0 , 
        "Last_attendance" : "2024-8-11 00:54:34"
    },
    "4" : {
        "name" : "Virat Kholi" , 
        "major" : "Acting" , 
        "Total_attendance" : 0 , 
        "Last_attendance" : "2024-8-11 00:54:34"
    }
}

for key , value in data.items():
    ref.child(key).set(value)



# attendance marking function 
# def markAttendence(name) : 
#     with open('attendance.csv', 'r+') as f :
#         myDataList = f.readline()
#         nameList = []
#         for line in myDataList : 
#             entry = line.split(',')
#             nameList.append(entry[0])
#         if name not in nameList:
#             now = datetime.now()
#             dtstring = now.strftime("%H :%M : %S" )
#             f.writelines(f'\n{name},{dtstring}')

# making a path to bring images automatically 
# the path of the images is stored in varibale named 'path'
# 'images' is used to store the images one by one in this list 
# 'classNames' splits only the name of the file 
path = 'practImages'
images =[]
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList : 
    currentImage = cv2.imread(f'{path}/{cl}')
    images.append(currentImage)
    classNames.append(os.path.splitext(cl)[0])
    fileName = os.path.join(path, cl)
    bucket = storage.bucket()
    blob = bucket.blob(cl)
    blob.upload_from_filename(fileName)
print(classNames)