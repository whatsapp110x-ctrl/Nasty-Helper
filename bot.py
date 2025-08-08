"""
Simple Telegram Bot using direct API calls for website redirection.
"""

import logging
import requests
import json
import time
import os
from config import ADMIN_ID, LOG_CHANNEL_ID, API_ID, API_HASH, MONGODB_URL

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token):
        """Initialize the bot with the given token."""
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.running = False
        # Message mapping: admin's message_id -> user's chat_id
        self.message_link = {}
        # User mapping: username -> chat_id for direct replies
        self.user_mapping = {}
        # All users who have interacted with the bot
        self.all_users = set()
        # Track user last activity time (user_id -> timestamp)
        self.user_last_activity = {}
        # Dynamic URL storage
        self.urls = {
            "URL 1": "https://nextbomb.in/",
            "URL 2": "https://www.callbomberz.in/",
            "URL 3": "https://callbomber.in/"
        }
        self.load_urls()
        
    def send_message(self, chat_id, text, reply_markup=None):
        """Send a message to a chat."""
        url = f"{self.api_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        
        try:
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def get_updates(self, offset=None):
        """Get updates from Telegram."""
        url = f"{self.api_url}/getUpdates"
        params = {'timeout': 30}
        if offset:
            params['offset'] = offset
            
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return None
    
    def handle_start_command(self, chat_id):
        """Handle the /start command."""
        message = "Your Bot is Alive Dude 😒"
        self.send_message(chat_id, message)
    
    def handle_urls_command(self, chat_id):
        """Handle the /urls command."""
        if not self.urls:
            self.send_message(chat_id, "❌ No URLs available. Admin can add URLs using /change.")
            return
            
        message = "🔗 Choose your URL option:"
        
        keyboard = {"inline_keyboard": []}
        for name, url in self.urls.items():
            keyboard["inline_keyboard"].append([{"text": name, "url": url}])
        
        self.send_message(chat_id, message, keyboard)
    
    def handle_ask_command(self, chat_id, args, user_info):
        """Handle the /ask command - users ask questions to admin."""
        if not args:
            self.send_message(chat_id, "Usage: /ask your question here")
            return
        
        question = " ".join(args)
        user_id = user_info.get('id', 'Unknown')
        username = user_info.get('username', 'NoUsername')
        first_name = user_info.get('first_name', '')
        
        # Send question to admin
        admin_message = f"{first_name} (@{username}) : {question}"
        
        # Send to admin and get message ID for mapping
        result = self.send_message(ADMIN_ID, admin_message)
        if result and result.get('ok'):
            admin_msg_id = result['result']['message_id']
            self.message_link[admin_msg_id] = chat_id
        
        # Only send confirmation to regular users, not to admin
        if chat_id != ADMIN_ID:
            self.send_message(chat_id, "✅ Your question has been sent to the admin.")
    
    def handle_reply_command(self, chat_id, args, reply_to_message=None):
        """Handle the /reply command - admin replies to users."""
        if chat_id != ADMIN_ID:
            self.send_message(chat_id, "❌ You are not authorized to reply.")
            return
        
        target_id = None
        reply_text = None
        
        # CASE 1: Reply to any message (including forwarded messages)
        if reply_to_message:
            replied_msg_id = reply_to_message.get('message_id')
            reply_text = " ".join(args) if args else "Admin replied to your message."
            
            # First check if it's from our ask system
            if replied_msg_id in self.message_link:
                target_id = self.message_link[replied_msg_id]
            # Check if it's a forwarded message
            elif reply_to_message.get('forward_from'):
                target_id = reply_to_message['forward_from']['id']
            # Check if it's forwarded from a chat
            elif reply_to_message.get('forward_from_chat'):
                target_id = reply_to_message['forward_from_chat']['id']
            # Check if it's a regular message from someone
            elif reply_to_message.get('from'):
                target_id = reply_to_message['from']['id']
        
        # CASE 2: Direct reply with userid, @username, or username
        elif args and len(args) >= 2:
            first_arg = args[0]
            reply_text = " ".join(args[1:])
            
            # Check if it's a userid (digits only)
            if first_arg.isdigit():
                target_id = int(first_arg)
            
            # Check if it's @username format
            elif first_arg.startswith('@'):
                username = first_arg[1:]  # Remove the @
                target_id = self.user_mapping.get(username)
                if not target_id:
                    self.send_message(chat_id, f"❌ Username @{username} not found. User must have used the bot first.")
                    return
            
            # Check if it's username without @
            else:
                username = first_arg
                target_id = self.user_mapping.get(username)
                if not target_id:
                    self.send_message(chat_id, f"❌ Username {username} not found. User must have used the bot first.")
                    return
        
        if not target_id or not reply_text:
            self.send_message(chat_id, 
                "⚠️ Usage:\n"
                "/reply <userid> <message>\n"
                "/reply @username <message>\n"
                "/reply username <message>\n"
                "Or reply to a question message with /reply <message>")
            return
        
        # Send reply to user
        user_message = f"💬 Reply from admin:\n\n{reply_text}"
        result = self.send_message(target_id, user_message)
        
        if result and result.get('ok'):
            self.send_message(chat_id, "✅ Reply sent.")
        else:
            self.send_message(chat_id, "❌ Failed to send reply. User may have blocked the bot.")
    
    def handle_user_command(self, chat_id, user_info, reply_to_message=None, chat_info=None):
        """Handle the /user command - get complete identification info."""
        # If admin replies to someone, show their info
        if reply_to_message and chat_id == ADMIN_ID:
            info_text = "👤 Message Info:\n\n"
            
            # Check if it's a forwarded message
            if 'forward_from' in reply_to_message:
                # Forwarded from a user
                forward_user = reply_to_message['forward_from']
                username = forward_user.get('username', 'NoUsername')
                user_id = forward_user.get('id', 'Unknown')
                first_name = forward_user.get('first_name', 'Unknown')
                
                info_text += (
                    f"📤 Original Sender (User):\n"
                    f"• Name: {first_name}\n"
                    f"• Username: @{username}\n"
                    f"• User ID: {user_id}\n\n"
                )
                
            elif 'forward_from_chat' in reply_to_message:
                # Forwarded from a channel/group
                forward_chat = reply_to_message['forward_from_chat']
                chat_title = forward_chat.get('title', 'Unknown')
                forward_chat_id = forward_chat.get('id', 'Unknown')
                chat_type = forward_chat.get('type', 'unknown')
                forward_username = forward_chat.get('username', 'NoUsername')
                
                info_text += (
                    f"📤 Original Source ({chat_type.title()}):\n"
                    f"• Title: {chat_title}\n"
                    f"• Username: @{forward_username}\n"
                    f"• Chat ID: {forward_chat_id}\n\n"
                )
                
            elif 'forward_sender_name' in reply_to_message:
                # Forwarded with privacy settings (name only)
                sender_name = reply_to_message['forward_sender_name']
                info_text += f"📤 Original Sender: {sender_name} (Privacy Protected)\n\n"
            
            # Current message sender info
            target_user = reply_to_message.get('from', {})
            username = target_user.get('username', 'NoUsername')
            user_id = target_user.get('id', 'Unknown')
            first_name = target_user.get('first_name', 'Unknown')
            target_chat = reply_to_message.get('chat', {})
            target_chat_id = target_chat.get('id', 'Unknown')
            chat_type = target_chat.get('type', 'unknown')
            
            info_text += f"👤 Message Forwarder:\n• Name: {first_name}\n• Username: @{username}\n• User ID: {user_id}\n• Chat ID: {target_chat_id}"
            
            # Add group info if it's a group
            if chat_type in ['group', 'supergroup']:
                group_title = target_chat.get('title', 'Unknown Group')
                info_text += f"\n• Group ID: {target_chat_id}\n• Group Name: {group_title}"
                
        else:
            # Show own info
            username = user_info.get('username', 'NoUsername')
            user_id = user_info.get('id', 'Unknown')
            first_name = user_info.get('first_name', 'Unknown')
            
            # Determine chat type and show appropriate info
            if chat_id < 0:  # Negative IDs are groups/channels
                if str(chat_id).startswith('-100'):  # Supergroup/channel
                    chat_type_text = "Supergroup/Channel"
                else:
                    chat_type_text = "Group"
                    
                info_text = (
                    f"👤 Your Info:\n"
                    f"• Name: {first_name}\n"
                    f"• Username: @{username}\n"
                    f"• User ID: {user_id}\n"
                    f"• Chat ID: {chat_id}\n"
                    f"• Group ID: {chat_id}\n"
                    f"• Chat Type: {chat_type_text}"
                )
            else:  # Private chat
                info_text = (
                    f"👤 Your Info:\n"
                    f"• Name: {first_name}\n"
                    f"• Username: @{username}\n"
                    f"• User ID: {user_id}\n"
                    f"• Chat ID: {chat_id}\n"
                    f"• Chat Type: Private"
                )
        
        self.send_message(chat_id, info_text)
    
    def handle_broadcast_command(self, chat_id, args):
        """Handle the /broadcast command - admin only."""
        if chat_id != ADMIN_ID:
            self.send_message(chat_id, "❌ You are not authorized to broadcast.")
            return
        
        if not args:
            self.send_message(chat_id, "Usage: /broadcast your message here")
            return
        
        broadcast_message = " ".join(args)
        success_count = 0
        failed_count = 0
        current_time = time.time()
        active_threshold = 24 * 60 * 60  # 24 hours in seconds
        
        # Send to users who have been active in the last 24 hours
        active_users = []
        for user_id in self.all_users:
            if user_id != ADMIN_ID:
                last_activity = self.user_last_activity.get(user_id, 0)
                if current_time - last_activity <= active_threshold:
                    active_users.append(user_id)
                    result = self.send_message(user_id, f"📢 Broadcast:\n\n{broadcast_message}")
                    if result and result.get('ok'):
                        success_count += 1
                    else:
                        failed_count += 1
        
        # Send summary to admin
        total_users = len(self.all_users) - 1  # Exclude admin
        active_count = len(active_users)
        summary = (
            f"✅ Broadcast completed!\n"
            f"• Active users (24h): {active_count}\n"
            f"• Total users: {total_users}\n"
            f"• Sent to: {success_count} users\n"
            f"• Failed: {failed_count} users"
        )
        self.send_message(chat_id, summary)
    
    def handle_text_message(self, chat_id, text):
        """Handle regular text messages."""
        # Don't send any response to regular text messages
        pass
    
    def process_update(self, update):
        """Process a single update."""
        try:
            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                
                if 'text' in message:
                    text = message['text']
                    user_info = message.get('from', {})
                    reply_to_message = message.get('reply_to_message')
                    
                    # Store user mapping for username replies and track all users
                    username = user_info.get('username')
                    if username:
                        self.user_mapping[username] = chat_id
                    
                    # Track all users who interact with the bot and their activity time
                    self.all_users.add(chat_id)
                    self.user_last_activity[chat_id] = time.time()
                    
                    # Handle commands
                    if text.startswith('/'):
                        parts = text.split()
                        command = parts[0].lower()
                        args = parts[1:] if len(parts) > 1 else []
                        
                        if command == '/start':
                            self.handle_start_command(chat_id)
                        elif command == '/urls':
                            self.handle_urls_command(chat_id)
                        elif command == '/change':
                            self.handle_change_command(chat_id, args)
                        elif command == '/remove':
                            self.handle_remove_command(chat_id, args)
                        elif command == '/ask':
                            self.handle_ask_command(chat_id, args, user_info)
                        elif command == '/reply':
                            self.handle_reply_command(chat_id, args, reply_to_message)
                        elif command == '/user':
                            self.handle_user_command(chat_id, user_info, reply_to_message, message.get('chat'))
                        elif command == '/broadcast':
                            self.handle_broadcast_command(chat_id, args)
                        else:
                            # Don't respond to unknown commands
                            pass
                    else:
                        # Handle regular text
                        self.handle_text_message(chat_id, text)
                        
                    logger.info(f"Processed message from chat {chat_id}: {text}")
                
            # Handle callback queries (button clicks)
            elif 'callback_query' in update:
                callback_query = update['callback_query']
                
                # Answer callback query
                self.answer_callback_query(callback_query['id'])
                logger.info(f"Processed callback query: {callback_query.get('data', 'N/A')}")
                    
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    def run(self):
        """Start the bot and begin polling for updates - 24/7 operation."""
        logger.info("Starting Telegram bot for 24/7 operation...")
        logger.info("Bot is ready to receive messages!")
        self.running = True
        offset = None
        
        while self.running:
            try:
                # Get updates with longer timeout for better efficiency
                result = self.get_updates(offset)
                
                if result and result.get('ok'):
                    updates = result.get('result', [])
                    
                    for update in updates:
                        self.process_update(update)
                        offset = update['update_id'] + 1
                        
                else:
                    if result:
                        logger.error(f"Error getting updates: {result}")
                    else:
                        logger.error("Failed to get updates - network issue")
                    time.sleep(10)  # Wait longer on errors
                    
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                self.running = False
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                logger.info("Restarting bot loop in 10 seconds...")
                time.sleep(10)  # Wait before retrying
    
    def answer_callback_query(self, callback_query_id):
        """Answer a callback query."""
        url = f"{self.api_url}/answerCallbackQuery"
        data = {'callback_query_id': callback_query_id}
        
        try:
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            logger.error(f"Error answering callback query: {e}")
            return None
    
    def load_urls(self):
        """Load URLs from file."""
        try:
            if os.path.exists('urls.txt'):
                with open('urls.txt', 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.urls = {}
                        for line in content.split('\n'):
                            if '|' in line:
                                name, url = line.split('|', 1)
                                self.urls[name.strip()] = url.strip()
        except Exception as e:
            logger.error(f"Error loading URLs: {e}")
    
    def save_urls(self):
        """Save URLs to file."""
        try:
            with open('urls.txt', 'w', encoding='utf-8') as f:
                for name, url in self.urls.items():
                    f.write(f"{name}|{url}\n")
        except Exception as e:
            logger.error(f"Error saving URLs: {e}")
    
    def handle_change_command(self, chat_id, args):
        """Handle the /change command - admin only."""
        if chat_id != ADMIN_ID:
            self.send_message(chat_id, "❌ You are not authorized to change URLs.")
            return
        
        if len(args) < 2:
            self.send_message(chat_id, 
                "📝 Usage: /change <name> <url>\n\n"
                "Example: /change URL1 https://example.com\n\n"
                f"Current URLs ({len(self.urls)}):")
            
            if self.urls:
                url_list = "\n".join([f"• {name}: {url}" for name, url in self.urls.items()])
                self.send_message(chat_id, url_list)
            return
        
        name = args[0]
        url = " ".join(args[1:])
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.urls[name] = url
        self.save_urls()
        
        self.send_message(chat_id, f"✅ URL updated!\n\n📝 {name}: {url}")
    
    def handle_remove_command(self, chat_id, args):
        """Handle the /remove command - admin only."""
        if chat_id != ADMIN_ID:
            self.send_message(chat_id, "❌ You are not authorized to remove URLs.")
            return
        
        if not args:
            if not self.urls:
                self.send_message(chat_id, "❌ No URLs available to remove.")
                return
                
            message = f"🗑️ Available URLs to remove ({len(self.urls)}):" + "\n\n"
            for i, (name, url) in enumerate(self.urls.items(), 1):
                message += f"{i}. {name}: {url}\n"
            message += "\n📝 Usage: /remove <name>\nExample: /remove URL1"
            
            self.send_message(chat_id, message)
            return
        
        name = args[0]
        
        if name in self.urls:
            removed_url = self.urls[name]
            del self.urls[name]
            self.save_urls()
            self.send_message(chat_id, f"✅ URL removed!\n\n🗑️ {name}: {removed_url}")
        else:
            self.send_message(chat_id, f"❌ URL '{name}' not found.\n\nUse /remove to see available URLs.")
    
    def stop(self):
        """Stop the bot."""
        self.running = False