"""
Claude API client for image analysis and face identification.
Handles image loading, encoding, and communication with Claude Vision API.
Supports both direct Anthropic API and Google Cloud Vertex AI.
"""

import os
import base64
import json
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict, Any, Union

from anthropic import Anthropic, AnthropicVertex
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
MAX_IMAGE_SIZE_MB = 5.0
MAX_IMAGE_DIMENSION = 8000
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic'}

# Available Claude models for Anthropic API
ANTHROPIC_MODELS = {
    'sonnet-4.5': 'claude-sonnet-4-5-20250929',
    'opus-4.5': 'claude-opus-4-5-20241101',
    'sonnet-3.7': 'claude-3-7-sonnet-20250219',
    'sonnet-3.5': 'claude-3-5-sonnet-20241022',
    'haiku-3.5': 'claude-3-5-haiku-20241022',
    'opus-3.5': 'claude-3-5-opus-20241022',
    'opus-3': 'claude-3-opus-20240229'
}

# Available Claude models for Vertex AI (different identifiers)
# Note: Use stable versions that are widely available
VERTEX_MODELS = {
    'sonnet-3.5': 'claude-3-5-sonnet@20240620',  # Stable version
    'haiku-3.5': 'claude-3-5-haiku@20241022',
    'opus-3': 'claude-3-opus@20240229',
    # Note: Newer models may not be available on Vertex AI yet
    # Fallback to closest available model
    'sonnet-4.5': 'claude-3-5-sonnet@20240620',  # Fallback to 3.5 stable
    'opus-4.5': 'claude-3-opus@20240229',  # Fallback to 3
    'sonnet-3.7': 'claude-3-5-sonnet@20240620',  # Fallback to 3.5 stable
    'opus-3.5': 'claude-3-opus@20240229'  # Fallback to 3
}


def get_model_name() -> str:
    """
    Get the Claude model to use from environment or config.
    Returns appropriate model identifier based on authentication method.

    Returns:
        Model identifier string
    """
    # Check if using Vertex AI
    use_vertex = os.getenv('USE_VERTEX_AI', 'false').lower() == 'true'
    model_map = VERTEX_MODELS if use_vertex else ANTHROPIC_MODELS

    # Check environment variable first
    model_env = os.getenv('CLAUDE_MODEL')

    if model_env:
        # If it's a short name, resolve it
        if model_env in model_map:
            resolved_model = model_map[model_env]
            # Warn if using fallback on Vertex AI
            if use_vertex and model_env in ['sonnet-4.5', 'opus-4.5', 'sonnet-3.7', 'opus-3.5']:
                print(f"Note: {model_env} not yet available on Vertex AI. Using {resolved_model} instead.")
            return resolved_model
        # Otherwise use as-is (allows custom model IDs)
        return model_env

    # Try loading from config.json
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                model_config = config.get('model', 'sonnet-3.5')

                # If it's a short name, resolve it
                if model_config in model_map:
                    resolved_model = model_map[model_config]
                    # Warn if using fallback on Vertex AI
                    if use_vertex and model_config in ['sonnet-4.5', 'opus-4.5', 'sonnet-3.7', 'opus-3.5']:
                        print(f"Note: {model_config} not yet available on Vertex AI. Using {resolved_model} instead.")
                    return resolved_model
                return model_config
    except Exception:
        pass

    # Default model based on auth method
    if use_vertex:
        return 'claude-3-5-sonnet@20240620'  # Default to stable Sonnet 3.5
    else:
        return 'claude-sonnet-4-5-20250929'


def get_claude_client() -> Union[Anthropic, AnthropicVertex]:
    """
    Initialize and return Claude client from environment.
    Supports both Anthropic API and Vertex AI based on configuration.

    Returns:
        Anthropic or AnthropicVertex: Initialized client

    Raises:
        ValueError: If required credentials not found in environment
    """
    # Check if using Vertex AI
    use_vertex = os.getenv('USE_VERTEX_AI', 'false').lower() == 'true'

    if use_vertex:
        # Vertex AI configuration
        project_id = os.getenv('VERTEX_PROJECT_ID')
        region = os.getenv('VERTEX_REGION', 'us-east5')

        if not project_id:
            raise ValueError(
                "VERTEX_PROJECT_ID not found in environment. "
                "Please add it to your .env file for Vertex AI authentication."
            )

        print(f"Using Vertex AI authentication (Project: {project_id}, Region: {region})")

        return AnthropicVertex(
            project_id=project_id,
            region=region
        )
    else:
        # Direct Anthropic API
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment. "
                "Please create a .env file with your API key, or set USE_VERTEX_AI=true "
                "to use Vertex AI authentication."
            )

        return Anthropic(api_key=api_key)


def load_and_encode_image(file_path: str) -> tuple[str, str]:
    """
    Load image, handle HEIC conversion, resize if needed, and base64 encode.

    Args:
        file_path: Path to image file

    Returns:
        Tuple of (base64_encoded_data, media_type)

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image format is not supported
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
            media_type = "image/jpeg"  # Convert to JPEG
        except ImportError:
            raise ValueError(
                "pillow-heif is required to process HEIC images. "
                "Install it with: pip install pillow-heif"
            )
    else:
        image = Image.open(file_path)
        # Map file extension to media type
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(suffix, 'image/jpeg')

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
        # Maintain aspect ratio
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

    # Encode to base64
    buffer.seek(0)
    encoded = base64.standard_b64encode(buffer.read()).decode('utf-8')

    return encoded, media_type


def analyze_faces_in_image(image_path: str, prompt: str, model: Optional[str] = None) -> str:
    """
    Send image to Claude with custom prompt for analysis.

    Args:
        image_path: Path to image file
        prompt: Analysis prompt for Claude
        model: Claude model to use

    Returns:
        Claude's response text

    Raises:
        Exception: If API call fails
    """
    client = get_claude_client()
    encoded_image, media_type = load_and_encode_image(image_path)

    # Use configured model if none specified
    if model is None:
        model = get_model_name()

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": encoded_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        return response.content[0].text

    except Exception as e:
        raise Exception(f"Claude API error analyzing {image_path}: {str(e)}")


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
        Description of all detected faces
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
    Use Claude to compare two facial descriptions and return similarity score.

    Args:
        description1: First facial description
        description2: Second facial description

    Returns:
        Similarity score from 0.0 (completely different) to 1.0 (same person)
    """
    client = get_claude_client()

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
        model = get_model_name()

        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        result_text = response.content[0].text

        # Extract JSON from response
        # Claude might wrap it in markdown code blocks
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
