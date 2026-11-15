
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Agent, Post, RoutingLog
from app.services.webhook_security import verify_signature
from app.services.agent_runtime import (
    evaluate_opportunity,
    generate_agent_comment
)

router = APIRouter()


@router.post("/agent/{agent_id}")
def receive_agent_webhook(
    agent_id: uuid.UUID,
    payload: dict,
    x_webhook_signature: str = Header(None),
    x_delivery_id: str = Header(None),
    db: Session = Depends(get_db)
):
    # 1. Verify the webhook signature.
    if not x_webhook_signature:
        raise HTTPException(
            status_code=401,
            detail="Missing webhook signature."
        )

    if not verify_signature(payload, x_webhook_signature):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature."
        )

    # 2. Validate the delivery ID.
    delivery_id = payload.get("delivery_id")

    if not delivery_id or delivery_id != x_delivery_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid delivery ID."
        )

    # 3. Validate the event.
    if payload.get("event") != "agent.post.relevant":
        raise HTTPException(
            status_code=400,
            detail="Unsupported webhook event."
        )

    # 4. Verify the recipient.
    recipient = payload.get("recipient", {})

    if recipient.get("agent_id") != str(agent_id):
        raise HTTPException(
            status_code=403,
            detail="Recipient agent ID mismatch."
        )

    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id, Agent.is_active.is_(True))
        .first()
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Active recipient agent not found."
        )

    # 5. Retrieve the original post from the database.
    post_data = payload.get("post", {})
    post_id = post_data.get("id")

    try:
        post_uuid = uuid.UUID(post_id)
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid post ID."
        )

    post = db.query(Post).filter(Post.id == post_uuid).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found."
        )

    # 6. Verify that this agent was actually notified.
    routing_log = (
        db.query(RoutingLog)
        .filter(
            RoutingLog.post_id == post.id,
            RoutingLog.target_agent_id == agent.id
        )
        .first()
    )

    if not routing_log:
        raise HTTPException(
            status_code=403,
            detail="No routing record found for this delivery."
        )

    if routing_log.status in ("ENGAGED", "IGNORED"):
        return {
            "status": "already_processed",
            "message": "This agent has already engaged with the post."
        }

    if routing_log.status != "NOTIFIED":
        raise HTTPException(
            status_code=409,
            detail=f"Delivery cannot be processed in status {routing_log.status}."
        )

    # 7. Ask the recipient agent to evaluate the opportunity.
    decision = evaluate_opportunity(agent, post)

    if not decision["should_engage"]:
        routing_log.status = "IGNORED"
        db.commit()

        return {
            "status": "ignored",
            "company_name": agent.company_name,
            "reason": decision["reason"]
        }

    # 8. Generate an autonomous business response.
    comment_content = generate_agent_comment(agent, post)

    # 9. Save the comment and update engagement status.
    from app.models import Comment

    comment = Comment(
        post_id=post.id,
        author_agent_id=agent.id,
        content=comment_content
    )

    db.add(comment)
    routing_log.status = "ENGAGED"
    db.commit()
    db.refresh(comment)

    return {
        "status": "engaged",
        "company_name": agent.company_name,
        "comment_id": str(comment.id),
        "comment": comment.content
    }
