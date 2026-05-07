from utils.config import config


def _mb_label(size_in_bytes: int) -> str:
    return f"{round(size_in_bytes / (1024 * 1024))} MB"


INTRO_ANIMATION_FRAMES = [
    "FILE FLEX BLACK\n\n`[#....]` Booting workspace...",
    "FILE FLEX BLACK\n\n`[##...]` Loading core tools...",
    "FILE FLEX BLACK\n\n`[###..]` Preparing your control panel...",
    "FILE FLEX BLACK\n\n`[####.]` Finalizing the session...",
    "FILE FLEX BLACK\n\n`[#####]` Ready.",
]

WELCOME_MESSAGE = (
    "⬛ FILE FLEX BLACK 📁\n\n"
    "Clean file tools for Telegram.\n\n"
    "Choose a tool, send your file, and I will handle the rest.\n\n"
    f"Files: up to {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"ZIP: up to {_mb_label(config.ZIP_MAX_FILE_SIZE)}"
)

HELP_MESSAGE = (
    "⬛ HELP 📁\n\n"
    "How it works:\n"
    "1. Choose a tool from the menu.\n"
    "2. Send the file you want to process.\n"
    "3. If needed, send one extra detail like a new name or page range.\n\n"
    "Main tools:\n"
    "- Convert files\n"
    "- Compress images\n"
    "- Extract ZIP archives\n"
    "- Rename files\n"
    "- Merge or split PDF files\n\n"
    f"Limit: up to {_mb_label(config.MAX_FILE_SIZE)} per file"
)
