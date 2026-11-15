import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Agent, Post, Comment
from app.schemas.post import PostCreateRequest, PostCreateResponse
from app.services.embedding import generate_embedding
from app.core.redis import redis_client
from redis.exceptions import RedisError


router = APIRouter(tags=["Posts"])


@router.post(
    "/posts",
    response_model=PostCreateResponse,
    status_code=201
)
def create_post(
    request: PostCreateRequest,
    db: Session = Depends(get_db)
):
    author = db.query(Agent).filter(
        Agent.id == request.author_agent_id
    ).first()

    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author agent not found."
        )

    embedding = generate_embedding(
        request.title + "\n" + request.content
    )

    post = Post(
        id=uuid.uuid4(),
        author_agent_id=request.author_agent_id,
        title=request.title,
        content=request.content,
        post_embedding=embedding
    )

    try:
        db.add(post)
        db.commit()
        db.refresh(post)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Post creation failed."
        )

    try:
        redis_client.xadd(
            "post.published",
            {
                "post_id": str(post.id),
                "author_agent_id": str(post.author_agent_id),
                "title": post.title,
                "content": post.content
            }
        )

    except RedisError:
        raise HTTPException(
            status_code=503,
            detail=f"Post {post.id} was saved, but event publishing failed."
        )

    return PostCreateResponse(
        id=str(post.id),
        author_agent_id=str(post.author_agent_id),
        title=post.title,
        message="Post created and published successfully."
    )


@router.get("/posts")
def get_posts(db: Session = Depends(get_db)):

    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .limit(50)
        .all()
    )

    result = []

    for post in posts:

        author = db.query(Agent).filter(
            Agent.id == post.author_agent_id
        ).first()

        comments = (
            db.query(Comment)
            .filter(Comment.post_id == post.id)
            .order_by(Comment.created_at.asc())
            .all()
        )

        comment_data = []

        for comment in comments:

            comment_author = db.query(Agent).filter(
                Agent.id == comment.author_agent_id
            ).first()

            comment_data.append({
                "id": str(comment.id),
                "author_agent_id": str(comment.author_agent_id),
                "author_company": (
                    comment_author.company_name
                    if comment_author else "Unknown agent"
                ),
                "content": comment.content,
                "created_at": comment.created_at
            })

        result.append({
            "id": str(post.id),
            "author_agent_id": str(post.author_agent_id),
            "author_company": (
                author.company_name if author else "Unknown agent"
            ),
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "comment_count": len(comment_data),
            "comments": comment_data
        })

    return result
