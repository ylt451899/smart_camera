# import MySQLdb
import mysql.connector
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
#連線資料庫
def insert_personInformation(inCamera,startTime,endTime):
    conn = mysql.connector.connect(host="127.0.0.1",user="root",password="",db="camera",charset='utf8')
    cursor = conn.cursor()

    SQL="INSERT INTO personinformation (inCamera, Picture, startTime, endTime) VALUES (%s, 0, %s, %s);"
    aa = [inCamera,startTime,endTime]
    cursor.execute(SQL,aa)
    conn.commit()
    last_insert_id = cursor.lastrowid
    print(cursor.lastrowid)
    # 更新 Picture 字段为最后插入的 ID
    SQL_2 = f"UPDATE personinformation SET Picture = {last_insert_id} WHERE id = {last_insert_id};"
    cursor.execute(SQL_2)
    conn.commit()

    # 获取插入后的 ID
    cursor.close()
    conn.close()  # 关闭连接
    return last_insert_id  # 返回 LAST_INSERT_ID()

#更新人物
def update_personInformation(personId,endTime):
    conn = mysql.connector.connect(host="127.0.0.1",user="root",password="",db="camera",charset='utf8')
    cursor = conn.cursor()

    SQL="UPDATE personinformation SET endTime=%s WHERE id=%s;"
    aa = [endTime,personId]
    cursor.execute(SQL,aa)
    conn.commit()
    # 获取插入后的 ID
    cursor.close()
    conn.close()  # 关闭连接
    return "update success"  # 返回 LAST_INSERT_ID()

def get_person_id():
    conn = mysql.connector.connect(host="127.0.0.1",user="root",password="",db="camera",charset='utf8')
    cursor = conn.cursor()

      # 执行查询语句
    SQL = "SELECT id FROM `personinformation`;"
    cursor.execute(SQL)
    # 获取查询结果
    results = cursor.fetchall()
    # 关闭游标和连接
    cursor.close()
    conn.close()
    # 返回查询结果
    return [row[0] for row in results]  # 假设你只想要 id 列的数据

# 打印获取的 person_id 列表
# print(get_person_id())
