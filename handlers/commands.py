import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from handlers.admin import register_user
from handlers.keyboards import home_keyboard
from handlers.messages import HELP_MESSAGE, INTRO_MESSAGE, WELCOME_MESSAGE
from handlers.states import reset_user_state


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reset_user_state(context.user_data)
    register_user(update)
    if update.message:
        await update.message.reply_text(INTRO_MESSAGE)
        await asyncio.sleep(0.6)
        await update.message.reply_text(WELCOME_MESSAGE, reply_markup=home_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    register_user(update)
    if update.message:
        await update.message.reply_text(HELP_MESSAGE, reply_markup=home_keyboard())
