from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from handlers.admin import is_admin_user
from handlers.keyboards import home_keyboard
from utils.config import config

JOIN_CHECK_CALLBACK = "join_check"


async def is_channel_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user:
        return False

    if is_admin_user(user.id):
        return True

    try:
        membership = await context.bot.get_chat_member(config.REQUIRED_CHANNEL_USERNAME, user.id)
        return membership.status in {"member", "administrator", "creator"}
    except Exception:
        return False


async def ensure_channel_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    message = update.effective_message

    if not message:
        return False

    if await is_channel_member(update, context):
        return True

    join_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Join Channel", url=config.REQUIRED_CHANNEL_URL)],
            [InlineKeyboardButton("Check Access", callback_data=JOIN_CHECK_CALLBACK)],
        ]
    )
    await message.reply_text(
        "ACCESS CHECK\n\n"
        "Join our required channel first to unlock FILE FLEX BLACK.\n"
        "Once you are in, tap Check Access and I will open the workspace.",
        reply_markup=join_keyboard,
    )
    return False


async def handle_join_check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    if await is_channel_member(update, context):
        await query.answer("Membership confirmed.")
        await query.edit_message_text(
            "Access confirmed.\n\nYour FILE FLEX BLACK workspace is ready.",
        )
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Choose a tool from the menu below to get started.",
            reply_markup=home_keyboard(),
        )
        return

    await query.answer("Channel membership is not visible yet. Join first, then try again.", show_alert=True)
