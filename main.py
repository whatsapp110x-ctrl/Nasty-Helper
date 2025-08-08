#!/usr/bin/env python3
"""
Main entry point for the Telegram bot.
This file starts the bot and handles the main execution loop.
Optimized for 24/7 hosting on Render.
"""

import logging
import os
import sys
from bot import TelegramBot
from config import BOT_TOKEN, ADMIN_ID, LOG_CHANNEL_ID, API_ID, API_HASH, MONGODB_URL

# Configure logging for production
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)

logger = logging.getLogger(__name__)

def validate_env_vars():
    """Ensure all required environment variables are set."""
    required_vars = {
        "TELEGRAM_BOT_TOKEN": BOT_TOKEN,
        "ADMIN_ID": ADMIN_ID,
        "LOG_CHANNEL_ID": LOG_CHANNEL_ID,
        "API_ID": API_ID,
        "API_HASH": API_HASH,
        "MONGODB_URL": MONGODB_URL
    }

    missing = [key for key, value in required_vars.items() if not value]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)


def main():
    """Main function to start the bot for 24/7 operation."""
    try:
        validate_env_vars()

        # Create and start the bot
        bot = TelegramBot(BOT_TOKEN)
        logger.info("Starting Telegram bot for 24/7 operation...")
        logger.info("Bot is now running on Render!")

        # Run the bot (this will loop forever)
        bot.run()

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        logger.error("Bot will restart automatically on Render")
        sys.exit(1)


if __name__ == '__main__':
    main()
