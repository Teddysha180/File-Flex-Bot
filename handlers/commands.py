import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from handlers.admin import register_user
from handlers.access import ensure_channel_membership
from handlers.keyboards import home_keyboard
from handlers.messages import HELP_MESSAGE, INTRO_ANIMATION_FRAMES, WELCOME_MESSAGE
from handlers.states import reset_user_state
from utils.database import db


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reset_user_state(context.user_data)
    register_user(update)
    if not await ensure_channel_membership(update, context):
        return
    if update.message:
        intro_message = await update.message.reply_text(
            INTRO_ANIMATION_FRAMES[0],
            parse_mode="Markdown",
        )
        for frame in INTRO_ANIMATION_FRAMES[1:]:
            await asyncio.sleep(0.35)
            await intro_message.edit_text(frame, parse_mode="Markdown")

        await asyncio.sleep(0.25)
        await update.message.reply_text(WELCOME_MESSAGE, reply_markup=home_keyboard())
        await _handle_start_payload(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    register_user(update)
    if not await ensure_channel_membership(update, context):
        return
    if update.message:
        await update.message.reply_text(HELP_MESSAGE, reply_markup=home_keyboard())


async def _handle_start_payload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not context.args:
        return

    payload = context.args[0].strip()
    if not payload.startswith("store_"):
        return

    share_token = payload.removeprefix("store_")
    store = db.get_file_store(share_token)
    if not store:
        await update.message.reply_text(
            "That shared file link is invalid or no longer available.",
            reply_markup=home_keyboard(),
        )
        return

    items = db.get_file_store_items(store["id"])
    if not items:
        await update.message.reply_text(
            "This shared file bundle is empty.",
            reply_markup=home_keyboard(),
        )
        return

    await update.message.reply_text(
        f"Preparing {len(items)} shared file(s) for you...",
        reply_markup=home_keyboard(),
    )

    for item in items:
        if item["file_type"] == "document":
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=item["file_id"],
                caption=item["caption"] or None,
                filename=item["file_name"] or None,
            )
        elif item["file_type"] == "photo":
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=item["file_id"],
                caption=item["caption"] or None,
            )
        elif item["file_type"] == "video":
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=item["file_id"],
                caption=item["caption"] or None,
                filename=item["file_name"] or None,
            )
