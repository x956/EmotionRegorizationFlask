from flask import Flask, render_template, Response, request, make_response
from camera import VideoCamera
import pymysql
import time
import datetime
import sys
sys.path.append(r'E:\\PyCharm Community Edition 2020.2.3\\EmotionRegorizationFlask\\resource')
import global_var
from io import BytesIO
import xlsxwriter

app = Flask(__name__)
global_var._init()

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


def create_workbook(Pno):
    connect=pymysql.connect(host='localhost', user='root', password='111111', database='emotional_analysis')
    cursor = connect.cursor()
    sql= "SELECT * FROM state where Pno= "+str(Pno)
    cursor.execute(sql)
    cursor.scroll(0,mode="absolute")
    results=cursor.fetchall()
    fields = cursor.description
    title = []
    for field in range(0, len(fields)):
        title.append(fields[field][0])
    output = BytesIO()
    # 创建Excel文件,不保存,直接输出
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    # 设置Sheet的名字为download
    worksheet = workbook.add_worksheet(str(Pno)+'病人数据')
    # 列首
    worksheet.write_row('A1', title)
    for i in range(len(results)):
        row = [str(results[i][0]),str(results[i][1]),str(results[i][2]),str(results[i][3])]
        worksheet.write_row('A' + str(i + 2), row)
    workbook.close()
    response = make_response(output.getvalue())
    output.close()
    return response


@app.route('/')
def hello_world():  # put application's code here
    return render_template('login.html')


@app.route('/verify',methods=['GET', 'POST'])
def verify():
    username=request.form.get('username')
    password=request.form.get('password')
    connect=pymysql.connect(host='localhost', user='root', password='111111', database='emotional_analysis')
    cursor = connect.cursor()
    sql = "SELECT * FROM doctor WHERE Daccount= '%s'" % username
    cursor.execute(sql)
    result = cursor.fetchone()
    connect.commit()
    connect.close()
    Dno = result[0]
    print(result)
    if(result and result[2] == password):
        return render_template('information.html',Dno = Dno)
    else:
        return render_template('login.html')

@app.route('/subm', methods=['GET', 'POST'])
def subm():
    name=request.form.get('name')
    sex=request.form.get('sex')
    phone=request.form.get('phone')
    Pno=request.form.get('Pno')
    Dno=request.form.get('Dno')
    connect = pymysql.connect(host='localhost', user='root', password='111111', database='emotional_analysis')
    cursor = connect.cursor()
    sql = "SELECT * FROM doctor WHERE Dno= '%s'" % Dno
    cursor.execute(sql)
    connect.commit()
    result = cursor.fetchone()
    if result:
        cursor = connect.cursor()
        sql = "SELECT * FROM patient WHERE Pno= '%s'" % Pno
        cursor.execute(sql)
        connect.commit()
        result = cursor.fetchone()
        if not result:
            sql = " insert patient(Pno,Pname,Psex,Dno,Phone) values('%s','%s','%s','%s','%s')" % (Pno,name,sex,Dno,phone)
            cursor.execute(sql)
            connect.commit()
        connect.close()
    global_var.set_value('name',name)
    global_var.set_value('Pno', Pno)
    return render_template('informationq.html',name=name,sex=sex,phone=phone,Pno=Pno,Dno=Dno)


@app.route('/puton', methods=['GET', 'POST'])
def puton():
    while 1:
        now_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        time.sleep(10)
        number = global_var.get_value('emotion_label_arg')
        emo="angry"
        if number == 0:
            emo="angry"
        elif number == 1:
            emo="disgust"
        elif number == 2:
            emo="fear"
        elif number == 3:
            emo="happy"
        elif number == 4:
            emo="sad"
        elif number == 5:
            emo="surprise"
        elif number == 6:
            emo="neutral"
        name = global_var.get_value('name')
        Pno = global_var.get_value('Pno')
        connect = pymysql.connect(host='localhost', user='root', password='111111', database='emotional_analysis')
        cursor = connect.cursor()
        sql = " insert state(Pno,Pname,State,time) values('%s','%s','%s','%s')" % (Pno, name, emo, now_time)
        cursor.execute(sql)
        connect.commit()
        connect.close()


@app.route('/upload_patient_info',methods=['GET', 'POST'])
def upload_patient_info():
    name = request.form.get('name')
    telephone = request.form.get('telephone')
    sex = request.form.get('sex')
    print(name,telephone,sex)
    return render_template('information.html')


@app.route('/download/<Pno>', methods=['GET'])
def download(Pno):
    response = create_workbook(Pno)
    response.headers['Content-Type'] = "utf-8"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Disposition"] = "attachment; filename="+str(Pno)+"--state"+".xlsx"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000')
