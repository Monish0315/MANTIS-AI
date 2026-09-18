from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Agent

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MANTIS Agent Runtime")


class AgentCreate(BaseModel):
    name: str
    description: str | None = None

@app.get("/agents")
def list_agents():
    db: Session = SessionLocal()

    agents = db.query(Agent).all()

    result = [
        {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "created_at": agent.created_at,
        }
        for agent in agents
    ]

    db.close()

    return result
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/agents")
def create_agent(agent_data: AgentCreate):
    db: Session = SessionLocal()

    agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)
    db.close()

    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "created_at": agent.created_at,
    }
@app.get("/agents/{agent_id}")
def get_agent(agent_id: int):
    db: Session = SessionLocal()

    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    db.close()

    if agent is None:
        return {"error": "Agent not found"}

    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "created_at": agent.created_at,
    }

@app.put("/agents/{agent_id}")
def update_agent(agent_id: int, agent_data: AgentCreate):
    db: Session = SessionLocal()

    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if agent is None:
        db.close()
        return {"error": "Agent not found"}

    agent.name = agent_data.name
    agent.description = agent_data.description

    db.commit()
    db.refresh(agent)
    db.close()

    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "created_at": agent.created_at,
    }

@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: int):
    db: Session = SessionLocal()

    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if agent is None:
        db.close()
        return {"error": "Agent not found"}

    db.delete(agent)
    db.commit()
    db.close()

    return {
        "message": "Agent deleted successfully",
        "id": agent_id,
    }    