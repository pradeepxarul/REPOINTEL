"""Input validation and normalization for GitHub usernames and URLs"""
import re
from typing import Tuple


def normalize_github_input(github_input: str) -> Tuple[str, bool]:
    """
    Normalize GitHub input (username or URL) to username
    
    Args:
        github_input: GitHub username or URL
            Examples: "torvalds", "https://github.com/torvalds", "https://github.com/torvalds?tab=repos"
    
    Returns:
        Tuple of (normalized_username, is_valid)
    
    Raises:
        ValueError: If input format is invalid
    
    Examples:
        >>> normalize_github_input("torvalds")
        ('torvalds', True)
        >>> normalize_github_input("https://github.com/torvalds")
        ('torvalds', True)
        >>> normalize_github_input("Torvalds")
        ('torvalds', True)
    """
    
    # Step 1: Clean input
    username = github_input.strip()
    
    # Step 2: Extract from URL if present
    if username.startswith('https://') or username.startswith('http://'):
        # Remove protocol
        username = re.sub(r'https?://', '', username)
        # Remove github.com/
        username = re.sub(r'github\.com/', '', username)
        # Remove trailing slash
        username = username.rstrip('/')
        # Remove query params and path segments
        username = username.split('?')[0]
        username = username.split('/')[0]
    
    # Step 3: Validate length (GitHub username requirements)
    if not (1 <= len(username) <= 39):
        raise ValueError(f'Username must be 1-39 characters, got {len(username)}')
    
    # Step 4: Validate format (GitHub username rules)
    # Alphanumeric + hyphens, cannot start/end with hyphen
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$', username):
        raise ValueError(f'Invalid GitHub username format: {username}')
    
    # Step 5: Normalize to lowercase (GitHub is case-insensitive)
    username = username.lower()
    
    return username, True


# Test validation if run directly
if __name__ == "__main__":
    test_cases = [
        ("torvalds", "torvalds"),
        ("Torvalds", "torvalds"),
        ("https://github.com/torvalds", "torvalds"),
        ("https://github.com/torvalds/", "torvalds"),
        ("https://github.com/torvalds?tab=repositories", "torvalds"),
    ]
    
    for input_val, expected in test_cases:
        result, _ = normalize_github_input(input_val)
        assert result == expected, f"Failed for {input_val}: got {result}, expected {expected}"
    
    print("[SUCCESS] All validation tests passed!")
