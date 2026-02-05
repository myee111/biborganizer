"""
Image processing utilities for Photo Organizer V2.

Handles image loading, format conversion, resizing, and compression.
"""

import base64
from io import BytesIO
from pathlib import Path
from PIL import Image
import pillow_heif


# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()


# Supported image formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic', '.heif'}


def load_image(file_path):
    """
    Load an image from file, handling HEIC/HEIF conversion.

    Args:
        file_path: Path to image file

    Returns:
        PIL.Image: Loaded image object

    Raises:
        ValueError: If file format is not supported
        FileNotFoundError: If file does not exist
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")

    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported image format: {path.suffix}. "
            f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )

    # Load image (HEIC/HEIF handled automatically by pillow_heif)
    image = Image.open(file_path)

    # Convert to RGB if necessary (handles RGBA, P, L, etc.)
    if image.mode not in ('RGB', 'L'):
        image = image.convert('RGB')

    return image


def prepare_image_for_api(image, max_dimension=3000, max_size_bytes=3.8 * 1024 * 1024):
    """
    Prepare image for API submission by resizing and compressing.
    GUARANTEED to return image under max_size_bytes.

    Args:
        image: PIL.Image object
        max_dimension: Maximum width or height in pixels (default: 3000 for safety)
        max_size_bytes: Maximum file size in bytes (default: 3.8MB for safety margin)

    Returns:
        bytes: JPEG-encoded image data, guaranteed under max_size_bytes
    """
    # Ensure RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Start with aggressive resize
    width, height = image.size
    if width > max_dimension or height > max_dimension:
        # Calculate new dimensions maintaining aspect ratio
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))

        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Helper function to compress
    def compress_image(img, quality):
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        size = buffer.tell()
        buffer.seek(0)
        return buffer.read(), size

    # Try reducing quality first
    for quality in [80, 70, 60, 50, 40, 30, 25]:
        data, size = compress_image(image, quality)
        if size <= max_size_bytes:
            return data

    # Quality reduction wasn't enough - progressively shrink the image
    current_image = image
    width, height = image.size

    # Try progressively smaller sizes
    for target_pixels in [2000, 1600, 1200, 1000, 800, 600]:
        if width > height:
            new_width = min(target_pixels, width)
            new_height = int(height * (new_width / width))
        else:
            new_height = min(target_pixels, height)
            new_width = int(width * (new_height / height))

        current_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Try multiple qualities at this size
        for quality in [70, 60, 50, 40, 30]:
            data, size = compress_image(current_image, quality)
            if size <= max_size_bytes:
                return data

    # ABSOLUTE LAST RESORT: Keep shrinking until it fits
    # This GUARANTEES we return something under the limit
    current_width = 500
    while current_width > 100:
        if width > height:
            new_width = current_width
            new_height = int(height * (current_width / width))
        else:
            new_height = current_width
            new_width = int(width * (current_width / height))

        tiny_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        for quality in [50, 40, 30, 20]:
            data, size = compress_image(tiny_image, quality)
            if size <= max_size_bytes:
                return data

        current_width -= 50

    # If we got here, return the smallest possible (should never happen)
    tiny = image.resize((200, int(200 * height / width)), Image.Resampling.LANCZOS)
    data, _ = compress_image(tiny, 20)
    return data


def encode_image_base64(image_bytes):
    """
    Encode image bytes to base64 string.

    Args:
        image_bytes: Image data as bytes

    Returns:
        str: Base64-encoded string
    """
    return base64.b64encode(image_bytes).decode('utf-8')


def is_supported_image(file_path):
    """
    Check if a file is a supported image format.

    Args:
        file_path: Path to file

    Returns:
        bool: True if file extension is supported
    """
    return Path(file_path).suffix.lower() in SUPPORTED_FORMATS
