from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from handlers.admin import is_admin_user
from handlers.keyboards import joined_keyboard
from utils.config import config


async def ensure_channel_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return False

    if is_admin_user(user.id):
        return True

    try:
        membership = await context.bot.get_chat_member(config.REQUIRED_CHANNEL_USERNAME, user.id)
        if membership.status in {"member", "administrator", "creator"}:
            return True
    except Exception:
        pass

    join_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Join Channel", url=config.REQUIRED_CHANNEL_URL)]]
    )
    await message.reply_text(
        "Join Required\n\n"
        "Please join our channel first to use this bot.\n"
        "After joining, tap I Joined to continue.",
        reply_markup=join_keyboard,
    )
    await message.reply_text(
        "Tap the button below after you join.",
        reply_markup=joined_keyboard(),
    )
    return False
