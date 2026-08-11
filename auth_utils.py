"""
auth_utils.py — Cryptographically Secure Session Persistence & Token Verification.

Provides HMAC-SHA256 signed session tokens with expiry validation, schema enforcement,
runtime secret key derivation, and user existence verification in the database.
"""

import hmac
import hashlib
import secrets
import time
import json
import base64
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Token validity: 30 days in seconds
TOKEN_TTL = 30 * 24 * 60 * 60


@st.cache_resource
def _get_runtime_entropy_key() -> str:
    """Generates a cryptographically strong 256-bit random key for this application instance."""
    return secrets.token_hex(32)


def _get_secret_key() -> str:
    """
    Retrieve or securely generate the HMAC signing key.
    Priority:
    1. Explicit secret: st.secrets["session"]["secret_key"]
    2. Derived deployment secret: hash of PostgreSQL connection URL
    3. Cryptographically strong in-memory runtime entropy key
    """
    try:
        if "session" in st.secrets and "secret_key" in st.secrets["session"]:
            key = st.secrets["session"]["secret_key"]
            if key and key != "nexus-default-secret-key-change-me":
                return key
    except Exception:
        pass

    try:
        if "postgres" in st.secrets:
            pg_url = st.secrets["postgres"].get("url", "") or st.secrets["postgres"].get("uri", "")
            if pg_url:
                return hashlib.sha256(f"nexus-secure-session-{pg_url}".encode("utf-8")).hexdigest()
    except Exception:
        pass

    return _get_runtime_entropy_key()


def create_session_token(user_id: int, username: str) -> str:
    """Create an HMAC-SHA256 signed session token encoding user_id, username, and expiry."""
    if not isinstance(user_id, int) or user_id <= 0 or not username:
        raise ValueError("Invalid user parameters for token creation")

    secret = _get_secret_key()
    payload = {
        "uid": user_id,
        "usr": str(username).strip(),
        "exp": int(time.time()) + TOKEN_TTL,
        "iat": int(time.time()),
        "nonce": secrets.token_hex(8)
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("ascii")

    signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def verify_session_token(token: str) -> dict | None:
    """
    Verify an HMAC-signed session token.
    Enforces signature validity, expiry, schema integrity, and database user existence.
    Returns payload dict or None.
    """
    if not token or not isinstance(token, str) or "." not in token:
        return None

    try:
        payload_b64, signature = token.rsplit(".", 1)
        payload_bytes = base64.urlsafe_b64decode(payload_b64.encode("ascii"))
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None

    # Verify signature with constant-time comparison
    secret = _get_secret_key()
    expected_sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        return None

    # Check expiry
    current_time = int(time.time())
    if not isinstance(payload.get("exp"), int) or payload["exp"] < current_time:
        return None

    # Schema validation
    uid = payload.get("uid")
    usr = payload.get("usr")
    if not isinstance(uid, int) or uid <= 0 or not usr or not isinstance(usr, str):
        return None

    # Verify user actually exists in the database
    try:
        from models import get_user_by_id
        user_record = get_user_by_id(uid)
        if not user_record or user_record.get("username", "").lower() != usr.lower():
            return None
    except Exception as e:
        logger.warning(f"Database validation failed during session verification: {e}")
        # If DB connection error occurs, fail closed
        return None

    return payload


def set_session_param(token: str):
    """Store the session token in query params."""
    try:
        st.query_params["session"] = token
    except Exception:
        pass


def get_session_param() -> str | None:
    """Read the session token from query params."""
    try:
        return st.query_params.get("session")
    except Exception:
        return None


def clear_session_param():
    """Remove the session token from query params."""
    try:
        if "session" in st.query_params:
            del st.query_params["session"]
    except Exception:
        pass
