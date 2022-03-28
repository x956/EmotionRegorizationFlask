# !/usr/bin/python3
import pymysql
import numpy as np
from sklearn.linear_model import LinearRegression
import time
# 在 analysis 表中，根据 id 查找 某年 某果树的最大值数据，返回当年产量，失败返回-1
from conn import get_conn

def select_id_year_analysis(id,year):
    db = pymysql.connect(host='localhost', user='root', password='180226', database='testdb')
    cursor = db.cursor()
    sql = 'SELECT * FROM analysis WHERE id = {0} AND year = {1}'.format(id,year)
    cursor.execute(sql)
    result = cursor.fetchone()
    # print('[{0}] 号果树 [{1}] 年数据:\n产量:{2}\n检测员:{3}\n检测时间:{4}'.format(result[0],result[1],result[2],result[3],result[4]))
    db.commit()
    db.close()
    return result[2]
# print(select_id_year(1,2019))
# 在 apple 表中 查找某年的所有检测记录，默认 2021 年,返回检测记录的列表，按时间升序排序
def select_id_year_apple(id,year=2021):
    db = pymysql.connect(host='218.199.186.97', user='root', password='123456', database='testdb')
    cursor = db.cursor()
    sql = 'SELECT * FROM apple WHERE id = {0} AND year = {1}'.format(id, year)
    cursor.execute(sql)
    result = cursor.fetchall()
    db.commit()
    # for item in result:
    #     print('[{0}] 号果树 [{1}] 年数据:\n产量:{2}\n检测员:{3}\n检测时间:{4}'.format(item[0], item[1], item[2], item[3],item[4]))
    # print(result)
    db.close()
    return result
# 在 analysis 表中查询某一年的所有果树数据,默认2021年
def select_year_analysis(year=2021):
    db = pymysql.connect(host='218.199.186.97', user='root', password='123456', database='testdb')
    cursor = db.cursor()
    # print('[{0}]年果园数据'.format(year))
    sql = 'SELECT * FROM analysis WHERE year = {0}'.format(year)
    cursor.execute(sql)
    result = cursor.fetchall()
    # db.commit()
    #print(result)
    # ans = 0
    # number = 0
    # for row in result:
    #     id = row[0]
    #     year = row[1]
    #     number = row[2]
    #     ans = ans + number
        # print("%s 号果树 %s 年 产量:%s 检测员:%s 日期:%s " % (id, year, number, name,date))
    db.close()
    #print('%d 年总产量：%d'%(year,ans))
    return result
# 插入某年某果树的数据，如果已有数据，则更新
def output_cnt(year=2021):
    result=select_year_analysis(year)
    ans = 0
    for row in result:
        ans = ans + row[2]
    return ans

def insert_id_year(id,number,name):
    db = pymysql.connect(host='218.199.186.97', user='root', password='123456', database='testdb')
    cur_time = time.strftime("%Y-%m-%d", time.localtime())
    year = int(cur_time[:4])
    # print(cur_time)
    # print(year)
    cursor = db.cursor()
    # 同一天 同一个人 的检测记录会覆盖
    sql = "SELECT * FROM apple WHERE id = {0} AND name = '{1}' AND date = '{2}'".format(id,name,cur_time)
    cnt = cursor.execute(sql)
    # apple 表的修改
    # 如果没有 同一天的检测记录，则插入
    if(cnt == 0):
        # 向 apple 表中插入一条检测记录
        sql1 = "INSERT INTO apple VALUES(%d,%04d,%d,'%s','%s')" % (id, year,number, name, cur_time)
        print(sql1)
        try:
            cursor.execute(sql1)
            db.commit()
            print('apple 首次插入成功')
        except:
            db.rollback()
            print('apple 首次插入失败')
    # 否则更新 当天的检测记录
    else:
        sql1 = "UPDATE apple SET number = %d"%(number)
        try:
            cursor.execute(sql1)
            db.commit()
            print('apple 更新成功')
        except:
            db.rollback()
            print('apple 更新失败')

    # analysis 表的修改
    # 如果 analysis 表中没有当年数据，则直接插入
    sql = "SELECT * FROM analysis WHERE id = {0} AND year = {1}".format(id, year)
    cnt = cursor.execute(sql)
    result = cursor.fetchone()
    if (cnt == 0):
        sql = "INSERT INTO analysis VALUES(%d,%04d,%d)" % (id, year, number)
        try:
            cursor.execute(sql)
            db.commit()
            print('analysis 插入成功')
        except:
            db.rollback()
            print('analysis 插入失败')
            db.close()
            return -2
    # 否则更新 analysis 表中的值
    else:
        if (number > result[2]):
            sql = 'UPDATE analysis SET number = %d' % (number)
            try:
                cursor.execute(sql)
                db.commit()
                print('analysis 更新成功')
            except:
                db.rollback()
                print('analysis 更新失败')
                db.close()
                return -3
    db.close()
# 预测 某棵树 后两年走势,返回[2,1]np.array列表
def predict_id(id):
    db = pymysql.connect(host='218.199.186.97', user='root', password='123456', database='testdb')
    cursor = db.cursor()
    sql = 'SELECT * FROM analysis WHERE id = {0}'.format(id)
    # cnt 接收返回的元组个数
    cursor.execute(sql)
    # print('cnt:',cnt)
    result = cursor.fetchall()
    years = []          # 年份数组
    num = []            # 产量数组
    # print(result)
    cnt=len(result)
    for item in result:
        years.append(item[1])
        num.append(item[2])
    years1 = np.array(years).reshape((cnt,1))
    # print('years1:',years1)
    # print('numbers:')
    num1 = np.array(num).reshape((cnt,1))
    lin_reg = LinearRegression()
    lin_reg.fit(years1, num1)
    # print('weights:')
    # print(lin_reg.intercept_, lin_reg.coef_)
    next2year = [[years[cnt-1]+1],[years[cnt-1]+2]]
    # print('后两年:')
    # print(next2year)
    # print('后两年预测:')
    ans = lin_reg.predict(next2year)
    return ans.reshape((1,2))


# 预测果园后两年走势，返回列表
def predict_all():
    db = pymysql.connect(host='218.199.186.97', user='root', password='123456', database='testdb')
    cursor = db.cursor()
    sql = 'SELECT * FROM analysis'
    # cnt 接收返回的元组个数
    cnt = cursor.execute(sql)
    # print('cnt:',cnt)
    result = cursor.fetchall()
    # print(result)
    # print(type(result[0][1]))
    # 构造 years[] 保存库里所有出现的年份
    year = []
    for item in result:
        if(year.count(item[1])==0):
            year.append(item[1])
            # print(item[1])
    years = sorted(year)
    # print('years:',years)
    len_y = len(years)
    # 构造num[] 保存每年的产量数组
    num = []
    for item in years:
        # print('item:',item)
        # print('cur year:', cur_year)
        # print(select_year_analysis(item))
        num.append(output_cnt(item))
    # 转换成 np.array
    years1 = np.array(years).reshape((len(years), 1))
    num1 = np.array(num).reshape((len_y, 1))
    # print(num1)
    lin_reg = LinearRegression()
    lin_reg.fit(years1, num1)
    # print('weights:')
    # print(lin_reg.intercept_, lin_reg.coef_)
    next2year = [[years[len_y - 1] + 1], [years[len_y - 1] + 2]]
    # print('后两年:')
    # print(next2year)
    # print('后两年预测:')
    ans = lin_reg.predict(next2year)
    # print('ans:',ans)
    # print('len_y:',len_y)
    res = []
    res.append(ans[0][0])
    res.append(ans[1][0])
    db.close()
    return res

# 验证登录 ,根据 用户名，密码 验证登录, 成功登录返回 1，失败返回 0
def login(name,key):
    db = pymysql.connect(host='218.199.186.97', user='root', password='123456', database='testdb')
    cursor = db.cursor()
    sql = 'SELECT * FROM user'
    cursor.execute(sql)
    result = cursor.fetchall()
    for item in result:
        if(item[0] == name and item[1] == key):
            db.close()
            return 1
    db.close()
    return 0

# 注册用户，成功返回 1，失败返回 0
def creat_user(name,key):
    db = pymysql.connect(host='218.199.186.97', user='root', password='123456', database='testdb')
    cursor = db.cursor()

    sql = "INSERT INTO user VALUES('%s','%s') "%(name,key)
    try:
        cursor.execute(sql)
        db.commit()
        result = cursor.fetchone()
        print('successfully create a user:%s'%(name))
        db.close()
        return 1
    except:
        db.rollback()
        print('create user error!')
        db.close()
        return 0

# 删除用户
def delete_user(name):
    db = pymysql.connect(host='218.199.186.97', user='root', password='123456', database='testdb')
    cursor = db.cursor()
    sql = "DELETE FROM user WHERE name = '%s'"%(name)
    try:
        cursor.execute(sql)
        db.commit()
        print('successfully delete a user:%s'%(name))
        return 1
    except:
        db.rollback()
        return 0

def select_id_year_num_apple(id, year, num): # 根据id、年份、果实数量来查询检测信息
    db = get_conn()
    cursor = db.cursor()
    sql = 'SELECT * FROM apple WHERE id = {0} AND year = {1} AND number = {2}'.format(id, year, num)
    cursor.execute(sql)
    result = cursor.fetchall()
    db.commit()
    db.close()
    return result
