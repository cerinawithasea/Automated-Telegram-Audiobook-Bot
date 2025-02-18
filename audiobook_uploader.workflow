name: Audiobook Uploader
description: Commands for managing automated audiobook uploading to Telegram

# Workflow for managing the audiobook uploading system
tags:
- automation
- telegram
- audiobooks

commands:
- name: Start Watching Audiobooks Directory
    command: python3 main.py watch '/Users/cerinawithasea/audiobooks/completed'
    description: Monitor the completed audiobooks directory for new files and automatically upload them
    tags:
    - watch
    - upload
    source_url: https://github.com/yourusername/ChannelAutoCaption
    authors:
    - CerinaWithASea
    working-directory: ~/ChannelAutoCaption
    environment:
    - name: AUDIOBOOKS_DIR
        value: "/Users/cerinawithasea/audiobooks/completed"
    examples: |
    This command will:
    1. Watch the specified directory for new .m4b files
    2. Process and upload new audiobooks to Telegram
    3. Log all activities to audiobook_uploader.log

- name: Setup Audiobooks Directory
    command: mkdir -p ~/audiobooks/completed
    description: Create the necessary directory structure for audiobook uploading
    tags:
    - setup
    working-directory: "~"
    examples: |
    Creates the following directory structure:
    ~/audiobooks/
    └── completed/

- name: Check Directory Status
    command: ls -la ~/audiobooks/completed
    description: List all audiobooks in the completed directory
    tags:
    - utility
    working-directory: "~"

- name: View Upload Logs
    command: tail -f ~/ChannelAutoCaption/audiobook_uploader.log
    description: View real-time log output from the uploader
    tags:
    - logs
    working-directory: "~"

- name: Test Upload Single File
    command: python3 main.py upload '/Users/cerinawithasea/audiobooks/completed/${filename}'
    description: Test upload a single audiobook file
    tags:
    - test
    - upload
    working-directory: ~/ChannelAutoCaption
    arguments:
    - name: filename
        description: Name of the audiobook file to upload
        default_value: "test.m4b"
    environment:
    - name: AUDIOBOOKS_DIR
        value: "/Users/cerinawithasea/audiobooks/completed"

