import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    
    MAX_FILE_SIZE = 100 * 1024 * 1024
    COMPRESSION_QUALITY = 65
    IMAGE_QUALITY = 90
    
    DAILY_LIMIT = 100
    ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    
    LOG_PROCESSING = os.getenv("LOG_PROCESSING", "true").lower() == "true"
    
    SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic"}
    SUPPORTED_DOCUMENT_FORMATS = {".pdf", ".docx", ".doc", ".txt"}
    SUPPORTED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"}
    
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", None)
    
    @staticmethod
    def validate():
        if not Config.BOT_TOKEN:
            raise RuntimeError("BOT_TOKEN environment variable is not set.")

config = Config()
