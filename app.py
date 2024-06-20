from flask import Flask
from config import Config
from views.line_bot import line_bot_bp

app = Flask(__name__)
app.config.from_object(Config)

# 註冊藍圖
app.register_blueprint(line_bot_bp, url_prefix='/line_bot')

if __name__ == "__main__":
    app.run()
