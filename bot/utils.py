import logging
from telegram import Update
from telegram.ext import ContextTypes

async def error_handler(_: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles errors in the telegram-python-bot library.
    """
    logging.error(f'Exception while handling an update: {context.error}')


def split_into_chunks(text: str, chunk_size: int = 4096) -> list[str]:
    """
    Splits a string into chunks of a given size.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


async def is_allowed(config, update: Update) -> bool:
    """
    Checks if the user is allowed to use the bot.
    """
    if config['allowed_user_ids'] == '*':
        return True

    user_id = update.message.from_user.id
    allowed_user_ids = config['allowed_user_ids'].split(',')
    # Check if user is allowed
    if str(user_id) in allowed_user_ids:
        return True
    
    logging.warn(f'User {user_id} is not allowed')
