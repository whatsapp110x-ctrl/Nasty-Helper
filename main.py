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
from config import BOT_TOKEN

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

def main():
    """Main function to start the bot for 24/7 operation."""
    try:
        # Get bot token from configuration (which checks environment variables with fallback)
        bot_token = BOT_TOKEN
        
        if not bot_token:
            logger.error("Bot token not available!")
            logger.error("Please set TELEGRAM_BOT_TOKEN environment variable or update config.py")
            sys.exit(1)
        
        # Create and start the bot
        bot = TelegramBot(bot_token)
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
