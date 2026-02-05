"""
Unified test suite for Photo Organizer V2.

Tests configuration, Vertex AI connection, database operations,
and basic organization workflows.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch

from v2.config import load_config, validate_config
from v2.image_utils import load_image, prepare_image_for_api, encode_image_base64, is_supported_image
from v2.vertex_claude import get_client, extract_json
from v2.database import load_database, add_person, list_people, get_person
from v2.organizer import (
    scan_directory_for_images,
    sanitize_directory_name,
    should_skip_file
)


class TestConfig:
    """Test configuration management."""

    def test_load_config(self):
        """Test configuration loads correctly."""
        config = load_config()
        assert 'project_id' in config
        assert 'region' in config
        assert 'model' in config
        assert 'confidence_threshold' in config

    def test_validate_config_success(self):
        """Test valid configuration passes validation."""
        config = {
            'project_id': 'test-project',
            'region': 'us-central1',
            'model': 'claude-3-5-sonnet@20240620',
            'confidence_threshold': 0.7
        }
        # Should not raise
        validate_config(config)

    def test_validate_config_missing_project_id(self):
        """Test validation fails without project_id."""
        config = {
            'project_id': None,
            'region': 'us-central1',
            'model': 'claude-3-5-sonnet@20240620',
            'confidence_threshold': 0.7
        }
        with pytest.raises(ValueError, match="VERTEX_PROJECT_ID"):
            validate_config(config)

    def test_validate_config_invalid_threshold(self):
        """Test validation fails with invalid threshold."""
        config = {
            'project_id': 'test-project',
            'region': 'us-central1',
            'model': 'claude-3-5-sonnet@20240620',
            'confidence_threshold': 1.5  # Invalid
        }
        with pytest.raises(ValueError, match="CONFIDENCE_THRESHOLD"):
            validate_config(config)


class TestImageUtils:
    """Test image processing utilities."""

    def test_is_supported_image(self):
        """Test file extension checking."""
        assert is_supported_image("photo.jpg")
        assert is_supported_image("photo.JPEG")
        assert is_supported_image("photo.png")
        assert is_supported_image("photo.heic")
        assert not is_supported_image("document.pdf")
        assert not is_supported_image("video.mp4")

    def test_sanitize_directory_name(self):
        """Test directory name sanitization."""
        assert sanitize_directory_name("John Doe") == "John_Doe"
        assert sanitize_directory_name("Alice & Bob") == "Alice__Bob"
        assert sanitize_directory_name("Test/Name") == "TestName"
        assert sanitize_directory_name("") == "Unknown"

    def test_should_skip_file(self):
        """Test file skipping logic."""
        assert should_skip_file(".hidden")
        assert should_skip_file("~temp")
        assert should_skip_file(".DS_Store")
        assert should_skip_file("Thumbs.db")
        assert not should_skip_file("photo.jpg")

    def test_extract_json(self):
        """Test JSON extraction from responses."""
        # Plain JSON
        result = extract_json('{"test": "value"}')
        assert result == {"test": "value"}

        # JSON in markdown code block
        result = extract_json('```json\n{"test": "value"}\n```')
        assert result == {"test": "value"}

        # JSON in generic code block
        result = extract_json('```\n{"test": "value"}\n```')
        assert result == {"test": "value"}


class TestVertexAI:
    """Test Vertex AI client initialization."""

    def test_get_client(self):
        """Test Vertex AI client initialization."""
        try:
            client = get_client()
            assert client is not None
        except Exception as e:
            pytest.skip(f"Vertex AI not configured: {e}")


class TestDatabase:
    """Test database operations."""

    def test_load_database(self):
        """Test database loading."""
        db = load_database()
        assert 'people' in db
        assert isinstance(db['people'], list)

    def test_list_people(self):
        """Test listing people."""
        people = list_people()
        assert isinstance(people, list)


class TestOrganizer:
    """Test organization logic."""

    def test_scan_directory_for_images(self, tmp_path):
        """Test directory scanning."""
        # Create test directory with files
        test_dir = tmp_path / "test_photos"
        test_dir.mkdir()

        # Create dummy image files
        (test_dir / "photo1.jpg").touch()
        (test_dir / "photo2.png").touch()
        (test_dir / "document.pdf").touch()
        (test_dir / ".hidden.jpg").touch()

        # Scan directory
        images = scan_directory_for_images(str(test_dir))

        # Should find only visible image files
        assert len(images) == 2
        assert any("photo1.jpg" in img for img in images)
        assert any("photo2.png" in img for img in images)
        assert not any(".hidden.jpg" in img for img in images)
        assert not any("document.pdf" in img for img in images)

    def test_scan_nonexistent_directory(self):
        """Test scanning non-existent directory raises error."""
        with pytest.raises(FileNotFoundError):
            scan_directory_for_images("/nonexistent/path")


# Integration tests (optional - require actual API access)
class TestIntegration:
    """Integration tests requiring Vertex AI access."""

    @pytest.mark.integration
    def test_simple_api_call(self):
        """Test basic Claude API call."""
        pytest.skip("Integration test - requires valid credentials and test image")
        # Uncomment and provide test image to run:
        # from v2.vertex_claude import analyze_image
        # response = analyze_image("test_image.jpg", "Describe this image briefly.")
        # assert len(response) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
