import os
import requests
from dotenv import load_dotenv
import json
from datetime import datetime

def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    return os.getenv('BOT_TOKEN')

def get_bot_updates(bot_token):
    """Retrieve recent updates from the bot."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching updates: {e}")
        return None

def parse_updates(updates):
    """Parse and format the updates for easy reading."""
    if not updates or not updates.get('ok'):
        return "No updates found or error in response"

    result = []
    for update in updates['result']:
        timestamp = datetime.fromtimestamp(update['message']['date'])
        chat_id = update['message']['chat']['id']
        username = update['message']['chat'].get('username', 'Unknown')
        text = update['message'].get('text', 'No text')
        
        result.append(
            f"Time: {timestamp}\n"
            f"Chat ID: {chat_id}\n"
            f"Username: {username}\n"
            f"Message: {text}\n"
            f"{'-' * 50}"
        )
    
    return "\n".join(result) if result else "No recent messages found"

def main():
    print("Telegram Bot Update Checker")
    print("=" * 50)
    print("\nThis script will help you get the correct chat ID for your bot.")
    print("\nInstructions:")
    print("1. Make sure you've already created your bot with @BotFather")
    print("2. Start a conversation with your bot on Telegram")
    print("3. Send a test message to your bot")
    print("4. This script will show recent interactions and their chat IDs\n")

    bot_token = load_environment()
    if not bot_token:
        print("Error: BOT_TOKEN not found in environment variables")
        print("Please make sure you have set it in your .env file")
        return

    print("Fetching recent updates...\n")
    updates = get_bot_updates(bot_token)
    
    if updates:
        print(parse_updates(updates))
        print("\nNOTE: Use the Chat ID shown above for your bot configuration")
        print("The Chat ID can be positive (for personal chats) or negative (for groups/channels)")
    else:
        print("\nNo updates received. Please:")
        print("1. Check your bot token is correct")
        print("2. Send a message to your bot on Telegram")
        print("3. Run this script again")

if __name__ == "__main__":
    main()

import os
import requests
from dotenv import load_dotenv
import json
from datetime import datetime

def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    return os.getenv('BOT_TOKEN')

def get_bot_updates(bot_token):
    """Retrieve recent updates from the bot."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching updates: {e}")
        return None

def parse_updates(updates):
    """Parse and format the updates for easy reading."""
    if not updates or not updates.get('ok'):
        return "No updates found or error in response"

    result = []
    for update in updates['result']:
        timestamp = datetime.fromtimestamp(update['message']['date'])
        chat_id = update['message']['chat']['id']
        username = update['message']['chat'].get('username', 'Unknown')
        text = update['message'].get('text', 'No text')
        
        result.append(
            f"Time: {timestamp}\n"
            f"Chat ID: {chat_id}\n"
            f"Username: {username}\n"
            f"Message: {text}\n"
            f"{'-' * 50}"
        )
    
    return "\n".join(result) if result else "No recent messages found"

def main():
    print("Telegram Bot Update Checker")
    print("=" * 50)
    print("\nThis script will help you get the correct chat ID for your bot.")
    print("\nInstructions:")
    print("1. Make sure you've already created your bot with @BotFather")
    print("2. Start a conversation with your bot on Telegram")
    print("3. Send a test message to your bot")
    print("4. This script will show recent interactions and their chat IDs\n")

    bot_token = load_environment()
    if not bot_token:
        print("Error: BOT_TOKEN not found in environment variables")
        print("Please make sure you have set it in your .env file")
        return

    print("Fetching recent updates...\n")
    updates = get_bot_updates(bot_token)
    
    if updates:
        print(parse_updates(updates))
        print("\nNOTE: Use the Chat ID shown above for your bot configuration")
        print("The Chat ID can be positive (for personal chats) or negative (for groups/channels)")
    else:
        print("\nNo updates received. Please:")
        print("1. Check your bot token is correct")
        print("2. Send a message to your bot on Telegram")
        print("3. Run this script again")

if __name__ == "__main__":
    main()

