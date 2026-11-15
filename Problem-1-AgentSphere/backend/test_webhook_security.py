
from app.workers.delivery_worker import generate_signature
from app.services.webhook_security import verify_signature

payload = {
    "event": "agent.post.relevant",
    "delivery_id": "test-001",
    "post": {
        "id": "post-001",
        "title": "Payment Partnership",
        "content": "Testing HMAC verification"
    }
}

# Generate sender signature.
signature = generate_signature(payload)

# Verify valid signature.
print("Valid signature:", verify_signature(payload, signature))

# Verify tampered payload.
tampered_payload = payload.copy()
tampered_payload["event"] = "agent.post.modified"

print(
    "Tampered signature:",
    verify_signature(tampered_payload, signature)
)
