import asyncio
import contextlib
import logging
import time
import telegram.error

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from handlers.keyboards import (
    BTN_ADMIN_ADD_ADMIN,
    BTN_ADMIN_ADMINS,
    BTN_ADMIN_BROADCAST,
    BTN_ADMIN_CANCEL,
    BTN_ADMIN_CREATE_STORE,
    BTN_ADMIN_DASHBOARD,
    BTN_ADMIN_FINISH_STORE,
    BTN_ADMIN_POST,
    BTN_ADMIN_REMOVE_ADMIN,
    BTN_ADMIN_STATUS,
    BTN_ADMIN_STORES,
    admin_keyboard,
    broadcast_confirm_keyboard,
    store_creation_keyboard,
)
from handlers.states import (
    STATE_KEY_ADMIN_STEP,
    STATE_KEY_BROADCAST_BUTTON_TEXT,
    STATE_KEY_BROADCAST_BUTTON_URL,
    STATE_KEY_BROADCAST_FILE_ID,
    STATE_KEY_BROADCAST_FILE_NAME,
    STATE_KEY_BROADCAST_TEXT,
    STATE_KEY_BROADCAST_TYPE,
    STATE_KEY_STORE_FILES,
    reset_user_state,
)
from utils.config import config
from utils.database import db


ADMIN_STEP_ADD_ADMIN = "admin_add_admin"
ADMIN_STEP_REMOVE_ADMIN = "admin_remove_admin"
ADMIN_STEP_BROADCAST_CONTENT = "broadcast_content"
ADMIN_STEP_BROADCAST_CAPTION = "broadcast_caption"
ADMIN_STEP_BROADCAST_BUTTON = "broadcast_button"
ADMIN_STEP_BROADCAST_CONFIRM = "broadcast_confirm"
ADMIN_STEP_STORE_FILES = "store_files"

logger = logging.getLogger(__name__)


def register_user(update: Update) -> None:
    user = update.effective_user
    if not user:
        return
    db.get_or_create_user(
        user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        last_name=user.last_name or "",
    )


def is_admin_user(user_id: int | None) -> bool:
    return bool(user_id) and db.is_admin(user_id)


def is_main_admin_user(user_id: int | None) -> bool:
    return bool(user_id) and user_id == config.MAIN_ADMIN_ID


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    register_user(update)
    user_id = update.effective_user.id if update.effective_user else None
    if not is_admin_user(user_id):
        if update.message:
            await update.message.reply_text("**Access Denied**: You do not have administrative privileges.", parse_mode="Markdown")
        return

    reset_user_state(context.user_data)
    if update.message:
        await update.message.reply_text(
            _dashboard_message(context), # parse_mode is set in _dashboard_message
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
            parse_mode="HTML"
        )


async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.message or not update.message.text:
        return False

    register_user(update)
    user_id = update.effective_user.id if update.effective_user else None
    if not is_admin_user(user_id):
        return False

    text = update.message.text.strip()
    admin_step = context.user_data.get(STATE_KEY_ADMIN_STEP)

    if text == BTN_ADMIN_DASHBOARD:
        reset_user_state(context.user_data)
        await update.message.reply_text(
            _dashboard_message(context),
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
            parse_mode="HTML"
        )
        return True

    if text == BTN_ADMIN_STATUS:
        reset_user_state(context.user_data)
        await update.message.reply_text(
            _bot_status_message(context),
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
            parse_mode="HTML"
        )
        return True

    if text == BTN_ADMIN_ADMINS:
        reset_user_state(context.user_data)
        await update.message.reply_text(
            _admins_message(),
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
            parse_mode="HTML"
        )
        return True

    if text == BTN_ADMIN_STORES:
        reset_user_state(context.user_data)
        await update.message.reply_text(
            await _stores_message(context),
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
            parse_mode="HTML"
        )
        return True

    if text == BTN_ADMIN_BROADCAST:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_CONTENT
        await update.message.reply_text(
            "⬛ <b>BROADCAST STUDIO</b>\n\n"
            "Step 1 of 3\n"
            "Send the message or media for this broadcast.\n\n"
            "<b>Supported formats:</b>\n"
            "• Text\n"
            "• Photo\n"
            "• Video\n"
            "• Document\n\n"
            "If you send media, you can include the caption immediately.",
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
            parse_mode="HTML"
        )
        return True

    if text == BTN_ADMIN_CREATE_STORE:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_STORE_FILES
        context.user_data[STATE_KEY_STORE_FILES] = []
        await update.message.reply_text(
            "⬛ <b>SHARE LINK CREATOR</b>\n\n"
            "Upload the files (Docs, Photos, or Videos) you want to bundle. "
            "When finished, tap Create Link to generate a professional shareable URL.",
            reply_markup=store_creation_keyboard(is_main_admin_user(user_id)),
            parse_mode="HTML",
        )
        return True

    if text == BTN_ADMIN_ADD_ADMIN and is_main_admin_user(user_id):
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_ADD_ADMIN
        await update.message.reply_text(
            "👤 <b>PROMOTE ADMIN</b>: Please send the Telegram User ID of the new administrator.",
            reply_markup=admin_keyboard(True),
            parse_mode="HTML"
        )
        return True

    if text == BTN_ADMIN_REMOVE_ADMIN and is_main_admin_user(user_id):
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_REMOVE_ADMIN
        await update.message.reply_text(
            "🗑 <b>REVOKE ADMIN</b>: Please send the Telegram User ID you wish to remove.",
            reply_markup=admin_keyboard(True),
            parse_mode="HTML"
        )
        return True

    if text == BTN_ADMIN_CANCEL:
        reset_user_state(context.user_data)
        await update.message.reply_text(
            "Canceled. You are back in the admin workspace.",
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
            parse_mode="HTML"
        )
        return True

    if text == BTN_ADMIN_FINISH_STORE:
        if admin_step != ADMIN_STEP_STORE_FILES:
            await update.message.reply_text(
                "Start `New Share Link` first, then upload files before creating the link.",
                parse_mode="HTML",
                reply_markup=admin_keyboard(is_main_admin_user(user_id)),
            )
            return True

        await _finish_store_creation(update, context)
        return True

    if admin_step == ADMIN_STEP_ADD_ADMIN and is_main_admin_user(user_id):
        try:
            admin_id = int(text)
            db.add_admin(admin_id, user_id)
            await update.message.reply_text(
                f"✅ <b>SUCCESS</b>: Admin {admin_id} has been added.",
                reply_markup=admin_keyboard(True),
                parse_mode="HTML",
            )
        except ValueError:
            await update.message.reply_text("<b>Error</b>: Please provide a valid numeric User ID.", parse_mode="HTML")
        finally:
            reset_user_state(context.user_data)
        return True

    if admin_step == ADMIN_STEP_REMOVE_ADMIN and is_main_admin_user(user_id):
        try:
            admin_id = int(text)
            removed = db.remove_admin(admin_id)
            message = f"✅ <b>SUCCESS</b>: Admin {admin_id} removed." if removed else "❌ <b>ERROR</b>: Admin not found or cannot be removed."
            await update.message.reply_text(
                message,
                reply_markup=admin_keyboard(True),
                parse_mode="HTML",
            )
        except ValueError:
            await update.message.reply_text("<b>Error</b>: Please provide a valid numeric User ID.", parse_mode="HTML")
        finally:
            reset_user_state(context.user_data)
        return True

    if admin_step == ADMIN_STEP_BROADCAST_CONTENT:
        context.user_data[STATE_KEY_BROADCAST_TYPE] = "text"
        context.user_data[STATE_KEY_BROADCAST_TEXT] = text
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_BUTTON
        await update.message.reply_text(
            "🔗 <b>STEP 2/3: CTA BUTTON</b>\n\n"
            "Format: Label | https://link.com\n"
            "Send skip if no button is needed.",
            parse_mode="HTML",
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
        )
        return True

    if admin_step == ADMIN_STEP_BROADCAST_CAPTION:
        context.user_data[STATE_KEY_BROADCAST_TEXT] = "" if text.lower() == "skip" else text
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_BUTTON
        await update.message.reply_text(
            "🔗 <b>STEP 2/3: CTA BUTTON</b>\n\n"
            "Format: Label | https://link.com\n"
            "Send skip if no button is needed.",
            parse_mode="HTML",
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
        )
        return True

    if admin_step == ADMIN_STEP_BROADCAST_BUTTON:
        if text.lower() == "skip":
            context.user_data[STATE_KEY_BROADCAST_BUTTON_TEXT] = None
            context.user_data[STATE_KEY_BROADCAST_BUTTON_URL] = None
        else:
            if "|" not in text:
                await update.message.reply_text(
                    "<b>Error</b>: Use this format: Button Text | https://example.com\n\nOr send skip.",
                    parse_mode="HTML",
                )
                return True
            button_text, button_url = [part.strip() for part in text.split("|", 1)]
            if not button_text or not button_url.startswith(("http://", "https://")):
                await update.message.reply_text(
                    "<b>Error</b>: Invalid format. Use: Button Text | https://example.com",
                    parse_mode="HTML",
                )
                return True
            context.user_data[STATE_KEY_BROADCAST_BUTTON_TEXT] = button_text
            context.user_data[STATE_KEY_BROADCAST_BUTTON_URL] = button_url

        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_CONFIRM
        await _send_broadcast_preview(update, context)
        await update.message.reply_text(
            "✨ <b>STEP 3/3: PREVIEW READY</b>\n\n"
            "Review the post above. Select Publish to send to all users or Cancel to discard.",
            parse_mode="HTML",
            reply_markup=broadcast_confirm_keyboard(),
        )
        return True

    if text == BTN_ADMIN_POST and admin_step == ADMIN_STEP_BROADCAST_CONFIRM:
        await _post_broadcast(update, context)
        return True

    return False


async def handle_admin_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.message or not update.message.photo:
        return False
    if not is_admin_user(update.effective_user.id if update.effective_user else None):
        return False

    if context.user_data.get(STATE_KEY_ADMIN_STEP) == ADMIN_STEP_STORE_FILES:
        photo = update.message.photo[-1]
        _append_store_item(
            context,
            file_type="photo",
            file_id=photo.file_id,
            caption=update.message.caption or "",
        )
        await update.message.reply_text(
            f"📸 <b>PHOTO #{len(context.user_data.get(STATE_KEY_STORE_FILES, []))}</b> added.\n"
            "Send more files or tap Create Link.",
            parse_mode="HTML", # Already HTML
            reply_markup=store_creation_keyboard(is_main_admin_user(update.effective_user.id)),
        )
        return True

    if context.user_data.get(STATE_KEY_ADMIN_STEP) != ADMIN_STEP_BROADCAST_CONTENT:
        return False

    photo = update.message.photo[-1]
    context.user_data[STATE_KEY_BROADCAST_TYPE] = "photo"
    context.user_data[STATE_KEY_BROADCAST_FILE_ID] = photo.file_id
    context.user_data[STATE_KEY_BROADCAST_TEXT] = update.message.caption or ""

    if update.message.caption:
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_BUTTON
        await update.message.reply_text(
            "🔗 <b>STEP 2/3: CTA BUTTON</b>\n\n"
            "Format: Label | https://link.com\n"
            "Send skip if no button is needed.",
            parse_mode="HTML",
            reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id)),
        )
    else:
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_CAPTION
        await update.message.reply_text(
            "📝 <b>STEP 2/3: CAPTION</b>\n\nSend a caption for this media or skip.",
            parse_mode="HTML",
            reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id)),
        )
    return True


async def handle_admin_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.message or not update.message.video:
        return False
    if not is_admin_user(update.effective_user.id if update.effective_user else None):
        return False

    if context.user_data.get(STATE_KEY_ADMIN_STEP) == ADMIN_STEP_STORE_FILES:
        video = update.message.video
        _append_store_item(
            context,
            file_type="video",
            file_id=video.file_id,
            file_name=video.file_name or "video.mp4",
            caption=update.message.caption or "",
        )
        await update.message.reply_text(
            f"🎬 <b>VIDEO #{len(context.user_data.get(STATE_KEY_STORE_FILES, []))}</b> added.\n"
            "Send more files or tap Create Link.",
            parse_mode="HTML", # Already HTML
            reply_markup=store_creation_keyboard(is_main_admin_user(update.effective_user.id)),
        )
        return True

    if context.user_data.get(STATE_KEY_ADMIN_STEP) != ADMIN_STEP_BROADCAST_CONTENT:
        return False

    video = update.message.video
    context.user_data[STATE_KEY_BROADCAST_TYPE] = "video"
    context.user_data[STATE_KEY_BROADCAST_FILE_ID] = video.file_id
    context.user_data[STATE_KEY_BROADCAST_TEXT] = update.message.caption or ""

    if update.message.caption:
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_BUTTON
        await update.message.reply_text(
            "🔗 <b>STEP 2/3: CTA BUTTON</b>\n\n"
            "Format: Label | https://link.com\n"
            "Send skip if no button is needed.",
            parse_mode="HTML",
            reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id)),
        )
    else:
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_CAPTION
        await update.message.reply_text(
            "📝 <b>STEP 2/3: CAPTION</b>\n\nSend a caption for this media or skip.",
            parse_mode="HTML",
            reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id)),
        )
    return True


async def handle_admin_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.message or not update.message.document:
        return False
    if not is_admin_user(update.effective_user.id if update.effective_user else None):
        return False

    if context.user_data.get(STATE_KEY_ADMIN_STEP) == ADMIN_STEP_STORE_FILES:
        document = update.message.document
        _append_store_item(
            context,
            file_type="document",
            file_id=document.file_id,
            file_name=document.file_name or "stored_file",
            caption=update.message.caption or "",
        )
        await update.message.reply_text(
            f"📄 <b>FILE #{len(context.user_data.get(STATE_KEY_STORE_FILES, []))}</b> added.\n"
            "Send more files or tap Create Link.",
            parse_mode="HTML", # Already HTML
            reply_markup=store_creation_keyboard(is_main_admin_user(update.effective_user.id)),
        )
        return True

    if context.user_data.get(STATE_KEY_ADMIN_STEP) != ADMIN_STEP_BROADCAST_CONTENT:
        return False

    document = update.message.document
    context.user_data[STATE_KEY_BROADCAST_TYPE] = "document"
    context.user_data[STATE_KEY_BROADCAST_FILE_ID] = document.file_id
    context.user_data[STATE_KEY_BROADCAST_FILE_NAME] = document.file_name or "broadcast_file"
    context.user_data[STATE_KEY_BROADCAST_TEXT] = update.message.caption or ""

    if update.message.caption:
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_BUTTON
        await update.message.reply_text(
            "🔗 <b>STEP 2/3: CTA BUTTON</b>\n\n"
            "Format: Label | https://link.com\n"
            "Send skip if no button is needed.",
            parse_mode="HTML",
            reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id)),
        )
    else:
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_CAPTION
        await update.message.reply_text(
            "📝 <b>STEP 2/3: CAPTION</b>\n\nSend a caption for this media or skip.",
            parse_mode="HTML",
            reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id)),
        )
    return True


def _dashboard_message(context: ContextTypes.DEFAULT_TYPE) -> str:
    stats = db.get_dashboard_stats()
    storage = db.get_storage_details()
    uptime = _format_uptime(context.application.bot_data.get("started_at"))

    return (
        "⬛ <b>FILE FLEX BLACK</b>\n\n"
        f"👥 Users: {stats['total_users']} (+{stats['new_users_today']} today)\n"
        f"🛠 Total Jobs: {stats['total_jobs']} ({stats['jobs_today']} today)\n"
        f"👤 Admins: {stats['total_admins']}\n\n"
        "⬛ <b>INFRASTRUCTURE</b>\n"
        f"• Backend: {storage['backend']}\n"
        f"• Persistent: {storage['persistent']}\n"
        f"• Uptime: {uptime}\n"
        f"• Storage Channel: {config.STORAGE_CHANNEL_ID}\n"
        "• Status: Healthy 🟢\n\n"
        "Use the controls below to manage the bot, publish broadcasts, and generate professional file share links."
    )


def _bot_status_message(context: ContextTypes.DEFAULT_TYPE) -> str:
    stats = db.get_dashboard_stats()
    storage = db.get_storage_details()
    uptime = _format_uptime(context.application.bot_data.get("started_at"))
    return (
        "📊 <b>SYSTEM DIAGNOSTICS</b>\n\n"
        f"• Tracked Users: {stats['total_users']}\n"
        f"• Admin Staff: {stats['total_admins']}\n"
        f"• Job History: {stats['total_jobs']}\n\n"
        "⬛ <b>STORAGE NODE</b>\n"
        f"• Engine: {storage['backend']}\n"
        f"• Persistent: {storage['persistent']}\n"
        f"• Path: {storage['location']}\n\n"
        "⬛ <b>RUNTIME</b>\n"
        f"• Uptime: {uptime}\n"
        "• API Status: Operational ✅"
    )


def _admins_message() -> str:
    admins = db.list_admins()
    if not admins:
        return "ℹ️ No administrative accounts found."

    lines = ["👥 <b>ADMINISTRATIVE TEAM</b>", ""]
    for admin in admins:
        label = admin["first_name"] or admin["username"] or str(admin["user_id"])
        role = "⭐ Main" if admin["is_main_admin"] else "👤 Admin"
        lines.append(f"• {label} | {role} | {admin['user_id']}")
    return "\n".join(lines)


def _broadcast_markup(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup | None:
    button_text = context.user_data.get(STATE_KEY_BROADCAST_BUTTON_TEXT)
    button_url = context.user_data.get(STATE_KEY_BROADCAST_BUTTON_URL)
    if not button_text or not button_url:
        return None
    return InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=button_url)]])


async def _send_broadcast_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    broadcast_type = context.user_data.get(STATE_KEY_BROADCAST_TYPE)
    text = context.user_data.get(STATE_KEY_BROADCAST_TEXT) or ""
    markup = _broadcast_markup(context)

    if broadcast_type == "text":
        await update.message.reply_text(text or "Preview", reply_markup=markup)
        return

    file_id = context.user_data.get(STATE_KEY_BROADCAST_FILE_ID)
    if broadcast_type == "photo":
        await update.message.reply_photo(photo=file_id, caption=text or None, reply_markup=markup)
        return
    if broadcast_type == "video":
        await update.message.reply_video(video=file_id, caption=text or None, reply_markup=markup)
        return
    if broadcast_type == "document":
        await update.message.reply_document(
            document=file_id,
            caption=text or None,
            filename=context.user_data.get(STATE_KEY_BROADCAST_FILE_NAME),
            reply_markup=markup,
        )


async def _post_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    user_ids = db.get_all_user_ids()
    if not user_ids:
        await update.message.reply_text("❌ NO USERS AVAILABLE TO RECEIVE BROADCAST.")
        reset_user_state(context.user_data)
        return

    broadcast_type = context.user_data.get(STATE_KEY_BROADCAST_TYPE)
    text = context.user_data.get(STATE_KEY_BROADCAST_TEXT) or ""
    file_id = context.user_data.get(STATE_KEY_BROADCAST_FILE_ID)
    markup = _broadcast_markup(context)

    sent_count = 0
    failed_count = 0

    await update.message.reply_text(f"🚀 Broadcast started for {len(user_ids)} users...", parse_mode="HTML")

    for target_user_id in user_ids:
        try:
            if broadcast_type == "text":
                await context.bot.send_message(target_user_id, text or " ", reply_markup=markup)
            elif broadcast_type == "photo":
                await context.bot.send_photo(target_user_id, photo=file_id, caption=text or None, reply_markup=markup)
            elif broadcast_type == "video":
                await context.bot.send_video(target_user_id, video=file_id, caption=text or None, reply_markup=markup)
            elif broadcast_type == "document":
                await context.bot.send_document(
                    target_user_id,
                    document=file_id,
                    caption=text or None,
                    filename=context.user_data.get(STATE_KEY_BROADCAST_FILE_NAME),
                    reply_markup=markup,
                )
            sent_count += 1
        except Exception:
            failed_count += 1

    reset_user_state(context.user_data)
    await update.message.reply_text(
        f"✅ <b>BROADCAST COMPLETE</b>\n\n• Delivered: {sent_count}\n• Failed: {failed_count}",
        reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id if update.effective_user else None)),
        parse_mode="HTML"
    )


def _format_uptime(started_at: float | None) -> str:
    if not started_at:
        return "Unknown"
    total_seconds = int(time.time() - started_at)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def _append_store_item(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    file_type: str,
    file_id: str,
    file_name: str = "",
    caption: str = "",
) -> None:
    items = context.user_data.setdefault(STATE_KEY_STORE_FILES, [])
    items.append(
        {
            "file_type": file_type,
            "file_id": file_id,
            "file_name": file_name,
            "caption": caption,
        }
    )


async def _finish_store_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    files = context.user_data.get(STATE_KEY_STORE_FILES, [])
    user_id = update.effective_user.id if update.effective_user else None
    if not files or not user_id:
        await update.message.reply_text(
            "No files have been added yet. Send at least one file first.",
            reply_markup=store_creation_keyboard(is_main_admin_user(user_id))
        )
        return

    if not config.STORAGE_CHANNEL_ID:
        await update.message.reply_text(
            "Storage channel is not configured yet. Set `STORAGE_CHANNEL_ID` first.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(is_main_admin_user(user_id))
        )
        return

    progress_message = await update.message.reply_text(
        f"⏳ <b>Starting batch upload for {len(files)} files...</b>",
        parse_mode="HTML"
    )

    sent_message_ids: list[int] = []
    for i, item in enumerate(files, 1):
        try:
            # Update progress every 3 files to keep the user informed and connection alive
            if i % 3 == 0 or i == len(files):
                try:
                    await progress_message.edit_text(
                        f"⏳ <b>Uploading {i}/{len(files)} files...</b>\nPlease wait, do not send new commands.",
                        parse_mode="HTML" # Already HTML
                    )
                except Exception:
                    pass

            sent_message = await _send_store_item_to_channel(context, item)
            if sent_message:
                sent_message_ids.append(sent_message.message_id)
            
            # Throttling starts at the limit (20 files) to speed up smaller batches 
            # while remaining safe for large ones.
            if i >= 20:
                await asyncio.sleep(0.4)
            
        except telegram.error.RetryAfter as e:
            # If throttled, wait the exact amount of time Telegram demands
            await asyncio.sleep(e.retry_after + 1)
            sent_message = await _send_store_item_to_channel(context, item)
            if sent_message:
                sent_message_ids.append(sent_message.message_id)
        except Exception as e:
            logger.error(f"Error during store creation batch upload: {e}")

    if not sent_message_ids:
        with contextlib.suppress(Exception):
            await progress_message.delete()
        await update.message.reply_text(
            "❌ Could not save files to storage channel.",
            reply_markup=admin_keyboard(is_main_admin_user(user_id))
        )
        return

    start_message_id = min(sent_message_ids)
    end_message_id = max(sent_message_ids)

    try:
        bot_username = context.bot.username or (await context.bot.get_me()).username
    except Exception:
        bot_username = None

    share_link = (
        f"https://t.me/{bot_username}?start=store_{start_message_id}_{end_message_id}"
        if bot_username
        else f"/start store_{start_message_id}_{end_message_id}"
    )

    total_files = len(files)
    reset_user_state(context.user_data)
    with contextlib.suppress(Exception):
        await progress_message.delete()
    await update.message.reply_text(
        f"⬛ <b>SHARE LINK GENERATED</b>\n\n"
        f"📁 Files: {total_files}\n"
        f"🔗 Link: <a href='{share_link}'>Open in Bot</a>\n\n"
        f"<code>{share_link}</code>\n\n"
        "Deliver files automatically to any user who clicks the button.",
        reply_markup=admin_keyboard(is_main_admin_user(user_id)),
        parse_mode="HTML"
    )


async def _stores_message(context: ContextTypes.DEFAULT_TYPE) -> str:
    return (
        "⬛ <b>SHARING GUIDE</b>\n\n"
        "Files are stored securely in your dedicated Telegram channel, ensuring links remain permanent across bot updates.\n\n"
        "💡 Save your generated links; the bot does not currently keep a searchable index of old share URLs."
    )


async def _send_store_item_to_channel(
    context: ContextTypes.DEFAULT_TYPE,
    item: dict,
):
    if item["file_type"] == "document":
        return await context.bot.send_document(
            chat_id=config.STORAGE_CHANNEL_ID,
            document=item["file_id"],
            caption=item.get("caption") or None,
            filename=item.get("file_name") or None,
        )

    if item["file_type"] == "photo":
        return await context.bot.send_photo(
            chat_id=config.STORAGE_CHANNEL_ID,
            photo=item["file_id"],
            caption=item.get("caption") or None,
        )

    if item["file_type"] == "video":
        return await context.bot.send_video(
            chat_id=config.STORAGE_CHANNEL_ID,
            video=item["file_id"],
            caption=item.get("caption") or None,
            filename=item.get("file_name") or None,
        )

    raise ValueError("Unsupported store item type")
