#!/usr/bin/env python3

import os
import sys
import asyncio
from pathlib import Path
from telegram_uploader import TelegramUploader

# Example usage:
# python test_uploader.py api_id api_hash chat_id file_path
#
# Or set environment variables:
# TELEGRAM_API_ID=your_api_id
# TELEGRAM_API_HASH=your_api_hash
# TELEGRAM_CHAT_ID=your_chat_id

async def test_upload(api_id: str, api_hash: str, chat_id: str, file_path: str):
    # Initialize the uploader with API credentials
    uploader = TelegramUploader(
        api_id=api_id,
        api_hash=api_hash
    )

    print(f"Starting upload of {file_path} to chat {chat_id}")
    try:
        # Start the client
        async with uploader.client:
            # Determine file type and use appropriate upload method
            path = Path(file_path)
            if path.suffix.lower() in ['.mp3', '.m4a', '.m4b', '.ogg', '.wav']:
                # For audio files, use upload_audio with metadata
                result = await uploader.upload_audio(
                    file_path=file_path,
                    chat_id=chat_id,
                    title=path.stem,
                    performer="Test Upload"
                )
            else:
                # For other files, use regular upload_file
                result = await uploader.upload_file(
                    file_path=file_path,
                    chat_id=chat_id,
                    caption=f"Test upload: {path.name}"
                )
            
            if result:
                print(f"\nUpload successful! Message ID: {result.id}")
            else:
                print("\nUpload failed!")

    except Exception as e:
        print(f"\nError during upload: {str(e)}")
        raise

def main():
    # Get credentials from command line or environment
    api_id = sys.argv[1] if len(sys.argv) > 1 else os.getenv('TELEGRAM_API_ID')
    api_hash = sys.argv[2] if len(sys.argv) > 2 else os.getenv('TELEGRAM_API_HASH')
    chat_id = sys.argv[3] if len(sys.argv) > 3 else os.getenv('TELEGRAM_CHAT_ID')
    file_path = sys.argv[4] if len(sys.argv) > 4 else None

    if not all([api_id, api_hash, chat_id, file_path]):
        print("Missing required parameters!")
        print("Usage: python test_uploader.py api_id api_hash chat_id file_path")
        print("Or set environment variables: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_CHAT_ID")
        sys.exit(1)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    # Run the upload test
    asyncio.run(test_upload(api_id, api_hash, chat_id, file_path))

if __name__ == "__main__":
    main()

