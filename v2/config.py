"""
Configuration management for Photo Organizer V2.

Loads settings from .env file and provides validation.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config():
    """
    Load configuration from .env file.

    Returns:
        dict: Configuration dictionary with the following keys:
            - project_id: GCP project ID (required)
            - region: Vertex AI region (default: us-central1)
            - model: Claude model name (default: claude-3-5-sonnet@20240620)
            - confidence_threshold: Similarity threshold (default: 0.7)

    Raises:
        ValueError: If required configuration is missing
    """
    # Load .env file from project root
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)

    config = {
        'project_id': os.getenv('VERTEX_PROJECT_ID'),
        'region': os.getenv('VERTEX_REGION', 'us-central1'),
        'model': os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet@20240620'),
        'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
    }

    validate_config(config)
    return config


def validate_config(config):
    """
    Validate that required configuration is present.

    Args:
        config: Configuration dictionary

    Raises:
        ValueError: If required fields are missing or invalid
    """
    if not config.get('project_id'):
        raise ValueError(
            "VERTEX_PROJECT_ID is required in .env file. "
            "Please set your GCP project ID."
        )

    if not config.get('region'):
        raise ValueError("VERTEX_REGION cannot be empty")

    if not config.get('model'):
        raise ValueError("CLAUDE_MODEL cannot be empty")

    threshold = config.get('confidence_threshold', 0)
    if not 0 <= threshold <= 1:
        raise ValueError(
            f"CONFIDENCE_THRESHOLD must be between 0 and 1, got {threshold}"
        )
