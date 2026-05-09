from utils.config import config


def _mb_label(size_in_bytes: int) -> str:
    return f"{round(size_in_bytes / (1024 * 1024))} MB"


INTRO_ANIMATION_FRAMES = [
    "☁️ <b>Initializing FileFlex Cloud...</b>",
    "📡 <b>Connecting to processing nodes...</b>",
    "🛡 <b>Verifying encryption layers...</b>",
    "✅ <b>Cloud Workspace Ready.</b>",
]

WELCOME_MESSAGE = (
    "<b>FileFlex Cloud</b>\n\n"
    "Your professional workspace for seamless file processing and conversion. "
    "Choose a module from the dashboard below to start.\n\n"
    f"🔹 <b>Upload Limit:</b> {_mb_label(config.MAX_FILE_SIZE)}\n"
    f"🔹 <b>Storage Engine:</b> Distributed Cloud"
)

HELP_MESSAGE = (
    "<b>Quick Start Guide</b>\n\n"
    "1️⃣ <b>Select a Module</b> from the dashboard.\n"
    "2️⃣ <b>Upload</b> the source file.\n"
    "3️⃣ <b>Download</b> your processed output.\n\n"
    "<b>Capabilities</b>\n"
    "• Professional File Conversion\n"
    "• Image Optimization & Compression\n"
    "• Archive Management (ZIP)\n"
    "• Secure File Renaming\n"
    "• PDF Management (Merge/Split)\n\n"
    f"Note: Maximum file size is {_mb_label(config.MAX_FILE_SIZE)} per operation."
)
