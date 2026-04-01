from telegram import KeyboardButton, ReplyKeyboardMarkup


BTN_EXTRACT_ZIP = "Archive Unpack"
BTN_COMPRESS_IMAGE = "Image Compress"
BTN_CONVERT_FILES = "File Convert"
BTN_RENAME_FILE = "File Rename"
BTN_MERGE_PDF = "PDF Merge"
BTN_SPLIT_PDF = "PDF Split"
BTN_HELP = "Help Center"
BTN_HOME = "Main Menu"
BTN_DONE = "Create Now"
BTN_ADMIN_DASHBOARD = "Overview"
BTN_ADMIN_STATUS = "System Status"
BTN_ADMIN_ADMINS = "Admin Team"
BTN_ADMIN_BROADCAST = "Broadcast Flow"
BTN_ADMIN_POST = "Send Broadcast"
BTN_ADMIN_ADD_ADMIN = "Add Admin"
BTN_ADMIN_REMOVE_ADMIN = "Remove Admin"
BTN_ADMIN_CANCEL = "Cancel Action"

BTN_JPG_TO_PDF = "JPG to PDF"
BTN_WORD_TO_PDF = "Word to PDF"
BTN_POWERPOINT_TO_PDF = "Slides to PDF"
BTN_EXCEL_TO_PDF = "Sheet to PDF"
BTN_HTML_TO_PDF = "HTML to PDF"
BTN_PDF_TO_JPG = "PDF to JPG"
BTN_PDF_TO_WORD = "PDF to Word"
BTN_PDF_TO_POWERPOINT = "PDF to Slides"
BTN_PDF_TO_EXCEL = "PDF to Sheet"
BTN_PDF_TO_PDFA = "PDF to PDF/A"
BTN_JPG_TO_PNG = "JPG to PNG"
BTN_PNG_TO_JPG = "PNG to JPG"


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
        input_field_placeholder="Choose a file tool",
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
        input_field_placeholder="Choose a conversion flow",
    )


def merge_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_DONE), KeyboardButton(BTN_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Send files, then create",
    )


def admin_keyboard(is_main_admin: bool) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(BTN_ADMIN_DASHBOARD), KeyboardButton(BTN_ADMIN_STATUS)],
        [KeyboardButton(BTN_ADMIN_ADMINS), KeyboardButton(BTN_ADMIN_BROADCAST)],
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
        input_field_placeholder="Send or cancel the broadcast",
    )
