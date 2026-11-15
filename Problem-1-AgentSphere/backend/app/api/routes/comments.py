import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Agent, Post, Comment, RoutingLog
from app.schemas.comment import (
    CommentCreateRequest,
    CommentCreateResponse
)

router = APIRouter()


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentCreateResponse,
    status_code=status.HTTP_201_CREATED
)
def create_comment(
    post_id: uuid.UUID,
    request: CommentCreateRequest,
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found."
        )

    agent = db.query(Agent).filter(
        Agent.id == request.author_agent_id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Author agent not found."
        )

    comment = Comment(
        id=uuid.uuid4(),
        post_id=post.id,
        author_agent_id=agent.id,
        content=request.content
    )

    db.add(comment)
    routing_log = (
        db.query(RoutingLog)
        .filter(
            RoutingLog.post_id == post.id,
            RoutingLog.target_agent_id == agent.id
        )
        .first()
    )


# Record engagement
    if routing_log and routing_log.status == "NOTIFIED":
        routing_log.status = "ENGAGED"
    db.commit()
    db.refresh(comment)

    return CommentCreateResponse(
        id=str(comment.id),
        post_id=str(comment.post_id),
        author_agent_id=str(comment.author_agent_id),
        content=comment.content,
        message="Comment created successfully."
    )
