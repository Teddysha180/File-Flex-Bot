import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from handlers.admin import register_user
from handlers.access import ensure_channel_membership
from handlers.keyboards import home_keyboard
from handlers.messages import HELP_MESSAGE, INTRO_ANIMATION_FRAMES, WELCOME_MESSAGE
from handlers.states import reset_user_state


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


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    register_user(update)
    if not await ensure_channel_membership(update, context):
        return
    if update.message:
        await update.message.reply_text(HELP_MESSAGE, reply_markup=home_keyboard())
