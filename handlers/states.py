from pathlib import Path

from utils.filesystem import cleanup_paths


ACTION_EXTRACT_ZIP = "extract_zip"
ACTION_COMPRESS_IMAGE = "compress_image"
ACTION_CONVERT_FILE = "convert_file"
ACTION_RENAME_FILE = "rename_file"
ACTION_MERGE_PDF = "merge_pdf"
ACTION_SPLIT_PDF = "split_pdf"

STATE_KEY_ADMIN_STEP = "admin_step"
STATE_KEY_BROADCAST_TYPE = "broadcast_type"
STATE_KEY_BROADCAST_FILE_ID = "broadcast_file_id"
STATE_KEY_BROADCAST_FILE_NAME = "broadcast_file_name"
STATE_KEY_BROADCAST_TEXT = "broadcast_text"
STATE_KEY_BROADCAST_BUTTON_TEXT = "broadcast_button_text"
STATE_KEY_BROADCAST_BUTTON_URL = "broadcast_button_url"
STATE_KEY_STORE_ID = "store_id"
STATE_KEY_STORE_FILES = "store_files"

STATE_KEY_ACTION = "selected_action"
STATE_KEY_CONVERSION_TARGET = "conversion_target"
STATE_KEY_PENDING_FILE = "pending_file"
STATE_KEY_PENDING_EXTENSION = "pending_extension"
STATE_KEY_PENDING_FILES = "pending_files"
STATE_KEY_JOB_DIR = "job_dir"
STATE_KEY_PENDING_INPUT = "pending_input"


def reset_user_state(user_data: dict) -> None:
    job_dir = user_data.pop(STATE_KEY_JOB_DIR, None)
    if job_dir:
        cleanup_paths([Path(job_dir)])

    user_data.pop(STATE_KEY_ACTION, None)
    user_data.pop(STATE_KEY_CONVERSION_TARGET, None)
    user_data.pop(STATE_KEY_PENDING_FILE, None)
    user_data.pop(STATE_KEY_PENDING_EXTENSION, None)
    user_data.pop(STATE_KEY_PENDING_FILES, None)
    user_data.pop(STATE_KEY_PENDING_INPUT, None)
    user_data.pop(STATE_KEY_ADMIN_STEP, None)
    user_data.pop(STATE_KEY_BROADCAST_TYPE, None)
    user_data.pop(STATE_KEY_BROADCAST_FILE_ID, None)
    user_data.pop(STATE_KEY_BROADCAST_FILE_NAME, None)
    user_data.pop(STATE_KEY_BROADCAST_TEXT, None)
    user_data.pop(STATE_KEY_BROADCAST_BUTTON_TEXT, None)
    user_data.pop(STATE_KEY_BROADCAST_BUTTON_URL, None)
    user_data.pop(STATE_KEY_STORE_ID, None)
    user_data.pop(STATE_KEY_STORE_FILES, None)
