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
# for key , value in data.items():
#     ref.child(value['name']).set(value)



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
path = 'practImages'  #define a path to a folder which  contains images of students
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

#i pick up images one by one from the 'images' list 

def findEncodings(images) :
    encodeList = [] #list to add encoded images 
    for img in images : 
        img = cv2.cvtColor(img , cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0] # assuming only face is there in one image [0]
        #encode it in an array like u do in CNN 
        encodeList.append(encode) # add it in the encode list 
    return encodeList


def markAttendence(name):
    with open('attendance.csv', 'r+') as f:
        # Read all lines from the file
        myDataList = f.readlines()

        # Extract names from existing entries
        nameList = [line.split(',')[0] for line in myDataList]

        if name not in nameList:
            now = datetime.now()
            dtstring = now.strftime("%H:%M:%S")
            f.write(f'\n{name},{dtstring}')

            # Move the file cursor to the beginning of the file
            f.seek(0)

            # Update nameList after adding the new entry
            nameList.append(name)
            

            
encodeListKnown = findEncodings(images)

print('encoding is done')


#find the image with which we have to match the image given by laptop video camera 

cap = cv2.VideoCapture(0)
counter = 0 
modeType = 0 
imageStudents = []

while True : 
    ret , img = cap.read() #cpature the frames in the video 
    imgs = cv2.resize(img ,(0,0) , None , 0.25 , 0.25 ) #resize the image for better processing 
    imgs = cv2.cvtColor(img , cv2.COLOR_BGR2RGB) 
    
    facesCurFrame = face_recognition.face_locations(imgs) #find the locations of the faces in the curent frame like (top , right ...)
    encodesCurrFrame = face_recognition.face_encodings(imgs,facesCurFrame) #converts the curent faces in to tuples of 128-deminsion array 
    
    #iterates on every image in the path and checkes whether the image matches the face detected in the web cam
    for encodeFace , faceLock in zip(encodesCurrFrame , facesCurFrame) : 
        matches = face_recognition.compare_faces(encodeListKnown , encodeFace) #encodedKnown list is compared to the encoded face detected on the web cam
        faceDist = face_recognition.face_distance(encodeListKnown , encodeFace) # the distance between the 'image' given and frame from web cam is compared (SVM Model)
        print(faceDist)
        matchIndex = np.argmin(faceDist) #the index of the minimum distance between them is choosen 
        
        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            print(name) #the name of the image from the list provided is shown 
            y1 , x2 , y2 , x1 = faceLock
            cv2.rectangle(img , (x1,y1) , (x2,y2) , (0,255,0),2)
            cv2.rectangle(img,(x1,y2-35) , (x2 , y2 ) , (0,255,0), cv2.FILLED )
            cv2.putText(img , name, (x1+6 , y2-6) , cv2.FONT_HERSHEY_COMPLEX , 1 , (255,255,255) , 2 )
            markAttendence(name)
            id = classNames[matchIndex]
            if counter == 0 :
                counter = 1 
            if counter != 0 : 
               if  counter == 1 :
                   studentInfo = db.reference(f'students/{id}').get()
                   ref = db.reference(f'students/{id}')
                   #get the image from storage 
                   blob = bucket.get_blob(f'practiceImages/{id}.png')
                   # update the data of attendance 
                   ref = db.reference(f'students/{id}')
                   now = datetime.now()
                   # prevTime= ref.child('Last_attendance').get(studentInfo['Last_attendance'])
                   prevTime = studentInfo.get('Last_attendance')
                   previous_time = datetime.strptime(prevTime, "%Y-%m-%d %H:%M:%S")
                   currentTime = datetime.now()
                   currentTime_str = currentTime.strftime("%Y-%m-%d %H:%M:%S")
                   #if the previous entered time is not in the ame day then only the attendance will be updated 
                #    if previous_time.date() != currentTime.date():
                   studentInfo['Last_attendance'] = currentTime_str
                   ref.child('Last_attendance').set(studentInfo['Last_attendance'])
                   studentInfo['Total_attendance'] += 1 
                   ref.child('Total_attendance').set(studentInfo['Total_attendance'])
                    #    studentInfo['marked_today'] = 'yes'
                    #    ref.child('marked_today').set(studentInfo['marked_today'])
                
                    #    studentInfo['marked_today'] = 'already marked'
                    #    ref.child('marked_today').set(studentInfo['marked_today'])
                   print(studentInfo)
                   counter +=1 
                   
                   
    cv2.imshow('Win' , img )
    cv2.waitKey(100)

#loading the image 
# imgMY = face_recognition.load_image_file('practImages\Screenshot 2023-12-23 174742.png')
# imgTest = face_recognition.load_image_file('images\WhatsApp Image 2023-12-23 at 10.28.58 AM.jpeg')
# #Converting the imgae from bgr to rgb cause the module takes only rgb
# imgMY = cv2.cvtColor(imgMY , cv2.COLOR_BGR2RGB)
# imgTest = cv2.cvtColor(imgTest , cv2.COLOR_BGR2RGB)

