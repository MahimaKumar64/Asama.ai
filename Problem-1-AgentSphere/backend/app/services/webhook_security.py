
import hashlib
import hmac
import json

from app.core.config import settings


def verify_signature(payload: dict, received_signature: str) -> bool:
    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True
    ).encode("utf-8")

    expected_signature = hmac.new(
        settings.hmac_secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        received_signature
    )
