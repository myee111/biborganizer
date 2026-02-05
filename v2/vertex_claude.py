"""
Claude API client using Vertex AI.

Provides functions for facial recognition tasks using Claude models on GCP.
"""

import json
import re
from anthropic import AnthropicVertex

from v2.config import load_config
from v2.image_utils import load_image, prepare_image_for_api, encode_image_base64
from v2.prompts import (
    OUTFIT_DESCRIPTION_PROMPT,
    DETECT_OUTFITS_PROMPT,
    COMPARE_OUTFITS_PROMPT
)


def get_client():
    """
    Initialize AnthropicVertex client from configuration.

    Returns:
        AnthropicVertex: Configured client instance

    Raises:
        ValueError: If configuration is invalid
    """
    config = load_config()
    return AnthropicVertex(
        project_id=config['project_id'],
        region=config['region']
    )


def analyze_image(image_path, prompt, max_tokens=2048):
    """
    Send an image with a prompt to Claude and return the response.

    Args:
        image_path: Path to image file
        prompt: Text prompt for analysis
        max_tokens: Maximum tokens in response (default: 2048)

    Returns:
        str: Claude's text response

    Raises:
        Exception: If API call fails
    """
    client = get_client()
    config = load_config()

    # Load and prepare image
    image = load_image(image_path)
    image_bytes = prepare_image_for_api(image)
    image_b64 = encode_image_base64(image_bytes)

    # Call Claude API
    response = client.messages.create(
        model=config['model'],
        max_tokens=max_tokens,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_b64
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
    )

    return response.content[0].text


def generate_outfit_description(image_path):
    """
    Generate a detailed outfit description for a person in an image.

    This is used when adding outfit types to the database.

    Args:
        image_path: Path to reference image

    Returns:
        str: Detailed outfit and clothing description
    """
    return analyze_image(image_path, OUTFIT_DESCRIPTION_PROMPT)


def detect_outfits(image_path):
    """
    Detect all people in an image and return their outfit descriptions.

    Args:
        image_path: Path to image file

    Returns:
        list: List of dicts with 'position', 'outfit_description', 'primary_colors', etc.
              or empty list if no people detected

    Raises:
        Exception: If API call fails or JSON parsing fails
    """
    try:
        response_text = analyze_image(image_path, DETECT_OUTFITS_PROMPT)
        result = extract_json(response_text)

        # Handle both formats: {"outfits": [...]} or [...]
        if isinstance(result, dict) and 'outfits' in result:
            return result['outfits']
        elif isinstance(result, list):
            return result
        else:
            print(f"Warning: Unexpected response format for {image_path}")
            return []

    except Exception as e:
        print(f"Warning: Error detecting outfits in {image_path}: {e}")
        return []


def compare_outfits(description1, description2, debug=False):
    """
    Compare two outfit descriptions and return similarity score.

    Args:
        description1: First outfit description
        description2: Second outfit description
        debug: If True, print detailed debug info

    Returns:
        float: Similarity score between 0.0 and 1.0 (returns 0.0 on any error)
    """
    response_text = None
    try:
        prompt = COMPARE_OUTFITS_PROMPT.format(
            description1=description1,
            description2=description2
        )

        client = get_client()
        config = load_config()

        response = client.messages.create(
            model=config['model'],
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        response_text = response.content[0].text

    except Exception as e:
        if debug:
            print(f"\n{'='*70}")
            print(f"EXCEPTION DETAILS:")
            print(f"{'='*70}")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {e}")
            import traceback
            print(f"Traceback:")
            traceback.print_exc()
            print(f"{'='*70}\n")
        return 0.0

    # Always show debug output if requested, even if parsing fails
    if debug:
        print(f"\n{'='*70}")
        print("COMPARISON DEBUG")
        print(f"{'='*70}")
        print(f"Description 1: {description1[:200]}...")
        print(f"Description 2: {description2[:200]}...")
        print(f"\nClaude Response ({len(response_text)} chars):")
        print(response_text)
        print(f"{'='*70}\n")

    # Try to extract JSON with multiple strategies
    try:
        # Strategy 1: Direct JSON load
        try:
            result = json.loads(response_text.strip())
            if isinstance(result, dict) and 'similarity' in result:
                score = float(result['similarity'])
                if debug:
                    print(f"✓ Strategy 1 (direct JSON): {score}")
                return score
        except:
            pass

        # Strategy 2: Extract from code block
        for pattern in [r'```json\s*\n?(.*?)\n?```', r'```\s*\n?(.*?)\n?```']:
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group(1).strip())
                    if isinstance(result, dict) and 'similarity' in result:
                        score = float(result['similarity'])
                        if debug:
                            print(f"✓ Strategy 2 (code block): {score}")
                        return score
                except:
                    pass

        # Strategy 3: Find JSON object with balanced braces
        brace_count = 0
        start_idx = response_text.find('{')
        if start_idx != -1:
            for i in range(start_idx, len(response_text)):
                if response_text[i] == '{':
                    brace_count += 1
                elif response_text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        try:
                            result = json.loads(response_text[start_idx:i+1])
                            if isinstance(result, dict) and 'similarity' in result:
                                score = float(result['similarity'])
                                if debug:
                                    print(f"✓ Strategy 3 (balanced braces): {score}")
                                return score
                        except:
                            break

        # Strategy 4: Search for "similarity": X.XX pattern
        sim_match = re.search(r'"similarity":\s*([0-9.]+)', response_text)
        if sim_match:
            try:
                score = float(sim_match.group(1))
                if 0.0 <= score <= 1.0:
                    if debug:
                        print(f"✓ Strategy 4 (similarity regex): {score}")
                    return score
            except:
                pass

        # Strategy 5: Any decimal number between 0 and 1
        number_match = re.search(r'\b(0?\.\d+|1\.0+|0)\b', response_text)
        if number_match:
            try:
                score = float(number_match.group(1))
                if 0.0 <= score <= 1.0:
                    if debug:
                        print(f"✓ Strategy 5 (any number): {score}")
                    return score
            except:
                pass

        # All strategies failed
        if debug:
            print("✗ All extraction strategies failed, returning 0.0")
        return 0.0

    except Exception as e:
        if debug:
            print(f"✗ Exception during extraction: {e}")
        return 0.0


def extract_json(text):
    """
    Extract JSON from response text, handling markdown code blocks.

    Args:
        text: Response text that may contain JSON

    Returns:
        dict or list: Parsed JSON object

    Raises:
        json.JSONDecodeError: If JSON parsing fails
    """
    original_text = text

    # Remove markdown code blocks if present
    if "```json" in text:
        match = re.search(r'```json\s*\n?(.*?)\n?```', text, re.DOTALL)
        if match:
            text = match.group(1)
    elif "```" in text:
        match = re.search(r'```\s*\n?(.*?)\n?```', text, re.DOTALL)
        if match:
            text = match.group(1)

    # Clean up whitespace
    text = text.strip()

    # Try to parse directly
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Try multiple strategies to extract JSON

        # Strategy 1: Find complete JSON object with balanced braces
        brace_count = 0
        start_idx = text.find('{')
        if start_idx != -1:
            for i in range(start_idx, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        try:
                            return json.loads(text[start_idx:i+1])
                        except json.JSONDecodeError:
                            break

        # Strategy 2: Find complete JSON array with balanced brackets
        bracket_count = 0
        start_idx = text.find('[')
        if start_idx != -1:
            for i in range(start_idx, len(text)):
                if text[i] == '[':
                    bracket_count += 1
                elif text[i] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        try:
                            return json.loads(text[start_idx:i+1])
                        except json.JSONDecodeError:
                            break

        # Strategy 3: Simple regex (last resort)
        json_match = re.search(r'(\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]+\}|\[[^\[\]]+\])', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # If all else fails, provide more helpful error with full text
        print(f"\n=== JSON PARSING ERROR ===")
        print(f"Original response: {original_text[:500]}")
        print(f"After cleanup: {text[:500]}")
        print(f"=========================\n")
        raise ValueError(f"Could not extract valid JSON from response: {e}")
