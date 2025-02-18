from mutagen.mp4 import MP4
from datetime import timedelta
import os

def format_duration(milliseconds):
    """Convert milliseconds to human readable duration."""
    seconds = int(milliseconds / 1000)
    days = seconds // 86400
    remaining = seconds % 86400
    hours = remaining // 3600
    remaining = remaining % 3600
    minutes = remaining // 60
    remaining_seconds = remaining % 60
    
    if days > 0:
        return f"{days}d {hours:02d}:{minutes:02d}:{remaining_seconds:02d}"
    elif hours > 0:
        return f"{hours}:{minutes:02d}:{remaining_seconds:02d}"
    else:
        return f"{minutes}:{remaining_seconds:02d}"

def extract_metadata(file_path):
    """Extract metadata from M4B file."""
    try:
        audio = MP4(file_path)
        
        # Print all available tags for debugging
        print("Available tags:", audio.tags.keys())
        
        # Try multiple possible publisher tags
        publisher = (
            audio.tags.get('cprt', [None])[0] or  # Copyright tag
            audio.tags.get('©pub', [None])[0] or  # Publisher tag
            audio.tags.get('purd', [None])[0] or  # Purchase date
            'Unknown Publisher'
        )
        
        metadata = {
            'title': audio.tags.get('©nam', ['Unknown Title'])[0],
            'author': audio.tags.get('©wrt', ['Unknown Author'])[0],
            'narrator': audio.tags.get('©ART', ['Unknown Narrator'])[0],
            'year': audio.tags.get('©day', ['Unknown'])[0],
            'publisher': publisher,
            'mediatype': 'Audiobook',
            'duration': format_duration(audio.info.length * 1000)  # Convert seconds to milliseconds
        }
        return metadata
        
    except Exception as e:
        raise Exception(f"Error reading metadata: {str(e)}")

def format_caption(metadata):
    """Generate caption from metadata in specified format."""
    return f"{metadata['title']}\n"\
        f"by {metadata['author']}\n"\
        f"Narrated by {metadata['narrator']}\n"\
        f"Length: {metadata['duration']}\n"\
        f"Release date: {metadata['year']}\n"\
        f"Publisher: {metadata['publisher']}\n"\
        f"#{metadata['mediatype']}"

def process_audiobook(file_path):
    """Process audiobook file and return formatted caption."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    if not file_path.lower().endswith('.m4b'):
        raise ValueError("File must be an M4B file")
        
    try:
        metadata = extract_metadata(file_path)
        return format_caption(metadata)
    except Exception as e:
        raise Exception(f"Error processing audiobook: {str(e)}")

if __name__ == "__main__":
    # Example usage
    try:
        file_path = "path/to/your/audiobook.m4b"
        caption = process_audiobook(file_path)
        print(caption)
    except Exception as e:
        print(f"Error: {str(e)}")
