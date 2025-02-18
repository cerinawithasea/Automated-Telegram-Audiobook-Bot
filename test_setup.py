import os
import logging
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
import telegram
from telegram.error import TelegramError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test connection to PostgreSQL database."""
    try:
        logger.info("Testing database connection...")
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        logger.info("✅ Database connection successful!")
        conn.close()
        return True
    except psycopg2.Error as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

async def test_telegram_bot():
    """Test Telegram bot connection and functionality."""
    try:
        logger.info("Testing Telegram bot connection...")
        bot = telegram.Bot(token=os.getenv('BOT_TOKEN'))
        bot_info = await bot.get_me()
        logger.info(f"✅ Successfully connected to bot: {bot_info.first_name}")
        return bot
    except TelegramError as e:
        logger.error(f"❌ Telegram bot connection failed: {str(e)}")
        return None

async def send_test_message(bot):
    """Send a test message to verify bot functionality."""
    try:
        logger.info("Sending test message...")
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = (
            f"\U0001F504 System Test ({current_time})\n\n"
            "✅ Database Connection: OK\n"
            "✅ Bot Connection: OK\n"
            "✅ Message Sending: OK\n\n"
            "Ready to process audiobook uploads! \U0001F4DA"
        )
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info("✅ Test message sent successfully!")
        return True
    except TelegramError as e:
        logger.error(f"❌ Failed to send test message: {str(e)}")
        return False

async def async_main():
    """Async main function to run all tests."""
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ['DATABASE_URL', 'BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    # Run tests
    if not test_database_connection():
        logger.error("❌ Database connection test failed!")
        sys.exit(1)

    bot = await test_telegram_bot()
    if not bot:
        logger.error("❌ Telegram bot connection test failed!")
        sys.exit(1)

    if not await send_test_message(bot):
        logger.error("❌ Sending test message failed!")
        sys.exit(1)

    logger.info("✅ All tests completed successfully!")

def main():
    """Main function to run all tests."""
    asyncio.run(async_main())

if __name__ == "__main__":
    main()

