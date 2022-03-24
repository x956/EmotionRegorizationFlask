import cv2

# from resource.emotion_sex_recognition import detect_regorization
import time
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

# 加载数据和图像的参数
detection_model_path = "E:\\biyepractice\EmotionRegorizationFlask\\resource\models\detection_models\haarcascade_frontalface_default.xml"
emotion_model_path = "E:\\biyepractice\EmotionRegorizationFlask\\resource\models\emotion_models\\fer2013_mini_XCEPTION.110-0.65.hdf5"
# gender_model_path = "E:\\biyepractice\EmotionRegorizationFlask\\resource\models\gender_models\simple_CNN.81-0.96.hdf5"
emotion_labels = get_labels('fer2013')
# gender_labels = get_labels('imdb')
font = cv2.FONT_HERSHEY_SIMPLEX

# 定义形状的超参数
frame_window = 10
gender_offsets = (30, 60)
emotion_offsets = (20, 40)

# 加载模型
face_detection = load_detection_model(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)
# gender_classifier = load_model(gender_model_path, compile=False)

# 获取用于推理的输入模型形状
emotion_target_size = emotion_classifier.input_shape[1:3]
# gender_target_size = gender_classifier.input_shape[1:3]

# 计算模式的起始列表
# gender_window = []
emotion_window = []

video_capture=cv2.VideoCapture(0)
# t0 = time.time()
#image=detect_regorization(video_capture)
while True:
    t0 = time.time()

    bgr_image = video_capture.read()[1]

    #图像模式的转换
    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    #查找人脸
    faces = detect_faces(face_detection, gray_image)

    for face_coordinates in faces:
        #获取坐标进行框选
        # x1, x2, y1, y2 = apply_offsets(face_coordinates, gender_offsets)
        # rgb_face = rgb_image[y1:y2, x1:x2]

        x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
        gray_face = gray_image[y1:y2, x1:x2]

        #图像大小
        try:
            #rgb_face = cv2.resize(rgb_face, (gender_target_size))
            gray_face = cv2.resize(gray_face, (emotion_target_size))
        except:
            continue
        #标准化
        gray_face = preprocess_input(gray_face, False)

        #扩展数组的形状
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        #计算相似度
        emotion_prediction = emotion_classifier.predict(gray_face)
        #寻找可能性最大的表情
        emotion_probability = np.max(emotion_prediction)
        emotion_label_arg = np.argmax(emotion_prediction)

        print("表情种类：",emotion_label_arg)

        emotion_label_arg = np.argmax(emotion_classifier.predict(gray_face))
        emotion_text = emotion_labels[emotion_label_arg]
        emotion_window.append(emotion_text)

        # rgb_face = np.expand_dims(rgb_face, 0)

        # rgb_face = preprocess_input(rgb_face, False)
        #相似度
        #gender_prediction = gender_classifier.predict(rgb_face)
        #找出相似度最高的性别
        #gender_label_arg = np.argmax(gender_prediction)
        #print("性别：",gender_label_arg)
        #gender_text = gender_labels[gender_label_arg]
        #gender_window.append(gender_text)

        #长度限制
        #if len(gender_window) > frame_window:
        #    emotion_window.pop(0)
        #    gender_window.pop(0)
        #获取名称
        try:
            emotion_mode = mode(emotion_window)
        #    gender_mode = mode(gender_window)
        except:
            continue

        #框的颜色
        if emotion_text == 'angry':
            color = emotion_probability * np.asarray((255, 0, 0))
        elif emotion_text == 'sad':
            color = emotion_probability * np.asarray((0, 0, 255))
        elif emotion_text == 'happy':
            color = emotion_probability * np.asarray((255, 255, 0))
        elif emotion_text == 'surprise':
            color = emotion_probability * np.asarray((0, 255, 255))
        else:
            color = emotion_probability * np.asarray((0, 255, 0))

        color = color.astype(int)
        color = color.tolist()

        #图像上绘制边框。
        draw_bounding_box(face_coordinates, rgb_image, color)

        #gender_mode=gender_mode+"  "+"<No entry>"
        #打印在图片上
        # draw_text(face_coordinates, rgb_image, gender_mode,
        #           color, 0, -20, 1, 1)
        #显示识别相似度百分比
        emotion_probability=int(emotion_probability*100)
        emotion_mode=emotion_mode+" "+str(emotion_probability)+"%"
        #显示视频帧率
        #fps = "fps:"+str(video_capture.get(cv2.CAP_PROP_FPS))
        #cv2.putText(rgb_image, fps, (5, 25), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 255, 0), 0)

        draw_text(face_coordinates, rgb_image, emotion_mode,
                  color, 0, -45, 1, 1)
        #输出部分数据
        demo="--"+emotion_mode+"--"#+gender_mode
        print(demo)
        #开启多线程传输数据，默认屏蔽
        #  thread1=threading.Thread(target=swop,args=(emotion_label_arg,j, gender_label_arg, 18, emotion_probability))
        #  thread1.start()

    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    #bgr_image = cv2.resize(bgr_image, dsize=(1280, 720))
    # cv2.imshow('window_frame', bgr_image)
    t1 = time.time()
    print("Total running time: %s s" % (str(t1 - t0)))


# t1 = time.time()
# print("Total running time: %s s" % (str(t1 - t0)))




video_capture.release()