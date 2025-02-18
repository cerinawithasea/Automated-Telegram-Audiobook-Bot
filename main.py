#!/usr/bin/env python3
import os
import sys
import click
import logging
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from pathlib import Path
from dotenv import load_dotenv
from metadata import AudiobookMetadata
from telegram import Bot, InputFile
from tqdm import tqdm

# Maximum file size (4GB for Telegram Premium)
MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024  # 4GB
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('audiobook_uploader.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def validate_env():
    """Validate required environment variables are set."""
    required_vars = ['BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        click.echo(f"Error: Missing required environment variables: {', '.join(missing)}")
        click.echo("Please set them in your .env file or environment.")
        sys.exit(1)


async def upload_to_telegram(bot: Bot, file_path: str, caption: str):
    """Upload a file to Telegram."""
    try:
        file_size = Path(file_path).stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise click.ClickException(f"File size {file_size/1024/1024/1024:.2f}GB exceeds Telegram's 4GB limit")

        with open(file_path, 'rb') as f:
            input_file = InputFile(f, filename=os.path.basename(file_path))
            await bot.send_document(
                chat_id=os.getenv('TELEGRAM_CHAT_ID'),
                document=input_file,
                caption=caption,
                write_timeout=1200,  # 20 minutes timeout for large files
                read_timeout=1200,   # 20 minutes read timeout
                connect_timeout=60,  # 1 minute connect timeout
            )
        return True  # Indicate successful upload
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}\nFull error: {repr(e)}")
        raise click.ClickException(f"Upload failed: {str(e)}")

@click.group()
def cli():
    """Audiobook Caption Generator and Telegram Uploader
    
    This tool helps you generate metadata-based captions for audiobooks
    and upload them to Telegram with proper formatting.
    """
    pass

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--no-upload', is_flag=True, help="Generate caption only, don't upload")
def upload(file_path, no_upload):
    """Upload an audiobook to Telegram with metadata caption.
    
    FILE_PATH should be the path to your .m4b audiobook file.
    """
    try:
        validate_env()
        metadata = AudiobookMetadata(file_path)
        caption = metadata.format_caption()
        
        if no_upload:
            click.echo("Generated caption:")
            click.echo(caption)
            return

        bot = Bot(token=os.getenv('BOT_TOKEN'))
        asyncio.run(upload_to_telegram(bot, file_path, caption))
        
        click.echo("Upload completed successfully!")
    except Exception as e:
        logger.error(f"Error in upload command: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def caption(file_path):
    """Generate a caption from an audiobook's metadata.
    
    FILE_PATH should be the path to your .m4b audiobook file.
    """
    try:
        metadata = AudiobookMetadata(file_path)
        click.echo(metadata.format_caption())
    except Exception as e:
        logger.error(f"Error generating caption: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
def test():
    """Test your configuration and Telegram bot access.
    
    Verifies environment variables and bot permissions.
    """
    try:
        validate_env()
        bot = Bot(token=os.getenv('BOT_TOKEN'))
        
        click.echo("Testing configuration...")
        asyncio.run(bot.send_message(
            chat_id=os.getenv('TELEGRAM_CHAT_ID'),
            text="Configuration test successful! 🎉"
        ))
        click.echo("✅ Test completed successfully!")
    except Exception as e:
        logger.error(f"Configuration test failed: {str(e)}")
        raise click.ClickException(f"Test failed: {str(e)}")

class AudiobookHandler(FileSystemEventHandler):
    """Handler for audiobook file events."""
    PROCESSED_DIR = 'processed'  # Directory for processed files
    
    def __init__(self):
        self.processing = set()
        self.is_shutting_down = False
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def is_file_ready(self, file_path):
        """Check if a file has a corresponding .ready marker file."""
        ready_marker = file_path + '.ready'
        return os.path.exists(ready_marker)

    async def async_process_file(self, event):
        if event.src_path in self.processing:
            return
            
        self.processing.add(event.src_path)
        try:
            # Wait a short time to ensure file is completely written
            await asyncio.sleep(2)
                    
            if not self.is_file_ready(event.src_path):
                logger.info(f"Skipping file without ready marker: {event.src_path}")
                return
                
            logger.info(f"New audiobook detected: {event.src_path}")
            metadata = AudiobookMetadata(event.src_path)
            caption = metadata.format_caption()
            
            file_size = Path(event.src_path).stat().st_size
            if file_size > MAX_FILE_SIZE:
                raise click.ClickException(f"File size {file_size/1024/1024/1024:.2f}GB exceeds Telegram's 4GB limit")
                
            bot = Bot(token=os.getenv('BOT_TOKEN'))
            if await upload_to_telegram(bot, event.src_path, caption):
                logger.info(f"Successfully uploaded: {event.src_path}")

                # Move file to processed directory after successful upload
                processed_dir = os.path.join(os.path.dirname(event.src_path), self.PROCESSED_DIR)
                if not os.path.exists(processed_dir):
                    os.makedirs(processed_dir)
                    logger.info(f"Created processed directory: {processed_dir}")

                processed_path = os.path.join(processed_dir, os.path.basename(event.src_path))
                try:
                    os.rename(event.src_path, processed_path)
                    logger.info(f"Moved file to processed directory: {processed_path}")
                except OSError as e:
                    logger.error(f"Failed to move file to processed directory: {str(e)}")
                    return

                # Remove the .ready marker file
                try:
                    ready_marker = event.src_path + '.ready'
                    if os.path.exists(ready_marker):
                        os.remove(ready_marker)
                        logger.info(f"Removed .ready marker file: {ready_marker}")
                except Exception as e:
                    logger.warning(f"Failed to remove .ready marker file: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing file {event.src_path}: {str(e)}\nFull error: {repr(e)}")
        finally:
            if event.src_path in self.processing:
                self.processing.remove(event.src_path)
    def on_created(self, event):
        if self.is_shutting_down:
            logger.info("Ignoring new file during shutdown")
            return
            
        if event.is_directory:
            return
            
        if event.src_path.lower().endswith('.ready'):
            m4b_file = event.src_path[:-6]  # Remove .ready extension
            if m4b_file.lower().endswith('.m4b') and os.path.exists(m4b_file):
                logger.info(f"Ready marker detected for {m4b_file}")
                if m4b_file not in self.processing:
                    logger.debug(f"Processing newly ready file: {m4b_file}")
                    new_event = type(event)(src_path=m4b_file)
                    self.loop.run_until_complete(self.async_process_file(new_event))
            return
        
        if not event.src_path.lower().endswith('.m4b'):
            return
        
        logger.info(f"New .m4b file detected: {event.src_path}")
        logger.info("Waiting 10 seconds to ensure file is completely written...")
        
        # Wait and check if file size is stable
        try:
            initial_size = os.path.getsize(event.src_path)
            time.sleep(10)  # Wait 10 seconds
            final_size = os.path.getsize(event.src_path)
            
            if initial_size != final_size:
                logger.info(f"File size changed during wait period. File is still being written: {event.src_path}")
                return
            
            # Create .ready file
            ready_file = event.src_path + '.ready'
            if not os.path.exists(ready_file):
                with open(ready_file, 'w') as f:
                    pass  # Create empty file
                logger.info(f"Created .ready marker for {event.src_path}")
            
        except OSError as e:
            logger.error(f"Error while checking file: {e}")
            return
        
        if self.is_file_ready(event.src_path):
            logger.debug(f"File ready for processing: {event.src_path}")
            try:
                self.loop.run_until_complete(self.async_process_file(event))
            except Exception as e:
                logger.error(f"Error processing {event.src_path}: {str(e)}\nFull error: {repr(e)}")

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}")
    if 'observer' in globals():
        logger.info("Stopping observer gracefully...")
        observer.stop()
    sys.exit(0)

@cli.command()
@click.argument('directory', type=click.Path(), default='/Users/cerinawithasea/audiobooks/completed')
def watch(directory):
    """Monitor a directory for new audiobooks and upload them.
    
    DIRECTORY is the path to watch for new .m4b files.
    Defaults to './watch_folder' if not specified.
    """
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        validate_env()
        logger.debug("Environment validation successful")
        
        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created watch directory: {directory}")
        
        click.echo(f"Watching {directory} for new audiobooks...")
        logger.info(f"Starting watch on directory: {directory}")
        
        event_handler = AudiobookHandler()
        observer = Observer()
        observer.schedule(event_handler, directory, recursive=False)
        observer.start()
        
        try:
            while True:
                if not observer.is_alive():
                    logger.error("Observer thread died unexpectedly")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            event_handler.is_shutting_down = True
            observer.stop()
            click.echo("\nStopping watch...")
        except Exception as e:
            logger.error(f"Unexpected error in watch loop: {str(e)}")
            event_handler.is_shutting_down = True
            observer.stop()
        finally:
            logger.info("Waiting for observer to complete...")
            observer.join(timeout=10)
            if observer.is_alive():
                logger.warning("Observer failed to stop gracefully")
        
    except Exception as e:
        logger.error(f"Error in watch command: {str(e)}")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli()

