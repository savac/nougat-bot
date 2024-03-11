# Nougat-bot

This repo contains code to deploy Facebook's [Nougat](https://github.com/facebookresearch/nougat) model as a Modal function. In addition, there is a Telegram bot that takes an image sent to the chat and passes it to the deployed model for OCR. The results are returned in the chat.

## Installation

1. Create a Telegram bot using the [@BotFather](https://t.me/botfather)
2. Create a `.env` file based on `.env.example` and add the necessary token and ids.
3. Run or inspect the following script to deploy model in Modal and start Telegram bot.
```
./deploy.sh
```

## Usage

Send photos of text on which to run the Nougat OCR to your Telegram bot.


## Acknowledgments

Parts of the Telegram bot code were taken from the excellent [chatgpt-telegram-bot](https://github.com/n3d1117/chatgpt-telegram-bot).
