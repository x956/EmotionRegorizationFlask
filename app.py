from flask import Flask, render_template, Response, make_response, request, redirect
from camera import VideoCamera
import pymysql

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
    connect = pymysql.connect(host='localhost', user='root', password='123456', database='emotional_analysis')
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

    return render_template('informationq.html',name=name,sex=sex,phone=phone,Pno=Pno,Dno=Dno)




@app.route('/cur_camera')
def cur_camera():
    return render_template('cur_camer.html')

@app.route('/upload_patient_info',methods=['GET', 'POST'])
def upload_patient_info():
    name = request.form.get('name')
    telephone = request.form.get('telephone')
    sex = request.form.get('sex')
    print(name,telephone,sex)

    return render_template('information.html')


if __name__ == '__main__':
    app.run(host='192.168.0.108',port='5000')
