from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from apscheduler.schedulers.background import BackgroundScheduler
import google.generativeai as genai
import json
from datetime import datetime

app = Flask(__name__)

# ✅ 初始化 Gemini
genai.configure(api_key="AIzaSyDmhLu5XPq6fpEIPO_f_vuw8St2njxJDuU")
model = genai.GenerativeModel('gemini-1.5-pro')

# ✅ 初始化 LINE Bot
line_bot_api = LineBotApi('btYRELB4P+YSCvuIuWxLzcsRBuU4d+uui1/9pWxCZRDS9U6BhGr6MgM9oVgzf8ott8gcjZsD2xuGI4AZVQ4f5vBiYun7G02g9JhLgP8TZY6Fqy9zI9lm/1ekNtNZW249ButepCSwrVO5biQj+zhb3gdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c2fd42d7c362fc5b9e865772402b3378')

# ✅ 使用者 ID（你要接收推播的那個 userId）
USER_ID = ''

# ✅ 每日單字功能（自動）
def generate_daily_vocab():
    prompt = (
        f"今天是 {today}，請隨機提供一個英文 B2 等級單字(每次都要不同)，請輸出包含以下：\n"
        "1. 單字及詞性:\n"
        "2. 英文解釋與中文意思:\n"
        "3. 一個英文例句與中譯:\n"
        "4. 一個與該單字有關的中翻英練習題:\n"
        "請用自然段落輸出，請勿使用星號、底線或其他標記符號。請務必根據日期變化給不同單字。並確保要照著格式使用中英混合回答我。"
    )
    response = model.generate_content(prompt)
    reply_msg = response.text
    line_bot_api.push_message(USER_ID, TextSendMessage(text=reply_msg))

# ✅ 設定定時任務
scheduler = BackgroundScheduler()
scheduler.add_job(generate_daily_vocab, 'cron', hour=8, minute=0)  # 每天早上 8:00AM
scheduler.start()

# ✅ 主 Webhook 處理
@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print(json_data)

    try:
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)

        tk = json_data['events'][0]['replyToken']
        event = json_data['events'][0]
        msg = event['message']['text'].strip()
        user_id = event['source']['userId']
        reply_msg = ''

        # 📌 顯示 userId 功能
        if msg == '我的ID':
            USER_ID = user_id
            reply_msg = f"你的 userId 是：{user_id}"

        # 📚 每日單字（即時版）
        elif msg == '每日單字':
            prompt = (
                f"今天是 {today}，請隨機提供一個英文 B2 等級單字(每次都要不同)，請輸出包含以下：\n"
                "1. 單字及詞性:\n"
                "2. 英文解釋與中文意思:\n"
                "3. 一個英文例句與中譯:\n"
                "4. 一個與該單字有關的中翻英練習題:\n"
                "請用自然段落輸出，請勿使用星號、底線或其他標記符號。請務必根據日期變化給不同單字。並確保要照著格式使用中英混合回答我。"
            )
            response = model.generate_content(prompt)
            reply_msg = response.text

        # 📝 翻譯建議
        elif msg.startswith("翻譯："):
            user_translation = msg[3:].strip()
            prompt = f"""
你是一位資深的 CEFR B2 英檢考官兼英文老師，專門幫助學生提升翻譯品質。以下是一位學生的中翻英作品：
「{user_translation}」

請針對以下幾個面向，分段提供具體建議，請勿使用星號或底線：

1. 語法與句型結構
2. 詞彙與用字選擇
3. 流暢度與邏輯性
4. 拼字、標點與大小寫
5. 整體評分與建議（1～5分）
6. 修改後範例
7. 延伸練習
"""
            response = model.generate_content(prompt)
            reply_msg = response.text

        # 💬 一般 AI 對話
        elif msg.lower().startswith('hi ai:'):
            prompt = msg[6:].strip()
            response = model.generate_content(prompt)
            reply_msg = response.text

        else:
            reply_msg = "請輸入『每日單字』或『翻譯：你的句子』，或用『hi ai:』跟我對話～\n如需知道你的 userId 請輸入『我的ID』"

        line_bot_api.reply_message(tk, TextSendMessage(text=reply_msg))

    except Exception as e:
        print('error:', e)

    return 'OK'

if __name__ == "__main__":
    app.run()
