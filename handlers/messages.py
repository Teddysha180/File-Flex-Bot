from utils.config import config


def _mb_label(size_in_bytes: int) -> str:
    return f"{round(size_in_bytes / (1024 * 1024))} MB"


INTRO_ANIMATION_FRAMES = [
    "🚀 *Initializing File Flex*...\n`[#---------] 10%`",
    "🛰 *Connecting to Cloud Nodes*...\n`[###-------] 30%`",
    "🔧 *Calibrating Image Engines*...\n`[######----] 60%`",
    "📦 *Loading Archive Core*...\n`[#########-] 90%`",
    "✅ *System Ready.*\n`[##########] 100%`",
]

WELCOME_MESSAGE = (
    "✨ *File Flex Pro* — High-performance file utilities.\n\n"
    "Select a suite below to begin. Upload your file, and I'll handle the processing instantly.\n\n"
    f"▫️ *Global Limit:* {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"▫️ *ZIP Capacity:* {_mb_label(config.ZIP_MAX_FILE_SIZE)}"
)

HELP_MESSAGE = (
    "📖 *Quick Start Guide*\n\n"
    "1️⃣ *Select a Tool*: Choose your desired operation from the menu.\n"
    "2️⃣ *Upload File*: Send the file you wish to process.\n"
    "3️⃣ *Refine*: Provide any extra input requested (like names or page ranges).\n\n"
    "*Primary Workflows:*\n"
    "• 🔄 Professional File Conversion\n"
    "• 🗜 Smart Image Optimization\n"
    "• 📦 Archive Extraction & Creation\n"
    "• 📝 Secure File Renaming\n"
    "• 📄 Advanced PDF Merging/Splitting\n\n"
    f"▫️ *Limit:* Up to {_mb_label(config.MAX_FILE_SIZE)} per operation."
)
