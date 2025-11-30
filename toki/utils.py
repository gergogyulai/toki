"""Utility functions for file processing."""

import hashlib
import datetime
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from hachoir.stream import InputStreamError

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4", ".mov", ".avi", ".heic"}
HASH_LENGTH = 8


def compute_file_hash(path: Path, hash_length: int = HASH_LENGTH) -> str:
    """Compute MD5 hash of file content."""
    md5_hash = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()[:hash_length]
    except Exception:
        return "00000000"[:hash_length]


def get_exif_datetime(path: Path) -> Tuple[Optional[datetime.datetime], str]:
    """Extract datetime and camera model from EXIF metadata."""
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return None, "Unknown"
            
            dt = None
            camera = "Unknown"
            
            if 36867 in exif:  # DateTimeOriginal
                dt = datetime.datetime.strptime(
                    exif[36867], "%Y:%m:%d %H:%M:%S"
                )
            elif 306 in exif:  # DateTime
                dt = datetime.datetime.strptime(exif[306], "%Y:%m:%d %H:%M:%S")
            
            if 272 in exif:  # Model
                camera = str(exif[272]).replace(" ", "_")
            
            return dt, camera
    except Exception:
        return None, "Unknown"


def get_video_datetime(path: Path) -> Optional[datetime.datetime]:
    """Extract datetime from video metadata."""
    try:
        parser = createParser(str(path))
        if not parser:
            return None
        metadata = extractMetadata(parser)
        if metadata and metadata.has("creation_date"):
            result = metadata.get("creation_date")
            parser.stream.close()
            return result
        parser.stream.close()
    except (Exception, InputStreamError):
        return None
    return None


def get_file_datetime(path: Path) -> Tuple[Optional[datetime.datetime], str]:
    """Extract datetime from file metadata (EXIF or video)."""
    ext = path.suffix.lower()
    
    if ext in {".jpg", ".jpeg", ".png", ".heic"}:
        return get_exif_datetime(path)
    elif ext in {".mp4", ".mov", ".avi"}:
        dt = get_video_datetime(path)
        return dt, "Unknown"
    
    return None, "Unknown"
