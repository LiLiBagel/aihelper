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
            user_translation = msg[3:].strip()
            prompt = f"""
        你是一位資深的 CEFR B2 英檢考官兼英文老師，專門幫助學生提升翻譯品質。以下是一位學生的中翻英作品：
        「{user_translation}」
        
        請你針對以下幾個面向，提供清楚、分段的建議，避免使用任何特殊符號（例如星號、底線）來標示段落。
        
        1. 語法與句型結構：指出句中的語法錯誤，並簡要說明為什麼不正確。
        2. 詞彙與用字選擇：檢查是否有更合適、符合 B2 水準的單字或片語可以使用。
        3. 句子流暢度與邏輯性：說明句子是否自然、連貫，有沒有邏輯不清或語意重複的地方。
        4. 拼字、標點與大小寫：修正任何拼字錯誤、標點或大小寫問題。
        5. 整體表現與建議：根據 CEFR B2 等級的標準，給這句話 1 到 5 分，並簡要說明評分依據。
        6. 修改後範例：提供修改後的完整句子，讓學生可以學習正確表達。
        7. 延伸練習：根據這句話的錯誤類型，設計 1 到 2 個延伸練習題目，例如改寫句子、同義轉換、或句子組合練習。
        
        請以清楚的段落方式輸出，不要使用星號、底線、Markdown 或 HTML 標籤。
        """
            response = model.generate_content(prompt)
            reply_msg = response.text

        else:
            reply_msg = "請輸入『每日單字』或『翻譯：你的句子』跟我對話～"

        text_message = TextSendMessage(text=reply_msg)
        line_bot_api.reply_message(tk, text_message)

    except Exception as e:
        print('error:', e)

    return 'OK'

if __name__ == "__main__":
    app.run()
