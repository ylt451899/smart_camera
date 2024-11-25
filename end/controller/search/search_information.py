from flask import Blueprint, request,jsonify
from model.DB import DB
import datetime
select_person_information = Blueprint('select_person_info', __name__)

# Flask 路由
@select_person_information.route('/info', methods=['POST'])
def get_person_information():
    try:

        # 取得 JSON 資料
        data = request.get_json()
        # 從請求中獲取 'feature'
        feature = data["feature"]
        # feature = request.values.get('feature')
        feature = feature.split(',')
        # 構建 SQL 查詢中的 feature 列表
        feature_text = "(" 
        for i in range(len(feature)):
            if(i == len(feature)-1): feature_text += f"'{feature[i]}' )"
            else:  feature_text += f"'{feature[i]}' ,"

        # 從 JSON 中解析時間
        start_datetime = datetime.datetime.strptime(data["start_datetime"], "%Y-%m-%d %H:%M")
        end_datetime = datetime.datetime.strptime(data["end_datetime"], "%Y-%m-%d %H:%M")

        # 從 JSON 中取得 camera 陣列
        camera = data.get('camera')  # camera 應該是個陣列

        # 其他查詢代碼...
        # 例如將 camera 陣列加入 SQL 查詢中
        camera_filter = ",".join(f"'{str(int(c.split('era')[1]) - 1)}'" for c in camera)
        # camera_filter = ",".join(f"'{c}'" for c in camera)
        
        print(camera_filter)
        print(start_datetime)
        print(end_datetime)
       

        sql = f"""
        SELECT p.id, p.inCamera, p.Picture, 
               GROUP_CONCAT(concat(f2.color, ' ', f2.feature)) as feature,
               p.startTime, p.endTime
        FROM personinformation p
        INNER JOIN (
            SELECT
                f.personId,
                SUM(
                    CASE
                    WHEN CONCAT(f.color, ' ', f.feature) IN {feature_text} THEN 1
                    ELSE 0
                    END
                ) AS calculatedSum
            FROM feature f
            WHERE CONCAT(f.color, ' ', f.feature) IN {feature_text}
            GROUP BY f.personId
        ) f
        ON p.id = f.personId
        INNER JOIN feature f2
        ON p.id = f2.personId
        WHERE p.inCamera IN ({camera_filter})
          AND p.startTime >= '{start_datetime}' 
          AND p.endTime <= '{end_datetime}'
        GROUP BY p.id
        ORDER BY f.calculatedSum DESC, p.endTime DESC;
        """

        # 執行 SQL 查詢
        result = DB(sql,"查詢")
        # 分割 feature 字串
        # 返回結果
        return jsonify({
            "status" : 200,
            "message": "查詢成功",
            "result": result,
        })
    
    except Exception as e:
        # 處理錯誤
        return jsonify({
            "status" : 404,
            "message": "查詢失敗",
            "error": str(e),
        })
