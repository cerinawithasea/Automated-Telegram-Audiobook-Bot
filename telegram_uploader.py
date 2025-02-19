import asyncio
import logging
import time
from pathlib import Path
from typing import Optional, Union, Dict, Any
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError, NetworkError, TimeoutError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramUploader:
    """Telegram uploader implementation using Pyrogram user client.
    
    Features:
    - Support for large files (up to 2GB)
    - Progress tracking with ETA
    - Automatic retries with exponential backoff
    - FloodWait handling
    - Network error recovery
    """
    
    def __init__(
        self,
        api_id: str,
        api_hash: str,
        session_string: Optional[str] = None
    ):
        """Initialize the uploader with Telegram API credentials.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash 
            session_string: Optional session string for resuming previous session
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_string = session_string
        self.client = Client(
            "uploader",
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string
        )
        self.max_retries = 3
        self.retry_delay = 30
    self, 
    api_id: str,
    api_hash: str,
    session_string: Optional[str] = None
):
    """Initialize the uploader with Telegram API credentials.
    
    Args:
        api_id: Telegram API ID
        api_hash: Telegram API hash 
        session_string: Optional session string for resuming previous session
    """
    self.api_id = api_id
    self.api_hash = api_hash
    self.session_string = session_string
    self.client = Client(
        "uploader",
        api_id=api_id,
        api_hash=api_hash,
        session_string=session_string
    )
    self.max_retries = 3
    self.retry_delay = 30
            @staticmethod
            def format_size(size: float) -> str:
                """Format size in bytes to human readable format."""
                units = ['B', 'KB', 'MB', 'GB', 'TB']
                size = float(size)
                unit_index = 0
                
                while size >= 1024.0 and unit_index < len(units) - 1:
                    size /= 1024.0
                    unit_index += 1
                
                return f"{size:.2f} {units[unit_index]}"

            @staticmethod
            def format_time(seconds: float) -> str:
                """Format time duration in seconds to human readable format."""
                if seconds < 60:
                    return f"{seconds:.1f}s"
                elif seconds < 3600:
                    minutes = seconds / 60
                    return f"{minutes:.1f}m"
                else:
                    hours = seconds / 3600
                    return f"{hours:.1f}h"

            def _init_upload_state(self, file_size: int) -> Dict[str, Any]:
                """Initialize the upload state dictionary for progress tracking.
                
                Args:
                    file_size: Size of the file in bytes
                    
                Returns:
                    Dict containing upload state information
                """
                return {
                    'start_time': time.time(),
                    'last_progress_update': 0,
                    'uploaded_bytes': 0,
                    'file_size': file_size
                }
    async def _progress_callback(
        self,
        current: int,
        total: int,
        message: Message,
        state: Dict[str, Any]
    ) -> None:
        """Update progress message with current upload status.
        
        Args:
            current: Current number of bytes uploaded
            total: Total file size in bytes
            message: Message to update with progress
            state: Upload state dictionary
        """
        try:
            now = time.time()
            # Limit progress updates to once per second
            if now - state['last_progress_update'] < 1:
                return
                
            if current == total:
                await message.edit_text("Finalizing upload...")
                return
            
            state['last_progress_update'] = now
            elapsed = now - state['start_time']
            speed = current / elapsed if elapsed > 0 else 0
            percentage = (current * 100) / total
            remaining = (total - current) / speed if speed > 0 else 0
            
            # Create progress bar
            bars = int(percentage / 5)  # 20 bars total
            progress_bar = '█' * bars + '░' * (20 - bars)
            
            status_text = (
                f"\U0001F4E4 Uploading...\n"
                f"Progress: {progress_bar} {percentage:.1f}%\n"
                f"Speed: {self.format_size(speed)}/s\n"
                f"Uploaded: {self.format_size(current)}/{self.format_size(total)}\n"
                f"Elapsed: {self.format_time(elapsed)}\n"
                f"Remaining: {self.format_time(remaining)}"
            )
            
            await message.edit_text(status_text)
            
        except Exception as e:
                             await progress_message.edit_text(error_msg)
                            await asyncio.sleep(wait_time)
                        else:
                            raise
        
            return None
            
        except Exception as e:
            error_msg = f"❌ Upload failed: {str(e)}"
            logger.error(error_msg)
            if 'progress_message' in locals():
                await progress_message.edit_text(error_msg)
            raise
        """Upload a file to Telegram with progress tracking and automatic retries.
        
        Features:
        - Supports files up to 2GB
        - Progress tracking with ETA
        - Automatic retries with exponential backoff
        - Rate limit handling
        
        Args:
            file_path: Path to file to upload
            chat_id: Telegram chat ID
            caption: Optional caption for the file
            **kwargs: Additional arguments passed to send_document

            Returns:
                Optional[Message]: The sent message if successful

            Raises:
                FileNotFoundError: If file doesn't exist
                RPCError: For Telegram API errors
            """
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            file_size = file_path.stat().st_size
            state = self._init_upload_state(file_size)

            try:
                async with self.client:
                    # Send initial progress message
                    progress_message = await self.client.send_message(
                        chat_id=chat_id,
                        text=f"Starting upload of {file_path.name} ({self.format_size(file_size)})..."
                    )
                    
                    retry_count = 0
                    while retry_count < self.max_retries:
                        try:
                            # Upload with progress tracking
                            result = await self.client.send_document(
                                chat_id=chat_id,
                                document=str(file_path),
                                caption=caption,
                                force_document=True,
                                progress=self._progress_callback,
                                progress_args=(progress_message, state),
                                **kwargs
                            )
                            
                            # Upload successful
                            await progress_message.edit_text(
                                f"✅ Upload complete: {file_path.name}\n"
                                f"Time taken: {self.format_time(time.time() - state['start_time'])}"
                            )
                            return result
                            
                        except FloodWait as e:
                            # Handle rate limiting
                            logger.warning(f"Rate limit hit, waiting {e.value}s...")
                            await progress_message.edit_text(
                                f"⏳ Rate limit hit, waiting {e.value} seconds..."
                            )
                            await asyncio.sleep(e.value)
                            continue
                            
                        except (NetworkError, TimeoutError, RPCError) as e:
                            retry_count += 1
                            if retry_count < self.max_retries:
                                wait_time = min(1800, self.retry_delay * (2 ** (retry_count - 1)))
                                error_msg = (
                                    f"⚠️ Upload error (attempt {retry_count}/{self.max_retries})\n"
                                    f"Error: {str(e)}\n"
                                    f"Retrying in {self.format_time(wait_time)}..."
                                )
                                logger.warning(error_msg)
                                await progress_message.edit_text(error_msg)
                                await asyncio.sleep(wait_time)
                            else:
                                raise
                
                return None
                
            except Exception as e:
                error_msg = f"❌ Upload failed: {str(e)}"
                logger.error(error_msg)
                if 'progress_message' in locals():
                    await progress_message.edit_text(error_msg)
                raise
                                retry_count = 0
                                while retry_count < self.max_retries:
                                    try:
                                        # Upload the file
                                        async with aiofiles.open(file_path, 'rb') as file:
                            result = await self.client.send_document(
                                chat_id=chat_id,
                                document=file,
                                caption=caption,
                                force_document=True,
                                progress=self._upload_progress_callback,
                                progress_args=(progress_message,),
                                **kwargs
                            )
                            
                            # Upload successful
                            await progress_message.edit_text(
                                f"✅ Upload complete: {file_path.name}\n"
                                f"Time taken: {self._format_time(time.time() - start_time)}"
                            )
                            return result
                            
                    except FloodWait as e:
                        # Handle rate limiting
                        logger.warning(f"Rate limit hit, waiting {e.value}s...")
                        await progress_message.edit_text(
                            f"⏳ Rate limit hit, waiting {e.value} seconds..."
                        )
                        await asyncio.sleep(e.value)
                        continue
                        
                    except (NetworkError, TimeoutError) as e:
                        retry_count += 1
                        if retry_count < self.max_retries:
                            wait_time = min(1800, self.retry_delay * (2 ** (retry_count - 1)))
                            error_msg = (
                                f"⚠️ Upload error (attempt {retry_count}/{self.max_retries})\n"
                                f"Error: {str(e)}\n"
                                f"Retrying in {wait_time}s..."
                            )
                            logger.warning(error_msg)
                            await progress_message.edit_text(error_msg)
                            await asyncio.sleep(wait_time)
                        else:
                            raise
                            
            return None
            
        except Exception as e:
            error_msg = f"❌ Upload failed: {str(e)}"
            logger.error(error_msg)
            if 'progress_message' in locals():
                await progress_message.edit_text(error_msg)
            raise

    async def _progress_callback(
        self,
        current: int,
        total: int,
        message: Message,
        state: Dict[str, Any]
    ) -> None:
        """Update progress message with current upload status.
        
        Displays:
        - Progress bar
        - Percentage complete
        - Upload speed
        - ETA
        - File size progress
        """
        try:
            if current == total:
                await message.edit_text("Finalizing upload...")
                return
            
            now = time.time()
            elapsed = now - start_time
            speed = current / elapsed if elapsed > 0 else 0
            percentage = (current * 100) / total
            time_remaining = (total - current) / speed if speed > 0 else 0
            
            # Create progress bar
            bars = int(percentage / 5)  # 20 bars total
            progress_bar = '█' * bars + '░' * (20 - bars)
            
            status_text = (
                f"📤 Uploading...\n"
                f"Progress: {progress_bar} {percentage:.1f}%\n"
                f"Speed: {self.format_size(speed)}/s\n"
                f"Uploaded: {self.format_size(current)}/{self.format_size(total)}\n"
                f"Elapsed: {self.format_time(elapsed)}\n"
                f"Remaining: {self.format_time(time_remaining)}"
            )
            
            # Update progress message
            await message.edit_text(status_text)
            
        except Exception as e:
            logger.error(f"Progress callback error: {e}")
            
            # Calculate progress metrics
            elapsed = now - self.start_time if hasattr(self, 'start_time') else 0
            speed = current / elapsed if elapsed > 0 else 0
            percentage = (current * 100) / total
            
            # Create progress string
            progress_str = '█' * int(percentage / 5) + '░' * (20 - int(percentage / 5))
            
            text = (
                f"\U0001F4E4 Uploading...\n"
                f"Progress: {progress_str} {percentage:.1f}%\n"
                f"Speed: {self._format_size(speed)}/s\n"
                f"Uploaded: {self._format_size(current)}/{self._format_size(total)}"
            )
            
            await message.edit_text(text)
            
        except Exception as e:
            logger.error(f"Progress callback error: {e}")
            
            # Create progress string
            progress_str = '█' * int(percentage / 5) + '░' * (20 - int(percentage / 5))
            
            text = (
                f"\U0001F4E4 Uploading...\n"
                f"Progress: {progress_str} {percentage:.1f}%\n"
                f"Speed: {self.format_size(speed)}/s\n"
                f"Uploaded: {self.format_size(current)}/{self.format_size(total)}\n"
                f"Elapsed: {self.format_time(elapsed)}\n"
                f"Remaining: {self.format_time(remaining)}"
            )
            
            await message.edit_text(text)
            
        except Exception as e:
            logger.error(f"Progress callback error: {e}")
        """Internal progress callback handler with rate limiting and error handling.
        
        Args:
            current: Current number of bytes uploaded
            total: Total file size in bytes
            state: Upload state dictionary
            message: Telegram message for progress updates
            progress_callback: Optional external progress callback
        """
        try:
            now = time.time()
            # Limit progress updates to once per second
            if now - state['last_progress_update'] < 1:
                return
                
            state['last_progress_update'] = now
            state['uploaded_bytes'] = current
            
            # Calculate progress metrics
            elapsed = now - state['start_time']
            speed = current / elapsed if elapsed > 0 else 0
            percentage = (current * 100) / total
            remaining = (total - current) / speed if speed > 0 else 0
            
            # Create progress string
            progress_bars = int(percentage / 5)  # 20 bars total
            progress_str = '█' * progress_bars + '░' * (20 - progress_bars)
            
            text = (
                f"📤 Uploading...\n"
                f"Progress: {progress_str} {percentage:.1f}%\n"
                f"Speed: {self.format_size(speed)}/s\n"
                f"Uploaded: {self.format_size(current)}/{self.format_size(total)}\n"
                f"Elapsed: {self.format_time(elapsed)}\n"
                f"Remaining: {self.format_time(remaining)}"
            )
            
            # Update progress message
            await message.edit_text(text)
            
            # Call external progress callback if provided
            if progress_callback:
                progress_callback(current, total, speed, {
                    'percentage': percentage,
                    'elapsed': elapsed,
                    'remaining': remaining,
                    'speed': speed
                })
                
        except Exception as e:
            logger.error(f"Progress callback error: {e}")

        try:
            if current == total:
                await message.edit_text("Upload completed!")
                return
            
            elapsed_time = time.time() - self.start_time
            if elapsed_time == 0:
                return

            speed = current / elapsed_time
            percentage = (current * 100) / total
            estimated_total = total / speed if speed > 0 else 0
            time_remaining = estimated_total - elapsed_time if estimated_total > elapsed_time else 0
            
            progress_bars = int(percentage / 5)  # 20 bars for 100%
            progress_str = '█' * progress_bars + '░' * (20 - progress_bars)

            text = f"\U0001F4E4 Uploading...\n"
            text += f"Progress: {progress_str} {percentage:.1f}%\n"
            text += f"Speed: {self.format_size(speed)}/s\n"
            text += f"Uploaded: {self.format_size(current)}/{self.format_size(total)}\n"
            
            if time_remaining > 0:
                text += f"Time remaining: {time_remaining:.1f}s"

            await message.edit_text(text)
        except Exception as e:
            logger.error(f"Progress callback error: {e}")

    async def upload_file(
        self,
        file_path: Union[str, Path],
        chat_id: Union[str, int],
        caption: Optional[str] = None,
        **kwargs
    ) -> Optional[Message]:
        """Upload a file to Telegram with progress tracking and error handling.
        
        Args:
            file_path: Path to file to upload
            chat_id: Telegram chat ID
            caption: Optional caption for the file
            **kwargs: Additional arguments passed to send_document
            
        Returns:
            Optional[Message]: The sent message if successful
            
        Raises:
            FileNotFoundError: If file doesn't exist
            NetworkError: For network related errors
        """
            logger.error(error_msg)
            if 'progress_message' in locals():
                await progress_message.edit_text(error_msg)
            raise
            
        return None
        """Upload a file to Telegram with robust error handling and progress tracking.
        
        Features:
        - Chunked upload for large files
        - Automatic retries with exponential backoff
        - Progress tracking
        - Timeout handling
        - Memory efficient
        self,
        file_path: Union[str, Path],
        chat_id: Union[str, int],
        caption: Optional[str] = None,
        progress_callback: Optional[ProgressCallback] = None,
        **kwargs
    ) -> Optional[Message]:
        """Upload a file to Telegram with robust error handling and progress tracking.
        
        Args:
            file_path: Path to file to upload
            chat_id: Telegram chat ID
            caption: Optional caption for the file
            progress_callback: Optional callback for progress updates
            **kwargs: Additional arguments passed to send_document
            
        Returns:
            Optional[Message]: The sent message if successful
            
        Raises:
            FileNotFoundError: If file doesn't exist
            NetworkError: For network related errors
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_size = file_path.stat().st_size
        start_time = time.time()
        
        try:
            async with self.client:
                # Send initial progress message
                progress_message = await self.client.send_message(
                    chat_id=chat_id,
                    text=f"Starting upload of {file_path.name} ({self.format_size(file_size)})..."
                )
                
                retry_count = 0
                while retry_count < self.max_retries:
                    try:
                        # Upload the file
                        async with aiofiles.open(file_path, 'rb') as file:
                            result = await self.client.send_document(
                                chat_id=chat_id,
                                document=file,
                                caption=caption,
                                force_document=True,
                                progress=progress_callback,
                                **kwargs
                            )
                            
                            # Upload successful
                            await progress_message.edit_text(
                                f"✅ Upload complete: {file_path.name}\n"
                                f"Time taken: {time.time() - start_time:.1f}s"
                            )
                            return result
                            
                    except FloodWait as e:
                        # Handle rate limiting
                        logger.warning(f"Rate limit hit, waiting {e.value}s...")
                        await progress_message.edit_text(
                            f"⏳ Rate limit hit, waiting {e.value} seconds..."
                        )
                        await asyncio.sleep(e.value)
                        continue
                        
                    except (NetworkError, TimeoutError) as e:
                        retry_count += 1
                        if retry_count < self.max_retries:
                            wait_time = min(1800, self.retry_delay * (2 ** (retry_count - 1)))
                            error_msg = (
                                f"⚠️ Upload error (attempt {retry_count}/{self.max_retries})\n"
                                f"Error: {str(e)}\n"
                                f"Retrying in {wait_time}s..."
                            )
                            logger.warning(error_msg)
                            await progress_message.edit_text(error_msg)
                            await asyncio.sleep(wait_time)
                        else:
                            raise
                            
            return None
            
        except Exception as e:
            error_msg = f"❌ Upload failed: {str(e)}"
            logger.error(error_msg)
            if 'progress_message' in locals():
                await progress_message.edit_text(error_msg)
            raise
        self,
        file_path: Union[str, Path],
        chat_id: Union[str, int],
        caption: Optional[str] = None,
        progress_callback: Optional[ProgressCallback] = None,
        state_callback: Optional[StateCallback] = None,
        chunk_size: int = 8388608,  # 8MB chunks
        max_retries: int = 3,
        **kwargs
    ) -> Optional[Message]:
        """Upload a file to Telegram with robust error handling and progress tracking.
        
        Features:
        - Chunked upload for large files
        - Automatic retries with exponential backoff
        - Progress tracking
        - Timeout handling
        - Memory efficient streaming
        
        Args:
            file_path: Path to file to upload
            chat_id: Telegram chat ID
            caption: Optional caption for the file
            progress_callback: Optional callback for progress updates
            state_callback: Optional callback for state changes
            chunk_size: Size of upload chunks in bytes
            max_retries: Maximum number of retry attempts
            **kwargs: Additional arguments passed to send_document
            
        Returns:
            Optional[Message]: The sent message if successful
            
        Raises:
            FileNotFoundError: If file doesn't exist
            TelegramError: For Telegram API errors
            NetworkError: For network related errors
        """
        # Path handling
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Initialize state
        file_size = file_path.stat().st_size
        state = self.__init_upload_state(file_size)
        
        # Calculate appropriate timeouts
        timeouts = self.calculate_timeouts(file_size)
        kwargs.update(timeouts)
        
        try:
            async with self.client:
                # Send initial progress message
                progress_message = await self.client.send_message(
                    chat_id=chat_id,
                    text=f"Preparing to upload {file_path.name} ({self.format_size(file_size)})..."
                )
                
                # Main upload loop with retries
                while state['retries'] < max_retries:
                    try:
                        # Stream file in chunks
                        async with aiofiles.open(file_path, 'rb') as file:
                            result = await self.client.send_document(
                                chat_id=chat_id,
                                document=file,
                                caption=caption,
                                force_document=True,
                                progress=lambda current, total: self._progress_callback(
                                    current, total, state, progress_message, progress_callback
                                ),
                                **kwargs
                            )
                            
                            # Upload successful
                            await progress_message.edit_text(
                                f"✅ Upload complete: {file_path.name}\n"
                                f"Time taken: {self.format_time(time.time() - state['start_time'])}"
                            )
                            return result
                            
                    except FloodWait as e:
                        # Handle rate limiting
                        wait_time = e.value
                        logger.warning(f"Rate limit hit, waiting {wait_time}s...")
                        await progress_message.edit_text(
                            f"⏳ Rate limit hit, waiting {wait_time} seconds..."
                        )
                        await asyncio.sleep(wait_time)
                        continue
                        
                    except (NetworkError, TimeoutError) as e:
                        # Handle network errors with exponential backoff
                        state['retries'] += 1
                        if state['retries'] < max_retries:
                            wait_time = min(1800, 60 * (2 ** (state['retries'] - 1)))
                            error_msg = (
                                f"⚠️ Upload error (attempt {state['retries']}/{max_retries})\n"
                                f"Error: {str(e)}\n"
                                f"Retrying in {self.format_time(wait_time)}..."
                            )
                            logger.warning(error_msg)
                            await progress_message.edit_text(error_msg)
                            await asyncio.sleep(wait_time)
                        else:
                            raise
                            
            return None
            
        except Exception as e:
            error_msg = f"❌ Upload failed: {str(e)}"
            logger.error(error_msg)
            if 'progress_message' in locals():
                await progress_message.edit_text(error_msg)
            raise
        """Upload a file to Telegram with automatic type detection.
        
        Args:
            file_path: Path to the file
            chat_id: Telegram chat ID
            caption: Optional caption for the file
            force_document: Force sending as document regardless of type
        
        Returns:
            Optional[Message]: Message object if successful
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        try:
            async with self.client:
                # Send initial message
                progress_message = await self.client.send_message(
                    chat_id=chat_id,
                    text=f"Starting upload of {file_path.name}..."
                )

                self.start_time = time.time()

                # Determine upload method based on file type
                if force_document:
                    upload_method = self.client.send_document
                else:
                    upload_method = self.get_telegram_method(file_path)

                # Upload the file
                result = await upload_method(
                    chat_id=chat_id,
                    document=str(file_path) if upload_method == self.client.send_document else str(file_path),
                    caption=caption,
                    progress=self.progress,
                    progress_args=(progress_message,)
                )

                await progress_message.edit_text(
                    f"Upload complete: {file_path.name}"
                )
                return result

        except FloodWait as e:
            retry_delay = e.value
            logger.warning(f"Rate limit hit, waiting {retry_delay} seconds")
            await asyncio.sleep(retry_delay)
            return await self.upload_file(file_path, chat_id, caption, force_document)
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            if 'progress_message' in locals():
                try:
                    await progress_message.edit_text(
                        f"Upload failed: {str(e)}"
                    )
                except Exception:
                    pass
            return None

    async def send_message(
        self,
        chat_id: Union[str, int],
        text: str
    ) -> Optional[Message]:
        """Send a text message to a Telegram chat.
        
        Args:
            chat_id: Telegram chat ID
            text: Message text to send
            
        Returns:
            Optional[Message]: The sent message if successful
        """
        try:
            async with self.client:
                return await self.client.send_message(
                    chat_id=chat_id,
                    text=text
                )
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None
            async with self.client:
                return await self.client.send_message(
                    chat_id=chat_id,
                    text=text,
                    disable_web_page_preview=True
                )
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            if retry and isinstance(e, FloodWait):
                await asyncio.sleep(e.value)
                return await self.send_message(chat_id, text, retry=False)
            return None
            async with self.client:
                return await self.client.send_message(
                    chat_id=chat_id,
                    text=text,
                    disable_web_page_preview=True
                )
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            if retry and isinstance(e, FloodWait):
                await asyncio.sleep(e.value)
                return await self.send_message(chat_id, text, retry=False)
            return None



    async def upload_file(
        self,
        file_path: Union[str, Path],
        chat_id: Union[str, int],
        caption: Optional[str] = None,
        progress_callback: Optional[ProgressCallback] = None,
        state_callback: Optional[StateCallback] = None,
        **kwargs
    ) -> Optional[Message]:
        """Upload a file to Telegram with robust error handling and progress tracking.
        
        Features:
        - Chunked upload for large files
        - Automatic retries with exponential backoff
        - Progress tracking
        - Timeout handling
        - Memory efficient streaming
        
        Args:
            file_path: Path to file to upload
            chat_id: Telegram chat ID
            caption: Optional caption for the file
            progress_callback: Optional callback for progress updates
            state_callback: Optional callback for state changes
            chunk_size: Size of upload chunks in bytes
            max_retries: Maximum number of retry attempts
            **kwargs: Additional arguments passed to send_document
            
        Returns:
            Optional[Message]: The sent message if successful
        """
        # Path handling
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            async with self.client:
                # Send initial message
                progress_message = await self.client.send_message(
                    chat_id=chat_id,
                    text=f"Starting upload of {file_path.name}..."
                )

                self.start_time = time.time()

                # Upload the file
                result = await self.client.send_document(
                    chat_id=chat_id,
                    document=str(file_path),
                    force_document=True,
                    progress=self.progress,
                    progress_args=(progress_message,)
                )

                return result

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return None

    async def send_message(self, chat_id: Union[int, str], text: str) -> Optional[Message]:
        """Send a text message to a Telegram chat.
        
        Args:
            chat_id: Telegram chat ID
            text: Message text to send
            
        Returns:
            Optional[Message]: The sent message if successful
        """
        try:
            async with self.client:
                return await self.client.send_message(
                    chat_id=chat_id,
                    text=text
                )
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None

    async def upload_audio(
        self,
        file_path: Union[str, Path],
        chat_id: Union[str, int],
        duration: int = 0,
        performer: str = "",
        title: str = "",
        **kwargs
    ) -> Optional[Message]:
        """Upload an audio file to Telegram with metadata.
        
        Args:
            file_path: Path to the audio file
            chat_id: Telegram chat ID
            duration: Duration in seconds
            performer: Audio performer name
            title: Audio title
            **kwargs: Additional arguments passed to send_audio
            
        Returns:
            Optional[Message]: Message object if successful
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_size = file_path.stat().st_size
        state = self._init_upload_state(file_size)

        try:
            async with self.client:
                # Send initial progress message
                progress_message = await self.client.send_message(
                    chat_id=chat_id,
                    text=f"Starting upload of {file_path.name} ({self.format_size(file_size)
        """Upload an audio file to Telegram.
        
        Args:
            file_path: Path to the audio file
            chat_id: Telegram chat ID
            duration: Duration in seconds
            performer: Audio performer name
            title: Audio title
        
        Returns:
            Optional[Message]: Message object if successful
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        try:
            async with self.client:
                # Send initial message
                progress_message = await self.client.send_message(
                    chat_id=chat_id,
                    text=f"Starting upload of {file_path.name}..."
                )

                self.start_time = time.time()

                # Upload the audio
                result = await self.client.send_audio(
                    chat_id=chat_id,
                    audio=str(file_path),
                    duration=duration,
                    performer=performer,
                    title=title,
                    progress=self.progress,
                    progress_args=(progress_message,)
                )

                return result

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return None

    async def send_message(
        self,
        chat_id: Union[str, int],
        text: str
    ) -> Optional[Message]:
        """Send a text message to a Telegram chat."""
        try:
            async with self.client:
                return await self.client.send_message(
                    chat_id=chat_id,
                    text=text
                )
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None


                file_size = file_path.stat().st_size
                self._upload_start_time = time.time()
                self._progress_callback = progress_callback

                # Calculate appropriate timeouts based on file size
                timeouts = self.calculate_timeouts(file_size)
                if 'timeouts' not in kwargs:
                    kwargs.update(timeouts)

                retry_count = 0
                while retry_count < self.max_retries:
                    try:
                        # Use proper streaming upload
                        with open(file_path, 'rb') as file:
                            result = await self.bot.send_document(
                                chat_id=chat_id,
                                document=file,
                                filename=file_path.name,
                                caption=caption,
                                progress_callback=self._progress,
                                **kwargs
                            )
                            return True

                    except RetryAfter as e:
                        logger.warning(f"Rate limit hit, waiting {e.retry_after} seconds...")
                        await asyncio.sleep(e.retry_after)
                        continue

                    except (NetworkError, TimedOut) as e:
                        retry_count += 1
                        if retry_count < self.max_retries:
                            wait_time = min(1800, 60 * (2 ** (retry_count - 1)))
                            logger.warning(f"Network error, retrying in {wait_time}s: {str(e)}")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error("Max retries reached. Upload failed.")
                            raise

                    except Exception as e:
                        logger.error(f"Upload failed: {str(e)}")
                        raise

                    # Update progress
                    state.uploaded_size += len(chunk)
                    state.current_chunk += 1


            # Send final message with caption
            await self.bot.send_message(
                chat_id=chat_id,
                text=caption if caption else f"Successfully uploaded: {file_path.name}"
            )

            return True

        except Exception as e:
            logger.error(f"Upload failed for {file_path}: {str(e)}")
            if state_callback:
                state_callback("Upload failed", {'error': str(e)})
            raise
        finally:
            self._current_upload = None
            self._upload_start_time = None

    async def upload_audio(
        self,
        file_path: Union[str, Path],
        chat_id: Union[str, int],
        caption: Optional[str] = None,
        chunk_size: int = 8388608,  # 8 MB chunks - optimized for audiobook uploads
        progress_callback: Optional[ProgressCallback] = None,
        state_callback: Optional[StateCallback] = None
    ) -> bool:
        """Upload an audio file to Telegram with optimizations for audiobooks.

        This method is specifically optimized for large audiobook files with
        the following features:
        1. 8 MB chunk size for efficient uploads
        2. Extended timeouts (10 min base + 2 min per 20 MB)
        3. Exponential backoff retry with resume capability
        4. Progress tracking for large files

        Args:
            file_path: Path to the audio file
            chat_id: Telegram chat/channel ID to upload to
            caption: Optional caption for the audio file
            chunk_size: Size of chunks for large file uploads (default: 8 MB)
            progress_callback: Optional callback for upload progress updates
            
        Returns:
            bool: True if upload successful, False otherwise
            
        Raises:
            FileNotFoundError: If the audio file does not exist
            TelegramError: If there is an error communicating with Telegram
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            uploader = self.ChunkedUploader(self.bot, chunk_size)
            state = await uploader.init_upload(file_path)
            
            if state_callback:
                state_callback("Initialized upload", {
                    "file_size": state.total_size,
                    "num_chunks": len(state.chunk_hashes)
                })

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
                        
                        # Upload file in chunks
                        async with aiofiles.open(file_path, 'rb') as file:
                            while state.current_chunk < len(state.chunk_hashes):
                                chunk = await file.read(chunk_size)
                                if not chunk:
                                    break
                                    
                                if not await uploader.verify_chunk(chunk, state.chunk_hashes[state.current_chunk]):
                                    logger.error(f"Chunk {state.current_chunk} verification failed")
                                    raise ValueError(f"Chunk verification failed at position {state.current_chunk}")
                                    
                                chunk_uploaded = await uploader.upload_chunk(
                                    chat_id=chat_id,
                                    chunk=chunk,
                                    filename=file_path.name,
                                    offset=state.current_chunk * chunk_size,
                                    total_size=state.total_size,
                                    timeouts=timeouts
                                )
                                
                                if not chunk_uploaded:
                                    raise NetworkError(f"Failed to upload chunk {state.current_chunk}")
                                    
                                state.uploaded_size += len(chunk)
                                state.current_chunk += 1
                                
                                if progress_callback:
                                    elapsed = time.time() - state.start_time
                                    speed = state.uploaded_size / elapsed if elapsed > 0 else 0
                                    remaining = state.total_size - state.uploaded_size
                                    eta = remaining / speed if speed > 0 else 0
                                    
                                    # Calculate human readable values
                                    speed_mb = speed / (1024 * 1024)  # Convert to MB/s
                                    percent = (state.uploaded_size / state.total_size) * 100
                                    
                                    # Format progress info
                                    progress_info = {
                                        'bytes_uploaded': state.uploaded_size,
                                        'total_bytes': state.total_size,
                                        'speed_mb': speed_mb,
                                        'eta_seconds': eta,
                                        'percent': percent,
                                        'current_chunk': state.current_chunk,
                                        'total_chunks': len(state.chunk_hashes)
                                    }
                                    
                                    progress_callback(state.uploaded_size, state.total_size, speed, progress_info)
                                    
                                if state_callback:
                                    state_callback("Chunk uploaded", {
                                        "chunk": state.current_chunk,
                                        "total_chunks": len(state.chunk_hashes),
                                        "uploaded_size": state.uploaded_size
                                    })
                                    
                        # Send completion message
                        await self.bot.send_message(
                            chat_id=chat_id,
                            text=caption if caption else f"Successfully uploaded {file_path.name}"
                        )
                        logger.info(f"Successfully uploaded {file_path.name}")
                        return True
                        
                except RetryAfter as e:
                    retry_count += 1
                    wait_time = e.retry_after
                    logger.warning(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                    continue
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
                        logger.error(f"Max retries ({self.max_retries}) reached. Upload failed.")
                        raise
                except Exception as e:
                    logger.error(f"Failed to upload {file_path}: {str(e)}")
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
