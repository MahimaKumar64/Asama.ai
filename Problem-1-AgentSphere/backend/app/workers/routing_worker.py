
import time
import uuid

import redis
from sqlalchemy.orm import Session

from app.core.redis import redis_client
from app.database.session import SessionLocal
from app.models import Agent, Post, RoutingLog
from app.services.routing import retrieve_candidates
from app.services.reranker import rerank_candidates

ROUTING_DEAD_LETTER_STREAM = "post.routing_dead_letters"
ROUTING_RETRY_KEY = "post.routing.retry_counts"

MAX_ROUTING_RETRIES = 3
BASE_ROUTING_RETRY_DELAY = 2


POST_STREAM = "post.published"
DELIVERY_STREAM = "webhook.deliveries"

CONSUMER_GROUP = "routing-group"
CONSUMER_NAME = "routing-worker-1"


def handle_routing_failure(message_id: str, fields: dict, error: Exception):
    attempts = redis_client.hincrby(
        ROUTING_RETRY_KEY,
        message_id,
        1
    )

    if attempts > MAX_ROUTING_RETRIES:
        redis_client.xadd(
            ROUTING_DEAD_LETTER_STREAM,
            {
                **fields,
                "source_message_id": message_id,
                "failure_reason": str(error),
                "attempts": str(attempts),
                "failed_at": str(time.time())
            }
        )

        redis_client.xack(
            POST_STREAM,
            CONSUMER_GROUP,
            message_id
        )

        redis_client.hdel(ROUTING_RETRY_KEY, message_id)

        print(
            f"Routing event moved to dead-letter stream: "
            f"{message_id}"
        )

        return

    delay = BASE_ROUTING_RETRY_DELAY * (2 ** (attempts - 1))

    print(
        f"Routing attempt {attempts} failed. "
        f"Retrying in {delay} seconds."
    )

    time.sleep(delay)


def process_post_event(message_id: str, fields: dict):
    db: Session = SessionLocal()

    try:
        post_id = uuid.UUID(fields["post_id"])

        post = db.query(Post).filter(
            Post.id == post_id
        ).first()

        if not post:
            raise ValueError(f"Post not found: {post_id}")

        author = db.query(Agent).filter(
            Agent.id == post.author_agent_id
        ).first()

        if not author:
            raise ValueError("Publishing agent not found.")

        # Stage 1 + 2:
        # Retrieve all eligible agents and the top 50 candidates.
        retrieval = retrieve_candidates(
            db=db,
            post=post,
            author=author,
            top_k=50
        )

        all_candidates = retrieval["all_candidates"]
        top_candidates = retrieval["top_candidates"]

        print(
            f"Post {post.id}: "
            f"{len(all_candidates)} eligible agents, "
            f"{len(top_candidates)} candidates sent for reranking."
        )

        # Stage 3:
        # Gemini evaluates only the top 50 candidates.
        evaluations = rerank_candidates(
            post,
            top_candidates
        )

        # Match each Gemini evaluation to its agent.
        evaluation_by_agent_id = {
            str(item["agent"].id): item
            for item in evaluations
        }

        selected_count = sum(
            1 for item in evaluations
            if item["routing_decision"] == "SELECTED"
        )

        outside_top_50_count = (
            len(all_candidates) - len(top_candidates)
        )

        print(
            f"Post {post.id}: "
            f"{len(evaluations)} agents evaluated by Gemini, "
            f"{selected_count} selected, "
            f"{outside_top_50_count} outside top 50."
        )

        delivery_jobs = []

        # Stage 4:
        # Create or update a routing record for EVERY eligible agent.
        for candidate in all_candidates:
            agent = candidate["agent"]
            agent_id = str(agent.id)

            evaluation = evaluation_by_agent_id.get(agent_id)

            if evaluation:
                # This agent was evaluated by Gemini.
                vector_score = evaluation["vector_score"]
                hybrid_score = evaluation["hybrid_score"]
                rerank_score = evaluation["rerank_score"]
                routing_decision = evaluation["routing_decision"]
                decision_reason = evaluation["decision_reason"]

            else:
                # This agent was eligible but outside the top 50.
                vector_score = candidate["vector_score"]
                hybrid_score = candidate["hybrid_score"]
                rerank_score = None
                routing_decision = "OUTSIDE_TOP_50"
                decision_reason = (
                    "Eligible agent was not retrieved in the top "
                    "candidate set. Gemini reranking was not performed."
                )

            existing_log = db.query(RoutingLog).filter(
                RoutingLog.post_id == post.id,
                RoutingLog.target_agent_id == agent.id
            ).first()

            is_new_log = existing_log is None

            if is_new_log:
                routing_log = RoutingLog(
                    id=uuid.uuid4(),
                    post_id=post.id,
                    target_agent_id=agent.id,
                    vector_score=vector_score,
                    hybrid_score=hybrid_score,
                    rerank_score=rerank_score,
                    routing_decision=routing_decision,
                    decision_reason=decision_reason,
                    status=(
                        "PENDING"
                        if routing_decision == "SELECTED"
                        else "NOT_APPLICABLE"
                    )
                )

                db.add(routing_log)
                db.flush()

            else:
                routing_log = existing_log

                # Refresh evaluation details.
                routing_log.vector_score = vector_score
                routing_log.hybrid_score = hybrid_score
                routing_log.rerank_score = rerank_score
                routing_log.routing_decision = routing_decision
                routing_log.decision_reason = decision_reason

                # Do not overwrite existing delivery or engagement states.
                if (
                    routing_decision == "SELECTED"
                    and routing_log.status == "NOT_APPLICABLE"
                ):
                    routing_log.status = "PENDING"

            # Only selected agents receive delivery jobs.
            if (
                routing_decision == "SELECTED"
                and routing_log.status == "PENDING"
                and agent.webhook_url
            ):
                delivery_jobs.append({
                    "delivery_id": str(routing_log.id),
                    "routing_log_id": str(routing_log.id),
                    "post_id": str(post.id),
                    "target_agent_id": str(agent.id),
                    "webhook_url": agent.webhook_url,
                    "company_name": agent.company_name,
                    "title": post.title,
                    "content": post.content,
                    "vector_score": str(vector_score),
                    "rerank_score": str(rerank_score)
                })

        # Save all agent evaluation records before queuing deliveries.
        db.commit()

        # Queue selected agents only.
        for job in delivery_jobs:
            redis_client.xadd(
                DELIVERY_STREAM,
                job
            )

        print(
            f"Post {post.id}: "
            f"{len(all_candidates)} routing records processed, "
            f"{len(delivery_jobs)} delivery jobs queued."
        )

        redis_client.xack(
            POST_STREAM,
            CONSUMER_GROUP,
            message_id
        )

        try:
            redis_client.hdel(
                ROUTING_RETRY_KEY,
                message_id
            )
        except redis.RedisError as exc:
            print(f"Retry counter cleanup failed: {exc}")

    except Exception as exc:
        db.rollback()

        print(
            f"Error processing event {message_id}: {exc}"
        )

        try:
            handle_routing_failure(message_id, fields, exc)
        except Exception as retry_exc:
            print(f"Failed to handle routing retry: {retry_exc}")

    finally:
        db.close()


def setup_consumer_group():
    try:
        redis_client.xgroup_create(
            POST_STREAM,
            CONSUMER_GROUP,
            id="0",
            mkstream=True
        )

        print("Routing consumer group created.")

    except redis.ResponseError as exc:
        if "BUSYGROUP" in str(exc):
            print("Routing consumer group already exists.")
        else:
            raise


def run_worker():
    setup_consumer_group()

    print("Routing worker started.")

    while True:
        try:
            # Recover messages left pending by failed workers.
            claimed = redis_client.xautoclaim(
                POST_STREAM,
                CONSUMER_GROUP,
                CONSUMER_NAME,
                min_idle_time=60000,
                start_id="0-0",
                count=10
            )

            pending_messages = claimed[1]

            if pending_messages:
                for message_id, fields in pending_messages:
                    process_post_event(message_id, fields)

                continue

            # Read new messages from the stream.
            response = redis_client.xreadgroup(
                CONSUMER_GROUP,
                CONSUMER_NAME,
                {POST_STREAM: ">"},
                count=5,
                block=5000
            )

            for stream, messages in response:
                for message_id, fields in messages:
                    process_post_event(message_id, fields)

        except redis.RedisError as exc:
            print(f"Redis error: {exc}")
            time.sleep(5)

        except Exception as exc:
            print(f"Worker error: {exc}")
            time.sleep(5)


if __name__ == "__main__":
    run_worker()
