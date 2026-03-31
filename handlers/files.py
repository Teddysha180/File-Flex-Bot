import logging
from pathlib import Path

from telegram import InputFile, Update
from telegram.ext import ContextTypes

from handlers.admin import (
    handle_admin_document,
    handle_admin_photo,
    handle_admin_text,
    handle_admin_video,
    register_user,
)
from handlers.access import ensure_channel_membership
from handlers.keyboards import (
    BTN_COMPRESS_IMAGE,
    BTN_CONVERT_FILES,
    BTN_DONE,
    BTN_EXTRACT_ZIP,
    BTN_HELP,
    BTN_HOME,
    BTN_JOINED,
    BTN_MERGE_PDF,
    BTN_RENAME_FILE,
    BTN_SPLIT_PDF,
    BTN_EXCEL_TO_PDF,
    BTN_HTML_TO_PDF,
    BTN_JPG_TO_PDF,
    BTN_JPG_TO_PNG,
    BTN_PDF_TO_EXCEL,
    BTN_PDF_TO_JPG,
    BTN_PDF_TO_PDFA,
    BTN_PDF_TO_POWERPOINT,
    BTN_PDF_TO_WORD,
    BTN_PNG_TO_JPG,
    BTN_POWERPOINT_TO_PDF,
    BTN_WORD_TO_PDF,
    convert_keyboard_for_buttons,
    home_keyboard,
    merge_keyboard,
)
from handlers.messages import HELP_MESSAGE
from handlers.states import (
    ACTION_COMPRESS_IMAGE,
    ACTION_CONVERT_FILE,
    ACTION_EXTRACT_ZIP,
    ACTION_MERGE_PDF,
    ACTION_RENAME_FILE,
    ACTION_SPLIT_PDF,
    STATE_KEY_ACTION,
    STATE_KEY_CONVERSION_TARGET,
    STATE_KEY_JOB_DIR,
    STATE_KEY_PENDING_EXTENSION,
    STATE_KEY_PENDING_FILE,
    STATE_KEY_PENDING_FILES,
    STATE_KEY_PENDING_INPUT,
    reset_user_state,
)
from utils.config import config
from utils.filesystem import (
    cleanup_paths,
    create_user_job_dir,
    download_document_to_path,
    download_photo_to_path,
    safe_file_name,
)
from utils.processing import (
    compress_image_file,
    convert_image_file,
    extract_zip_archive,
    is_conversion_available,
    is_ghostscript_available,
    is_libreoffice_available,
    merge_pdf_files,
    rename_file_copy,
    split_pdf,
)


logger = logging.getLogger(__name__)

CONVERSION_BUTTONS = {
    BTN_JPG_TO_PDF: "jpg_to_pdf",
    BTN_WORD_TO_PDF: "word_to_pdf",
    BTN_POWERPOINT_TO_PDF: "powerpoint_to_pdf",
    BTN_EXCEL_TO_PDF: "excel_to_pdf",
    BTN_HTML_TO_PDF: "html_to_pdf",
    BTN_PDF_TO_JPG: "pdf_to_jpg",
    BTN_PDF_TO_WORD: "pdf_to_word",
    BTN_PDF_TO_POWERPOINT: "pdf_to_powerpoint",
    BTN_PDF_TO_EXCEL: "pdf_to_excel",
    BTN_PDF_TO_PDFA: "pdf_to_pdfa",
    BTN_JPG_TO_PNG: "jpg_to_png",
    BTN_PNG_TO_JPG: "png_to_jpg",
}


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.photo:
        return

    register_user(update)

    if not await ensure_channel_membership(update, context):
        return

    if await handle_admin_photo(update, context):
        return

    action = context.user_data.get(STATE_KEY_ACTION)
    if action not in {ACTION_COMPRESS_IMAGE, ACTION_CONVERT_FILE}:
        await update.message.reply_text(
            "Choose a tool from the main menu first.",
            reply_markup=home_keyboard(),
        )
        return

    job_dir = _get_or_create_job_dir(update, context)
    input_path = job_dir / "photo_input.jpg"

    try:
        _validate_upload_size(update.message.photo[-1].file_size, config.MAX_FILE_SIZE)
        await download_photo_to_path(update.message.photo[-1], input_path)
        await _process_file_action(update, context, input_path)
    except Exception:
        logger.exception("Failed to process photo")
        reset_user_state(context.user_data)
        await update.message.reply_text(
            "I couldn't process that image. Please try a different file.",
            reply_markup=home_keyboard(),
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.document:
        return

    register_user(update)

    if not await ensure_channel_membership(update, context):
        return

    if await handle_admin_document(update, context):
        return

    action = context.user_data.get(STATE_KEY_ACTION)
    if not action:
        await update.message.reply_text(
            "Choose a tool from the main menu first.",
            reply_markup=home_keyboard(),
        )
        return

    document = update.message.document
    file_name = safe_file_name(document.file_name or "uploaded_file")
    job_dir = _get_or_create_job_dir(update, context)
    input_path = job_dir / file_name

    try:
        max_size = config.ZIP_MAX_FILE_SIZE if action == ACTION_EXTRACT_ZIP else config.MAX_FILE_SIZE
        _validate_upload_size(document.file_size, max_size, is_zip=action == ACTION_EXTRACT_ZIP)
        await download_document_to_path(document, input_path)

        if action == ACTION_RENAME_FILE:
            context.user_data[STATE_KEY_PENDING_FILE] = str(input_path)
            context.user_data[STATE_KEY_PENDING_EXTENSION] = Path(file_name).suffix
            await update.message.reply_text(
                "Send the new file name you want to use.",
                reply_markup=home_keyboard(),
            )
            return

        if action == ACTION_MERGE_PDF:
            if input_path.suffix.lower() != ".pdf":
                raise ValueError("Merge PDF only accepts PDF files")
            pending_files = context.user_data.setdefault(STATE_KEY_PENDING_FILES, [])
            pending_files.append(str(input_path))
            await update.message.reply_text(
                f"PDF added. Total files: {len(pending_files)}. Tap Finish when you're ready to merge.",
                reply_markup=merge_keyboard(),
            )
            return

        if action == ACTION_SPLIT_PDF:
            context.user_data[STATE_KEY_PENDING_FILE] = str(input_path)
            context.user_data[STATE_KEY_PENDING_INPUT] = "range"
            await update.message.reply_text(
                "Send the page range in this format: 1-3.",
                reply_markup=home_keyboard(),
            )
            return

        await _process_file_action(update, context, input_path)
    except ValueError as exc:
        await update.message.reply_text(
            str(exc),
            reply_markup=home_keyboard(),
        )
        reset_user_state(context.user_data)
    except Exception:
        logger.exception("Failed to process document")
        reset_user_state(context.user_data)
        await update.message.reply_text(
            "Something went wrong while processing that file. Please try again.",
            reply_markup=home_keyboard(),
        )


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    register_user(update)

    if not await ensure_channel_membership(update, context):
        return

    if await handle_admin_text(update, context):
        return

    text = update.message.text.strip()

    if text == BTN_HOME:
        reset_user_state(context.user_data)
        await update.message.reply_text("Back at the main menu.", reply_markup=home_keyboard())
        return

    if text == BTN_JOINED:
        if not await ensure_channel_membership(update, context):
            return
        reset_user_state(context.user_data)
        await update.message.reply_text("Access confirmed. Welcome back.", reply_markup=home_keyboard())
        return

    if text == BTN_HELP:
        reset_user_state(context.user_data)
        await update.message.reply_text(HELP_MESSAGE, reply_markup=home_keyboard())
        return

    if text == BTN_CONVERT_FILES:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        available_buttons = _available_conversion_buttons()
        await update.message.reply_text(
            _available_conversions_message(),
            reply_markup=convert_keyboard_for_buttons(available_buttons),
        )
        return

    if text in CONVERSION_BUTTONS:
        conversion_target = CONVERSION_BUTTONS[text]
        if not is_conversion_available(conversion_target):
            await update.message.reply_text(
                _conversion_unavailable_message(conversion_target),
                reply_markup=home_keyboard(),
            )
            return

        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        context.user_data[STATE_KEY_CONVERSION_TARGET] = conversion_target
        await update.message.reply_text(
            _conversion_prompt(conversion_target),
            reply_markup=home_keyboard(),
        )
        return

    if text == BTN_EXTRACT_ZIP:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_EXTRACT_ZIP
        await update.message.reply_text(
            f"Send the ZIP file you want to extract.\n\nZIP limit: {round(config.ZIP_MAX_FILE_SIZE / (1024 * 1024))} MB.",
            reply_markup=home_keyboard(),
        )
        return

    if text == BTN_COMPRESS_IMAGE:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_COMPRESS_IMAGE
        await update.message.reply_text(
            f"Send a JPG or PNG image to compress.\n\nFile limit: {round(config.MAX_FILE_SIZE / (1024 * 1024))} MB.",
            reply_markup=home_keyboard(),
        )
        return

    if text == BTN_RENAME_FILE:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_RENAME_FILE
        await update.message.reply_text(
            f"Send the file you want to rename.\n\nFile limit: {round(config.MAX_FILE_SIZE / (1024 * 1024))} MB.",
            reply_markup=home_keyboard(),
        )
        return

    if text == BTN_MERGE_PDF:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_MERGE_PDF
        context.user_data[STATE_KEY_PENDING_FILES] = []
        await update.message.reply_text(
            f"Send PDF files one by one, then tap Finish when you're ready.\n\nPer-file limit: {round(config.MAX_FILE_SIZE / (1024 * 1024))} MB.",
            reply_markup=merge_keyboard(),
        )
        return

    if text == BTN_SPLIT_PDF:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_SPLIT_PDF
        await update.message.reply_text(
            f"Send the PDF you want to split.\n\nFile limit: {round(config.MAX_FILE_SIZE / (1024 * 1024))} MB.",
            reply_markup=home_keyboard(),
        )
        return

    if text == BTN_DONE:
        await _finish_merge(update, context)
        return

    action = context.user_data.get(STATE_KEY_ACTION)
    pending_file = context.user_data.get(STATE_KEY_PENDING_FILE)
    pending_input = context.user_data.get(STATE_KEY_PENDING_INPUT)

    if action == ACTION_RENAME_FILE and pending_file:
        await _finish_rename(update, context, text)
        return

    if action == ACTION_SPLIT_PDF and pending_input == "range" and pending_file:
        await _finish_split(update, context, text)
        return

    await update.message.reply_text(
        "Choose a tool from the main menu.",
        reply_markup=home_keyboard(),
    )


async def unknown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    register_user(update)
    if not await ensure_channel_membership(update, context):
        return
    if update.message:
        await update.message.reply_text(
            "Use the main menu to choose a tool.",
            reply_markup=home_keyboard(),
        )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.video:
        return

    register_user(update)

    if not await ensure_channel_membership(update, context):
        return

    if await handle_admin_video(update, context):
        return

    await update.message.reply_text(
        "Video uploads are only supported in the admin broadcast flow right now.",
        reply_markup=home_keyboard(),
    )


async def _process_file_action(update: Update, context: ContextTypes.DEFAULT_TYPE, input_path: Path) -> None:
    if not update.message:
        return

    action = context.user_data.get(STATE_KEY_ACTION)
    job_dir = input_path.parent

    try:
        if action == ACTION_EXTRACT_ZIP:
            if input_path.suffix.lower() != ".zip":
                raise ValueError("Please send a ZIP file.")
            extracted_files = extract_zip_archive(input_path, job_dir / "extracted")
            if not extracted_files:
                raise ValueError("That ZIP archive is empty.")

            for file_path in extracted_files[:10]:
                with file_path.open("rb") as file_handle:
                    await update.message.reply_document(
                        document=InputFile(file_handle, filename=file_path.name)
                    )

            await update.message.reply_text("Extraction complete.", reply_markup=home_keyboard())
            reset_user_state(context.user_data)
            return

        if action == ACTION_COMPRESS_IMAGE:
            compressed_path = compress_image_file(input_path)
            with compressed_path.open("rb") as file_handle:
                await update.message.reply_document(
                    document=InputFile(file_handle, filename=compressed_path.name),
                    caption="Your compressed image is ready.",
                    reply_markup=home_keyboard(),
                )
            reset_user_state(context.user_data)
            return

        if action == ACTION_CONVERT_FILE:
            conversion_target = context.user_data.get(STATE_KEY_CONVERSION_TARGET)
            if not conversion_target:
                raise ValueError("Choose a conversion first")

            _validate_conversion_input(input_path, conversion_target)
            converted_path = convert_image_file(input_path, conversion_target)
            with converted_path.open("rb") as file_handle:
                await update.message.reply_document(
                    document=InputFile(file_handle, filename=converted_path.name),
                    caption="Your converted file is ready.",
                    reply_markup=home_keyboard(),
                )
            reset_user_state(context.user_data)
            return

        raise ValueError("Choose a valid tool first.")
    except ValueError as exc:
        await update.message.reply_text(str(exc), reply_markup=home_keyboard())
        reset_user_state(context.user_data)
    finally:
        cleanup_paths([job_dir])


async def _finish_rename(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    source_path = Path(context.user_data[STATE_KEY_PENDING_FILE])
    extension = context.user_data.get(STATE_KEY_PENDING_EXTENSION, "")
    job_dir = source_path.parent
    succeeded = False

    try:
        new_name = safe_file_name(text)
        if not new_name:
            raise ValueError("Send a valid file name.")
        if not Path(new_name).suffix and extension:
            new_name = f"{new_name}{extension}"

        renamed_path = rename_file_copy(source_path, new_name)
        with renamed_path.open("rb") as file_handle:
            await update.message.reply_document(
                document=InputFile(file_handle, filename=renamed_path.name),
                caption="Your renamed file is ready.",
                reply_markup=home_keyboard(),
            )
        succeeded = True
        reset_user_state(context.user_data)
    except ValueError as exc:
        await update.message.reply_text(str(exc), reply_markup=home_keyboard())
    finally:
        if succeeded:
            cleanup_paths([job_dir])


async def _finish_split(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    source_path = Path(context.user_data[STATE_KEY_PENDING_FILE])
    job_dir = source_path.parent
    succeeded = False

    try:
        if "-" not in text:
            raise ValueError("Send the page range in this format: 1-3.")
        start_text, end_text = text.split("-", 1)
        start_page = int(start_text.strip())
        end_page = int(end_text.strip())
        if start_page < 1 or end_page < start_page:
            raise ValueError("Invalid page range")

        split_path = split_pdf(source_path, start_page, end_page)
        with split_path.open("rb") as file_handle:
            await update.message.reply_document(
                document=InputFile(file_handle, filename=split_path.name),
                caption="Your split PDF is ready.",
                reply_markup=home_keyboard(),
            )
        succeeded = True
        reset_user_state(context.user_data)
    except ValueError as exc:
        await update.message.reply_text(str(exc), reply_markup=home_keyboard())
    finally:
        if succeeded:
            cleanup_paths([job_dir])


async def _finish_merge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    action = context.user_data.get(STATE_KEY_ACTION)
    pending_files = context.user_data.get(STATE_KEY_PENDING_FILES, [])
    if action != ACTION_MERGE_PDF or not pending_files:
        await update.message.reply_text("No PDF files have been added yet.", reply_markup=home_keyboard())
        return

    job_dir = Path(pending_files[0]).parent
    try:
        output_path = merge_pdf_files(pending_files)
        with output_path.open("rb") as file_handle:
            await update.message.reply_document(
                document=InputFile(file_handle, filename=output_path.name),
                caption="Your merged PDF is ready.",
                reply_markup=home_keyboard(),
            )
        reset_user_state(context.user_data)
    except ValueError as exc:
        await update.message.reply_text(str(exc), reply_markup=home_keyboard())
    finally:
        cleanup_paths([job_dir])


def _get_or_create_job_dir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Path:
    existing_job_dir = context.user_data.get(STATE_KEY_JOB_DIR)
    if existing_job_dir:
        return Path(existing_job_dir)

    user_id = update.effective_user.id if update.effective_user else 0
    job_dir = create_user_job_dir(user_id)
    context.user_data[STATE_KEY_JOB_DIR] = str(job_dir)
    return job_dir


def _validate_upload_size(file_size: int | None, max_size: int, *, is_zip: bool = False) -> None:
    if file_size is None or file_size <= max_size:
        return

    size_label = round(max_size / (1024 * 1024))
    if is_zip:
        raise ValueError(f"ZIP files can be up to {size_label} MB.")

    raise ValueError(f"Files can be up to {size_label} MB.")


def _validate_conversion_input(input_path: Path, conversion_target: str) -> None:
    suffix = input_path.suffix.lower()

    if conversion_target in {"jpg_to_pdf", "jpg_to_png"} and suffix not in {".jpg", ".jpeg"}:
        raise ValueError("This conversion needs a JPG file")

    if conversion_target == "png_to_jpg" and suffix != ".png":
        raise ValueError("PNG to JPG needs a PNG file")

    if conversion_target == "word_to_pdf" and suffix not in {".doc", ".docx"}:
        raise ValueError("Word to PDF needs DOC or DOCX")

    if conversion_target == "powerpoint_to_pdf" and suffix not in {".ppt", ".pptx"}:
        raise ValueError("PowerPoint to PDF needs PPT or PPTX")

    if conversion_target == "excel_to_pdf" and suffix not in {".xls", ".xlsx"}:
        raise ValueError("Excel to PDF needs XLS or XLSX")

    if conversion_target == "html_to_pdf" and suffix not in {".html", ".htm"}:
        raise ValueError("HTML to PDF needs HTML or HTM")

    if conversion_target in {"pdf_to_jpg", "pdf_to_word", "pdf_to_powerpoint", "pdf_to_excel", "pdf_to_pdfa"} and suffix != ".pdf":
        raise ValueError("This conversion needs a PDF file")


def _conversion_prompt(conversion_target: str) -> str:
    prompts = {
        "jpg_to_pdf": "Send a JPG image to convert to PDF.",
        "word_to_pdf": "Send a Word file to convert to PDF.",
        "powerpoint_to_pdf": "Send a PowerPoint file to convert to PDF.",
        "excel_to_pdf": "Send an Excel file to convert to PDF.",
        "html_to_pdf": "Send an HTML file to convert to PDF.",
        "pdf_to_jpg": "Send a PDF file to convert to JPG.",
        "pdf_to_word": "Send a PDF file to convert to Word.",
        "pdf_to_powerpoint": "Send a PDF file to convert to PowerPoint.",
        "pdf_to_excel": "Send a PDF file to convert to Excel.",
        "pdf_to_pdfa": "Send a PDF file to convert to PDF/A.",
        "jpg_to_png": "Send a JPG image to convert to PNG.",
        "png_to_jpg": "Send a PNG file to convert to JPG.",
    }
    base_prompt = prompts.get(conversion_target, "Send the file you want to convert.")
    return f"{base_prompt}\n\nFile limit: {round(config.MAX_FILE_SIZE / (1024 * 1024))} MB."


def _available_conversion_buttons() -> list[str]:
    return [
        button
        for button, conversion_target in CONVERSION_BUTTONS.items()
        if is_conversion_available(conversion_target)
    ]


def _available_conversions_message() -> str:
    lines = [
        "Choose a conversion below.",
        "",
        "To PDF: JPG, Word, PowerPoint, Excel, HTML",
        "From PDF: JPG, Word, PowerPoint, Excel, PDF/A",
        "Image Formats: JPG -> PNG, PNG -> JPG",
    ]

    if not is_libreoffice_available():
        lines.extend(
            [
                "",
                "Office-to-PDF options are hidden on this deployment.",
            ]
        )

    if not is_ghostscript_available():
        lines.append("PDF to PDF/A is hidden on this deployment.")

    lines.extend(["", "Use Back to Menu any time to return to the main screen."])

    return "\n".join(lines)


def _conversion_unavailable_message(conversion_target: str) -> str:
    if conversion_target in {"word_to_pdf", "powerpoint_to_pdf", "excel_to_pdf", "html_to_pdf"}:
        return (
            "That conversion is currently unavailable on this deployment.\n\n"
            "LibreOffice is not installed on the running server yet."
        )

    if conversion_target == "pdf_to_pdfa":
        return (
            "That conversion is currently unavailable on this deployment.\n\n"
            "Ghostscript is not installed on the running server yet."
        )

    return "That conversion is currently unavailable on this deployment."
