# Audiobook Caption Generator and Uploader

A Python tool that automatically extracts metadata from M4B audiobooks, generates formatted captions, and uploads them to Telegram. Ideal for organizing and backing up your audiobook collection with consistent, metadata-rich captions.

## Features

- Extracts metadata from M4B audiobook files (title, author, narrator, length, etc.)
- Generates formatted captions using audiobook metadata
- Uploads audiobooks to Telegram with captions
- Handles large files efficiently
- Easy to use command-line interface
- Automatically moves processed files to a separate directory after successful upload

## Prerequisites
## Prerequisites

- Python 3.6 or later
- Telegram account
- Telegram Bot Token (obtained from @BotFather)
- API credentials from my.telegram.org

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

1. Create a Telegram bot:
- Message @BotFather on Telegram
- Use /newbot command to create a new bot
- Save the bot token provided

2. Get your API credentials:
- Visit https://my.telegram.org/apps
- Create a new application
- Save your API_ID and API_HASH

3. Set up environment variables:
```bash
export BOT_TOKEN="your_bot_token"
export API_ID="your_api_id"
export API_HASH="your_api_hash"
export TELEGRAM_CHAT_ID="your_chat_id"
```

Or create a .env file:
```
BOT_TOKEN=your_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
TELEGRAM_CHAT_ID=your_chat_id
```

## Usage

## Directory Structure

The tool uses the following directory structure:
- `/path/to/watch` - Directory to monitor for new audiobooks
- `/path/to/watch/processed` - Directory where successfully uploaded files are moved

When running in watch mode, files are automatically moved to the 'processed' subdirectory after successful upload.

1. Generate caption for an audiobook:
```bash
python main.py caption /path/to/your/audiobook.m4b
```

2. Upload audiobook with caption:
```bash
python main.py upload /path/to/your/audiobook.m4b
```

3. Test the setup:
```bash
python main.py test
```

4. Watch directory for new audiobooks:
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

1. **Bot not responding**:
- Verify your BOT_TOKEN is correct
- Ensure you've started a chat with your bot
- Check if the bot has proper permissions

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

3. **Bot initialization fails**
- Double-check your API_ID and API_HASH
- Ensure BOT_TOKEN is valid and bot is active
- Try restarting your bot in @BotFather

4. **Caption formatting issues**
- Check for special characters in metadata
- Ensure metadata is UTF-8 encoded
- Verify tag names match expected format

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
