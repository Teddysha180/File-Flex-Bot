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
    "FILE FLEX BLACK\n\n"
    "A clean, professional file workspace built for Telegram.\n\n"
    "Choose a tool from the menu, send your file, and the bot will guide the rest with a simple, controlled workflow.\n\n"
    "Core tools:\n"
    "- File conversion\n"
    "- Image compression\n"
    "- ZIP extraction\n"
    "- File rename\n"
    "- PDF merge and split\n\n"
    "Upload limits:\n"
    f"- Standard files: up to {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"- ZIP files: up to {_mb_label(config.ZIP_MAX_FILE_SIZE)}\n"
    f"- ZIP extraction: up to {config.ZIP_MAX_EXTRACTED_FILES} files / {_mb_label(config.ZIP_MAX_EXTRACTED_SIZE)} total"
)

HELP_MESSAGE = (
    "FILE FLEX BLACK HELP\n\n"
    "How it works:\n"
    "1. Choose a tool from the menu.\n"
    "2. Send the file you want to process.\n"
    "3. If needed, send one extra detail such as a new file name or a page range.\n\n"
    "Conversion library:\n"
    "- To PDF: JPG, Word, PowerPoint, Excel, HTML\n"
    "- From PDF: JPG, Word, PowerPoint, Excel, PDF/A\n"
    "- Image formats: JPG to PNG, PNG to JPG\n\n"
    "Best results:\n"
    "- Send documents as files to preserve format and quality\n"
    "- Use Home anytime to reset the workflow\n"
    "- If a step feels wrong, return to the menu and start that task again\n\n"
    "Upload limits:\n"
    f"- Standard files: up to {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"- ZIP files: up to {_mb_label(config.ZIP_MAX_FILE_SIZE)}\n"
    f"- ZIP extraction: up to {config.ZIP_MAX_EXTRACTED_FILES} files / {_mb_label(config.ZIP_MAX_EXTRACTED_SIZE)} total"
)
