from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # 載入 .env 文件中的環境變數

app = Flask(__name__)

# 從環境變量中獲取 LINE 的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
DATABASE_URL = os.getenv('DATABASE_URL')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 連接到 PostgreSQL 資料庫
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route("/")
def index():
    return "Hello, this is the LINE bot service."

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    incoming_message = event.message.text
    app.logger.info(f"Received message: {incoming_message}")

    # 查詢資料庫中是否有對應的回應
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT response FROM keyword_responses WHERE keyword = %s", (incoming_message,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:
        response_message = TextSendMessage(text=result[0])
    else:
        response_message = TextSendMessage(text=incoming_message)
    
    app.logger.info(f"Response message: {response_message}")
    line_bot_api.reply_message(
        event.reply_token,
        response_message
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
