import json
import os
import time

from flask import Flask, render_template, Response, make_response, request, redirect
from camera import VideoCamera
import pymysql

import cv2
from resource.emotion_sex_recognition import detect_regorization

app = Flask(__name__)

#相机推流
def gen(camera):
    while True:
        frame=camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#相机喂流
@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def hello_world():  # put application's code here
    return render_template('login.html')


@app.route('/verify',methods=['GET', 'POST'])
def verify():
    username=request.form.get('username')
    password=request.form.get('password')
    connect=pymysql.connect('localhost','root','123456','emotional_analysis')
    cursor = connect.cursor()
    sql = "SELECT * FROM doc_account WHERE Daccount= '%s'" % username
    cursor.execute(sql)
    result = cursor.fetchone()
    connect.commit()
    connect.close()
    print(result)
    if(result and result[1] == password):
        return render_template('cur_camer.html')
    else:
        return render_template('login.html')

@app.route('/cur_camera')
def cur_camera():
    return render_template('cur_camer.html')

if __name__ == '__main__':
    app.run(host='192.168.0.108',port='5000')
