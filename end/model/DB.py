from flask import Flask, jsonify
# import MySQLdb
import mysql.connector
from dotenv import load_dotenv
import os
# 載入環境變數
load_dotenv()
app = Flask(__name__)

# 建立 MySQL 連接
def get_db_connection():
    return mysql.connector.connect(
        host= os.getenv("dbHost"),
        user= os.getenv("dbUser"),
        password= os.getenv("dbPassword"),
        db= os.getenv("dbName"),
        charset='utf8'
    )

# 回應函數
def response(status, message, result=None):
    return {
        "status": status,
        "message": message,
        "result": result,
    }

# SQL 執行函數
def DB(sql, func):
    conn = get_db_connection()
    cursor = conn.cursor()  # 使用字典游標方便取得結果
    try:
        cursor.execute(sql)
        if func == "查詢":
            result = cursor.fetchall()  # 獲取所有查詢結果
            return result
            # return response(200, f"{func} 成功", result)
        else:
            conn.commit()  # 執行寫入類操作需要提交
            return "aaa"
            # return response(200, f"{func} 成功")
    except Exception as e:
        return "error"
        # return response(404, str(e))
    finally:
        cursor.close()
        conn.close()  # 關閉連接
