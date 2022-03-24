
import os
import time

from flask import Flask, render_template, Response, make_response
from camera import VideoCamera
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
    return render_template('cur_camer.html')

@app.route('/cur_camera')
def cur_camera():
    return render_template('cur_camer.html')

if __name__ == '__main__':
    app.run()
