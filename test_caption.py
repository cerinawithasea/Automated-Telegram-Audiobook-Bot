#!/usr/bin/env python3
import sys
import os
from caption_generator import extract_metadata, format_caption

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_caption.py <path_to_audiobook.m4b>")
        sys.exit(1)

    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist!")
        sys.exit(1)
        
    if not file_path.lower().endswith('.m4b'):
        print("Warning: File does not have .m4b extension. Results may be unreliable.")
    
    try:
        print("\nExtracting metadata...")
        metadata = extract_metadata(file_path)
        
        print("\nRaw Metadata:")
        for key, value in metadata.items():
            print(f"{key}: {value}")
            
        print("\nFormatted Caption:")
        caption = format_caption(metadata)
        print("-" * 50)
        print(caption)
        print("-" * 50)
        
    except Exception as e:
        print(f"\nError processing file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
