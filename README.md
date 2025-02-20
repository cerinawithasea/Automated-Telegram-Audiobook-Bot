# Audiobook Caption Generator and Uploader (upload not working yet)

A Python tool that automatically extracts metadata from M4B audiobooks, generates formatted captions, and uploads them to Telegram. Ideal for organizing and backing up your audiobook collection with consistent, metadata-rich captions.

## Features

- Extracts metadata from M4B audiobook files (title, author, narrator, length, etc.)
- Generates formatted captions using audiobook metadata
- Uploads audiobooks to Telegram with captions
- Handles large files efficiently
- Easy to use command-line interface
- Automatically moves processed files to a separate directory after successful upload

## Prerequisites

- Python 3.8 or later
- Telegram account
- API credentials from my.telegram.org (API_ID and API_HASH)
- Active Telegram group/channel for uploading

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/audiobook-caption-generator.git
cd audiobook-caption-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Get your API credentials:
- Visit https://my.telegram.org/apps
- Create a new application
- Save your API_ID and API_HASH

2. Set up your upload channel:
- Create a Telegram group or channel
- Note down the group/channel ID (you can use @username_to_id_bot)
- Ensure you have admin rights in the group/channel

3. Create a .env file in the project root:
```
API_ID=your_api_id
API_HASH=your_api_hash
TELEGRAM_CHAT_ID=your_chat_id
```

Note: The chat_id for groups/channels should include the -100 prefix
(e.g., -1001234567890)

## Usage

## Directory Structure

The tool uses the following directory structure:
- `/path/to/watch` - Directory to monitor for new audiobooks
- `/path/to/watch/processed` - Directory where successfully uploaded files are moved

When running in watch mode, files are automatically moved to the 'processed' subdirectory after successful upload.

1. Test the uploader setup:
```bash
python test_uploader.py /path/to/your/audiobook.m4b
```

2. Upload an audiobook with metadata:
```python
from telegram_uploader import TelegramUploader

async def upload_book():
    uploader = TelegramUploader(
        api_id="your_api_id",
        api_hash="your_api_hash"
    )
    
    await uploader.upload_audio(
        file_path="/path/to/audiobook.m4b",
        chat_id="your_chat_id",
        title="Book Title",
        performer="Author Name"
    )
```

3. Watch directory for new audiobooks:
```bash
python main.py watch /path/to/watch/directory
```
Files will be automatically uploaded and moved to a 'processed' subdirectory after successful upload.

5. Show help:
```bash
python main.py --help
```

## Metadata Format

The tool generates captions in the following format:
```
[Title]
by [Author]
Narrated by [Narrator]
Length: [Duration]
Release date: [Year]
Publisher: [Publisher]
#Audiobook
```

## Supported File Formats

- M4B (primary format)
- MP3 (limited support)
- M4A (limited support)

The tool is optimized for M4B files with proper metadata tags.

## Metadata Tags

The tool looks for the following metadata tags:
- title (required)
- composer/author (required)
- artist/narrator (required)
- duration/length (automatically calculated)
- year (optional)
- publisher (optional)

If you're using MP3Tag, use these fields:
- Title
- Composer
- Artist
- Year
- Publisher

## Troubleshooting

1. **Upload Errors**:
- Ensure your API credentials are correct
- Check your internet connection
- Verify group/channel permissions
- Double-check the chat_id format (should include -100 prefix)

2. **Metadata not showing**:
- Verify your audiobook has proper metadata tags
- Check supported metadata fields in the documentation
- Try using MP3Tag to add missing metadata

3. **Upload failures**:
- Check your internet connection
- Verify file size is within Telegram limits (2GB for normal accounts)
- Ensure bot has permission to send files

4. **Environment Variables**:
- Make sure all required variables are set
- Check for typos in variable names
- Verify credentials are correct

## Common Issues and Solutions

1. **File size too large**
- Files over 2GB need Telegram Premium
- Consider splitting large audiobooks into parts

2. **Missing metadata**
- Use MP3Tag to add metadata before uploading
- Required fields: Title, Author, Narrator

3. **Authentication Issues**:
- Verify API_ID and API_HASH are correct
- Check your .env file configuration
- Ensure you have proper permissions in the group/channel
- Try clearing the session file and re-authenticating

4. **Caption formatting issues**:
- Check for special characters in metadata
- Ensure metadata is UTF-8 encoded
- Verify tag names match expected format

5. **Large File Uploads**:
- Supported up to 2GB file size
- Progress bar shows upload status
- ETA and speed information provided
- Automatic retry on network errors

## Acknowledgments

This project is built upon the work of:
- [ChannelAutoCaption](https://github.com/samadii/ChannelAutoCaption) by samadii
- [telegram-upload](https://github.com/Nekmo/telegram-upload) by Nekmo

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License
