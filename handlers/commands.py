from telegram import Update
from telegram.ext import ContextTypes

from handlers.keyboards import home_keyboard
from handlers.messages import HELP_MESSAGE, WELCOME_MESSAGE
from handlers.states import reset_user_state


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reset_user_state(context.user_data)
    if update.message:
        await update.message.reply_text(WELCOME_MESSAGE, reply_markup=home_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(HELP_MESSAGE, reply_markup=home_keyboard())
