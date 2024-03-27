import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
import winsound


# from PIL import ImageGrab

path = 'C:/Users/banda/Downloads/Face/image_folder'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)



def mail_sent(toaddr, filename, path, body):
    fromaddr = "testingautomation243@gmail.com"
    toaddr = toaddr
    msg = MIMEMultipart() 
    msg['From'] = fromaddr 
    msg['To'] = toaddr 
    msg['Subject'] = "Face Recorded detection"
    body = body
    msg.attach(MIMEText(body, 'plain')) 
    filename = filename
    attachment = open(path, "rb") 
    p = MIMEBase('application', 'octet-stream') 
    p.set_payload((attachment).read()) 
    encoders.encode_base64(p) 
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
    msg.attach(p) 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login(fromaddr, "qfbhurcoigibaezh") 
    text = msg.as_string() 
    s.sendmail(fromaddr, toaddr, text)
    print("sebnt mail")
    s.quit() 
    

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markPerson(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()

        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            #dtString = now.strftime('%H:%M:%S')
            date_s =  now.strftime('%d/%m/%y')
            time_s = now.strftime('%H:%M:%S')
            status = "KNOWN PERSON"
            f.writelines(f'\n{name},{date_s},{time_s},{status}')


encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)

width= int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height= int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

writer= cv2.VideoWriter('known.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 20, (width,height))

writer1= cv2.VideoWriter('unknown.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 20, (width,height))
name1=""
while True:
    ls=[]
    success, img = cap.read()
# img = captureScreen()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
# print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            markPerson(name)
            if name not in name1:
                name1 = name
                writer.write(img)
                for v in range(500000):
                    pass
                writer.release()
                mail_sent("penjarathilak9662@gmail.com", "known.mp4",  "C:/Users/banda/Downloads/Face/known.mp4", "known person detected attached recording above")
            
        else:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, "Unknown Person", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            winsound.Beep(1500, 2000)
            writer1.write(img)
            for v in range(500000):
                pass
            writer1.release()
            mail_sent("bandavamshi90@gmail.com", "unknown.mp4",  "C:/Users/banda/Downloads/Face/unknown.mp4", "unknown person detected attached recording above")
       
    cv2.imshow('Webcam', img)
    cv2.waitKey(1)
    writer.release()
