from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from handlers.admin import is_admin_user
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
        "Access required\n\n"
        "Join our channel first to use File Flex.\n\n"
        "Channel: arts_of_drawings\n"
        "After joining, come back and send /start again.",
        reply_markup=join_keyboard,
    )
    return False
