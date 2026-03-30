from telegram import Update
from telegram.ext import ContextTypes

from telegram import InputFile

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
            "✨ *File Flex Control Center*\n\nChoose a tool suite below to process your files.",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:category:archives":
        await query.edit_message_text(
            "📦 *Archive Tools*\n\nExtract ZIP archives or create a ZIP bundle from multiple files.",
            reply_markup=archives_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:category:images":
        await query.edit_message_text(
            "🖼 *Image Tools*\n\nEnhance, resize, watermark, compress, or read text from images.",
            reply_markup=image_tools_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:category:documents":
        await query.edit_message_text(
            "📄 *PDF Tools*\n\nWork with PDF files, merge or split them, rename documents, or open the full conversion suite.",
            reply_markup=documents_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:category:video":
        await query.edit_message_text(
            "🎬 *Video Tools*\n\nConvert video clips to GIFs or compress them for faster sharing.",
            reply_markup=video_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:stats":
        if update.effective_user:
            stats = db.get_user_stats(update.effective_user.id)
            if stats:
                stats_text = (
                    f"📊 *Your Statistics*\n\n"
                    f"📁 Total files processed: {stats['total_files']}\n"
                    f"💾 Storage saved: {stats['storage_saved'] / (1024*1024):.1f} MB\n"
                    f"📈 Files this week: {stats['files_this_week']}\n"
                    f"📅 Member since: {stats['member_since']}\n\n"
                    f"Keep using File Flex to save more storage!"
                )
            else:
                stats_text = "No processing history yet. Send your first file to get started!"
            
            await query.edit_message_text(
                stats_text,
                reply_markup=settings_keyboard(),
                parse_mode="Markdown"
            )
        return

    if data == "menu:settings":
        await query.edit_message_text(
            "⚙️ *Help & Settings*\n\nView your statistics, recent activity, and guidance for supported tools.",
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
                history_text = "📋 *Recent Activity* (Last 5 operations)\n\n"
                for idx, record in enumerate(history, 1):
                    action, input_file, output_file, in_size, out_size, proc_time, timestamp = record
                    history_text += f"{idx}. {action.upper()}\n"
                    history_text += f"   📝 {input_file[:30]}\n"
                    history_text += f"   ⏱️ {proc_time:.1f}s\n\n"
            else:
                history_text = "No processing history yet."
            
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
            "📦 Send a `.zip` file and I'll extract its contents for you.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown",
        )
        return

    if data == "menu:create_zip":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CREATE_ZIP
        context.user_data[STATE_KEY_PENDING_FILES] = []
        await query.edit_message_text(
            "🗃️ Send files or photos you want bundled into one ZIP. Tap Finish when ready.",
            reply_markup=queue_actions_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:compress_image":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_COMPRESS_IMAGE
        await query.edit_message_text(
            "🗜️ Send a JPG or PNG image and I'll return a smaller compressed version.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:resize_image":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_RESIZE_IMAGE
        context.user_data[STATE_KEY_PENDING_INPUT] = "width"
        await query.edit_message_text(
            "📐 Send the image. I'll resize it to standard dimensions (800x600).",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:enhance_image":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_ENHANCE_IMAGE
        await query.edit_message_text(
            "✨ Send an image and I'll enhance its quality (brightness, contrast, sharpness).",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:watermark_image":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_WATERMARK_IMAGE
        await query.edit_message_text(
            "💧 Send an image and I'll add a watermark to it.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:ocr_image":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_OCR_IMAGE
        await query.edit_message_text(
            "🔤 Send an image with text and I'll extract all the text from it.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:convert_file":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await query.edit_message_text(
            "🔄 *Convert Files*\n\nChoose a professional conversion workflow below.",
            reply_markup=conversion_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:convert:to_pdf_menu":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await query.edit_message_text(
            "📄 *Convert To PDF*\n\nAvailable under this section:\n• JPG -> PDF\n• Word -> PDF\n• PowerPoint -> PDF\n• Excel -> PDF\n• HTML -> PDF",
            reply_markup=convert_to_pdf_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:convert:from_pdf_menu":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await query.edit_message_text(
            "📤 *Convert From PDF*\n\nAvailable under this section:\n• PDF -> JPG\n• PDF -> Word\n• PDF -> PowerPoint\n• PDF -> Excel\n• PDF -> PDF/A",
            reply_markup=convert_from_pdf_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:convert:image_formats_menu":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_CONVERT_FILE
        await query.edit_message_text(
            "🖼 *Image Format Conversion*\n\nSwitch between common image formats.",
            reply_markup=image_format_conversion_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:merge_pdf":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_MERGE_PDF
        context.user_data[STATE_KEY_PENDING_FILES] = []
        await query.edit_message_text(
            "🧩 Send PDF files one by one. When done, tap Finish and I'll merge them.",
            reply_markup=queue_actions_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:split_pdf":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_SPLIT_PDF
        context.user_data[STATE_KEY_PENDING_INPUT] = "file"
        await query.edit_message_text(
            "✂️ Send a PDF file, then I'll ask for the page range you want to extract.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:rename_file":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_RENAME_FILE
        await query.edit_message_text(
            "📝 Send any file, then I'll ask for the new name.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:video_to_gif":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_VIDEO_TO_GIF
        await query.edit_message_text(
            "🎬 Send a video file and I'll convert it to an animated GIF.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "menu:compress_video":
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ACTION] = ACTION_COMPRESS_VIDEO
        context.user_data[STATE_KEY_PENDING_INPUT] = "quality"
        await query.edit_message_text(
            "🎥 Send a video file and I'll compress it (medium quality).",
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
                "No files have been added yet. Send at least one file first.",
                reply_markup=queue_actions_keyboard(),
            )
            return

        try:
            if action == ACTION_MERGE_PDF:
                output_path = merge_pdf_files(pending_files)
                caption = "✅ Your merged PDF is ready."
            elif action == ACTION_CREATE_ZIP:
                output_path = create_zip_from_files(pending_files)
                caption = "✅ Your ZIP archive is ready."
            else:
                await query.edit_message_text(
                    "That action is no longer active. Choose a tool below.",
                    reply_markup=main_menu_keyboard(),
                )
                reset_user_state(context.user_data)
                return

            with output_path.open("rb") as file_handle:
                await query.message.reply_document(
                    document=InputFile(file_handle, filename=output_path.name),
                    caption=caption,
                    reply_markup=main_menu_keyboard(),
                )
            reset_user_state(context.user_data)
            await query.edit_message_text(
                "Done! Choose another tool below for your next task.",
                reply_markup=main_menu_keyboard(),
                parse_mode="Markdown"
            )
        except ValueError as exc:
            await query.edit_message_text(
                f"❌ {exc}\n\nPlease send valid files and try again.",
                reply_markup=queue_actions_keyboard(),
                parse_mode="Markdown"
            )


def _conversion_prompt(conversion_target: str) -> str:
    prompt_map = {
        "jpg_to_png": "Send a JPG image as a file or photo.",
        "png_to_jpg": "Send a PNG file.",
        "image_to_pdf": "Send an image file and I’ll convert it to PDF.",
        "jpg_to_pdf": "Send a JPG image and I’ll convert it to PDF.",
        "word_to_pdf": "Send a Word document (`.doc` or `.docx`).",
        "powerpoint_to_pdf": "Send a PowerPoint file (`.ppt` or `.pptx`).",
        "excel_to_pdf": "Send an Excel file (`.xls` or `.xlsx`).",
        "html_to_pdf": "Send an HTML file (`.html` or `.htm`).",
        "pdf_to_jpg": "Send a PDF file and I’ll turn its pages into JPG images.",
        "pdf_to_word": "Send a PDF file and I’ll convert it to Word.",
        "pdf_to_powerpoint": "Send a PDF file and I’ll build a PowerPoint from its pages.",
        "pdf_to_excel": "Send a PDF file and I’ll extract its text into Excel sheets.",
        "pdf_to_pdfa": "Send a PDF file and I’ll convert it to PDF/A if the required system tool is available.",
    }
    return prompt_map.get(conversion_target, "Send the file you want to convert.")
