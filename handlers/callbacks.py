from telegram import Update
from telegram.ext import ContextTypes

from telegram import InputFile

from utils.config import config
from handlers.keyboards import (
    archives_menu_keyboard,
    back_to_menu_keyboard,
    conversion_keyboard,
    convert_from_pdf_keyboard,
    convert_to_pdf_keyboard,
    documents_menu_keyboard,
    image_format_conversion_keyboard,
    image_tools_keyboard,
    main_menu_keyboard,
    queue_actions_keyboard,
    settings_keyboard,
    video_menu_keyboard,
)
from handlers.states import (
    ACTION_COMPRESS_IMAGE,
    ACTION_COMPRESS_VIDEO,
    ACTION_CONVERT_FILE,
    ACTION_CREATE_ZIP,
    ACTION_ENHANCE_IMAGE,
    ACTION_EXTRACT_ZIP,
    ACTION_MERGE_PDF,
    ACTION_OCR_IMAGE,
    ACTION_RENAME_FILE,
    ACTION_RESIZE_IMAGE,
    ACTION_SPLIT_PDF,
    ACTION_VIDEO_TO_GIF,
    ACTION_WATERMARK_IMAGE,
    STATE_KEY_ACTION,
    STATE_KEY_CONVERSION_TARGET,
    STATE_KEY_PENDING_FILES,
    STATE_KEY_PENDING_INPUT,
    reset_user_state,
)
from utils.processing import create_zip_from_files, merge_pdf_files
from utils.database import db


async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = query.data or ""

    if data == "menu:home":
        reset_user_state(context.user_data)
        await query.edit_message_text(
            "✨ *File Flex Hub*\n\nSelect a professional tool suite below to get started.",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:category:archives":
        await query.edit_message_text(
            "📦 *Archive Solutions*\n\nExtract content from ZIP files or bundle multiple files into a single archive.",
            reply_markup=archives_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:category:images":
        await query.edit_message_text(
            "🖼 *Image Suite*\n\nOptimize, resize, watermark, or extract text from your images with ease.",
            reply_markup=image_tools_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:category:documents":
        await query.edit_message_text(
            "📄 *Document Lab*\n\nAdvanced PDF management: merge, split, rename, or access our full conversion engine.",
            reply_markup=documents_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:category:video":
        await query.edit_message_text(
            "🎬 *Video Workshop*\n\nOptimize your clips for sharing or convert them into animated GIFs.",
            reply_markup=video_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:stats":
        if update.effective_user:
            stats = db.get_user_stats(update.effective_user.id)
            if stats:
                stats_text = (
                    f"📊 *User Performance Profile*\n\n"
                    f"📂 *Processed:* `{stats['total_files']}` files\n"
                    f"💾 *Data Saved:* `{stats['storage_saved'] / (1024*1024):.1f} MB`\n"
                    f"📈 *Active:* `{stats['files_this_week']}` this week\n"
                    f"📅 *Joined:* `{stats['member_since']}`\n\n"
                    f"Efficiency level: *Optimal* ✨"
                )
            else:
                stats_text = "📊 *No activity recorded yet.* Send your first file to start tracking your efficiency!"
            
            await query.edit_message_text(
                stats_text,
                reply_markup=settings_keyboard(),
                parse_mode="Markdown"
            )
        return

    if data == "menu:settings":
        await query.edit_message_text(
            "⚙️ *Preferences & Info*\n\nAccess your statistics, activity logs, and technical guidance.",
            reply_markup=settings_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:help":
        from handlers.messages import HELP_MESSAGE
        await query.edit_message_text(
            HELP_MESSAGE,
            reply_markup=settings_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:history":
        if update.effective_user:
            history = db.get_processing_history(update.effective_user.id, limit=5)
            if history:
                history_text = "📋 *Recent Operations*\n\n"
                for idx, record in enumerate(history, 1):
                    action, input_file, output_file, in_size, out_size, proc_time, timestamp = record
                    history_text += f"{idx}. *{action.upper()}*\n"
                    history_text += f"   ▫️ `{input_file[:25]}`\n"
                    history_text += f"   ▫️ `{proc_time:.1f}s` processing\n\n"
            else:
                history_text = "📋 *No recent activity found.*"
            
            await query.edit_message_text(
                history_text,
                reply_markup=settings_keyboard(),
                parse_mode="Markdown"
            )
        return

    if data == "menu:extract_zip":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_EXTRACT_ZIP
        await query.edit_message_text(
            "📦 *Ready*: Upload a `.zip` file to begin extraction.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown",
        )
        return

    if data == "menu:create_zip":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CREATE_ZIP
        context.user_data[STATE_KEY_PENDING_FILES] = []
        await query.edit_message_text(
            "🗃️ *Ready*: Upload the files you wish to archive. Tap *Finish* when the queue is complete.",
            reply_markup=queue_actions_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:compress_image":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_COMPRESS_IMAGE
        await query.edit_message_text(
            "🗜️ *Ready*: Upload an image for intelligent size optimization.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:resize_image":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_RESIZE_IMAGE
        context.user_data[STATE_KEY_PENDING_INPUT] = "width"
        await query.edit_message_text(
            "📐 *Ready*: Upload an image to resize it to our standard 800x600 profile.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:enhance_image":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_ENHANCE_IMAGE
        await query.edit_message_text(
            "✨ *Ready*: Upload an image to apply quality enhancements automatically.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:watermark_image":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_WATERMARK_IMAGE
        await query.edit_message_text(
            "💧 *Ready*: Upload an image to apply the default bot watermark.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:ocr_image":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_OCR_IMAGE
        await query.edit_message_text(
            "🔤 *Ready*: Upload an image to perform text extraction (OCR).",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:convert_file":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await query.edit_message_text(
            "🔄 *Workflow Selector*\n\nSelect a professional file conversion path below.",
            reply_markup=conversion_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:convert:to_pdf_menu":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await query.edit_message_text(
            "📄 *Destination: PDF*\n\nSupported inputs: Images, Word, PPT, Excel, and HTML.",
            reply_markup=convert_to_pdf_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:convert:from_pdf_menu":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await query.edit_message_text(
            "📤 *Source: PDF*\n\nConvert your PDFs into Images, Word, PPT, or Excel files.",
            reply_markup=convert_from_pdf_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:convert:image_formats_menu":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await query.edit_message_text(
            "🖼 *Format Switcher*\n\nQuickly convert between common web image formats.",
            reply_markup=image_format_conversion_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:merge_pdf":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_MERGE_PDF
        context.user_data[STATE_KEY_PENDING_FILES] = []
        await query.edit_message_text(
            "🧩 *Ready*: Upload PDF files in sequence. Tap *Finish* to compile the final document.",
            reply_markup=queue_actions_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:split_pdf":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_SPLIT_PDF
        context.user_data[STATE_KEY_PENDING_INPUT] = "file"
        await query.edit_message_text(
            "✂️ *Ready*: Upload a PDF file to begin the page extraction process.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:rename_file":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_RENAME_FILE
        await query.edit_message_text(
            "📝 *Ready*: Upload the file you wish to rename.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:video_to_gif":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_VIDEO_TO_GIF
        await query.edit_message_text(
            "🎬 *Ready*: Upload a video clip to convert it into a GIF.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:compress_video":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_COMPRESS_VIDEO
        context.user_data[STATE_KEY_PENDING_INPUT] = "quality"
        await query.edit_message_text(
            "🎥 *Ready*: Upload a video file for bitrate optimization.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    conversion_map = {
        "menu:convert:jpg_to_png": "jpg_to_png",
        "menu:convert:png_to_jpg": "png_to_jpg",
        "menu:convert:image_to_pdf": "image_to_pdf",
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
    if data in conversion_map:
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        context.user_data[STATE_KEY_CONVERSION_TARGET] = conversion_map[data]
        prompt = _conversion_prompt(conversion_map[data])
        await query.edit_message_text(
            prompt,
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:queue:finish":
        action = context.user_data.get(STATE_KEY_ACTION)
        pending_files = context.user_data.get(STATE_KEY_PENDING_FILES, [])
        if not pending_files:
            await query.edit_message_text(
                "⚠️ *Queue Empty*: Please upload at least one file before finishing.",
                reply_markup=queue_actions_keyboard(),
            )
            return

        try:
            if action == ACTION_MERGE_PDF:
                output_path = merge_pdf_files(pending_files)
                caption = "✅ *Document Merged*: Your PDF is ready."
            elif action == ACTION_CREATE_ZIP:
                output_path = create_zip_from_files(pending_files)
                caption = "✅ *Archive Created*: Your ZIP bundle is ready."
            else:
                await query.edit_message_text(
                    "🚫 *Action Expired*: Please restart the process from the menu.",
                    reply_markup=main_menu_keyboard(),
                )
                reset_user_state(context.user_data)
                return

            with output_path.open("rb") as file_handle:
                await query.message.reply_document(
                    document=InputFile(file_handle, filename=output_path.name),
                    caption=caption,
                    reply_markup=main_menu_keyboard(),
                    parse_mode="Markdown"
                )
            reset_user_state(context.user_data)
            await query.edit_message_text(
                "✨ *Task Complete!* What would you like to do next?",
                reply_markup=main_menu_keyboard(),
                parse_mode="Markdown"
            )
        except ValueError as exc:
            await query.edit_message_text(
                f"⚠️ *Error*: {exc}\n\nPlease verify your files and try again.",
                reply_markup=queue_actions_keyboard(),
                parse_mode="Markdown"
            )


def _conversion_prompt(conversion_target: str) -> str:
    prompt_map = {
        "jpg_to_png": "🖼 ➔ 📂 *JPG to PNG*: Please upload your JPG image.",
        "png_to_jpg": "🖼 ➔ 📂 *PNG to JPG*: Please upload your PNG image.",
        "image_to_pdf": "🖼 ➔ 📄 *Image to PDF*: Upload any image to convert it.",
        "jpg_to_pdf": "🖼 ➔ 📄 *JPG to PDF*: Upload your JPG image.",
        "word_to_pdf": "📝 ➔ 📄 *Word to PDF*: Send your `.doc` or `.docx` file.",
        "powerpoint_to_pdf": "📊 ➔ 📄 *PPT to PDF*: Send your `.ppt` or `.pptx` file.",
        "excel_to_pdf": "📈 ➔ 📄 *Excel to PDF*: Send your `.xls` or `.xlsx` file.",
        "html_to_pdf": "🌐 ➔ 📄 *HTML to PDF*: Send your `.html` file.",
        "pdf_to_jpg": "📄 ➔ 🖼 *PDF to JPG*: Send a PDF to extract pages as images.",
        "pdf_to_word": "📄 ➔ 📝 *PDF to Word*: Convert your PDF to an editable document.",
        "pdf_to_powerpoint": "📄 ➔ 📊 *PDF to PPT*: Turn PDF pages into a presentation.",
        "pdf_to_excel": "📄 ➔ 📈 *PDF to Excel*: Extract data tables into a spreadsheet.",
        "pdf_to_pdfa": "🛡 *Archival PDF*: Convert your PDF to the PDF/A standard.",
    }
    base = prompt_map.get(conversion_target, "Please upload the file you wish to process.")
    size_label = f"{round(config.MAX_FILE_SIZE / (1024 * 1024))} MB"
    return f"{base}\n\n▫️ *Limit:* {size_label}"
