import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

SHEET_NAME = "DailyVocab"
sheet = client.open(SHEET_NAME).sheet1

# 新增 user id
def add_user(user_id):
    user_ids = sheet.col_values(1)
    if user_id not in user_ids:
        sheet.append_row([user_id, ""])  # 第二欄可存單字紀錄或其他資訊

# 取得所有 user id
def get_all_users():
    return sheet.col_values(1)

# 取得該使用者的單字清單（例如第二欄）
def get_user_vocab(user_id):
    records = sheet.get_all_records()
    for row in records:
        if row['user_id'] == user_id:
            return row['vocab'].split(',') if row['vocab'] else []
    return []

# 加入新單字
def add_user_vocab(user_id, new_vocab):
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):  # 從第2行起
        if row['user_id'] == user_id:
            vocab_list = row['vocab'].split(',') if row['vocab'] else []
            vocab_list.append(new_vocab)
            sheet.update_cell(idx, 2, ','.join(vocab_list))
            return
