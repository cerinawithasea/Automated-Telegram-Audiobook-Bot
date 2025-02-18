#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

from caption_generator import process_audiobook
from telegram_uploader import TelegramUploader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_file(file_path: str) -> Path:
    """Validate that the file exists and is an M4B file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != '.m4b':
        raise ValueError(f"Invalid file type. Expected .m4b, got {path.suffix}")
    return path

def load_environment():
    """Load and validate environment variables."""
    load_dotenv()
    required_vars = ['BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")
    return {
        'bot_token': os.getenv('BOT_TOKEN'),
        'chat_id': os.getenv('TELEGRAM_CHAT_ID')
    }

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
        logger.info("Generating caption...")
        caption = process_audiobook(str(file_path))
        logger.info("Caption generated successfully")
        print("\nGenerated Caption:")
        print("-----------------")
        print(caption)
        print("-----------------\n")

        # Initialize uploader
        uploader = TelegramUploader(env['bot_token'])
        logger.info("Telegram uploader initialized")

        # Confirm upload
        confirmation = input("Proceed with upload? (y/n): ")
        if confirmation.lower() != 'y':
            logger.info("Upload cancelled by user")
            return

        # Upload file
        logger.info("Starting upload...")
        result = await uploader.upload_audio(
            file_path=str(file_path),
            caption=caption,
            chat_id=env['chat_id']
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

