#!/usr/bin/env python3
"""
Main entry point for the Telegram bot.
Optimized for 24/7 hosting on Render (Web Service with keep-alive) or Worker.
"""
import logging
import sys

from keep_alive import keep_alive  # must start BEFORE the bot loop
from bot import TelegramBot
from config import BOT_TOKEN, ADMIN_ID, LOG_CHANNEL_ID, API_ID, API_HASH, MONGODB_URL

# Production logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("bot.log")]
)
logger = logging.getLogger(__name__)

def validate_env_vars():
    """
    Ensure all required configuration values are present.
    The keys below should match EXACTLY what your config.py expects.
    """
    required = {
        "BOT_TOKEN": BOT_TOKEN,
        "ADMIN_ID": ADMIN_ID,
        "LOG_CHANNEL_ID": LOG_CHANNEL_ID,
        "API_ID": API_ID,
        "API_HASH": API_HASH,
        "MONGODB_URL": MONGODB_URL,
    }
    missing = [name for name, val in required.items() if val in (None, "", 0)]
    if missing:
        logger.error("Missing required configuration values: %s", ", ".join(missing))
        sys.exit(1)

    # Optional: enforce integer ids if your bot relies on them
    for name in ("ADMIN_ID", "LOG_CHANNEL_ID", "API_ID"):
        val = {"ADMIN_ID": ADMIN_ID, "LOG_CHANNEL_ID": LOG_CHANNEL_ID, "API_ID": API_ID}[name]
        try:
            int(val)  # just validate; keep original type if config handles it
        except Exception:
            logger.error("%s must be an integer; got %r", name, val)
            sys.exit(1)

def main():
    try:
        validate_env_vars()

        # Start the tiny Flask keep-alive **before** blocking bot loop (for Render Web Services)
        # keep_alive() should either:
        #   - run in a background thread and bind to os.environ["PORT"], or
        #   - be a no-op if you're deploying as a Worker.
        keep_alive()

        bot = TelegramBot(BOT_TOKEN)
        logger.info("Starting Telegram bot...")
        bot.run()  # blocking loop

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception("Fatal error starting bot: %s", e)
        # Let Render restart the process
        sys.exit(1)

if __name__ == "__main__":
    main()
