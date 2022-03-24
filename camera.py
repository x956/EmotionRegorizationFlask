import cv2
from resource.emotion_sex_recognition import detect_regorization
from statistics import mode

import cv2
from keras.models import load_model
import numpy as np

from resource.utils_base.datasets import get_labels
from resource.utils_base.inference import detect_faces
from resource.utils_base.inference import draw_text
from resource.utils_base.inference import draw_bounding_box
from resource.utils_base.inference import apply_offsets
from resource.utils_base.inference import load_detection_model
from resource.utils_base.preprocessor import preprocess_input

import threading
from urllib import parse,request
import time

class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        # 加载数据和图像的参数
        detection_model_path = "E:\\biyepractice\EmotionRegorizationFlask\\resource\models\detection_models\haarcascade_frontalface_default.xml"
        emotion_model_path = "E:\\biyepractice\EmotionRegorizationFlask\\resource\models\emotion_models\\fer2013_mini_XCEPTION.110-0.65.hdf5"
        # gender_model_path = "E:\\biyepractice\EmotionRegorizationFlask\\resource\models\gender_models\simple_CNN.81-0.96.hdf5"
        self.emotion_labels = get_labels('fer2013')
        # gender_labels = get_labels('imdb')
        font = cv2.FONT_HERSHEY_SIMPLEX

        # 定义形状的超参数
        frame_window = 10
        gender_offsets = (30, 60)
        self.emotion_offsets = (20, 40)

        # 加载模型
        self.face_detection = load_detection_model(detection_model_path)
        self.emotion_classifier = load_model(emotion_model_path, compile=False)
        # gender_classifier = load_model(gender_model_path, compile=False)

        # 获取用于推理的输入模型形状
        self.emotion_target_size = self.emotion_classifier.input_shape[1:3]
        # gender_target_size = gender_classifier.input_shape[1:3]

        # 计算模式的起始列表
        # gender_window = []
        self.emotion_window = []
        #print("正常读入的画面类型",type(self.video))
        #self.video=detect_regorization(cv2.VideoCapture(0))
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        #image = self.video
        image=detect_regorization(self.video,self.face_detection,
                                  self.emotion_offsets,self.emotion_target_size,
                                  self.emotion_classifier,self.emotion_labels,
                                  self.emotion_window)
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
