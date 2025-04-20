from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import google.generativeai as genai
import json

app = Flask(__name__)

# 初始化 Gemini
genai.configure(api_key="AIzaSyDmhLu5XPq6fpEIPO_f_vuw8St2njxJDuU")
model = genai.GenerativeModel('gemini-1.5-pro')

# 初始化 LINE Bot API
line_bot_api = LineBotApi('btYRELB4P+YSCvuIuWxLzcsRBuU4d+uui1/9pWxCZRDS9U6BhGr6MgM9oVgzf8ott8gcjZsD2xuGI4AZVQ4f5vBiYun7G02g9JhLgP8TZY6Fqy9zI9lm/1ekNtNZW249ButepCSwrVO5biQj+zhb3gdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c2fd42d7c362fc5b9e865772402b3378')

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print(json_data)

    try:
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)

        tk = json_data['events'][0]['replyToken']
        msg = json_data['events'][0]['message']['text'].strip()
        reply_msg = ''

        # 功能一：每日單字
        if msg == '每日單字':
            prompt = (
                "請給我一個英文B2等級單字，包含：\n"
                "1. 單字及詞性\n"
                "2. 英文解釋與中文意思\n"
                "3. 一個英文例句與中譯\n"
                "4. 一個與該單字有關的中翻英練習題"
            )
            response = model.generate_content(prompt)
            reply_msg = response.text

        # 功能二：翻譯建議
        elif msg.startswith("翻譯："):
            user_translation = msg[3:]
            prompt = (
                f"請檢查以下翻譯句子，並提供改進建議及說明語法錯誤（如果有）：\n'{user_translation}'"
            )
            response = model.generate_content(prompt)
            reply_msg = response.text

        # 功能三：hi ai: 的原始功能
        elif msg.lower().startswith('hi ai:'):
            prompt = msg[6:].strip()
            response = model.generate_content(prompt)
            reply_msg = response.text

        else:
            reply_msg = "請輸入『每日單字』或『翻譯：你的句子』，或用 hi ai: 跟我對話～"

        text_message = TextSendMessage(text=reply_msg)
        line_bot_api.reply_message(tk, text_message)

    except Exception as e:
        print('error:', e)

    return 'OK'

if __name__ == "__main__":
    app.run()
