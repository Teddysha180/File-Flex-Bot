import os
import shutil
import uuid
from pathlib import Path

from telegram import Document, PhotoSize, Video
from utils.config import config


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = config.DATA_DIR
DOWNLOAD_DIR = DATA_DIR / "downloads"


def ensure_download_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return DOWNLOAD_DIR


def create_user_job_dir(user_id: int) -> Path:
    ensure_download_dir()
    job_dir = DOWNLOAD_DIR / f"user_{user_id}_{uuid.uuid4().hex}"
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


def cleanup_paths(paths: list[Path]) -> None:
    for path in paths:
        if not path:
            continue
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink(missing_ok=True)


def safe_file_name(file_name: str) -> str:
    allowed = []
    for char in file_name.strip():
        if char.isalnum() or char in {"-", "_", ".", " "}:
            allowed.append(char)
    return "".join(allowed).strip().replace(" ", "_")


async def download_document_to_path(document: Document, destination: Path) -> None:
    telegram_file = await document.get_file()
    await telegram_file.download_to_drive(custom_path=str(destination))


async def download_photo_to_path(photo: PhotoSize, destination: Path) -> None:
    telegram_file = await photo.get_file()
    await telegram_file.download_to_drive(custom_path=str(destination))


async def download_video_to_path(video: Video, destination: Path) -> None:
    telegram_file = await video.get_file()
    await telegram_file.download_to_drive(custom_path=str(destination))
