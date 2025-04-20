from openai import OpenAI
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import json

app = Flask(__name__)

# 初始化 OpenAI Client（新版 SDK 用法）
client = OpenAI(api_key='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')
# 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
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
            response = client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            reply_msg = response.choices[0].message.content

        # 功能二：翻譯建議
        elif msg.startswith("翻譯："):
            user_translation = msg[3:]
            prompt = (
                f"請檢查以下翻譯句子，並提供改進建議及說明語法錯誤（如果有）：\n'{user_translation}'"
            )
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            reply_msg = response.choices[0].message.content

        # 功能三：hi ai: 的原始功能
        elif msg.lower().startswith('hi ai:'):
            prompt = msg[6:].strip()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            reply_msg = response.choices[0].message.content

        else:
            reply_msg = "請輸入『每日單字』或『翻譯：你的句子』，或用 hi ai: 跟我對話～"

        text_message = TextSendMessage(text=reply_msg)
        line_bot_api.reply_message(tk, text_message)

    except Exception as e:
        print('error:', e)

    return 'OK'

if __name__ == "__main__":
    app.run()
