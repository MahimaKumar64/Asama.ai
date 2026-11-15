import hashlib
import hmac
import json
import time
import uuid

import httpx
import redis

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis import redis_client
from app.database.session import SessionLocal
from app.models import RoutingLog

DELIVERY_STREAM = "webhook.deliveries"
CONSUMER_GROUP = "delivery-group"
CONSUMER_NAME = "delivery-worker-1"

MAX_RETRIES = 3
BASE_RETRY_DELAY = 2
DEAD_LETTER_STREAM = "webhook.dead_letters"


def generate_signature(payload: dict) -> str:
    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True
    ).encode("utf-8")

    signature = hmac.new(
        settings.hmac_secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    return signature


def send_to_dead_letter(job, failure_reason):
    redis_client.xadd(
        DEAD_LETTER_STREAM,
        {
            "job": json.dumps(job, default=str),
            "failure_reason": failure_reason,
            "attempts": str(MAX_RETRIES + 1),
            "failed_at": str(time.time())
        }
    )

    print(
        f"Delivery moved to dead-letter stream: "
        f"{job['delivery_id']}"
    )


def send_webhook(job: dict) -> bool:
    payload = {
        "event": "agent.post.relevant",
        "delivery_id": job["delivery_id"],
        "post": {
            "id": job["post_id"],
            "title": job["title"],
            "content": job["content"]
        },
        "recipient": {
            "agent_id": job["target_agent_id"],
            "company_name": job["company_name"]
        },
        "relevance": {
            "vector_score": float(job["vector_score"]),
            "rerank_score": float(job["rerank_score"])
        }
    }

    signature = generate_signature(payload)

    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
        "X-Delivery-ID": job["delivery_id"]
    }

    try:
        response = httpx.post(
            job["webhook_url"],
            json=payload,
            headers=headers,
            timeout=10.0
        )

        response.raise_for_status()
        print(
            f"Webhook delivered successfully to "
            f"{job['company_name']}: HTTP {response.status_code}"
        )
        return True

    except httpx.HTTPStatusError as exc:
        print(
            f"Webhook returned HTTP {exc.response.status_code} "
            f"for {job['company_name']}"
        )
        return False

    except httpx.RequestError as exc:
        print(f"Webhook connection failed: {exc}")
        return False


def update_delivery_status(
    routing_log_id: str,
    status: str,
    allowed_current_statuses: tuple
):
    db: Session = SessionLocal()

    try:
        routing_log = (
            db.query(RoutingLog)
            .filter(
                RoutingLog.id == uuid.UUID(routing_log_id),
                RoutingLog.status.in_(allowed_current_statuses)
            )
            .first()
        )

        if routing_log:
            routing_log.status = status
            db.commit()
            print(f"Delivery status updated: {status}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def deliver_with_retries(job: dict) -> bool:
    for attempt in range(MAX_RETRIES + 1):

        # Check whether the recipient has already processed this delivery.
        db: Session = SessionLocal()

        try:
            routing_log = (
                db.query(RoutingLog)
                .filter(
                    RoutingLog.id == uuid.UUID(job["routing_log_id"])
                )
                .first()
            )

            if not routing_log:
                raise ValueError("Routing log not found.")

            if routing_log.status in ("ENGAGED", "IGNORED"):
                print(
                    f"Recipient already processed delivery: "
                    f"{routing_log.status}"
                )
                return True

            # Mark notification before calling the receiver.
            if routing_log.status == "PENDING":
                routing_log.status = "NOTIFIED"
                db.commit()

        finally:
            db.close()

        print(
            f"Delivery attempt {attempt + 1} "
            f"for {job['company_name']}"
        )

        if send_webhook(job):
            # Do not overwrite ENGAGED or IGNORED here.
            # The recipient runtime may already have made its decision.
            return True

        if attempt < MAX_RETRIES:
            delay = BASE_RETRY_DELAY * (2 ** attempt)

            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)

    send_to_dead_letter(
        job,
        "Webhook delivery failed after maximum retries"
    )

    update_delivery_status(
        job["routing_log_id"],
        "FAILED",
        ("PENDING", "NOTIFIED")
    )

    print(
        f"Delivery permanently failed for "
        f"{job['company_name']}"
    )

    return False


def setup_consumer_group():
    try:
        redis_client.xgroup_create(
            DELIVERY_STREAM,
            CONSUMER_GROUP,
            id="0",
            mkstream=True
        )
        print("Delivery consumer group created.")

    except redis.ResponseError as exc:
        if "BUSYGROUP" in str(exc):
            print("Delivery consumer group already exists.")
        else:
            raise


def process_delivery(message_id: str, fields: dict):
    try:
        success = deliver_with_retries(fields)

        redis_client.xack(
            DELIVERY_STREAM,
            CONSUMER_GROUP,
            message_id
        )

        if success:
            print(f"Delivery job {message_id} acknowledged.")
        else:
            print(f"Failed delivery job {message_id} acknowledged.")

    except Exception as exc:
        print(f"Error processing delivery {message_id}: {exc}")
        # Leave the message pending for recovery.


def run_worker():
    setup_consumer_group()
    print("Delivery worker started.")

    while True:
        try:
            claimed = redis_client.xautoclaim(
                DELIVERY_STREAM,
                CONSUMER_GROUP,
                CONSUMER_NAME,
                min_idle_time=60000,
                start_id="0-0",
                count=10
            )

            pending_messages = claimed[1]

            if pending_messages:
                for message_id, fields in pending_messages:
                    process_delivery(message_id, fields)
                continue

            response = redis_client.xreadgroup(
                CONSUMER_GROUP,
                CONSUMER_NAME,
                {DELIVERY_STREAM: ">"},
                count=5,
                block=5000
            )

            for stream, messages in response:
                for message_id, fields in messages:
                    process_delivery(message_id, fields)

        except redis.RedisError as exc:
            print(f"Redis error: {exc}")
            time.sleep(5)

        except Exception as exc:
            print(f"Unexpected worker error: {exc}")
            time.sleep(5)


if __name__ == "__main__":
    run_worker()
