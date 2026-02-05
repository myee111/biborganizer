"""
Vision client wrapper that automatically selects Claude or Gemini based on configuration.
Provides a unified interface for face detection and analysis.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_provider() -> str:
    """
    Get the configured AI provider (claude or gemini).

    Returns:
        Provider name: 'claude' or 'gemini'
    """
    return os.getenv('AI_PROVIDER', 'gemini').lower()


def generate_facial_description(image_path: str) -> str:
    """
    Generate detailed facial description for database entry.
    Automatically uses configured provider (Claude or Gemini).

    Args:
        image_path: Path to reference image

    Returns:
        Detailed facial description text
    """
    provider = get_provider()

    if provider == 'gemini':
        from gemini_client import generate_facial_description as gemini_gen
        return gemini_gen(image_path)
    else:
        from claude_client import generate_facial_description as claude_gen
        return claude_gen(image_path)


def detect_and_describe_all_faces(image_path: str) -> str:
    """
    Detect all faces in image and provide descriptions.
    Automatically uses configured provider (Claude or Gemini).

    Args:
        image_path: Path to image file

    Returns:
        Description of all detected faces
    """
    provider = get_provider()

    if provider == 'gemini':
        from gemini_client import detect_and_describe_all_faces as gemini_detect
        return gemini_detect(image_path)
    else:
        from claude_client import detect_and_describe_all_faces as claude_detect
        return claude_detect(image_path)


def compare_face_descriptions(description1: str, description2: str) -> float:
    """
    Compare two facial descriptions and return similarity score.
    Automatically uses configured provider (Claude or Gemini).

    Args:
        description1: First facial description
        description2: Second facial description

    Returns:
        Similarity score from 0.0 to 1.0
    """
    provider = get_provider()

    if provider == 'gemini':
        from gemini_client import compare_face_descriptions as gemini_compare
        return gemini_compare(description1, description2)
    else:
        from claude_client import compare_face_descriptions as claude_compare
        return claude_compare(description1, description2)
