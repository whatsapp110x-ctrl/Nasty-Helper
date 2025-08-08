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

# Bot token (MUST be set as environment variable)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Bot token not provided. Please set TELEGRAM_BOT_TOKEN environment variable.")

# Admin/Owner configuration
try:
    ADMIN_ID = int(os.getenv('ADMIN_ID'))
except (TypeError, ValueError):
    raise ValueError("ADMIN_ID environment variable is missing or invalid.")
OWNER_ID = ADMIN_ID  # Alias for admin ID

# Log channel configuration
try:
    LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID'))
except (TypeError, ValueError):
    raise ValueError("LOG_CHANNEL_ID environment variable is missing or invalid.")

# Telegram API configuration (for advanced features)
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
if not API_ID or not API_HASH:
    raise ValueError("API_ID or API_HASH environment variables are missing.")
try:
    API_ID = int(API_ID)
except ValueError:
    raise ValueError("API_ID must be an integer.")

# Database configuration
MONGODB_URL = os.getenv('MONGODB_URL')
if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is missing.")

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
