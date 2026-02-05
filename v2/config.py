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
            - confidence_threshold: Similarity threshold (default: 0.5)
            - timestamp_exact_match_seconds: Time window for automatic clustering (default: 10)
            - timestamp_high_priority_seconds: Time window for high priority clustering (default: 30)

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
        'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', '0.5')),
        'timestamp_exact_match_seconds': int(os.getenv('TIMESTAMP_EXACT_MATCH_SECONDS', '10')),
        'timestamp_high_priority_seconds': int(os.getenv('TIMESTAMP_HIGH_PRIORITY_SECONDS', '30'))
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

    exact_match = config.get('timestamp_exact_match_seconds', 0)
    if exact_match < 0 or exact_match > 300:
        raise ValueError(
            f"TIMESTAMP_EXACT_MATCH_SECONDS must be between 0 and 300, got {exact_match}"
        )

    high_priority = config.get('timestamp_high_priority_seconds', 0)
    if high_priority < 0 or high_priority > 300:
        raise ValueError(
            f"TIMESTAMP_HIGH_PRIORITY_SECONDS must be between 0 and 300, got {high_priority}"
        )

    if exact_match > high_priority:
        raise ValueError(
            f"TIMESTAMP_EXACT_MATCH_SECONDS ({exact_match}) cannot be greater than "
            f"TIMESTAMP_HIGH_PRIORITY_SECONDS ({high_priority})"
        )
