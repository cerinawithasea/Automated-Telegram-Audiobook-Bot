from typing import Dict, Optional, Union
from pathlib import Path
import logging
from datetime import timedelta
from mutagen.mp4 import MP4, MP4StreamInfoError
from mutagen import MutagenError

class AudiobookMetadata:
    """Handles metadata extraction and formatting for audiobook files.
    
    This class provides a robust interface for extracting and formatting metadata
    from audiobook files (primarily M4B), with proper error handling and fallbacks.
    
    Attributes:
        file_path (Path): Path to the audiobook file
        raw_metadata (Dict): Raw metadata extracted from the file
        duration_seconds (float): Duration of the audiobook in seconds
    """
    
    def __init__(self, file_path: Union[str, Path]) -> None:
        """Initialize with audiobook file path.
        
        Args:
            file_path: Path to the audiobook file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file type is not supported
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Audiobook file not found: {file_path}")
        
        self.raw_metadata: Dict = {}
        self.duration_seconds: float = 0.0
        self._extract_metadata()
    
    def _extract_metadata(self) -> None:
        """Extract metadata from the audiobook file.
        
        Raises:
            ValueError: If metadata extraction fails
        """
        try:
            audio = MP4(self.file_path)
            self.raw_metadata = dict(audio.tags or {})
            self.duration_seconds = audio.info.length
        except MP4StreamInfoError:
            logging.error(f"Failed to read audio stream from {self.file_path}")
            raise ValueError("Invalid audio file format")
        except MutagenError as e:
            logging.error(f"Failed to extract metadata: {e}")
            raise ValueError(f"Metadata extraction failed: {e}")
    
    def get_title(self) -> str:
        """Get the audiobook title.
        
        Returns:
            str: Title of the audiobook, or filename if not found
        """
        return self._get_tag("©nam") or self.file_path.stem
    
    def get_author(self) -> Optional[str]:
        """Get the book's author/composer.
        
        Returns:
            Optional[str]: Author name if found, None otherwise
        """
        return self._get_tag("©wrt")
    
    def get_narrator(self) -> Optional[str]:
        """Get the narrator/artist name.
        
        Returns:
            Optional[str]: Narrator name if found, None otherwise
        """
        return self._get_tag("©ART")
    
    def get_publisher(self) -> Optional[str]:
        """Get the publisher name.
        
        Returns:
            Optional[str]: Publisher name if found, None otherwise
        """
        return self._get_tag("©pub")
    
    def get_release_year(self) -> Optional[str]:
        """Get the release year.
        
        Returns:
            Optional[str]: Release year if found, None otherwise
        """
        return self._get_tag("©day")
    
    def get_duration_formatted(self) -> str:
        """Get formatted duration string.
        
        Returns:
            str: Duration in format "Xd HH:MM:SS" or "HH:MM:SS"
        """
        duration = timedelta(seconds=int(self.duration_seconds))
        days = duration.days
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        seconds = duration.seconds % 60
        
        if days > 0:
            return f"{days}d {hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _get_tag(self, key: str) -> Optional[str]:
        """Safely extract a metadata tag value.
        
        Args:
            key: Metadata key to extract
            
        Returns:
            Optional[str]: Tag value if found, None otherwise
        """
        try:
            value = self.raw_metadata.get(key, [None])[0]
            return str(value) if value is not None else None
        except (IndexError, TypeError, ValueError):
            return None
    
    def format_caption(self) -> str:
        """Format metadata into a Telegram caption.
        
        Returns:
            str: Formatted caption string with available metadata
        """
        title = self.get_title()
        author = self.get_author()
        narrator = self.get_narrator()
        duration = self.get_duration_formatted()
        year = self.get_release_year()
        publisher = self.get_publisher()
        
        caption_parts = [title]
        
        if author:
            caption_parts.append(f"by {author}")
        if narrator:
            caption_parts.append(f"Narrated by {narrator}")
        if duration:
            caption_parts.append(f"Length: {duration}")
        if year:
            caption_parts.append(f"Release date: {year}")
        if publisher:
            caption_parts.append(f"Publisher: {publisher}")
        
        caption_parts.append("#audiobook")
        return "\n".join(caption_parts)
