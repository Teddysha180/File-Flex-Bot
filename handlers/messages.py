from utils.config import config


def _mb_label(size_in_bytes: int) -> str:
    return f"{round(size_in_bytes / (1024 * 1024))} MB"


INTRO_ANIMATION_FRAMES = [
    "Initializing Black workspace...\n`[#---------] 10%`",
    "Connecting services...\n`[###-------] 30%`",
    "Preparing file tools...\n`[######----] 60%`",
    "Loading secure transfer modules...\n`[#########-] 90%`",
    "Workspace ready.\n`[##########] 100%`",
]

WELCOME_MESSAGE = (
    "<b>Black</b>\n"
    "<i>Cloud file workspace</i>\n\n"
    "Choose a tool below to get started. Upload a file, and Black will process it for you.\n\n"
    f"<b>File limit:</b> {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"<b>ZIP limit:</b> {_mb_label(config.ZIP_MAX_FILE_SIZE)}"
)

HELP_MESSAGE = (
    "<b>Help Center</b>\n\n"
    "<b>How it works</b>\n"
    "1. Select a tool from the menu.\n"
    "2. Upload your file.\n"
    "3. Follow the prompt if an extra step is needed.\n"
    "4. Receive the processed file.\n\n"
    "<b>Available tools</b>\n"
    "- File conversion\n"
    "- Image compression\n"
    "- ZIP extraction\n"
    "- File renaming\n"
    "- PDF merge\n"
    "- PDF split\n\n"
    f"<b>Standard limit:</b> {_mb_label(config.MAX_FILE_SIZE)} per task."
)
