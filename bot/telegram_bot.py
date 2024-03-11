from __future__ import annotations

import logging
import io

from telegram import Update
from telegram import BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    Application,
    ContextTypes,
)

from utils import error_handler, split_into_chunks, is_allowed

from PIL import Image

import modal


class TelegramBot:
    def __init__(self, config: dict):
        self.config = config
        self.commands = [
            BotCommand(command="start", description="start command"),
            BotCommand(command="help", description="help command"),
        ]

    async def post_init(self, application: Application) -> None:
        await application.bot.set_my_commands(self.commands)

    async def help(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not await is_allowed(self.config, update):
            return
        
        commands_description = [
            f"/{command.command} - {command.description}" for command in self.commands
        ]
        help_text = "\n".join(commands_description)

        await update.message.reply_text(help_text, disable_web_page_preview=True)

    async def ocr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await is_allowed(self.config, update):
            return
        
        image = update.message.effective_attachment[-1]
        media_file = await context.bot.get_file(image.file_id)
        bytes_jpg = io.BytesIO(await media_file.download_as_bytearray())

        # convert jpg from telegram to png as required by Nougat
        image_jpg = Image.open(bytes_jpg)
        bytes_png = io.BytesIO()
        image_jpg.save(bytes_png, format="PNG")
        bytes_png.seek(0)

        cls = modal.Cls.lookup("nougat-app", "Model")
        model = cls()
        response = model.generate.remote(bytes_png.getvalue(), max_new_tokens=1000)

        chunks = split_into_chunks(response)
        for chunk in chunks:
            await update.message.reply_text(chunk)

    def run(self):
        """
        Runs the bot indefinitely until the user presses Ctrl+C
        """
        application = (
            ApplicationBuilder()
            .token(self.config["token"])
            .post_init(self.post_init)
            .concurrent_updates(True)
            .build()
        )

        application.add_handler(CommandHandler("start", self.help))
        application.add_handler(CommandHandler("help", self.help))

        application.add_handler(
            MessageHandler(filters.PHOTO | filters.Document.IMAGE, self.ocr)
        )

        application.add_error_handler(error_handler)

        application.run_polling()
