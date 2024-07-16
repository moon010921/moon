from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextMessage,MessageEvent,LocationMessage
import os
import pandas as pd
import dotenv
import requests
from geopy.distance import geodesic
dotenv.load_dotenv()

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('TOKEN'))
Handler = WebhookHandler(os.getenv('SECRET'))
r = requests.get('http://data.tycg.gov.tw/api/v1/rest/datastore/a1b4714b-3b75-4ff8-a8f2-cc377e4eaa0f?format=json&limit=300')
all_records = r.json()['result']['records']
df = pd.DataFrame(all_records)

# 转换经纬度为浮点数
df['lat'] = df['lat'].astype(float)
df['lng'] = df['lng'].astype(float)

# 用户位置（示例）
user_location = (24.123456, 121.123456)  # 替换为您的经纬度

# 计算所有站点的距离
df['distance'] = df.apply(lambda row: geodesic(user_location, (row['lat'], row['lng'])).kilometers, axis=1)

# 输出结果
print(df[['sarea', 'lat', 'lng', 'distance']])  # 替换'站名'为实际的列名


@app.route('/')
def home():
    return '窩不知道' 


@app.route('/callback',methods=['POST'])
def callable():
    signature = request.headers['X-Line-Signature']
    print(signature)
    bady = request.get_data(as_text=True)
    print('失敗')
    Handler.handle(bady,signature)
    print(bady)
    
    return '窩不知道'
@Handler.add(MessageEvent, message=TextMessage)
def Handle_message(event):
    if event.message.text == "0":
        s="我"
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=s)
            )
    elif event.message.text == "1":
        s="你"
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=s)
            )
@Handler.add(MessageEvent, message=LocationMessage)
def Handle_message(event):
    user_lat = event.message.latitude
    user_lon = event.message.longitude
        # 用户位置
    user_location = (user_lat, user_lon)

    # 计算所有站点的距离
    df['distance'] = df.apply(lambda row: geodesic(user_location, (row['lat'], row['lng'])).kilometers, axis=1)

    # 找出最近的站点
    nearest_station = df.loc[df['distance'].idxmin()]

    # 发送回复
    reply_message = f"您最近的站点是: {nearest_station['sarea']}, 距离: {nearest_station['distance']:.2f} 公里"
    line_bot_api.reply_message(event.reply_token, TextMessage(text=reply_message))


if __name__ == '__main__':
    app.run(port=5050)
