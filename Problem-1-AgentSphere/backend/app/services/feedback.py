
import math

from sqlalchemy.orm import Session

from app.models import Agent, Post, RoutingLog
from datetime import datetime, timedelta, timezone


IGNORED_THRESHOLD = 3
FEEDBACK_STRENGTH = 0.1
IGNORE_AFTER_HOURS = 24


def normalize_vector(vector):
    magnitude = math.sqrt(sum(value * value for value in vector))

    if magnitude == 0:
        return vector

    return [value / magnitude for value in vector]


def mark_unengaged_notifications(db: Session):
    cutoff_time = datetime.now(timezone.utc) - timedelta(
        hours=IGNORE_AFTER_HOURS
    )

    expired_logs = (
        db.query(RoutingLog)
        .filter(
            RoutingLog.status == "NOTIFIED",
            RoutingLog.created_at <= cutoff_time
        )
        .all()
    )

    for log in expired_logs:
        log.status = "IGNORED"

    db.commit()

    return len(expired_logs)


def process_ignored_feedback(db: Session):
    # Fetch ignored notifications whose feedback has not been applied.
    ignored_logs = (
        db.query(RoutingLog)
        .filter(
            RoutingLog.status == "IGNORED",
            RoutingLog.feedback_applied.is_(False)
        )
        .order_by(RoutingLog.created_at.asc())
        .all()
    )

    # Group ignored notifications by recipient agent.
    logs_by_agent = {}

    for log in ignored_logs:
        logs_by_agent.setdefault(log.target_agent_id, []).append(log)

    agents_updated = 0
    notifications_processed = 0

    for agent_id, logs in logs_by_agent.items():

        # Require at least three ignored notifications.
        while len(logs) >= IGNORED_THRESHOLD:

            selected_logs = logs[:IGNORED_THRESHOLD]
            ignored_embeddings = []

            for log in selected_logs:
                post = db.query(Post).filter(Post.id == log.post_id).first()

                if post and post.post_embedding is not None:
                    ignored_embeddings.append(list(post.post_embedding))

            # Only adjust when all three post embeddings are available.
            if len(ignored_embeddings) != IGNORED_THRESHOLD:
                break

            agent = db.query(Agent).filter(Agent.id == agent_id).first()

            if not agent or agent.interest_embedding is None:
                break

            current_vector = list(agent.interest_embedding)
            dimensions = len(current_vector)

            if any(len(vector) != dimensions for vector in ignored_embeddings):
                break

            # Calculate the average embedding of ignored posts.
            average_embedding = [
                sum(vector[i] for vector in ignored_embeddings)
                / IGNORED_THRESHOLD
                for i in range(dimensions)
            ]

            # Move the agent's interest vector away from ignored topics.
            updated_vector = [
                current_vector[i] - FEEDBACK_STRENGTH * average_embedding[i]
                for i in range(dimensions)
            ]

            agent.interest_embedding = normalize_vector(updated_vector)

            # Prevent these notifications from being processed again.
            for log in selected_logs:
                log.feedback_applied = True

            agents_updated += 1
            notifications_processed += IGNORED_THRESHOLD

            logs = logs[IGNORED_THRESHOLD:]

    db.commit()

    return {
        "agents_updated": agents_updated,
        "notifications_processed": notifications_processed
    }
