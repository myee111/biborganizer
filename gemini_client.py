"""
Gemini API client for image analysis and face identification.
Supports both Google AI Studio (API key) and Vertex AI.
"""

import os
import json
from io import BytesIO
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
MAX_IMAGE_SIZE_MB = 5.0
MAX_IMAGE_DIMENSION = 8000
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic'}

# Available Gemini models
GEMINI_MODELS = {
    'flash': 'gemini-2.0-flash-exp',
    'flash-1.5': 'gemini-1.5-flash',
    'pro': 'gemini-1.5-pro',
    'pro-2': 'gemini-2.0-flash-exp'
}


def get_model_name() -> str:
    """
    Get the Gemini model to use from environment or config.

    Returns:
        Model identifier string
    """
    model_env = os.getenv('GEMINI_MODEL', 'flash')

    if model_env in GEMINI_MODELS:
        return GEMINI_MODELS[model_env]

    # Allow custom model IDs
    return model_env


def get_gemini_client():
    """
    Initialize Gemini client with API key.

    Returns:
        Configured genai client
    """
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in environment. "
            "Get your API key from: https://aistudio.google.com/apikey"
        )

    client = genai.Client(api_key=api_key)
    print(f"Using Gemini API (model: {get_model_name()})")
    return client


def load_and_prepare_image(file_path: str) -> bytes:
    """
    Load image, handle HEIC conversion, resize if needed, and return bytes.

    Args:
        file_path: Path to image file

    Returns:
        Image data as bytes
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported image format: {suffix}")

    # Handle HEIC images
    if suffix == '.heic':
        try:
            import pillow_heif
            heif_file = pillow_heif.read_heif(file_path)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
            )
        except ImportError:
            raise ValueError(
                "pillow-heif is required to process HEIC images. "
                "Install it with: pip install pillow-heif"
            )
    else:
        image = Image.open(file_path)

    # Convert to RGB if necessary
    if image.mode in ('RGBA', 'P', 'LA'):
        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        rgb_image.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
        image = rgb_image
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    # Resize if image is too large
    width, height = image.size
    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        ratio = min(MAX_IMAGE_DIMENSION / width, MAX_IMAGE_DIMENSION / height)
        new_size = (int(width * ratio), int(height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    # Compress to stay under size limit
    buffer = BytesIO()
    quality = 95

    while quality > 20:
        buffer.seek(0)
        buffer.truncate()
        image.save(buffer, format='JPEG', quality=quality, optimize=True)
        size_mb = buffer.tell() / (1024 * 1024)

        if size_mb <= MAX_IMAGE_SIZE_MB:
            break
        quality -= 10

    buffer.seek(0)
    return buffer.read()


def analyze_faces_in_image(image_path: str, prompt: str, model: Optional[str] = None) -> str:
    """
    Send image to Gemini with custom prompt for analysis.

    Args:
        image_path: Path to image file
        prompt: Analysis prompt for Gemini
        model: Gemini model to use (optional)

    Returns:
        Gemini's response text
    """
    client = get_gemini_client()

    if model is None:
        model = get_model_name()

    try:
        # Load image
        image_bytes = load_and_prepare_image(image_path)

        # Create image part
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )

        # Generate response
        response = client.models.generate_content(
            model=model,
            contents=[image_part, prompt],
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=2048,
            )
        )

        return response.text

    except Exception as e:
        raise Exception(f"Gemini API error analyzing {image_path}: {str(e)}")


def generate_facial_description(image_path: str) -> str:
    """
    Generate detailed facial description for database entry.

    Args:
        image_path: Path to reference image

    Returns:
        Detailed facial description text
    """
    prompt = """Analyze this image and provide a detailed description of the person's facial features.

Focus on permanent, distinctive characteristics:
- Face shape (oval, round, square, heart-shaped, etc.)
- Eye color, shape, and spacing
- Eyebrow shape and thickness
- Nose shape and size
- Mouth and lip characteristics
- Chin and jawline
- Skin tone
- Hair color, texture, and style (note this may change)
- Distinctive features (dimples, freckles, scars, etc.)
- Approximate age range
- Any other notable facial characteristics

Be specific and detailed. This description will be used to identify this person in other photos.
If multiple people are in the image, describe only the most prominent person."""

    return analyze_faces_in_image(image_path, prompt)


def detect_and_describe_all_faces(image_path: str) -> str:
    """
    Detect all faces in image and provide descriptions.

    Args:
        image_path: Path to image file

    Returns:
        Description of all detected faces in JSON format
    """
    prompt = """Analyze this image and identify all human faces present.

For each face detected, provide:
1. A brief description of their location in the image (e.g., "left side", "center", "background")
2. Detailed facial features similar to a police description

If no faces are detected, respond with "NO_FACES_DETECTED".

Format your response as a JSON array:
[
  {
    "position": "center of image",
    "description": "detailed facial description..."
  },
  ...
]

If no faces found, return: {"faces": []}"""

    return analyze_faces_in_image(image_path, prompt)


def compare_face_descriptions(description1: str, description2: str) -> float:
    """
    Use Gemini to compare two facial descriptions and return similarity score.

    Args:
        description1: First facial description
        description2: Second facial description

    Returns:
        Similarity score from 0.0 (completely different) to 1.0 (same person)
    """
    client = get_gemini_client()
    model_name = get_model_name()

    prompt = f"""Compare these two facial descriptions and determine if they describe the same person.

Description 1:
{description1}

Description 2:
{description2}

Analyze the permanent facial features (face shape, eye characteristics, nose, bone structure, etc.).
Ignore temporary features like hair style, facial hair, or makeup unless they're very distinctive.

Provide your response as a JSON object with:
- "similarity": a number from 0.0 to 1.0 (0.0 = definitely different people, 1.0 = definitely same person)
- "reasoning": brief explanation of your assessment

Example: {{"similarity": 0.85, "reasoning": "Very similar face shape, eye color, and nose structure. Minor differences could be due to age or photo angle."}}"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=1024,
            )
        )

        result_text = response.text

        # Extract JSON from response
        if "```json" in result_text:
            start = result_text.find("```json") + 7
            end = result_text.find("```", start)
            result_text = result_text[start:end].strip()
        elif "```" in result_text:
            start = result_text.find("```") + 3
            end = result_text.find("```", start)
            result_text = result_text[start:end].strip()

        result = json.loads(result_text)
        return float(result.get("similarity", 0.0))

    except Exception as e:
        print(f"Warning: Error comparing descriptions: {e}")
        return 0.0
