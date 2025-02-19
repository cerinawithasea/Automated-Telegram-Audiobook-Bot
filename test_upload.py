#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from humanize import naturalsize
from telegram_uploader import TelegramUploader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_file(file_path: str) -> Path:
    """Validate that the file exists."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return path

def load_environment():
    """Load and validate environment variables."""
    load_dotenv()
    required_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")
    
    env = {
        'api_id': os.getenv('TELEGRAM_API_ID'),
        'api_hash': os.getenv('TELEGRAM_API_HASH')
    }
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not chat_id:
        chat_id = input("Please enter Telegram chat ID: ").strip()
        if not chat_id:
            raise ValueError("Chat ID is required")
            
    env['chat_id'] = chat_id
    return env

async def main():
    """Main execution function."""
    try:
        if len(sys.argv) != 2:
            print(f"Usage: {sys.argv[0]} /path/to/audiobook.m4b")
            sys.exit(1)

        # Validate input file
        file_path = validate_file(sys.argv[1])
        logger.info(f"Processing file: {file_path}")

        # Load environment variables
        env = load_environment()
        logger.info("Environment variables loaded successfully")

        # Generate caption
        # Generate caption
        file_size = file_path.stat().st_size
        caption = f"Audiobook: {file_path.stem}\nSize: {naturalsize(file_size)}"
        
        # Initialize uploader with progress callback
        uploader = TelegramUploader(
            api_id=env['api_id'],
            api_hash=env['api_hash']
        )
        logger.info("Telegram uploader initialized")
        
        # Check file size
        max_size = 2000 * 1024 * 1024  # 2GB limit for Telegram
        if file_size > max_size:
            raise ValueError(f"File too large: {naturalsize(file_size)} exceeds {naturalsize(max_size)}")
        def progress_callback(current, total, speed=None, eta=None):
            percentage = (current / total) * 100
            current_size = naturalsize(current)
            total_size = naturalsize(total)
            speed_str = f"Speed: {naturalsize(speed)}/s" if speed else ""
            eta_str = f"ETA: {eta}" if eta else ""
            logger.info(f"Progress: {percentage:.1f}% | {current_size}/{total_size} | {speed_str} | {eta_str}")

        uploader.progress_callback = progress_callback
        # Confirm upload
        confirmation = input("Proceed with upload? (y/n): ")
        if confirmation.lower() != 'y':
            logger.info("Upload cancelled by user")
            return

        # Upload file
        # Start upload
        logger.info("Starting upload...")
        result = await uploader.upload_file(
            file_path=str(file_path),
            chat_id=env['chat_id'],
            caption=caption,
            chunk_size=2097152  # 2MB chunks
        )
        if result:
            logger.info("Upload completed successfully!")
        else:
            logger.error("Upload failed")

    except FileNotFoundError as e:
        logger.error(f"File error: {str(e)}")
        sys.exit(1)
    except EnvironmentError as e:
        logger.error(f"Environment error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

