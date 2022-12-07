from flask import Flask, jsonify, render_template, request,Response
import requests
import webbrowser
import time

import cv2
import numpy as np
from pyzbar.pyzbar import decode

# Insert image to program to test
# read the image
# img = cv2.imread('1.png')
# decode the qr code
# code = decode(img)

app = Flask(__name__)



# WebCam version
cam = cv2.VideoCapture(0)
cam.set(3,640)
cam.set(4,480)

# Center Circle
def center_handle(x,y,w,h):
    x1 = int(w/2)
    y1 = int(h/2)
    cx = x+x1
    cy = y+y1
    return cx,cy



def genFrames():
    detect = []
    cars = 0
    offset = 5 # Allowable Error
    once = False
    while True:
        sucess, img = cam.read()
        # Crossing line
        # cv2.line(img,(320,0),(320,480), (255,127,0), 3)

        if decode(img) != None:
            for qr in decode(img):
            
                # Extract data from qr code
                data = qr.data.decode('utf-8')
                # Extract dimensions and location of qr code
                points = np.array([qr.polygon],np.int32)
                points = points.reshape((-1,1,2))
                # Draw box
                cv2.polylines(img,[points],True,(255,0,255),5)
                # Draw circle in middle of bounding box
                (x,y,w,h) = qr.rect
                center = center_handle(x,y,w,h)
                detect.append(center)
                cv2.circle(img,center,4,(255,0,255),-1) 
                # print(center)
                
                
                # Increase counter based on location
                for(x,y) in detect:
                    # print(x,y)
                    if ((y < (300+offset)) and (y > (300-offset) and (x > 0) and (x < 320)) and once == False):
                        # cars+=1
                        cv2.line(img,(0,300),(320,300), (0,127,255), 3) 
                        detect.remove((x,y))
                        once = True
                    elif ((y < (300+offset)) and (y > (300-offset) and (x > 330) and (x < 720)) and cars > 0):
                        cars-=1
                        cv2.line(img,(410,360),(660,360), (0,127,255), 3) 
                        detect.remove((x,y))
                    elif ((y < (280+offset)) and (y > (280-offset) and (x > 0) and (x < 320)) and once == True):
                        
                        cars+=1
                        # cv2.line(img,(410,360),(660,360), (0,127,255), 3) 
                        detect.remove((x,y))
                        once = False
                        break
                        
                    # elif ((y < (550+offset)) and (y > (550-offset) and (x > 700) and (x < 1100))):
                    #     cars-=1
                    #     cv2.line(img,(700,550),(1100,550), (0,127,255), 3) 
                    #     detect.remove((x,y))    

        cv2.line(img,(0,300),(320,300), (255,127,0), 3)
        cv2.line(img,(0,280),(320,280), (255,200,0), 3)
        cv2.line(img,(330,300),(720,300), (0,0,255), 3)
        cv2.putText(img,"Cars: " + str(cars),(250,70),cv2.FONT_HERSHEY_SIMPLEX,2,(122,56,255),5)

        # cv2.imshow('Dectect me pls',img)
        # cv2.waitKey(1)

        ret, buffer = cv2.imencode('.jpg',img)
        img = buffer.tobytes()
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')


@app.route('/video')
def video():
    return Response(genFrames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__=="__main__":
    app.run(debug=True)

