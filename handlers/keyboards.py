from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


# --- Home Menu ---
BTN_CONVERT_FILES = "🔄 Conversion"
BTN_COMPRESS_IMAGE = "🖼 Image Tools"
BTN_EXTRACT_ZIP = "📦 Archives"
BTN_RENAME_FILE = "📝 Rename"
BTN_MERGE_PDF = "📄 Merge PDF"
BTN_SPLIT_PDF = "✂️ Split PDF"
BTN_HELP = "ℹ️ Info & Support"
BTN_HOME = "🏠 Main Menu"

# --- Functional & Admin ---
BTN_DONE = "✅ Finalize"
BTN_ADMIN_DASHBOARD = "📊 Analytics"
BTN_ADMIN_STATUS = "⚙️ Node Status"
BTN_ADMIN_ADMINS = "👥 Team"
BTN_ADMIN_BROADCAST = "📢 Broadcast"
BTN_ADMIN_CREATE_STORE = "🔗 New Share"
BTN_ADMIN_FINISH_STORE = "✨ Generate Link"
BTN_ADMIN_STORES = "📖 Guide"
BTN_ADMIN_POST = "🚀 Deploy"
BTN_ADMIN_ADD_ADMIN = "➕ Add Member"
BTN_ADMIN_REMOVE_ADMIN = "❌ Remove"
BTN_ADMIN_CANCEL = "🔙 Cancel"

BTN_JPG_TO_PDF = "🖼 → 📄 PDF"
BTN_WORD_TO_PDF = "📝 → 📄 PDF"
BTN_POWERPOINT_TO_PDF = "📊 → 📄 PDF"
BTN_EXCEL_TO_PDF = "📈 → 📄 PDF"
BTN_HTML_TO_PDF = "🌐 → 📄 PDF"
BTN_PDF_TO_JPG = "📄 → 🖼 JPG"
BTN_PDF_TO_WORD = "📄 → 📝 Word"
BTN_PDF_TO_POWERPOINT = "📄 → 📊 PPT"
BTN_PDF_TO_EXCEL = "📄 → 📈 Excel"
BTN_PDF_TO_PDFA = "🛡 PDF/A"
BTN_JPG_TO_PNG = "JPG ↔ PNG"
BTN_PNG_TO_JPG = "PNG ↔ JPG"


def home_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_CONVERT_FILES), KeyboardButton(BTN_COMPRESS_IMAGE)],
            [KeyboardButton(BTN_EXTRACT_ZIP), KeyboardButton(BTN_RENAME_FILE)],
            [KeyboardButton(BTN_MERGE_PDF), KeyboardButton(BTN_SPLIT_PDF)],
            [KeyboardButton(BTN_HELP)],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Select a module...",
    )


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📊 My Stats", callback_data="menu:stats"), InlineKeyboardButton("🕒 History", callback_data="menu:history")],
            [InlineKeyboardButton("💬 Live Support", url="https://t.me/your_support_handle")],
            [InlineKeyboardButton("🏠 Return home", callback_data="menu:home")]
        ]
    )


def convert_keyboard() -> ReplyKeyboardMarkup:
    return convert_keyboard_for_buttons(
        [
            BTN_JPG_TO_PDF,
            BTN_WORD_TO_PDF,
            BTN_POWERPOINT_TO_PDF,
            BTN_EXCEL_TO_PDF,
            BTN_HTML_TO_PDF,
            BTN_PDF_TO_JPG,
            BTN_PDF_TO_WORD,
            BTN_PDF_TO_POWERPOINT,
            BTN_PDF_TO_EXCEL,
            BTN_PDF_TO_PDFA,
            BTN_JPG_TO_PNG,
            BTN_PNG_TO_JPG,
        ]
    )


def convert_keyboard_for_buttons(buttons: list[str]) -> ReplyKeyboardMarkup:
    rows: list[list[KeyboardButton]] = []
    row: list[KeyboardButton] = []

    for button in buttons:
        row.append(KeyboardButton(button))
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    rows.append([KeyboardButton(BTN_HOME)])

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Choose a conversion mode",
    )


def merge_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_DONE), KeyboardButton(BTN_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Send files, then finish merge",
    )


def admin_keyboard(is_main_admin: bool) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(BTN_ADMIN_DASHBOARD), KeyboardButton(BTN_ADMIN_STATUS)],
        [KeyboardButton(BTN_ADMIN_ADMINS), KeyboardButton(BTN_ADMIN_BROADCAST)],
        [KeyboardButton(BTN_ADMIN_CREATE_STORE), KeyboardButton(BTN_ADMIN_FINISH_STORE)],
        [KeyboardButton(BTN_ADMIN_STORES)],
    ]

    if is_main_admin:
        rows.append([KeyboardButton(BTN_ADMIN_ADD_ADMIN), KeyboardButton(BTN_ADMIN_REMOVE_ADMIN)])

    rows.append([KeyboardButton(BTN_HOME), KeyboardButton(BTN_ADMIN_CANCEL)])

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Choose an admin action",
    )


def broadcast_confirm_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_ADMIN_POST), KeyboardButton(BTN_ADMIN_CANCEL)],
            [KeyboardButton(BTN_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Publish or cancel",
    )


def store_creation_keyboard(is_main_admin: bool) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(BTN_ADMIN_FINISH_STORE), KeyboardButton(BTN_ADMIN_CANCEL)],
    ]

    if is_main_admin:
        rows.append([KeyboardButton(BTN_ADMIN_ADD_ADMIN), KeyboardButton(BTN_ADMIN_REMOVE_ADMIN)])

    rows.append([KeyboardButton(BTN_HOME)])

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Send files, then create the link",
    )
