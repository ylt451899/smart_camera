# import MySQLdb
import mysql.connector
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
#連線資料庫
def insert_feature(personId, Feature, Color):
    print("insert_feature")
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root", password="",
            db="camera", charset='utf8')
        cursor = conn.cursor()

        # personId 一個 feature跟color會是陣列
        SQL = "INSERT INTO feature(personId,Feature,Color) VALUES(%s,%s,%s)"
        aa = []
        for i in range(len(Feature)):
            aa.append((personId, Feature[i], Color[i]))

        cursor.executemany(SQL, aa)
        conn.commit()

        print(f"Inserted {cursor.rowcount} rows into the 'feature' table.")  # Show how many rows were inserted
    except mysql.connector.Error as err:
        print(f"Error: {err}")  # Show error if something goes wrong
    finally:
        cursor.close()
        conn.close()  # 关闭连接
# def insert_feature(personId,Feature,Color):
#     print("insert_feature")
#     conn = mysql.connector.connect(
#         host="127.0.0.1",
#         user="root",password="",
#         db="camera",charset='utf8')
#     cursor = conn.cursor()
#     # personId 一個 feature跟color會是陣列
#     SQL="INSERT INTO feature(personId,Feature,Color) VALUES(%s,%s,%s)"
#     aa = []
#     for i in range(0,len(Feature)):
#         aa.append([personId,Feature[i],Color[i]])
#     print('SQL insert:',cursor.executemany(SQL,aa))
#     conn.commit()
#     cursor.close()
#     conn.close()  # 关闭连接

def update_feature(personId,Feature,Color):
    conn = mysql.connector.connect(host="127.0.0.1",user="root",password="",db="camera",charset='utf8')
    cursor = conn.cursor()
    # personId 一個 feature跟color會是陣列
    SQL="INSERT INTO feature(personId,Feature,Color) VALUES(%s,%s,%s)"
    aa = []
    for i in range(0,len(Feature)):
        aa.append([personId,Feature[i],Color[i]])
    print('SQL insert:',cursor.executemany(SQL,aa))
    conn.commit()
    cursor.close()
    conn.close()  # 关闭连接

