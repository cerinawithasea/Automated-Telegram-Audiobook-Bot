import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Get bot token from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')

def get_bot_info():
    # Telegram Bot API endpoint for getMe
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    
    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        data = response.json()
        
        if data["ok"]:
            bot_info = data["result"]
            print("\nBot Information:")
            print(f"Username: @{bot_info['username']}")
            print(f"Bot ID: {bot_info['id']}")
            print(f"Name: {bot_info['first_name']}")
            if bot_info.get('can_read_all_group_messages'):
                print("Can read all group messages: Yes")
            if bot_info.get('supports_inline_queries'):
                print("Supports inline queries: Yes")
        else:
            print("Failed to get bot information")
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    get_bot_info()

