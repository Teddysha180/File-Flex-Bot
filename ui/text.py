"""Central place for editable bot copy.

Edit this file when you want to change wording, prompts, or system messages.
"""

from utils.config import config
from ui.labels import BRAND_NAME, BRAND_TAGLINE


def size_label(size_in_bytes: int) -> str:
    return f"{round(size_in_bytes / (1024 * 1024))} MB"


INTRO_ANIMATION_FRAMES = [
    "Initializing FileFlex Bot workspace...\n`[#---------] 10%`",
    "Connecting services...\n`[###-------] 30%`",
    "Preparing file tools...\n`[######----] 60%`",
    "Loading secure transfer modules...\n`[#########-] 90%`",
    "Workspace ready.\n`[##########] 100%`",
]

WELCOME_MESSAGE = (
    f"<b>{BRAND_NAME}</b>\n"
    f"<i>{BRAND_TAGLINE}</i>\n\n"
    f"Choose a tool below to get started. Upload a file, and {BRAND_NAME} will process it for you.\n\n"
    f"<b>File limit:</b> {size_label(config.MAX_FILE_SIZE)}\n"
    f"<b>ZIP limit:</b> {size_label(config.ZIP_MAX_FILE_SIZE)}"
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
    f"<b>Standard limit:</b> {size_label(config.MAX_FILE_SIZE)} per task."
)

ACCESS_REQUIRED_MESSAGE = (
    "<b>Access Required</b>\n\n"
    "Join the updates channel to use FileFlex Bot.\n\n"
    "After joining, tap <b>Verify Access</b> to continue."
)

ACCESS_CONFIRMED_MESSAGE = (
    "<b>Access confirmed</b>\n\nYour FileFlex Bot workspace is ready."
)

MAIN_MENU_MESSAGE = "<b>Main Menu</b>\n\nChoose a tool to continue."
DEFAULT_FALLBACK_MESSAGE = "Choose a tool from the menu to begin."
UNKNOWN_REQUEST_MESSAGE = "Please choose one of the available tools from the menu."
DOCUMENT_TOOL_REQUIRED_MESSAGE = "Choose a tool from the menu before uploading a file."
PHOTO_TOOL_REQUIRED_MESSAGE = "Choose a tool from the main menu before uploading an image."
PHOTO_PROCESSING_FAILED_MESSAGE = "<b>Processing failed</b>\n\nThis image could not be processed."
UNEXPECTED_ERROR_MESSAGE = "<b>Something went wrong</b>\n\nPlease return to the main menu and try again."
VIDEO_DISABLED_MESSAGE = (
    "<b>Video uploads unavailable</b>\n\nDirect video uploads are only available in admin broadcast mode."
)


def link_unavailable_message() -> str:
    return "<b>Link unavailable</b>\n\nThis share link is invalid or has expired."


def share_files_unavailable_message() -> str:
    return "<b>Files unavailable</b>\n\nThese files could not be retrieved. They may have been removed."


def preparing_share_message(file_count: int) -> str:
    return f"Preparing {file_count} file(s)..."


TEMPORARY_DELIVERY_MESSAGE = (
    "<b>Temporary delivery</b>\n\n"
    "These files will be removed from this chat in 5 minutes.\n\n"
    "Forward them to Saved Messages if you want to keep a copy."
)


def request_unavailable_message(detail: str) -> str:
    return f"<b>Request unavailable</b>\n\n{detail}"


TOOL_INTRO_MESSAGES = {
    "extract_zip": lambda: (
        "<b>Extract ZIP</b>\n\n"
        "Upload a ZIP file to extract its contents.\n\n"
        f"<b>Limit:</b> {size_label(config.ZIP_MAX_FILE_SIZE)}"
    ),
    "compress_image": lambda: (
        "<b>Compress Image</b>\n\n"
        "Upload an image to reduce file size while keeping good visual quality.\n\n"
        f"<b>Limit:</b> {size_label(config.MAX_FILE_SIZE)}"
    ),
    "rename_file": lambda: (
        "<b>Rename File</b>\n\n"
        "Upload a file first, then send the new name you want to use.\n\n"
        f"<b>Limit:</b> {size_label(config.MAX_FILE_SIZE)}"
    ),
    "merge_pdf": lambda: (
        "<b>Merge PDF</b>\n\n"
        "Upload PDF files in the order you want them merged, then tap <b>Finish Merge</b>.\n\n"
        f"<b>Limit:</b> {size_label(config.MAX_FILE_SIZE)}"
    ),
    "split_pdf": lambda: (
        "<b>Split PDF</b>\n\n"
        "Upload a PDF, then send the page range you want to extract.\n\n"
        f"<b>Limit:</b> {size_label(config.MAX_FILE_SIZE)}"
    ),
}


def tool_intro_message(tool_key: str) -> str:
    return TOOL_INTRO_MESSAGES[tool_key]()


CONVERSION_PROMPTS = {
    "jpg_to_pdf": "<b>JPG to PDF</b>\n\nUpload a JPG image.",
    "word_to_pdf": "<b>Word to PDF</b>\n\nUpload a DOC or DOCX file.",
    "powerpoint_to_pdf": "<b>PowerPoint to PDF</b>\n\nUpload a PPT or PPTX file.",
    "excel_to_pdf": "<b>Excel to PDF</b>\n\nUpload an XLS or XLSX file.",
    "html_to_pdf": "<b>HTML to PDF</b>\n\nUpload an HTML file.",
    "pdf_to_jpg": "<b>PDF to JPG</b>\n\nUpload a PDF file.",
    "pdf_to_word": "<b>PDF to Word</b>\n\nUpload a PDF file.",
    "pdf_to_powerpoint": "<b>PDF to PowerPoint</b>\n\nUpload a PDF file.",
    "pdf_to_excel": "<b>PDF to Excel</b>\n\nUpload a PDF file.",
    "pdf_to_pdfa": "<b>PDF to PDF/A</b>\n\nUpload a PDF file.",
    "jpg_to_png": "<b>JPG to PNG</b>\n\nUpload a JPG image.",
    "png_to_jpg": "<b>PNG to JPG</b>\n\nUpload a PNG image.",
}


def conversion_prompt(conversion_target: str) -> str:
    base_prompt = CONVERSION_PROMPTS.get(conversion_target, "Upload the file you want to convert.")
    return f"{base_prompt}\n\n<b>Limit:</b> {size_label(config.MAX_FILE_SIZE)}"


CONVERSION_LIST_MESSAGE = (
    "<b>Convert Files</b>\n\n"
    "Choose a conversion type below.\n\n"
    "<b>To PDF</b>: JPG, Word, PowerPoint, Excel, HTML\n"
    "<b>From PDF</b>: JPG, Word, PowerPoint, Excel, PDF/A\n"
    "<b>Image formats</b>: JPG, PNG"
)

INLINE_CONVERSION_SELECTOR_MESSAGE = (
    "<b>Convert Files</b>\n\n"
    "Choose a conversion group below."
)

INLINE_TO_PDF_MESSAGE = (
    "<b>Convert to PDF</b>\n\n"
    "Choose the source file type."
)

INLINE_FROM_PDF_MESSAGE = (
    "<b>Convert from PDF</b>\n\n"
    "Choose the output format."
)

INLINE_IMAGE_FORMATS_MESSAGE = (
    "<b>Image Format Conversion</b>\n\n"
    "Choose the format you want to convert."
)


def conversion_list_message(*, libreoffice_available: bool, ghostscript_available: bool) -> str:
    lines = [CONVERSION_LIST_MESSAGE]
    if not libreoffice_available:
        lines.append("\n<b>Notice:</b> Office to PDF conversions are currently unavailable.")
    if not ghostscript_available:
        lines.append("\n<b>Notice:</b> PDF/A conversion is currently unavailable.")
    lines.append("\nSelect a conversion or return to the main menu.")
    return "".join(lines)


def conversion_unavailable_message(conversion_target: str) -> str:
    if conversion_target in {"word_to_pdf", "powerpoint_to_pdf", "excel_to_pdf", "html_to_pdf"}:
        return (
            "<b>Conversion unavailable</b>\n\n"
            "Office conversions require LibreOffice, which is not available on this server."
        )
    if conversion_target == "pdf_to_pdfa":
        return (
            "<b>Conversion unavailable</b>\n\n"
            "PDF/A conversion requires Ghostscript, which is not installed on this server."
        )
    return "<b>Conversion unavailable</b>\n\nThis conversion is not available right now."


RENAME_FILE_RECEIVED_MESSAGE = (
    "<b>File uploaded</b>\n\nSend the new file name. Include the extension if you want to change it."
)
SPLIT_FILE_RECEIVED_MESSAGE = (
    "<b>PDF uploaded</b>\n\nSend the page range to extract, for example <code>1-5</code>."
)


def merge_queue_message(file_count: int) -> str:
    return (
        f"<b>Added to merge queue</b>\n\n{file_count} PDF file(s) ready.\n"
        "Send another PDF or tap <b>Finish Merge</b>."
    )


def result_caption(label: str) -> str:
    return f"<b>Completed</b>\n\nYour {label} is ready."


WAIT_TITLES = {
    "extract_zip": "Extracting ZIP",
    "compress_image": "Compressing image",
    "convert_file": "Converting file",
    "rename_file": "Renaming file",
    "split_pdf": "Splitting PDF",
    "merge_pdf": "Merging PDFs",
    "default": "Processing",
}

WAIT_ANIMATION_FRAMES = [
    "Processing.",
    "Processing..",
    "Processing...",
    "Finalizing...",
]

EXTRACTION_COMPLETE_MESSAGE = "<b>Extraction complete</b>\n\nYour files are ready."
EMPTY_MERGE_QUEUE_MESSAGE = "<b>Merge queue is empty</b>\n\nUpload at least one PDF file first."


ADMIN_ACCESS_DENIED_MESSAGE = "Access denied. You do not have administrative privileges."
ADMIN_CANCELLED_MESSAGE = "Canceled. You are back in the admin workspace."
ADMIN_INVALID_USER_ID_MESSAGE = "<b>Error</b>: Please provide a valid numeric User ID."
ADMIN_NO_BROADCAST_USERS_MESSAGE = "No users are available to receive this broadcast."
ADMIN_SHARING_EMPTY_MESSAGE = "No files have been added yet. Send at least one file first."
ADMIN_STORAGE_NOT_CONFIGURED_MESSAGE = "Storage channel is not configured yet. Set `STORAGE_CHANNEL_ID` first."
ADMIN_STORE_UPLOAD_FAILED_MESSAGE = "Could not save files to the storage channel."

BROADCAST_CONTENT_MESSAGE = (
    "<b>Broadcast</b>\n\n"
    "Step 1 of 3\n"
    "Send the message or media for this broadcast.\n\n"
    "<b>Supported formats</b>\n"
    "- Text\n"
    "- Photo\n"
    "- Video\n"
    "- Document\n\n"
    "If you send media, you can include the caption immediately."
)

STORE_CREATOR_MESSAGE = (
    "<b>Create Share Link</b>\n\n"
    "Upload the files you want to bundle. When finished, tap <b>Generate Link</b>."
)

ADMIN_ADD_PROMPT_MESSAGE = "<b>Add Admin</b>\n\nSend the Telegram user ID for the new admin."
ADMIN_REMOVE_PROMPT_MESSAGE = "<b>Remove Admin</b>\n\nSend the Telegram user ID you want to remove."
ADMIN_FINISH_STORE_HINT_MESSAGE = "Start `Create Share Link` first, then upload files before generating the link."

BROADCAST_BUTTON_STEP_MESSAGE = (
    "<b>Step 2 of 3</b>\n\n"
    "Send the button in this format:\n"
    "<code>Label | https://example.com</code>\n\n"
    "Send <code>skip</code> if no button is needed."
)

BROADCAST_CAPTION_STEP_MESSAGE = (
    "<b>Step 2 of 3</b>\n\nSend a caption for this media, or send <code>skip</code>."
)

BROADCAST_PREVIEW_READY_MESSAGE = (
    "<b>Step 3 of 3</b>\n\nReview the preview above. Tap <b>Publish</b> to send it to users or <b>Cancel</b> to discard it."
)

BROADCAST_BUTTON_FORMAT_ERROR_MESSAGE = (
    "<b>Error</b>: Use this format:\n<code>Button Text | https://example.com</code>\n\nOr send <code>skip</code>."
)
BROADCAST_BUTTON_INVALID_MESSAGE = "<b>Error</b>: Invalid format. Use <code>Button Text | https://example.com</code>."


def admin_added_message(admin_id: int) -> str:
    return f"<b>Completed</b>\n\nAdmin {admin_id} has been added."


def admin_removed_message(admin_id: int, removed: bool) -> str:
    if removed:
        return f"<b>Completed</b>\n\nAdmin {admin_id} has been removed."
    return "<b>Error</b>\n\nAdmin not found or cannot be removed."


def store_item_added_message(item_label: str, count: int) -> str:
    return f"<b>{item_label} added</b>\n\n{count} file(s) in this share bundle.\nSend more files or tap <b>Generate Link</b>."


def dashboard_message(*, total_users: int, new_users_today: int, total_jobs: int, jobs_today: int, total_admins: int, backend: str, persistent: str, uptime: str, storage_channel_id: int) -> str:
    return (
        f"<b>{BRAND_NAME}</b>\n"
        "<i>Admin workspace</i>\n\n"
        f"<b>Users</b>: {total_users} (+{new_users_today} today)\n"
        f"<b>Jobs</b>: {total_jobs} ({jobs_today} today)\n"
        f"<b>Admins</b>: {total_admins}\n\n"
        "<b>Infrastructure</b>\n"
        f"- Backend: {backend}\n"
        f"- Persistent: {persistent}\n"
        f"- Uptime: {uptime}\n"
        f"- Storage Channel: {storage_channel_id}\n"
        "- Status: Healthy\n\n"
        "Use the controls below to manage the bot, publish broadcasts, and generate share links."
    )


def bot_status_message(*, total_users: int, total_admins: int, total_jobs: int, backend: str, persistent: str, location: str, uptime: str) -> str:
    return (
        "<b>System Status</b>\n\n"
        f"<b>Tracked Users</b>: {total_users}\n"
        f"<b>Admins</b>: {total_admins}\n"
        f"<b>Jobs</b>: {total_jobs}\n\n"
        "<b>Storage</b>\n"
        f"- Engine: {backend}\n"
        f"- Persistent: {persistent}\n"
        f"- Path: {location}\n\n"
        "<b>Runtime</b>\n"
        f"- Uptime: {uptime}\n"
        "- API Status: Operational"
    )


def admins_message(admins: list[dict]) -> str:
    if not admins:
        return "No administrative accounts found."

    lines = ["<b>Admins</b>", ""]
    for admin in admins:
        label = admin["first_name"] or admin["username"] or str(admin["user_id"])
        role = "Main Admin" if admin["is_main_admin"] else "Admin"
        lines.append(f"- {label} | {role} | {admin['user_id']}")
    return "\n".join(lines)


def broadcast_started_message(user_count: int) -> str:
    return f"Broadcast started for {user_count} users..."


def broadcast_complete_message(sent_count: int, failed_count: int) -> str:
    return (
        "<b>Broadcast complete</b>\n\n"
        f"- Delivered: {sent_count}\n"
        f"- Failed: {failed_count}"
    )


def store_upload_progress_start(file_count: int) -> str:
    return f"<b>Starting upload for {file_count} file(s)...</b>"


def store_upload_progress_update(current: int, total: int) -> str:
    return (
        f"<b>Uploading {current}/{total} files...</b>\n"
        "Please wait and do not send new commands."
    )


def share_link_generated_message(total_files: int, share_link: str) -> str:
    return (
        "<b>Share link generated</b>\n\n"
        f"<b>Files</b>: {total_files}\n"
        f"<b>Link</b>: <a href='{share_link}'>Open in Bot</a>\n\n"
        f"<code>{share_link}</code>\n\n"
        "Anyone with this link can open the bundle in the bot."
    )


SHARING_GUIDE_MESSAGE = (
    "<b>Sharing Guide</b>\n\n"
    "Files are stored in your Telegram storage channel so shared links remain stable across deployments.\n\n"
    "Save your generated links because the bot does not keep a searchable list of previous share URLs."
)


def performance_profile_message(stats: dict | None) -> str:
    if not stats:
        return "No activity recorded yet. Send your first file to start tracking usage."
    return (
        "<b>Usage</b>\n\n"
        f"<b>Processed</b>: {stats['total_files']} files\n"
        f"<b>Saved</b>: {stats['storage_saved'] / (1024 * 1024):.1f} MB\n"
        f"<b>This week</b>: {stats['files_this_week']} files\n"
        f"<b>Member since</b>: {stats['member_since']}"
    )


SETTINGS_MESSAGE = (
    "<b>Workspace Info</b>\n\n"
    "View usage, recent activity, and support information."
)


def history_message(history: list[tuple]) -> str:
    if not history:
        return "No recent activity found."

    lines = ["<b>Recent Activity</b>", ""]
    for index, record in enumerate(history, 1):
        action, input_file, _output_file, _in_size, _out_size, proc_time, _timestamp = record
        lines.append(f"{index}. {action.upper()}")
        lines.append(f"   {input_file[:25]}")
        lines.append(f"   {proc_time:.1f}s")
        lines.append("")
    return "\n".join(lines).rstrip()
