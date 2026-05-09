from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from ui import labels

BTN_CONVERT_FILES = labels.BTN_CONVERT_FILES
BTN_COMPRESS_IMAGE = labels.BTN_COMPRESS_IMAGE
BTN_EXTRACT_ZIP = labels.BTN_EXTRACT_ZIP
BTN_RENAME_FILE = labels.BTN_RENAME_FILE
BTN_MERGE_PDF = labels.BTN_MERGE_PDF
BTN_SPLIT_PDF = labels.BTN_SPLIT_PDF
BTN_HELP = labels.BTN_HELP
BTN_HOME = labels.BTN_HOME

BTN_DONE = labels.BTN_DONE
BTN_ADMIN_DASHBOARD = labels.BTN_ADMIN_DASHBOARD
BTN_ADMIN_STATUS = labels.BTN_ADMIN_STATUS
BTN_ADMIN_ADMINS = labels.BTN_ADMIN_ADMINS
BTN_ADMIN_BROADCAST = labels.BTN_ADMIN_BROADCAST
BTN_ADMIN_CREATE_STORE = labels.BTN_ADMIN_CREATE_STORE
BTN_ADMIN_FINISH_STORE = labels.BTN_ADMIN_FINISH_STORE
BTN_ADMIN_STORES = labels.BTN_ADMIN_STORES
BTN_ADMIN_POST = labels.BTN_ADMIN_POST
BTN_ADMIN_ADD_ADMIN = labels.BTN_ADMIN_ADD_ADMIN
BTN_ADMIN_REMOVE_ADMIN = labels.BTN_ADMIN_REMOVE_ADMIN
BTN_ADMIN_CANCEL = labels.BTN_ADMIN_CANCEL

BTN_JPG_TO_PDF = labels.BTN_JPG_TO_PDF
BTN_WORD_TO_PDF = labels.BTN_WORD_TO_PDF
BTN_POWERPOINT_TO_PDF = labels.BTN_POWERPOINT_TO_PDF
BTN_EXCEL_TO_PDF = labels.BTN_EXCEL_TO_PDF
BTN_HTML_TO_PDF = labels.BTN_HTML_TO_PDF
BTN_PDF_TO_JPG = labels.BTN_PDF_TO_JPG
BTN_PDF_TO_WORD = labels.BTN_PDF_TO_WORD
BTN_PDF_TO_POWERPOINT = labels.BTN_PDF_TO_POWERPOINT
BTN_PDF_TO_EXCEL = labels.BTN_PDF_TO_EXCEL
BTN_PDF_TO_PDFA = labels.BTN_PDF_TO_PDFA
BTN_JPG_TO_PNG = labels.BTN_JPG_TO_PNG
BTN_PNG_TO_JPG = labels.BTN_PNG_TO_JPG


def _reply_keyboard(rows: list[list[str]], placeholder: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(label) for label in row] for row in rows],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder=placeholder,
    )


def home_keyboard() -> ReplyKeyboardMarkup:
    return _reply_keyboard(labels.HOME_MENU_ROWS, "Choose a tool")


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Usage", callback_data="menu:stats"), InlineKeyboardButton("Recent Activity", callback_data="menu:history")],
            [InlineKeyboardButton("Back to Home", callback_data="menu:home")],
        ]
    )


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(BTN_CONVERT_FILES, callback_data="menu:convert_file")],
            [InlineKeyboardButton(BTN_COMPRESS_IMAGE, callback_data="menu:compress_image")],
            [InlineKeyboardButton(BTN_MERGE_PDF, callback_data="menu:merge_pdf"), InlineKeyboardButton(BTN_SPLIT_PDF, callback_data="menu:split_pdf")],
            [InlineKeyboardButton(BTN_EXTRACT_ZIP, callback_data="menu:extract_zip"), InlineKeyboardButton(BTN_RENAME_FILE, callback_data="menu:rename_file")],
            [InlineKeyboardButton(BTN_HELP, callback_data="menu:help")],
        ]
    )


def convert_keyboard() -> ReplyKeyboardMarkup:
    return convert_keyboard_for_buttons(labels.CONVERSION_BUTTON_ORDER)


def conversion_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("To PDF", callback_data="menu:convert:to_pdf_menu")],
            [InlineKeyboardButton("From PDF", callback_data="menu:convert:from_pdf_menu")],
            [InlineKeyboardButton("Image Formats", callback_data="menu:convert:image_formats_menu")],
            [InlineKeyboardButton("Back to Home", callback_data="menu:home")],
        ]
    )


def convert_keyboard_for_buttons(buttons: list[str]) -> ReplyKeyboardMarkup:
    rows: list[list[str]] = []
    row: list[str] = []

    for button in buttons:
        row.append(button)
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    rows.append([BTN_HOME])
    return _reply_keyboard(rows, "Choose a conversion")


def merge_keyboard() -> ReplyKeyboardMarkup:
    return _reply_keyboard([[BTN_DONE, BTN_HOME]], "Upload PDFs, then finish merge")


def queue_actions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Finish", callback_data="menu:queue:finish")],
            [InlineKeyboardButton("Back to Home", callback_data="menu:home")],
        ]
    )


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Back to Home", callback_data="menu:home")]])


def admin_keyboard(is_main_admin: bool) -> ReplyKeyboardMarkup:
    rows = list(labels.ADMIN_MENU_ROWS)
    if is_main_admin:
        rows.extend(labels.ADMIN_MAIN_ONLY_ROWS)
    rows.extend(labels.ADMIN_FOOTER_ROWS)
    return _reply_keyboard(rows, "Choose an admin action")


def broadcast_confirm_keyboard() -> ReplyKeyboardMarkup:
    return _reply_keyboard([[BTN_ADMIN_POST, BTN_ADMIN_CANCEL], [BTN_HOME]], "Publish or cancel")


def store_creation_keyboard(is_main_admin: bool) -> ReplyKeyboardMarkup:
    rows = [[BTN_ADMIN_FINISH_STORE, BTN_ADMIN_CANCEL]]
    if is_main_admin:
        rows.extend(labels.ADMIN_MAIN_ONLY_ROWS)
    rows.append([BTN_HOME])
    return _reply_keyboard(rows, "Upload files, then generate link")


def archives_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(BTN_EXTRACT_ZIP, callback_data="menu:extract_zip")],
            [InlineKeyboardButton("Create ZIP", callback_data="menu:create_zip")],
            [InlineKeyboardButton("Back to Home", callback_data="menu:home")],
        ]
    )


def image_tools_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(BTN_COMPRESS_IMAGE, callback_data="menu:compress_image")],
            [InlineKeyboardButton("Resize Image", callback_data="menu:resize_image"), InlineKeyboardButton("Enhance Image", callback_data="menu:enhance_image")],
            [InlineKeyboardButton("Watermark Image", callback_data="menu:watermark_image"), InlineKeyboardButton("Extract Text", callback_data="menu:ocr_image")],
            [InlineKeyboardButton("Back to Home", callback_data="menu:home")],
        ]
    )


def documents_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(BTN_MERGE_PDF, callback_data="menu:merge_pdf"), InlineKeyboardButton(BTN_SPLIT_PDF, callback_data="menu:split_pdf")],
            [InlineKeyboardButton(BTN_RENAME_FILE, callback_data="menu:rename_file")],
            [InlineKeyboardButton(BTN_CONVERT_FILES, callback_data="menu:convert_file")],
            [InlineKeyboardButton("Back to Home", callback_data="menu:home")],
        ]
    )


def video_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Video to GIF", callback_data="menu:video_to_gif")],
            [InlineKeyboardButton("Compress Video", callback_data="menu:compress_video")],
            [InlineKeyboardButton("Back to Home", callback_data="menu:home")],
        ]
    )


def convert_to_pdf_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(BTN_JPG_TO_PDF, callback_data="menu:convert:jpg_to_pdf"), InlineKeyboardButton(BTN_WORD_TO_PDF, callback_data="menu:convert:word_to_pdf")],
            [InlineKeyboardButton(BTN_POWERPOINT_TO_PDF, callback_data="menu:convert:powerpoint_to_pdf"), InlineKeyboardButton(BTN_EXCEL_TO_PDF, callback_data="menu:convert:excel_to_pdf")],
            [InlineKeyboardButton(BTN_HTML_TO_PDF, callback_data="menu:convert:html_to_pdf")],
            [InlineKeyboardButton("Back to Home", callback_data="menu:home")],
        ]
    )


def convert_from_pdf_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(BTN_PDF_TO_JPG, callback_data="menu:convert:pdf_to_jpg"), InlineKeyboardButton(BTN_PDF_TO_WORD, callback_data="menu:convert:pdf_to_word")],
            [InlineKeyboardButton(BTN_PDF_TO_POWERPOINT, callback_data="menu:convert:pdf_to_powerpoint"), InlineKeyboardButton(BTN_PDF_TO_EXCEL, callback_data="menu:convert:pdf_to_excel")],
            [InlineKeyboardButton(BTN_PDF_TO_PDFA, callback_data="menu:convert:pdf_to_pdfa")],
            [InlineKeyboardButton("Back to Home", callback_data="menu:home")],
        ]
    )


def image_format_conversion_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(BTN_JPG_TO_PNG, callback_data="menu:convert:jpg_to_png"), InlineKeyboardButton(BTN_PNG_TO_JPG, callback_data="menu:convert:png_to_jpg")],
            [InlineKeyboardButton("Back to Home", callback_data="menu:home")],
        ]
    )
