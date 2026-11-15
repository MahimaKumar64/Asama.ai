from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models import RoutingLog, Comment, Agent, Post
from app.services.feedback import (
    mark_unengaged_notifications,
    process_ignored_feedback
)

router = APIRouter()


@router.get("/analytics/engagement")
def get_engagement_rate(db: Session = Depends(get_db)):

    notifications = (
        db.query(func.count(RoutingLog.id))
        .filter(
            RoutingLog.status.in_(["NOTIFIED", "ENGAGED", "IGNORED"])
        )
        .scalar()
    )

    engagements = (
        db.query(func.count(RoutingLog.id))
        .filter(RoutingLog.status == "ENGAGED")
        .scalar()
    )

    rate = (
        engagements / notifications
        if notifications > 0
        else 0
    )

    return {
        "notifications_sent": notifications,
        "comments_received": engagements,
        "engagement_rate": round(rate, 4),
        "engagement_percentage": round(rate * 100, 2)
    }


@router.post("/analytics/process-feedback")
def trigger_feedback_processing(db: Session = Depends(get_db)):
    ignored_count = mark_unengaged_notifications(db)

    result = process_ignored_feedback(db)

    return {
        "message": "Feedback processing completed",
        "newly_ignored": ignored_count,
        "agents_updated": result["agents_updated"],
        "notifications_processed": result["notifications_processed"]
    }


@router.get("/routing")
def get_routing_activity(db: Session = Depends(get_db)):

    records = (
        db.query(RoutingLog, Agent, Post)
        .join(
            Agent,
            Agent.id == RoutingLog.target_agent_id
        )
        .join(
            Post,
            Post.id == RoutingLog.post_id
        )
        .order_by(RoutingLog.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": str(log.id),
            "post_id": str(log.post_id),
            "post_title": post.title,

            "target_agent_id": str(log.target_agent_id),
            "target_company": agent.company_name,

            "vector_score": log.vector_score,
            "hybrid_score": log.hybrid_score,
            "rerank_score": log.rerank_score,

            "routing_decision": log.routing_decision,
            "decision_reason": log.decision_reason,

            "status": log.status,
            "created_at": log.created_at
        }
        for log, agent, post in records
    ]
