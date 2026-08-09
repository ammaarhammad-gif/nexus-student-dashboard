"""
auth_utils.py — Session persistence via HMAC-signed tokens in query params.

Provides create_session_token() and verify_session_token() so the user
can stay logged in across page refreshes when "Keep me logged in" is checked.
"""

import hmac
import hashlib
import time
import json
import base64
import streamlit as st


# Token validity: 30 days in seconds
TOKEN_TTL = 30 * 24 * 60 * 60


def _get_secret_key() -> str:
    """Get or generate a secret key for HMAC signing."""
    try:
        return st.secrets["session"]["secret_key"]
    except (KeyError, AttributeError):
        # Fallback: derive from the postgres URL so it's consistent per deployment
        try:
            pg_url = st.secrets["postgres"].get("url", "") or st.secrets["postgres"].get("uri", "")
            return hashlib.sha256(f"nexus-session-{pg_url}".encode()).hexdigest()
        except (KeyError, AttributeError):
            return "nexus-default-secret-key-change-me"


def create_session_token(user_id: int, username: str) -> str:
    """Create an HMAC-signed session token encoding user_id, username, and expiry."""
    secret = _get_secret_key()
    payload = {
        "uid": user_id,
        "usr": username,
        "exp": int(time.time()) + TOKEN_TTL
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("ascii")

    signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

    return f"{payload_b64}.{signature}"


def verify_session_token(token: str) -> dict | None:
    """Verify an HMAC-signed session token. Returns payload dict or None if invalid/expired."""
    if not token or "." not in token:
        return None

    try:
        payload_b64, signature = token.rsplit(".", 1)
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes)
    except Exception:
        return None

    # Verify signature
    secret = _get_secret_key()
    expected_sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        return None

    # Check expiry
    if payload.get("exp", 0) < int(time.time()):
        return None

    return payload


def set_session_param(token: str):
    """Store the session token in query params."""
    st.query_params["session"] = token


def get_session_param() -> str | None:
    """Read the session token from query params."""
    return st.query_params.get("session")


def clear_session_param():
    """Remove the session token from query params."""
    if "session" in st.query_params:
        del st.query_params["session"]
