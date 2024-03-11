#!/bin/bash
modal deploy --name nougat-app modal/nougat_app.py
if [ $? -eq 0 ]; then
    echo "App deployed successfully. Starting the bot..."
    python bot/main.py
else
    echo "Could not deploy the app. Exiting..."
fi
