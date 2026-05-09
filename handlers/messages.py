from utils.config import config


def _mb_label(size_in_bytes: int) -> str:
    return f"{round(size_in_bytes / (1024 * 1024))} MB"


INTRO_ANIMATION_FRAMES = [
    "🚀 Initializing File Flex...\n`[#---------] 10%`",
    "🛰 Connecting to Cloud Nodes...\n`[###-------] 30%`",
    "🔧 Calibrating Image Engines...\n`[######----] 60%`",
    "📦 Loading Archive Core...\n`[#########-] 90%`",
    "✅ System Ready.\n`[##########] 100%`",
]

WELCOME_MESSAGE = (
    "⬛ *FILE FLEX BLACK*\n\n"
    "Select a tool suite below to begin. Upload your file and I will handle the rest instantly.\n\n"
    f"▫️ Global Limit: {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"▫️ ZIP Capacity: {_mb_label(config.ZIP_MAX_FILE_SIZE)}"
)

HELP_MESSAGE = (
    "⬛ *QUICK START GUIDE*\n\n"
    "1. Select a Tool: Choose from the menu.\n"
    "2. Upload File: Send the file to process.\n"
    "3. Refine: Provide extra input if requested.\n\n"
    "⬛ *PRIMARY WORKFLOWS*\n"
    "• 🔄 Professional File Conversion\n"
    "• 🗜 Smart Image Optimization\n"
    "• 📦 Archive Extraction & Creation\n"
    "• 📝 Secure File Renaming\n"
    "• 📄 Advanced PDF Merging/Splitting\n\n"
    f"▫️ Limit: Up to {_mb_label(config.MAX_FILE_SIZE)} per operation."
)
