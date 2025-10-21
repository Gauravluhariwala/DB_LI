"""
Session Token Management for Pagination Consistency
Ensures same company filter is used across all pages of a search
"""

import json
import base64
import hmac
import hashlib
import time
from typing import List, Dict, Any

# Secret key for HMAC signing (in production, use environment variable)
SECRET_KEY = "your-secret-key-change-in-production-use-env-var"
TOKEN_TTL = 3600  # 1 hour

def generate_session_token(
    company_names: List[str],
    company_criteria: Dict[str, Any],
    people_criteria: Dict[str, Any],
    search_id: str = None
) -> str:
    """
    Generate secure session token containing company filter

    Args:
        company_names: List of company names used in filter
        company_criteria: Original company search criteria
        people_criteria: Original people search criteria
        search_id: Unique search identifier for analytics

    Returns:
        Base64-encoded signed token
    """
    current_time = int(time.time())

    payload = {
        "v": 1,  # Token version
        "cnames": company_names,  # Company names
        "ch": hashlib.md5(json.dumps(company_criteria, sort_keys=True).encode()).hexdigest(),
        "ph": hashlib.md5(json.dumps(people_criteria, sort_keys=True).encode()).hexdigest(),
        "iat": current_time,  # Issued at
        "exp": current_time + TOKEN_TTL,  # Expires
        "sid": search_id or f"search_{current_time}"  # Search ID
    }

    # Serialize and encode
    payload_json = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()

    # Sign with HMAC
    signature = hmac.new(
        SECRET_KEY.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).hexdigest()

    # Combine: payload.signature
    token = f"{payload_b64}.{signature}"

    return token

def decode_session_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate session token

    Args:
        token: Session token from previous request

    Returns:
        Decoded payload with company_names list

    Raises:
        ValueError: If token invalid, expired, or tampered
    """
    try:
        # Split token
        parts = token.split('.')
        if len(parts) != 2:
            raise ValueError("Invalid token format")

        payload_b64, signature = parts

        # Verify signature
        expected_signature = hmac.new(
            SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid token signature - token may have been tampered with")

        # Decode payload
        payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
        payload = json.loads(payload_json)

        # Check expiry
        current_time = int(time.time())
        if payload.get('exp', 0) < current_time:
            raise ValueError(f"Token expired. Tokens are valid for {TOKEN_TTL/60:.0f} minutes.")

        return payload

    except Exception as e:
        raise ValueError(f"Invalid session token: {str(e)}")

def validate_token_matches_criteria(
    token_payload: Dict[str, Any],
    company_criteria: Dict[str, Any],
    people_criteria: Dict[str, Any]
) -> bool:
    """
    Verify token matches current search criteria

    Returns True if criteria haven't changed, False otherwise
    """
    current_company_hash = hashlib.md5(json.dumps(company_criteria, sort_keys=True).encode()).hexdigest()
    current_people_hash = hashlib.md5(json.dumps(people_criteria, sort_keys=True).encode()).hexdigest()

    return (
        token_payload.get('ch') == current_company_hash and
        token_payload.get('ph') == current_people_hash
    )
