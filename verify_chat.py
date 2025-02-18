import os
from telegram import Bot
import asyncio
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def verify_chat():
    try:
        # Load environment variables
        load_dotenv()
        bot_token = os.getenv('BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            logger.error("Missing required environment variables (BOT_TOKEN or TELEGRAM_CHAT_ID)")
            return
        
        # Create bot instance
        bot = Bot(token=bot_token)
        
        # Send test message
        logger.info(f"Attempting to send message to chat ID: {chat_id}")
        message = "🎯 Test message from your audiobook bot!\n\nIf you can see this message, the bot is working correctly."
        
        await bot.send_message(
            chat_id=int(chat_id),
            text=message
        )
        logger.info("Message sent successfully!")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error("Error details:", exc_info=True)
        
if __name__ == "__main__":
    asyncio.run(verify_chat())

