import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", "7852430043"))
    ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    REQUIRED_CHANNEL_USERNAME = os.getenv("REQUIRED_CHANNEL_USERNAME", "@arts_of_drawings")
    REQUIRED_CHANNEL_URL = os.getenv("REQUIRED_CHANNEL_URL", "https://t.me/arts_of_drawings")
    DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()
    REQUIRE_PERSISTENT_STORAGE = os.getenv("REQUIRE_PERSISTENT_STORAGE", "false").lower() == "true"
    
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024
    ZIP_MAX_FILE_SIZE = int(os.getenv("ZIP_MAX_FILE_SIZE_MB", "50")) * 1024 * 1024
    ZIP_MAX_EXTRACTED_SIZE = int(os.getenv("ZIP_MAX_EXTRACTED_SIZE_MB", "200")) * 1024 * 1024
    ZIP_MAX_EXTRACTED_FILES = int(os.getenv("ZIP_MAX_EXTRACTED_FILES", "100"))
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
