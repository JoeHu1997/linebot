from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 環境變量讀取
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# 檢查環境變量是否正確加載
app.logger.info(f"LINE_CHANNEL_ACCESS_TOKEN: {LINE_CHANNEL_ACCESS_TOKEN}")
app.logger.info(f"LINE_CHANNEL_SECRET: {LINE_CHANNEL_SECRET}")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 LINE 發送的請求標頭的 'X-Line-Signature' 值
    signature = request.headers['X-Line-Signature']
    app.logger.info(f"X-Line-Signature: {signature}")

    # 獲取請求正文
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # 驗證簽名
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    response_message = TextSendMessage(text=event.message.text)
    app.logger.info(f"Response message: {response_message}")
    # 回應用戶發送的消息
    line_bot_api.reply_message(
        event.reply_token,
        response_message
    )

if __name__ == "__main__":
    app.run()
