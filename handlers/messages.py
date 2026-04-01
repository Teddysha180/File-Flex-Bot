from utils.config import config


def _mb_label(size_in_bytes: int) -> str:
    return f"{round(size_in_bytes / (1024 * 1024))} MB"


INTRO_ANIMATION_FRAMES = [
    "File Flex\n\n`[■□□□□]` Starting the workspace...",
    "File Flex\n\n`[■■□□□]` Loading smart file tools...",
    "File Flex\n\n`[■■■□□]` Organizing your control panel...",
    "File Flex\n\n`[■■■■□]` Polishing the experience...",
    "File Flex\n\n`[■■■■■]` Everything looks ready.",
]

WELCOME_MESSAGE = (
    "File Flex\n\n"
    "A cleaner file workspace for Telegram.\n\n"
    "Pick a tool from the menu and send your file. The bot will guide the next step clearly, so the whole flow feels simple and organized.\n\n"
    "What you can do here:\n"
    "• Convert files between popular formats\n"
    "• Compress images for faster sharing\n"
    "• Extract ZIP archives safely\n"
    "• Rename files neatly\n"
    "• Merge or split PDF documents\n\n"
    "Upload limits:\n"
    f"• Standard files: up to {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"• ZIP files: up to {_mb_label(config.ZIP_MAX_FILE_SIZE)}\n"
    f"• ZIP extraction: up to {config.ZIP_MAX_EXTRACTED_FILES} files / {_mb_label(config.ZIP_MAX_EXTRACTED_SIZE)} total"
)

HELP_MESSAGE = (
    "Help Center\n\n"
    "How File Flex works:\n"
    "1. Choose a tool from the menu.\n"
    "2. Send the file you want to work with.\n"
    "3. If needed, send one extra detail like a new file name or a page range.\n\n"
    "Conversion library:\n"
    "• To PDF: JPG, Word, PowerPoint, Excel, HTML\n"
    "• From PDF: JPG, Word, PowerPoint, Excel, PDF/A\n"
    "• Image formats: JPG to PNG, PNG to JPG\n\n"
    "For the smoothest results:\n"
    "• Send documents as files so their original format stays intact.\n"
    "• Use Main Menu anytime to reset the flow and start fresh.\n"
    "• If something feels off, resend the file after choosing the correct tool.\n\n"
    "Upload limits:\n"
    f"• Standard files: up to {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"• ZIP files: up to {_mb_label(config.ZIP_MAX_FILE_SIZE)}\n"
    f"• ZIP extraction: up to {config.ZIP_MAX_EXTRACTED_FILES} files / {_mb_label(config.ZIP_MAX_EXTRACTED_SIZE)} total"
)
