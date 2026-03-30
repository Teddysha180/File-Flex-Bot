from telegram import KeyboardButton, ReplyKeyboardMarkup


BTN_EXTRACT_ZIP = "Extract ZIP"
BTN_COMPRESS_IMAGE = "Compress Image"
BTN_CONVERT_FILES = "Convert Files"
BTN_RENAME_FILE = "Rename File"
BTN_MERGE_PDF = "Merge PDF"
BTN_SPLIT_PDF = "Split PDF"
BTN_HELP = "Help"
BTN_HOME = "Home"
BTN_DONE = "Done"

BTN_JPG_TO_PDF = "JPG -> PDF"
BTN_WORD_TO_PDF = "Word -> PDF"
BTN_POWERPOINT_TO_PDF = "PowerPoint -> PDF"
BTN_EXCEL_TO_PDF = "Excel -> PDF"
BTN_HTML_TO_PDF = "HTML -> PDF"
BTN_PDF_TO_JPG = "PDF -> JPG"
BTN_PDF_TO_WORD = "PDF -> Word"
BTN_PDF_TO_POWERPOINT = "PDF -> PowerPoint"
BTN_PDF_TO_EXCEL = "PDF -> Excel"
BTN_PDF_TO_PDFA = "PDF -> PDF/A"
BTN_JPG_TO_PNG = "JPG -> PNG"
BTN_PNG_TO_JPG = "PNG -> JPG"


def home_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_EXTRACT_ZIP), KeyboardButton(BTN_COMPRESS_IMAGE)],
            [KeyboardButton(BTN_CONVERT_FILES), KeyboardButton(BTN_RENAME_FILE)],
            [KeyboardButton(BTN_MERGE_PDF), KeyboardButton(BTN_SPLIT_PDF)],
            [KeyboardButton(BTN_HELP), KeyboardButton(BTN_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def convert_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_JPG_TO_PDF), KeyboardButton(BTN_WORD_TO_PDF)],
            [KeyboardButton(BTN_POWERPOINT_TO_PDF), KeyboardButton(BTN_EXCEL_TO_PDF)],
            [KeyboardButton(BTN_HTML_TO_PDF), KeyboardButton(BTN_PDF_TO_JPG)],
            [KeyboardButton(BTN_PDF_TO_WORD), KeyboardButton(BTN_PDF_TO_POWERPOINT)],
            [KeyboardButton(BTN_PDF_TO_EXCEL), KeyboardButton(BTN_PDF_TO_PDFA)],
            [KeyboardButton(BTN_JPG_TO_PNG), KeyboardButton(BTN_PNG_TO_JPG)],
            [KeyboardButton(BTN_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def merge_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_DONE), KeyboardButton(BTN_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
