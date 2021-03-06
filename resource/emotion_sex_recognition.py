from statistics import mode

import cv2
import numpy as np

from .utils_base.inference import detect_faces
from .utils_base.inference import draw_text
from .utils_base.inference import draw_bounding_box
from .utils_base.inference import apply_offsets
from .utils_base.preprocessor import preprocess_input

from urllib import parse,request
import global_var

#这是数据传输模块，没有需要的时候不需要使用
def swop(emotion,name,sex,age,gl):
    values={"id":name,"number":emotion}
    data=parse.urlencode(values)
    try:
        url = 'http://127.0.0.1.ngrok.xiaomiqiu.cn/saw_2'
        req = request.Request(url, data.encode(encoding='utf-8'))
        print("服务器接入成功，数据成功传输!")
    except:
        print("服务器接入失败，数据将临时保存")

#预先打开窗口


#连接网络摄像头识别
#video_capture = cv2.VideoCapture(0)

def detect_regorization(video_capture,face_detection,
                        emotion_offsets,emotion_target_size,emotion_classifier,
                        emotion_labels,emotion_window):

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
        # emotion_label_arg = np.argmax(emotion_prediction)
        global_var.set_value('emotion_label_arg', np.argmax(emotion_prediction))

        #print("表情种类：",emotion_label_arg)

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
        #print(demo)
        #开启多线程传输数据，默认屏蔽
        #  thread1=threading.Thread(target=swop,args=(emotion_label_arg,j, gender_label_arg, 18, emotion_probability))
        #  thread1.start()

    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    #bgr_image = cv2.resize(bgr_image, dsize=(1280, 720))
    # cv2.imshow('window_frame', bgr_image)
    return bgr_image

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
# video_capture.release()
# cv2.destroyAllWindows()
