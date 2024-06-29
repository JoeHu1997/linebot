import os
from dotenv import load_dotenv

load_dotenv()  # 讀取 .env 文件中的環境變量

class Config:
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
