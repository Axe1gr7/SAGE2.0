from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.data.database import get_db
from app.models.SAGE_BD import Evento
from app.schemas.evento import EventoCreate, EventoUpdate, EventoResponse
from app.auth import get_current_admin
from datetime import datetime

router = APIRouter(prefix="/eventos", tags=["Eventos"])

@router.get("/", response_model=list[EventoResponse])
async def list_eventos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    return db.query(Evento).filter(Evento.estatus == 0).offset(skip).limit(limit).all()

@router.get("/proximos", response_model=list[EventoResponse])
async def list_proximos_eventos(limit: int = 10, db: Session = Depends(get_db)):
    now = datetime.now()
    return db.query(Evento).filter(
        Evento.estatus == 0,
        Evento.fecha_inicio >= now
    ).order_by(Evento.fecha_inicio.asc()).limit(limit).all()

@router.post("/", response_model=EventoResponse)
async def create_evento(evento: EventoCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_evento = Evento(**evento.dict())
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

@router.get("/{id}", response_model=EventoResponse)
async def get_evento(id: int, db: Session = Depends(get_db)):
    evento = db.query(Evento).filter(Evento.id_evento == id, Evento.estatus == 0).first()
    if not evento:
        raise HTTPException(404, "Evento no encontrado")
    return evento

@router.put("/{id}", response_model=EventoResponse)
async def update_evento(id: int, evento_update: EventoUpdate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_evento = db.query(Evento).filter(Evento.id_evento == id, Evento.estatus == 0).first()
    if not db_evento:
        raise HTTPException(404, "Evento no encontrado")
    for key, value in evento_update.dict(exclude_unset=True).items():
        setattr(db_evento, key, value)
    db.commit()
    db.refresh(db_evento)
    return db_evento

@router.delete("/{id}")
async def delete_evento(id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_evento = db.query(Evento).filter(Evento.id_evento == id).first()
    if not db_evento:
        raise HTTPException(404, "Evento no encontrado")
    db_evento.estatus = 1
    db.commit()
    return {"msg": "Evento eliminado (soft delete)"}