from utils.config import config


def _mb_label(size_in_bytes: int) -> str:
    return f"{round(size_in_bytes / (1024 * 1024))} MB"


INTRO_ANIMATION_FRAMES = [
    "Starting system...",
    "Connecting to cloud nodes...",
    "Calibrating processing engines...",
    "Loading modules...",
    "System ready.",
]

WELCOME_MESSAGE = (
    "**FILEFLEX CLOUD**\n\n"
    "Welcome to your professional file management suite. Select a tool below to begin. "
    "Upload your file and we will handle the rest.\n\n"
    f"• **Global Limit**: {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"• **Archive Capacity**: {_mb_label(config.ZIP_MAX_FILE_SIZE)}"
)

HELP_MESSAGE = (
    "**QUICK START GUIDE**\n\n"
    "1. **Select Tool**: Choose a function from the menu.\n"
    "2. **Upload**: Send the file you wish to process.\n"
    "3. **Process**: Follow any additional prompts to complete the task.\n\n"
    "**CORE CAPABILITIES**\n"
    "• Professional File Conversion\n"
    "• Image Optimization & Compression\n"
    "• Archive Management (ZIP)\n"
    "• Secure File Renaming\n"
    "• PDF Management (Merge/Split)\n\n"
    f"Note: Maximum file size is {_mb_label(config.MAX_FILE_SIZE)} per operation."
)
