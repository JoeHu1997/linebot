from flask import Blueprint, request, abort, current_app
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line_bot_bp = Blueprint('line_bot_bp', __name__)

def get_line_bot_api():
    return LineBotApi(current_app.config['LINE_CHANNEL_ACCESS_TOKEN'])

def get_handler():
    handler = WebhookHandler(current_app.config['LINE_CHANNEL_SECRET'])
    
    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):
        incoming_message = event.message.text
        current_app.logger.info(f"Received message: {incoming_message}")

        if "結構物估價" in incoming_message:
            response_message = TextSendMessage(
                text="請輸入想要估價的結構物種類:\n1. 擋土牆\n2. 水溝加蓋\n3. 截角改善"
            )
        else:
            response_message = TextSendMessage(text=incoming_message)
        
        current_app.logger.info(f"Response message: {response_message}")
        line_bot_api = get_line_bot_api()
        line_bot_api.reply_message(
            event.reply_token,
            response_message
        )

    return handler

@line_bot_bp.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    current_app.logger.info(f"Request body: {body}")

    try:
        handler = get_handler()
        handler.handle(body, signature)
    except InvalidSignatureError:
        current_app.logger.error("Invalid signature. Check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        current_app.logger.error(f"Exception: {e}")
        abort(500)

    return 'OK'
