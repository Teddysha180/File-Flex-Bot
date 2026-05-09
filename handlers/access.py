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
        "🛡 *Security Verification*\n\n"
        "To unlock the full potential of *File Flex Pro*, please join our update channel.\n\n"
        "After joining, tap *Check Access* to activate your workspace.",
        reply_markup=join_keyboard,
        parse_mode="Markdown"
    )
    return False


async def handle_join_check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    if await is_channel_member(update, context):
        await query.answer("✅ Access Granted.")
        await query.edit_message_text(
            "🔓 *Verification Successful*\n\nYour File Flex workspace is now active.",
            parse_mode="Markdown"
        )
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Select a tool from the menu to begin your first task.",
            reply_markup=home_keyboard(),
            parse_mode="Markdown"
        )
        return

    await query.answer("⚠️ Membership not found. Please join the channel and try again.", show_alert=True)
