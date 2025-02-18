#!/usr/bin/env python3
import os
import shutil
"""
Audiobook Uploader for Telegram
Reads audiobook metadata and uploads to Telegram with formatted captions.
"""

import os
import logging
from typing import Dict, Optional
from mutagen import File
from mutagen.mp4 import MP4
from datetime import timedelta
import humanize
from telegram_uploader import TelegramUploader
from typing import Callable, Optional

ProgressCallback = Callable[[int, int], None]

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AudiobookMetadata:
    """Class to handle audiobook metadata extraction and formatting."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.metadata = None
        self._read_metadata()

    def _read_metadata(self) -> None:
        """Read metadata from audiobook file."""
        try:
            audio = File(self.file_path)
            if isinstance(audio, MP4):
                self.metadata = {
                    'title': audio.tags.get('\xa9nam', [''])[0],
                    'artist': audio.tags.get('\xa9ART', [''])[0],
                    'narrator': audio.tags.get('----:com.apple.iTunes:NARRATOR', [''])[0],
                    'duration': str(timedelta(seconds=int(audio.info.length))),
                    'year': audio.tags.get('\xa9day', [''])[0],
                    'publisher': audio.tags.get('----:com.apple.iTunes:PUBLISHER', [''])[0],
                }
            else:
                raise ValueError("Unsupported audio format")
        except Exception as e:
            logger.error(f"Error reading metadata: {str(e)}")
            self.metadata = None

    def format_caption(self) -> Optional[str]:
        """Format metadata into a Telegram caption."""
        if not self.metadata:
            return None
        
        caption = "📚 *{}*\n".format(self.metadata.get('title', 'Unknown Title'))
        
        if self.metadata.get('artist'):
            caption += "✍️ by {}\n".format(self.metadata['artist'])
        
        if self.metadata.get('narrator'):
            caption += "🎙️ Narrated by {}\n".format(self.metadata['narrator'])
        
        if self.metadata.get('duration'):
            caption += "⏱️ Length: {}\n".format(self.metadata['duration'])
        
        if self.metadata.get('year'):
            caption += "📅 Released: {}\n".format(self.metadata['year'])
        
        if self.metadata.get('publisher'):
            caption += "🏢 Publisher: {}\n".format(self.metadata['publisher'])
        
        return caption


def progress_callback(current: int, total: int) -> None:
    """Callback to track upload progress."""
    try:
        percentage = (current / total) * 100 if total else 0
        transferred = humanize.naturalsize(current)
        total_size = humanize.naturalsize(total)
        logger.info(f"Upload progress: {percentage:.1f}% ({transferred} / {total_size})")
    except Exception as e:
        logger.error(f"Error in progress callback: {str(e)}")

async def main():
    """Main function to handle the upload process."""
    try:
        # Get file path from command line or environment
        file_path = os.getenv('AUDIOBOOK_PATH')
        if not file_path:
            logger.error("No audiobook path provided")
            return

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return

        # Read metadata and format caption
        logger.info(f"Reading metadata from: {os.path.basename(file_path)}")
        audiobook = AudiobookMetadata(file_path)
        caption = audiobook.format_caption()
        if not caption:
            logger.error("Failed to generate caption from metadata")
            return

        # Upload to Telegram with progress tracking
        logger.info("Initializing Telegram upload...")
        # Validate required environment variables
        bot_token = os.getenv('BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not bot_token or not chat_id:
            logger.error("Missing required environment variables: BOT_TOKEN and/or TELEGRAM_CHAT_ID")
            return False

        logger.info("Initializing Telegram upload...")
        uploader = TelegramUploader(
            bot_token=bot_token
        )
        success = await uploader.upload_audio(
            file_path=file_path,
            caption=caption,
            progress_callback=progress_callback,
            chat_id=os.getenv('TELEGRAM_CHAT_ID')
        )
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return False
        
        if success:
            logger.info(f"Successfully uploaded: {os.path.basename(file_path)}")
            
            # Create processed directory if it doesn't exist
            processed_dir = os.path.join(os.path.dirname(file_path), 'processed')
            os.makedirs(processed_dir, exist_ok=True)
            
            # Move the audiobook file
            processed_path = os.path.join(processed_dir, os.path.basename(file_path))
            try:
                shutil.move(file_path, processed_path)
                logger.info(f"Moved file to processed directory: {processed_path}")
                
                # Move the .ready file if it exists
                ready_file = file_path + '.ready'
                if os.path.exists(ready_file):
                    ready_processed_path = processed_path + '.ready'
                    shutil.move(ready_file, ready_processed_path)
                    logger.info(f"Moved .ready file to processed directory: {ready_processed_path}")
            except Exception as e:
                logger.error(f"Failed to move file to processed directory: {str(e)}")
        else:
            logger.error(f"Failed to upload: {os.path.basename(file_path)}")

    except Exception as e:
        logger.error(f"Error during upload process: {str(e)}", exc_info=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

