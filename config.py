"""
Configuration settings for the Telegram bot.
Contains constants and configuration values.
"""

import os

# Bot configuration
BOT_NAME = "Link Sharing Bot"
BOT_VERSION = "1.0.0"

# Website configuration
MAIN_WEBSITE = "https://nextbomb.in"

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Bot token (should be set as environment variable)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8372107408:AAEdnBUYJLmDhOKycjQHsvN30bmKjfCejcY')

# Admin/Owner configuration
ADMIN_ID = int(os.getenv('ADMIN_ID', '7052170756'))
OWNER_ID = ADMIN_ID  # Alias for admin ID

# Log channel configuration
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', '-1002319385484'))

# Telegram API configuration (for advanced features)
API_ID = int(os.getenv('API_ID', '29756601'))
API_HASH = os.getenv('API_HASH', '967c4656b8dd6a475b7786e3287ba2d3')

# Database configuration
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb+srv://whatsapp110x:whatsapp110x@cluster0.dh2ygtt.mongodb.net/sample_mflix?retryWrites=true&w=majority&appName=Cluster0')

# Render deployment configuration
PORT = int(os.getenv('PORT', 8000))
HOST = '0.0.0.0'

# Bot settings
POLL_INTERVAL = 1.0
TIMEOUT = 20

# Error messages
ERROR_MESSAGES = {
    'no_token': 'Bot token not provided. Please set TELEGRAM_BOT_TOKEN environment variable.',
    'general_error': 'Sorry, something went wrong. Please try again later.',
    'unknown_command': "I'm not sure how to help with that. Try /help to see available commands!"
}

# Success messages
SUCCESS_MESSAGES = {
    'bot_started': 'Bot started successfully!',
    'user_welcomed': 'User welcomed successfully!'
}

# Command descriptions
COMMAND_DESCRIPTIONS = {
    'start': 'Start the bot and see welcome message',
    'help': 'Show all available commands',
    'website': 'Get the main website link',
    'info': 'Get information about this bot'
}
