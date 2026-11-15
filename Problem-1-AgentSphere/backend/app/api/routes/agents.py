import uuid

from fastapi import APIRouter, Depends, HTTPException,  Body
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Agent
from app.schemas.agent import (
    AgentRegisterRequest,
    AgentRegisterResponse
)
from app.services.embedding import generate_embedding


router = APIRouter(tags=["Agents"])


@router.post(
    "/agents/register",
    response_model=AgentRegisterResponse,
    status_code=201
)
def register_agent(
    request: AgentRegisterRequest,
    db: Session = Depends(get_db)
):
    embedding = generate_embedding(request.interest_manifesto)

    agent = Agent(
        id=uuid.uuid4(),
        company_name=request.company_name,
        industry_category=request.industry_category,
        webhook_url=str(request.webhook_url),
        interest_manifesto=request.interest_manifesto,
        interest_embedding=embedding
    )

    try:
        db.add(agent)
        db.commit()
        db.refresh(agent)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Agent registration failed."
        )

    return AgentRegisterResponse(
        id=str(agent.id),
        company_name=agent.company_name,
        industry_category=agent.industry_category,
        message="Agent registered successfully."
    )


@router.get("/agents")
def get_agents(db: Session = Depends(get_db)):
    agents = (
        db.query(Agent)
        .order_by(Agent.created_at.desc())
        .all()
    )

    return [
        {
            "id": str(agent.id),
            "company_name": agent.company_name,
            "industry_category": agent.industry_category,
            "interest_manifesto": agent.interest_manifesto,
            "trust_score": agent.trust_score,
            "is_active": agent.is_active,
            "created_at": agent.created_at
        }
        for agent in agents
    ]


@router.patch("/agents/{agent_id}/webhook")
def update_agent_webhook(
    agent_id: uuid.UUID,
    webhook_url: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(
        Agent.id == agent_id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found."
        )

    if not webhook_url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook URL."
        )

    agent.webhook_url = webhook_url
    db.commit()

    return {
        "message": "Webhook URL updated successfully.",
        "agent_id": str(agent.id),
        "webhook_url": agent.webhook_url
    }
