from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database.session import get_db
from app.models.user import User
from app.models.soar import Playbook, PlaybookAction, PlaybookExecution
from app.core.security import get_current_user
from app.services import soar_service
from datetime import datetime, timezone
from pydantic import BaseModel

router = APIRouter(prefix="/api/soar", tags=["SOAR"])


class PlaybookCreate(BaseModel):
    name: str
    description: str = ""
    trigger_type: str = "all_threats"
    trigger_config: dict = {}
    auto_run: bool = False
    actions: list[dict] = []


@router.get("/playbooks")
def list_playbooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playbooks = db.query(Playbook).order_by(desc(Playbook.created_at)).all()
    return {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "trigger_type": p.trigger_type,
                "trigger_config": p.trigger_config,
                "is_active": p.is_active,
                "auto_run": p.auto_run,
                "actions_count": len(p.actions),
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in playbooks
        ]
    }


@router.post("/playbooks")
def create_playbook(
    request: PlaybookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playbook = Playbook(
        name=request.name,
        description=request.description,
        trigger_type=request.trigger_type,
        trigger_config=request.trigger_config,
        auto_run=request.auto_run,
        created_by=current_user.id,
    )
    db.add(playbook)
    db.flush()

    for i, act in enumerate(request.actions):
        action = PlaybookAction(
            playbook_id=playbook.id,
            action_type=act.get("type", "log_event"),
            action_config=act.get("config", {}),
            order=i,
        )
        db.add(action)

    db.commit()
    db.refresh(playbook)
    return {"id": playbook.id, "name": playbook.name, "detail": "Playbook created"}


@router.post("/playbooks/{playbook_id}/toggle")
def toggle_playbook(
    playbook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playbook = db.query(Playbook).filter(Playbook.id == playbook_id).first()
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    playbook.is_active = not playbook.is_active
    db.commit()
    return {"id": playbook.id, "is_active": playbook.is_active}


@router.delete("/playbooks/{playbook_id}")
def delete_playbook(
    playbook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playbook = db.query(Playbook).filter(Playbook.id == playbook_id).first()
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    db.delete(playbook)
    db.commit()
    return {"detail": "Playbook deleted"}


@router.get("/executions")
def list_executions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.query(PlaybookExecution).count()
    items = db.query(PlaybookExecution).order_by(desc(PlaybookExecution.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            {
                "id": e.id,
                "playbook_id": e.playbook_id,
                "triggered_by": e.triggered_by,
                "status": e.status,
                "result": e.result,
                "started_at": e.started_at.isoformat() if e.started_at else None,
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/trigger/{threat_id}")
def manual_trigger(
    threat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.threat import Threat
    threat = db.query(Threat).filter(Threat.id == threat_id).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    soar_service.check_and_trigger(db, threat)
    return {"detail": "SOAR playbooks evaluated"}
