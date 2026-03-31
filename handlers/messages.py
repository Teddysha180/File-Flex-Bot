from utils.config import config


def _mb_label(size_in_bytes: int) -> str:
    return f"{round(size_in_bytes / (1024 * 1024))} MB"


INTRO_MESSAGE = (
    "File Flex\n"
    "Preparing your workspace..."
)

WELCOME_MESSAGE = (
    "File Flex\n\n"
    "A clean, fast file toolkit built for Telegram.\n\n"
    "Choose a tool below to get started.\n\n"
    "Core tools:\n"
    "• Convert Files\n"
    "• Compress Image\n"
    "• Extract ZIP\n"
    "• Rename File\n"
    "• Merge PDFs\n"
    "• Split PDF\n\n"
    "Upload limits:\n"
    f"• Standard files: up to {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"• ZIP files: up to {_mb_label(config.ZIP_MAX_FILE_SIZE)}\n"
    f"• ZIP extraction: up to {config.ZIP_MAX_EXTRACTED_FILES} files / {_mb_label(config.ZIP_MAX_EXTRACTED_SIZE)} total"
)

HELP_MESSAGE = (
    "How to use File Flex:\n\n"
    "1. Choose a tool from the keyboard.\n"
    "2. Send your file.\n"
    "3. If needed, send one extra detail such as a new file name or a page range.\n\n"
    "Conversion categories:\n"
    "• To PDF: JPG, Word, PowerPoint, Excel, HTML\n"
    "• From PDF: JPG, Word, PowerPoint, Excel, PDF/A\n"
    "• Image formats: JPG -> PNG, PNG -> JPG\n\n"
    "Best results:\n"
    "• Send documents as files to preserve their original format.\n"
    "• Use Back to Menu at any time to return to the main screen.\n\n"
    "Upload limits:\n"
    f"• Standard files: up to {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"• ZIP files: up to {_mb_label(config.ZIP_MAX_FILE_SIZE)}\n"
    f"• ZIP extraction: up to {config.ZIP_MAX_EXTRACTED_FILES} files / {_mb_label(config.ZIP_MAX_EXTRACTED_SIZE)} total"
)
