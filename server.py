import openai
from openai import OpenAI

from flask import Flask, request

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage   # 載入 TextSendMessage 模組
import json

app = Flask(__name__)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print(json_data)
    try:
        line_bot_api = LineBotApi('btYRELB4P+YSCvuIuWxLzcsRBuU4d+uui1/9pWxCZRDS9U6BhGr6MgM9oVgzf8ott8gcjZsD2xuGI4AZVQ4f5vBiYun7G02g9JhLgP8TZY6Fqy9zI9lm/1ekNtNZW249ButepCSwrVO5biQj+zhb3gdB04t89/1O/w1cDnyilFU=')
        handler = WebhookHandler('c2fd42d7c362fc5b9e865772402b3378')
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']
        msg = json_data['events'][0]['message']['text']
        print("pass 0")
        # 取出文字的前五個字元，轉換成小寫
        ai_msg = msg[:6].lower()
        print(ai_msg)
        reply_msg = ''
        # 取出文字的前五個字元是 hi ai:
        if ai_msg == 'hi ai:':
            openai.api_key = 'sk-lilibagel-Lk9Zpf3dTWbmzzT1xzhrT3BlbkFJozgKyyieCp5o69ytqA6C'
            try :
                client = OpenAI()
                print("pass1")
                print(msg[6:])
                # 將第六個字元之後的訊息發送給 OpenAI
                response = client.completions.create(
                    model="ft:davinci-002:personal::9foev6P4",#gpt-3.5-turbo-instruct
                    prompt = msg[6:],
                    max_tokens=200,
                )   
                print("pass2")
                reply_msg = response.choices[0].text
                print("pass3")
                # 接收到回覆訊息後，移除換行符號
            except Exception as ex:
                print("error:%s",ex)

        else:
            reply_msg = msg
        text_message = TextSendMessage(text=reply_msg)
        line_bot_api.reply_message(tk,text_message)
    except:
        print('error')
    return 'OK'

if __name__ == "__main__":
    app.run()
