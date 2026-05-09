import asyncio
import logging
from contextlib import suppress
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
    BTN_EXCEL_TO_PDF,
    BTN_EXTRACT_ZIP,
    BTN_HELP,
    BTN_HOME,
    BTN_HTML_TO_PDF,
    BTN_JPG_TO_PDF,
    BTN_JPG_TO_PNG,
    BTN_MERGE_PDF,
    BTN_PDF_TO_EXCEL,
    BTN_PDF_TO_JPG,
    BTN_PDF_TO_PDFA,
    BTN_PDF_TO_POWERPOINT,
    BTN_PDF_TO_WORD,
    BTN_PNG_TO_JPG,
    BTN_POWERPOINT_TO_PDF,
    BTN_RENAME_FILE,
    BTN_SPLIT_PDF,
    BTN_WORD_TO_PDF,
    back_to_menu_keyboard,
    conversion_keyboard,
    convert_from_pdf_keyboard,
    convert_to_pdf_keyboard,
    convert_keyboard_for_buttons,
    home_keyboard,
    image_format_conversion_keyboard,
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
from ui.text import (
    DEFAULT_FALLBACK_MESSAGE,
    DOCUMENT_TOOL_REQUIRED_MESSAGE,
    EMPTY_MERGE_QUEUE_MESSAGE,
    EXTRACTION_COMPLETE_MESSAGE,
    INLINE_CONVERSION_SELECTOR_MESSAGE,
    INLINE_FROM_PDF_MESSAGE,
    INLINE_IMAGE_FORMATS_MESSAGE,
    INLINE_TO_PDF_MESSAGE,
    MAIN_MENU_MESSAGE,
    PHOTO_PROCESSING_FAILED_MESSAGE,
    PHOTO_TOOL_REQUIRED_MESSAGE,
    RENAME_FILE_RECEIVED_MESSAGE,
    SPLIT_FILE_RECEIVED_MESSAGE,
    UNEXPECTED_ERROR_MESSAGE,
    UNKNOWN_REQUEST_MESSAGE,
    VIDEO_DISABLED_MESSAGE,
    WAIT_ANIMATION_FRAMES,
    WAIT_TITLES,
    conversion_list_message,
    conversion_prompt,
    conversion_unavailable_message,
    merge_queue_message,
    request_unavailable_message,
    result_caption,
    tool_intro_message,
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
            PHOTO_TOOL_REQUIRED_MESSAGE,
            reply_markup=home_keyboard(),
            parse_mode="HTML",
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
            PHOTO_PROCESSING_FAILED_MESSAGE,
            reply_markup=home_keyboard(),
            parse_mode="HTML",
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
            DOCUMENT_TOOL_REQUIRED_MESSAGE,
            reply_markup=home_keyboard(),
            parse_mode="HTML",
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
                RENAME_FILE_RECEIVED_MESSAGE,
                reply_markup=home_keyboard(),
                parse_mode="HTML",
            )
            return

        if action == ACTION_MERGE_PDF:
            if input_path.suffix.lower() != ".pdf":
                raise ValueError("PDF Merge only accepts PDF files.")
            pending_files = context.user_data.setdefault(STATE_KEY_PENDING_FILES, [])
            pending_files.append(str(input_path))
            await update.message.reply_text(
                merge_queue_message(len(pending_files)),
                reply_markup=merge_keyboard(),
                parse_mode="HTML",
            )
            return

        if action == ACTION_SPLIT_PDF:
            context.user_data[STATE_KEY_PENDING_FILE] = str(input_path)
            context.user_data[STATE_KEY_PENDING_INPUT] = "range"
            await update.message.reply_text(
                SPLIT_FILE_RECEIVED_MESSAGE,
                reply_markup=home_keyboard(),
                parse_mode="HTML",
            )
            return

        await _process_file_action(update, context, input_path)
    except ValueError as exc:
        await update.message.reply_text(
            request_unavailable_message(str(exc)),
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
        reset_user_state(context.user_data)
    except Exception:
        logger.exception("Failed to process document")
        reset_user_state(context.user_data)
        await update.message.reply_text(
            UNEXPECTED_ERROR_MESSAGE,
            reply_markup=home_keyboard(),
            parse_mode="HTML",
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
        await update.message.reply_text(
            MAIN_MENU_MESSAGE,
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
        return

    if text == BTN_HELP:
        reset_user_state(context.user_data)
        await update.message.reply_text(HELP_MESSAGE, reply_markup=home_keyboard(), parse_mode="HTML")
        return

    if text == BTN_CONVERT_FILES:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await update.message.reply_text(
            INLINE_CONVERSION_SELECTOR_MESSAGE,
            reply_markup=conversion_keyboard(),
            parse_mode="HTML",
        )
        return

    if text in CONVERSION_BUTTONS:
        conversion_target = CONVERSION_BUTTONS[text]
        if not is_conversion_available(conversion_target):
            await update.message.reply_text(
                _conversion_unavailable_message(conversion_target),
                reply_markup=home_keyboard(),
                parse_mode="HTML",
            )
            return

        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        context.user_data[STATE_KEY_CONVERSION_TARGET] = conversion_target
        await update.message.reply_text(
            _conversion_prompt(conversion_target),
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
        return

    if text == BTN_EXTRACT_ZIP:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_EXTRACT_ZIP
        await update.message.reply_text(
            tool_intro_message("extract_zip"),
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
        return

    if text == BTN_COMPRESS_IMAGE:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_COMPRESS_IMAGE
        await update.message.reply_text(
            tool_intro_message("compress_image"),
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
        return

    if text == BTN_RENAME_FILE:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_RENAME_FILE
        await update.message.reply_text(
            tool_intro_message("rename_file"),
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
        return

    if text == BTN_MERGE_PDF:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_MERGE_PDF
        context.user_data[STATE_KEY_PENDING_FILES] = []
        await update.message.reply_text(
            tool_intro_message("merge_pdf"),
            reply_markup=merge_keyboard(),
            parse_mode="HTML",
        )
        return

    if text == BTN_SPLIT_PDF:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_SPLIT_PDF
        await update.message.reply_text(
            tool_intro_message("split_pdf"),
            reply_markup=home_keyboard(),
            parse_mode="HTML",
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
        DEFAULT_FALLBACK_MESSAGE,
        reply_markup=home_keyboard(),
        parse_mode="HTML",
    )


async def unknown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    register_user(update)
    if not await ensure_channel_membership(update, context):
        return
    if update.message:
        await update.message.reply_text(
            UNKNOWN_REQUEST_MESSAGE,
            reply_markup=home_keyboard(),
            parse_mode="HTML",
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
        VIDEO_DISABLED_MESSAGE,
        reply_markup=home_keyboard(),
        parse_mode="HTML",
    )


async def _process_file_action(update: Update, context: ContextTypes.DEFAULT_TYPE, input_path: Path) -> None:
    if not update.message:
        return

    action = context.user_data.get(STATE_KEY_ACTION)
    job_dir = input_path.parent
    wait_message = None
    wait_task = None

    try:
        wait_message, wait_task = await _start_wait_animation(update, _wait_title_for_action(action))

        if action == ACTION_EXTRACT_ZIP:
            if input_path.suffix.lower() != ".zip":
                raise ValueError("Please upload a ZIP file.")
            extracted_files = extract_zip_archive(input_path, job_dir / "extracted")
            if not extracted_files:
                raise ValueError("This ZIP archive is empty.")

            for file_path in extracted_files[:10]:
                with file_path.open("rb") as file_handle:
                    await update.message.reply_document(
                        document=InputFile(file_handle, filename=file_path.name)
                    )

            await update.message.reply_text(
                EXTRACTION_COMPLETE_MESSAGE,
                reply_markup=home_keyboard(),
                parse_mode="HTML",
            )
            reset_user_state(context.user_data)
            return

        if action == ACTION_COMPRESS_IMAGE:
            compressed_path = compress_image_file(input_path)
            with compressed_path.open("rb") as file_handle:
                await update.message.reply_document(
                    document=InputFile(file_handle, filename=compressed_path.name),
                    caption=result_caption("compressed image"),
                    reply_markup=home_keyboard(),
                    parse_mode="HTML",
                )
            reset_user_state(context.user_data)
            return

        if action == ACTION_CONVERT_FILE:
            conversion_target = context.user_data.get(STATE_KEY_CONVERSION_TARGET)
            if not conversion_target:
                raise ValueError("Choose a conversion type first.")

            _validate_conversion_input(input_path, conversion_target)
            converted_path = convert_image_file(input_path, conversion_target)
            with converted_path.open("rb") as file_handle:
                await update.message.reply_document(
                    document=InputFile(file_handle, filename=converted_path.name),
                    caption=result_caption("converted file"),
                    reply_markup=home_keyboard(),
                    parse_mode="HTML",
                )
            reset_user_state(context.user_data)
            return

        raise ValueError("Choose a tool from the menu first.")
    except ValueError as exc:
        await update.message.reply_text(
            request_unavailable_message(str(exc)),
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
        reset_user_state(context.user_data)
    finally:
        await _stop_wait_animation(wait_message, wait_task)
        cleanup_paths([job_dir])


async def _finish_rename(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    source_path = Path(context.user_data[STATE_KEY_PENDING_FILE])
    extension = context.user_data.get(STATE_KEY_PENDING_EXTENSION, "")
    job_dir = source_path.parent
    succeeded = False
    wait_message = None
    wait_task = None

    try:
        new_name = safe_file_name(text)
        if not new_name:
            raise ValueError("Send a valid file name.")
        if not Path(new_name).suffix and extension:
            new_name = f"{new_name}{extension}"

        wait_message, wait_task = await _start_wait_animation(update, "Renaming file")
        renamed_path = rename_file_copy(source_path, new_name)
        with renamed_path.open("rb") as file_handle:
            await update.message.reply_document(
                document=InputFile(file_handle, filename=renamed_path.name),
                caption=result_caption("renamed file"),
                reply_markup=home_keyboard(),
                parse_mode="HTML",
            )
        succeeded = True
        reset_user_state(context.user_data)
    except ValueError as exc:
        await update.message.reply_text(
            request_unavailable_message(str(exc)),
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("Failed to finish rename")
        reset_user_state(context.user_data)
        await update.message.reply_text(
            request_unavailable_message("Please check the file name and try again."),
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
    finally:
        await _stop_wait_animation(wait_message, wait_task)
        if succeeded:
            cleanup_paths([job_dir])


async def _finish_split(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    source_path = Path(context.user_data[STATE_KEY_PENDING_FILE])
    job_dir = source_path.parent
    succeeded = False
    wait_message = None
    wait_task = None

    try:
        if "-" not in text:
            raise ValueError("Send the page range in this format: 1-3.")
        start_text, end_text = text.split("-", 1)
        start_page = int(start_text.strip())
        end_page = int(end_text.strip())
        if start_page < 1 or end_page < start_page:
            raise ValueError("That page range is not valid.")

        wait_message, wait_task = await _start_wait_animation(update, "Splitting PDF")
        split_path = split_pdf(source_path, start_page, end_page)
        with split_path.open("rb") as file_handle:
            await update.message.reply_document(
                document=InputFile(file_handle, filename=split_path.name),
                caption=result_caption("split PDF"),
                reply_markup=home_keyboard(),
                parse_mode="HTML",
            )
        succeeded = True
        reset_user_state(context.user_data)
    except ValueError as exc:
        await update.message.reply_text(
            request_unavailable_message(str(exc)),
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
    finally:
        await _stop_wait_animation(wait_message, wait_task)
        if succeeded:
            cleanup_paths([job_dir])


async def _finish_merge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    action = context.user_data.get(STATE_KEY_ACTION)
    pending_files = context.user_data.get(STATE_KEY_PENDING_FILES, [])
    if action != ACTION_MERGE_PDF or not pending_files:
        await update.message.reply_text(
            EMPTY_MERGE_QUEUE_MESSAGE,
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
        return

    job_dir = Path(pending_files[0]).parent
    wait_message = None
    wait_task = None
    try:
        wait_message, wait_task = await _start_wait_animation(update, "Merging PDFs")
        output_path = merge_pdf_files(pending_files)
        with output_path.open("rb") as file_handle:
            await update.message.reply_document(
                document=InputFile(file_handle, filename=output_path.name),
                caption=result_caption("merged PDF"),
                reply_markup=home_keyboard(),
                parse_mode="HTML",
            )
        reset_user_state(context.user_data)
    except ValueError as exc:
        await update.message.reply_text(
            request_unavailable_message(str(exc)),
            reply_markup=home_keyboard(),
            parse_mode="HTML",
        )
    finally:
        await _stop_wait_animation(wait_message, wait_task)
        cleanup_paths([job_dir])


async def _start_wait_animation(update: Update, title: str):
    if not update.message:
        return None, None

    wait_message = await update.message.reply_text(
        f"<b>{title}</b>\n<code>{WAIT_ANIMATION_FRAMES[0]}</code>",
        parse_mode="HTML",
    )
    wait_task = asyncio.create_task(_animate_wait_message(wait_message, title))
    return wait_message, wait_task


async def _stop_wait_animation(wait_message, wait_task) -> None:
    if wait_task:
        wait_task.cancel()
        with suppress(asyncio.CancelledError):
            await wait_task

    if wait_message:
        with suppress(Exception):
            await wait_message.delete()


async def _animate_wait_message(wait_message, title: str) -> None:
    frame_index = 1
    while True:
        await asyncio.sleep(0.8)
        with suppress(Exception):
            await wait_message.edit_text(
                f"<b>{title}</b>\n<code>{WAIT_ANIMATION_FRAMES[frame_index]}</code>",
                parse_mode="HTML",
            )
        frame_index = (frame_index + 1) % len(WAIT_ANIMATION_FRAMES)


def _wait_title_for_action(action: str | None) -> str:
    if action == ACTION_EXTRACT_ZIP:
        return WAIT_TITLES["extract_zip"]
    if action == ACTION_COMPRESS_IMAGE:
        return WAIT_TITLES["compress_image"]
    if action == ACTION_CONVERT_FILE:
        return WAIT_TITLES["convert_file"]
    return WAIT_TITLES["default"]


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
        raise ValueError(f"ZIP files are limited to {size_label} MB.")

    raise ValueError(f"File size exceeds the {size_label} MB limit.")


def _validate_conversion_input(input_path: Path, conversion_target: str) -> None:
    suffix = input_path.suffix.lower()

    if conversion_target in {"jpg_to_pdf", "jpg_to_png"} and suffix not in {".jpg", ".jpeg"}:
        raise ValueError("This conversion requires a JPG file.")

    if conversion_target == "png_to_jpg" and suffix != ".png":
        raise ValueError("PNG to JPG requires a PNG file.")

    if conversion_target == "word_to_pdf" and suffix not in {".doc", ".docx"}:
        raise ValueError("Word to PDF requires a DOC or DOCX file.")

    if conversion_target == "powerpoint_to_pdf" and suffix not in {".ppt", ".pptx"}:
        raise ValueError("PowerPoint to PDF requires a PPT or PPTX file.")

    if conversion_target == "excel_to_pdf" and suffix not in {".xls", ".xlsx"}:
        raise ValueError("Excel to PDF requires an XLS or XLSX file.")

    if conversion_target == "html_to_pdf" and suffix not in {".html", ".htm"}:
        raise ValueError("HTML to PDF requires an HTML or HTM file.")

    if conversion_target in {"pdf_to_jpg", "pdf_to_word", "pdf_to_powerpoint", "pdf_to_excel", "pdf_to_pdfa"} and suffix != ".pdf":
        raise ValueError("This conversion requires a PDF file.")


def _conversion_prompt(conversion_target: str) -> str:
    return conversion_prompt(conversion_target)


def _available_conversion_buttons() -> list[str]:
    return [
        button
        for button, conversion_target in CONVERSION_BUTTONS.items()
        if is_conversion_available(conversion_target)
    ]


def _available_conversions_message() -> str:
    return conversion_list_message(
        libreoffice_available=is_libreoffice_available(),
        ghostscript_available=is_ghostscript_available(),
    )


def _conversion_unavailable_message(conversion_target: str) -> str:
    return conversion_unavailable_message(conversion_target)


async def handle_conversion_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    data = query.data or ""
    if not data.startswith("menu:convert:"):
        return

    await query.answer()

    if data == "menu:convert:to_pdf_menu":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await query.edit_message_text(
            INLINE_TO_PDF_MESSAGE,
            reply_markup=convert_to_pdf_keyboard(),
            parse_mode="HTML",
        )
        return

    if data == "menu:convert:from_pdf_menu":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await query.edit_message_text(
            INLINE_FROM_PDF_MESSAGE,
            reply_markup=convert_from_pdf_keyboard(),
            parse_mode="HTML",
        )
        return

    if data == "menu:convert:image_formats_menu":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await query.edit_message_text(
            INLINE_IMAGE_FORMATS_MESSAGE,
            reply_markup=image_format_conversion_keyboard(),
            parse_mode="HTML",
        )
        return

    conversion_map = {
        "menu:convert:jpg_to_png": "jpg_to_png",
        "menu:convert:png_to_jpg": "png_to_jpg",
        "menu:convert:jpg_to_pdf": "jpg_to_pdf",
        "menu:convert:word_to_pdf": "word_to_pdf",
        "menu:convert:powerpoint_to_pdf": "powerpoint_to_pdf",
        "menu:convert:excel_to_pdf": "excel_to_pdf",
        "menu:convert:html_to_pdf": "html_to_pdf",
        "menu:convert:pdf_to_jpg": "pdf_to_jpg",
        "menu:convert:pdf_to_word": "pdf_to_word",
        "menu:convert:pdf_to_powerpoint": "pdf_to_powerpoint",
        "menu:convert:pdf_to_excel": "pdf_to_excel",
        "menu:convert:pdf_to_pdfa": "pdf_to_pdfa",
    }

    conversion_target = conversion_map.get(data)
    if not conversion_target:
        return

    if not is_conversion_available(conversion_target):
        await query.edit_message_text(
            _conversion_unavailable_message(conversion_target),
            reply_markup=back_to_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    reset_user_state(context.user_data)
    context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
    context.user_data[STATE_KEY_CONVERSION_TARGET] = conversion_target
    await query.edit_message_text(
        _conversion_prompt(conversion_target),
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML",
    )
