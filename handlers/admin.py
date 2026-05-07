import time
from datetime import datetime

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
    STATE_KEY_STORE_ID,
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
            await update.message.reply_text("You don't have access to the admin workspace.")
        return

    reset_user_state(context.user_data)
    if update.message:
        await update.message.reply_text(
            _dashboard_message(context),
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
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
        )
        return True

    if text == BTN_ADMIN_STATUS:
        reset_user_state(context.user_data)
        await update.message.reply_text(
            _bot_status_message(context),
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
        )
        return True

    if text == BTN_ADMIN_ADMINS:
        reset_user_state(context.user_data)
        await update.message.reply_text(
            _admins_message(),
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
        )
        return True

    if text == BTN_ADMIN_STORES:
        reset_user_state(context.user_data)
        await update.message.reply_text(
            await _stores_message(context),
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
        )
        return True

    if text == BTN_ADMIN_BROADCAST:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_CONTENT
        await update.message.reply_text(
            "Broadcast Composer\n\n"
            "Step 1 of 3\n"
            "Send the content for the post now.\n\n"
            "Supported formats:\n"
            "• Text message\n"
            "• Photo\n"
            "• Video\n"
            "• Document\n\n"
            "If you send media, you can include the caption right away.",
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
        )
        return True

    if text == BTN_ADMIN_CREATE_STORE:
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_STORE_FILES
        context.user_data[STATE_KEY_STORE_FILES] = []
        await update.message.reply_text(
            "Store Creator\n\n"
            "Send one or many files now.\n\n"
            "Supported formats:\n"
            "- Documents\n"
            "- Photos\n"
            "- Videos\n\n"
            "When you finish uploading, tap `Done Creating` and I'll generate a share link.",
            reply_markup=store_creation_keyboard(is_main_admin_user(user_id)),
            parse_mode="Markdown",
        )
        return True

    if text == BTN_ADMIN_ADD_ADMIN and is_main_admin_user(user_id):
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_ADD_ADMIN
        await update.message.reply_text(
            "Send the Telegram user ID you want to promote to admin.",
            reply_markup=admin_keyboard(True),
        )
        return True

    if text == BTN_ADMIN_REMOVE_ADMIN and is_main_admin_user(user_id):
        reset_user_state(context.user_data)
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_REMOVE_ADMIN
        await update.message.reply_text(
            "Send the Telegram user ID you want to remove from the admin team.",
            reply_markup=admin_keyboard(True),
        )
        return True

    if text == BTN_ADMIN_CANCEL:
        reset_user_state(context.user_data)
        await update.message.reply_text(
            "Admin action canceled. You're back in the admin workspace.",
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
        )
        return True

    if text == BTN_ADMIN_FINISH_STORE:
        if admin_step != ADMIN_STEP_STORE_FILES:
            await update.message.reply_text(
                "Start `Create Store` first, then upload files before finishing.",
                parse_mode="Markdown",
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
                f"Admin added: `{admin_id}`",
                reply_markup=admin_keyboard(True),
                parse_mode="Markdown",
            )
        except ValueError:
            await update.message.reply_text("Send a valid numeric Telegram user ID.")
        finally:
            reset_user_state(context.user_data)
        return True

    if admin_step == ADMIN_STEP_REMOVE_ADMIN and is_main_admin_user(user_id):
        try:
            admin_id = int(text)
            removed = db.remove_admin(admin_id)
            message = f"Admin removed: `{admin_id}`" if removed else "That admin account wasn't found or can't be removed."
            await update.message.reply_text(
                message,
                reply_markup=admin_keyboard(True),
                parse_mode="Markdown",
            )
        except ValueError:
            await update.message.reply_text("Send a valid numeric Telegram user ID.")
        finally:
            reset_user_state(context.user_data)
        return True

    if admin_step == ADMIN_STEP_BROADCAST_CONTENT:
        context.user_data[STATE_KEY_BROADCAST_TYPE] = "text"
        context.user_data[STATE_KEY_BROADCAST_TEXT] = text
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_BUTTON
        await update.message.reply_text(
            "Step 2 of 3\n"
            "Send the call-to-action button in this format:\n"
            "`Button Text | https://example.com`\n\n"
            "Or send `skip` to publish without a button.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
        )
        return True

    if admin_step == ADMIN_STEP_BROADCAST_CAPTION:
        context.user_data[STATE_KEY_BROADCAST_TEXT] = "" if text.lower() == "skip" else text
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_BUTTON
        await update.message.reply_text(
            "Step 2 of 3\n"
            "Send the call-to-action button in this format:\n"
            "`Button Text | https://example.com`\n\n"
            "Or send `skip` to publish without a button.",
            parse_mode="Markdown",
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
                    "Use this button format:\n`Button Text | https://example.com`\n\nOr send `skip`.",
                    parse_mode="Markdown",
                )
                return True
            button_text, button_url = [part.strip() for part in text.split("|", 1)]
            if not button_text or not button_url.startswith(("http://", "https://")):
                await update.message.reply_text(
                    "That button format doesn't look valid. Use:\n`Button Text | https://example.com`",
                    parse_mode="Markdown",
                )
                return True
            context.user_data[STATE_KEY_BROADCAST_BUTTON_TEXT] = button_text
            context.user_data[STATE_KEY_BROADCAST_BUTTON_URL] = button_url

        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_CONFIRM
        await _send_broadcast_preview(update, context)
        await update.message.reply_text(
            "Step 3 of 3\nPreview ready.\n\nTap `Send Broadcast` to deliver it to all users, or `Cancel Action` to discard it.",
            parse_mode="Markdown",
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
            f"Stored photo #{len(context.user_data.get(STATE_KEY_STORE_FILES, []))}. Send more files or tap `Done Creating`.",
            parse_mode="Markdown",
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
            "Step 2 of 3\n"
            "Send the call-to-action button in this format:\n"
            "`Button Text | https://example.com`\n\n"
            "Or send `skip` to publish without a button.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id)),
        )
    else:
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_CAPTION
        await update.message.reply_text(
            "Step 2 of 3\nSend the caption for this post, or send `skip`.",
            parse_mode="Markdown",
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
            f"Stored video #{len(context.user_data.get(STATE_KEY_STORE_FILES, []))}. Send more files or tap `Done Creating`.",
            parse_mode="Markdown",
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
            "Step 2 of 3\n"
            "Send the call-to-action button in this format:\n"
            "`Button Text | https://example.com`\n\n"
            "Or send `skip` to publish without a button.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id)),
        )
    else:
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_CAPTION
        await update.message.reply_text(
            "Step 2 of 3\nSend the caption for this post, or send `skip`.",
            parse_mode="Markdown",
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
            f"Stored file #{len(context.user_data.get(STATE_KEY_STORE_FILES, []))}. Send more files or tap `Done Creating`.",
            parse_mode="Markdown",
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
            "Step 2 of 3\n"
            "Send the call-to-action button in this format:\n"
            "`Button Text | https://example.com`\n\n"
            "Or send `skip` to publish without a button.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id)),
        )
    else:
        context.user_data[STATE_KEY_ADMIN_STEP] = ADMIN_STEP_BROADCAST_CAPTION
        await update.message.reply_text(
            "Step 2 of 3\nSend the caption for this post, or send `skip`.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id)),
        )
    return True


def _dashboard_message(context: ContextTypes.DEFAULT_TYPE) -> str:
    stats = db.get_dashboard_stats()
    storage = db.get_storage_details()
    uptime = _format_uptime(context.application.bot_data.get("started_at"))

    return (
        "Admin Workspace\n\n"
        f"Total users: {stats['total_users']}\n"
        f"New today: {stats['new_users_today']}\n"
        f"New this week: {stats['new_users_week']}\n"
        f"Total jobs: {stats['total_jobs']}\n"
        f"Jobs today: {stats['jobs_today']}\n"
        f"Jobs this week: {stats['jobs_week']}\n"
        "Stored bundles: channel-based links\n"
        f"Admin accounts: {stats['total_admins']}\n"
        f"Share storage: Telegram channel {config.STORAGE_CHANNEL_ID}\n"
        f"Storage: {storage['backend']} ({storage['persistent']})\n"
        f"Uptime: {uptime}\n"
        "Health endpoint: /health\n\n"
        "Choose an action below to review status, manage admins, prepare a broadcast, or create a shared file bundle."
    )


def _bot_status_message(context: ContextTypes.DEFAULT_TYPE) -> str:
    stats = db.get_dashboard_stats()
    storage = db.get_storage_details()
    uptime = _format_uptime(context.application.bot_data.get("started_at"))
    return (
        "System Status\n\n"
        f"Users tracked: {stats['total_users']}\n"
        f"Admin accounts: {stats['total_admins']}\n"
        "Stored bundles: channel-based links\n"
        f"Share storage: Telegram channel {config.STORAGE_CHANNEL_ID}\n"
        f"Storage backend: {storage['backend']}\n"
        f"Storage location: {storage['location']}\n"
        f"Persistent storage: {storage['persistent']}\n"
        f"Total jobs: {stats['total_jobs']}\n"
        f"Uptime: {uptime}\n"
        "Health endpoint: /health\n"
        "Deployment: active"
    )


def _admins_message() -> str:
    admins = db.list_admins()
    if not admins:
        return "No admin accounts found."

    lines = ["Admin Team", ""]
    for admin in admins:
        label = admin["first_name"] or admin["username"] or str(admin["user_id"])
        role = "Main Admin" if admin["is_main_admin"] else "Admin"
        lines.append(f"• {label} - {role} - {admin['user_id']}")
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
        await update.message.reply_text("No users are available for broadcast.")
        reset_user_state(context.user_data)
        return

    broadcast_type = context.user_data.get(STATE_KEY_BROADCAST_TYPE)
    text = context.user_data.get(STATE_KEY_BROADCAST_TEXT) or ""
    file_id = context.user_data.get(STATE_KEY_BROADCAST_FILE_ID)
    markup = _broadcast_markup(context)

    sent_count = 0
    failed_count = 0

    await update.message.reply_text(f"Broadcast started for {len(user_ids)} users.")

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
        f"Broadcast complete.\n\nDelivered: {sent_count}\nFailed: {failed_count}",
        reply_markup=admin_keyboard(is_main_admin_user(update.effective_user.id if update.effective_user else None)),
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
            reply_markup=store_creation_keyboard(is_main_admin_user(user_id)),
        )
        return

    if not config.STORAGE_CHANNEL_ID:
        await update.message.reply_text(
            "Storage channel is not configured yet. Set `STORAGE_CHANNEL_ID` first.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
        )
        return

    sent_message_ids: list[int] = []
    for item in files:
        sent_message = await _send_store_item_to_channel(context, item)
        sent_message_ids.append(sent_message.message_id)

    if not sent_message_ids:
        await update.message.reply_text(
            "I couldn't save those files to the storage channel.",
            reply_markup=admin_keyboard(is_main_admin_user(user_id)),
        )
        return

    start_message_id = min(sent_message_ids)
    end_message_id = max(sent_message_ids)

    bot_username = context.bot.username or (await context.bot.get_me()).username
    share_link = (
        f"https://t.me/{bot_username}?start=store_{start_message_id}_{end_message_id}"
        if bot_username
        else f"/start store_{start_message_id}_{end_message_id}"
    )

    total_files = len(files)
    reset_user_state(context.user_data)
    await update.message.reply_text(
        "Store created successfully.\n\n"
        f"Files saved: {total_files}\n"
        f"Channel messages: {start_message_id} to {end_message_id}\n"
        f"Share this link with users:\n{share_link}\n\n"
        "When a user opens the link and starts the bot, the saved files will be sent automatically.",
        reply_markup=admin_keyboard(is_main_admin_user(user_id)),
    )


async def _stores_message(context: ContextTypes.DEFAULT_TYPE) -> str:
    return (
        "Stored Links\n\n"
        "This bot now saves shared files in the Telegram storage channel instead of the local database.\n\n"
        "New bundles will survive redeploys, but the bot does not keep an index of past links.\n"
        "Please save each generated share link after creation."
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
