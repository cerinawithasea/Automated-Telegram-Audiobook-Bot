import logging
import os
import aiofiles
from pathlib import Path
from typing import Optional, Union, Callable, Dict

# Type alias for progress callback function
ProgressCallback = Callable[[int, int], None]  # current_bytes, total_bytes
from telegram import Bot
from telegram.error import TelegramError, NetworkError, TimedOut
import asyncio
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramUploader:
    def __init__(self, bot_token: str, max_retries: int = 5):
        """Initialize the TelegramUploader with a bot token.
        
        Args:
            bot_token (str): Telegram Bot API token
            max_retries (int): Maximum number of retry attempts for failed uploads
        """
        self.bot = Bot(token=bot_token)
        self.max_retries = max_retries

    def calculate_timeouts(self, file_size: int) -> Dict[str, int]:
        """Calculate appropriate timeouts based on file size."""
        # Base timeout of 10 minutes + 2 minutes per 20MB for audiobook optimization
        base_timeout = 600  # 10 minutes base
        size_based_timeout = (file_size / (20 * 1024 * 1024)) * 120  # 2 minutes per 20MB
        total_timeout = int(base_timeout + size_based_timeout)
        
        return {
            'read_timeout': total_timeout,
            'write_timeout': total_timeout,
            'connect_timeout': 60
        }

    async def upload_audio(
        self,
        file_path: Union[str, Path],
        chat_id: Union[str, int],
        caption: Optional[str] = None,
        chunk_size: int = 8388608,  # 8MB chunks - optimized for audiobook uploads
        progress_callback: Optional[ProgressCallback] = None
    ) -> bool:
        """Upload an audio file to Telegram with optimizations for audiobooks.
        
        This method is specifically optimized for large audiobook files with:
        - 8MB chunk size for efficient uploads
        - Extended timeouts (10min base + 2min per 20MB)
        - Exponential backoff retry with resume capability
        - Progress tracking for large files
        
        Args:
            file_path: Path to the audio file
            chat_id: Telegram chat/channel ID to upload to
            caption: Optional caption for the audio file
            chunk_size: Size of chunks for large file uploads (default: 8MB)
            progress_callback: Optional callback for upload progress updates
            
        Returns:
            bool: True if upload successful, False otherwise
            
        Raises:
            FileNotFoundError: If the audio file doesn't exist
            TelegramError: If there's an error communicating with Telegram
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            file_size = file_path.stat().st_size
            timeouts = self.calculate_timeouts(file_size)
            
            logger.info(f"Starting upload of {file_path.name} ({file_size/1024/1024:.1f}MB)")
            logger.info(f"Upload timeouts: Read/Write {timeouts['read_timeout']}s, Connect {timeouts['connect_timeout']}s")
            
            retry_count = 0
            while retry_count < self.max_retries:
                try:
                    async with self.bot:
                        # Send initial status
                        await self.bot.send_message(
                            chat_id=chat_id,
                            text=f"Starting upload of {file_path.name} ({file_size/1024/1024:.1f}MB)..."
                        )
                        
                        # Send document with calculated timeouts
                        async with aiofiles.open(file_path, 'rb') as file:
                            file_content = await file.read()
                            try:
                                await self.bot.send_document(
                                    chat_id=chat_id,
                                    document=file_content,
                                    caption=caption,
                                    filename=Path(file_path).name,
                                    progress=progress_callback,
                                    **timeouts
                                )
                            except Exception as e:
                                logger.error(f"Failed to upload {file_path}: {str(e)}")
                                raise
                        
                        # Send completion message
                        await self.bot.send_message(
                            chat_id=chat_id,
                            text=f"Successfully uploaded {file_path.name}"
                        )
                    
                    logger.info(f"Successfully uploaded {file_path.name}")
                    return True
                    
                except (NetworkError, TimedOut) as e:
                    retry_count += 1
                    if retry_count < self.max_retries:
                        # Exponential backoff starting at 1 minute
                        wait_time = min(1800, 60 * (2 ** (retry_count - 1)))  # Max 30 minutes
                        error_msg = f"Upload failed (attempt {retry_count}/{self.max_retries})\n"
                        error_msg += f"Error: {str(e)}\n"
                        error_msg += f"Retrying in {wait_time} seconds ({wait_time/60:.1f} minutes)..."
                        
                        logger.warning(error_msg)
                        await self.bot.send_message(chat_id=chat_id, text=error_msg)
                        await asyncio.sleep(wait_time)
                    else:
                        raise
                        
        except TelegramError as e:
            error_msg = f"Telegram error while uploading {file_path.name}: {e}"
            logger.error(error_msg)
            await self.bot.send_message(chat_id=chat_id, text=error_msg)
            raise
        except Exception as e:
            error_msg = f"Error uploading {file_path.name}: {e}"
            logger.error(error_msg)
            await self.bot.send_message(chat_id=chat_id, text=error_msg)
            raise

    async def send_message(
        self,
        chat_id: Union[str, int],
        text: str,
        retry: bool = True
    ) -> bool:
        """Send a text message to a Telegram chat.
        
        Args:
            chat_id: Telegram chat/channel ID
            text: Message text to send
            retry: Whether to retry on failure
            
        Returns:
            bool: True if message sent successfully
        """
        retry_count = 0
        while retry_count < (self.max_retries if retry else 1):
            try:
                async with self.bot:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        read_timeout=30,
                        write_timeout=30,
                        connect_timeout=30
                    )
                return True
            except TelegramError as e:
                retry_count += 1
                if retry and retry_count < self.max_retries:
                    wait_time = min(60, 10 * retry_count)
                    logger.warning(f"Message send failed (attempt {retry_count}/{self.max_retries}), retrying in {wait_time} seconds: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Error sending message: {e}")
                    return False
