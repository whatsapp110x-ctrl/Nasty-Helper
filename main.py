import logging
import asyncio
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient

# Import config values
from config import (
    BOT_TOKEN, ADMIN_ID, MAIN_WEBSITE, COMMAND_DESCRIPTIONS,
    SUCCESS_MESSAGES, ERROR_MESSAGES, POLL_INTERVAL, TIMEOUT,
    MONGODB_URL
)
from keep_alive import keep_alive  # For Render/Repl.it uptime

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Connect to MongoDB
mongo_client = MongoClient(MONGODB_URL)
db = mongo_client["telegram_bot"]
users_col = db["users"]

# Store user in DB if new
def save_user(user):
    if not users_col.find_one({"user_id": user.id}):
        users_col.insert_one({
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "date_added": datetime.utcnow()
        })

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    await update.message.reply_text("👋 Welcome! Use /help to see my commands.")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "\n".join([f"/{cmd} - {desc}" for cmd, desc in COMMAND_DESCRIPTIONS.items()])
    await update.message.reply_text(f"📖 Available Commands:\n\n{help_text}")

# /website command
async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🌐 Visit: {MAIN_WEBSITE}")

# /info command
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🆔 User ID: {user.id}\n"
        f"👤 Username: @{user.username if user.username else 'N/A'}\n"
        f"📅 First Name: {user.first_name}"
    )

# Admin-only /broadcast
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("🚫 Not authorized.")

    if not context.args:
        return await update.message.reply_text("Usage: /broadcast <message>")

    message = " ".join(context.args)
    sent_count = 0

    for user in users_col.find():
        try:
            await context.bot.send_message(chat_id=user["user_id"], text=message)
            sent_count += 1
        except Exception as e:
            logging.warning(f"Failed to send to {user['user_id']}: {e}")

    await update.message.reply_text(f"✅ Broadcast sent to {sent_count} users.")

# Main bot function
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).read_timeout(TIMEOUT).write_timeout(TIMEOUT).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("website", website))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("broadcast", broadcast))

    # Update BotFather menu
    await app.bot.set_my_commands([
        BotCommand(cmd, desc) for cmd, desc in COMMAND_DESCRIPTIONS.items()
    ])

    logging.info(SUCCESS_MESSAGES["bot_started"])
    await app.run_polling(poll_interval=POLL_INTERVAL)

if __name__ == "__main__":
    keep_alive()  # Start web server for uptime pings
    asyncio.run(main())
