from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, PostbackEvent
import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

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

    if incoming_message == "結構物計算":
        buttons_template = ButtonsTemplate(
            title="結構物計算",
            text="請選擇一個選項",
            actions=[
                PostbackAction(label="擋土牆", data="calculate_retain_wall"),
                PostbackAction(label="水溝加蓋", data="calculate_ditch_cover"),
                PostbackAction(label="截角改善", data="calculate_corner_improvement")
            ]
        )
        template_message = TemplateSendMessage(
            alt_text="結構物計算選項",
            template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    else:
        # 查詢資料庫中是否有對應的回應
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT response FROM keyword_responses WHERE keyword = %s", (incoming_message,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            reply_message = result[0]
        elif "," in incoming_message:
            try:
                dimensions = incoming_message.split(",")
                length = float(dimensions[0].strip())
                height = float(dimensions[1].strip())
                area = length * height
                reply_message = f"計算結果：長度 {length}m，高度 {height}m，面積 {area} 平方米。"
            except ValueError:
                reply_message = "輸入格式錯誤，請輸入正確的長度和高度，格式：長度,高度"
        else:
            reply_message = incoming_message

        response_message = TextSendMessage(text=reply_message)
        app.logger.info(f"Response message: {response_message}")
        line_bot_api.reply_message(
            event.reply_token,
            response_message
        )

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    app.logger.info(f"Postback data: {data}")
    if data == "calculate_retain_wall":
        reply_message = TextSendMessage(text="你選擇了擋土牆。請輸入長度和高度，格式：長度,高度")
    elif data == "calculate_ditch_cover":
        reply_message = TextSendMessage(text="你選擇了水溝加蓋。請輸入長度和寬度，格式：長度,寬度")
    elif data == "calculate_corner_improvement":
        reply_message = TextSendMessage(text="你選擇了截角改善。請輸入長度和寬度，格式：長度,寬度")
    else:
        reply_message = TextSendMessage(text="未知選項。")

    line_bot_api.reply_message(event.reply_token, reply_message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
