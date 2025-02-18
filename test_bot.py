import os
from telegram import Bot
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def send_test_message():
    try:
        # Initialize bot with token
        bot = Bot(token=os.getenv('BOT_TOKEN'))
        
        # Send test message
        await bot.send_message(
            chat_id=5423238284,  # Your verified chat ID
            text="Hello! Your bot is working correctly! 🎉\n\nThis confirms that:\n1. Bot token is valid\n2. Chat ID is correct\n3. Bot has permission to send messages"
        )
        print("Test message sent successfully!")
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(send_test_message())

