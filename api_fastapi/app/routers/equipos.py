from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data.database import get_db
from app.models.SAGE_BD import Equipo, EstadoOperativo
from app.schemas.equipo import EquipoResponse, EquipoUpdate
from app.auth import get_current_admin

router = APIRouter(prefix="/equipos", tags=["Equipos"])

@router.get("/", response_model=list[EquipoResponse])
async def list_equipos(espacio_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Equipo).filter(Equipo.estatus == 0)
    if espacio_id:
        query = query.filter(Equipo.id_espacio == espacio_id)
    return query.all()

@router.get("/{id}", response_model=EquipoResponse)
async def get_equipo(id: int, db: Session = Depends(get_db)):
    equipo = db.query(Equipo).filter(Equipo.id_equipo == id, Equipo.estatus == 0).first()
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")
    return equipo

@router.put("/{id}/estado", response_model=EquipoResponse)
async def cambiar_estado_equipo(id: int, nuevo_estado: EstadoOperativo, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    equipo = db.query(Equipo).filter(Equipo.id_equipo == id, Equipo.estatus == 0).first()
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")
    equipo.estado_operativo = nuevo_estado
    db.commit()
    db.refresh(equipo)
    return equipo

@router.post("/", response_model=EquipoResponse)
async def create_equipo(eq: EquipoUpdate, id_espacio: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_eq = Equipo(
        id_espacio=id_espacio,
        nombre_equipo=eq.nombre_equipo,
        tipo_equipo=eq.tipo_equipo,
        estado_operativo=eq.estado_operativo or EstadoOperativo.OPERATIVO
    )
    db.add(db_eq)
    db.commit()
    db.refresh(db_eq)
    return db_eq

@router.put("/{id}", response_model=EquipoResponse)
async def update_equipo(id: int, eq: EquipoUpdate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_eq = db.query(Equipo).filter(Equipo.id_equipo == id, Equipo.estatus == 0).first()
    if not db_eq:
        raise HTTPException(404, "Equipo no encontrado")
    if eq.nombre_equipo: db_eq.nombre_equipo = eq.nombre_equipo
    if eq.tipo_equipo: db_eq.tipo_equipo = eq.tipo_equipo
    if eq.estado_operativo: db_eq.estado_operativo = eq.estado_operativo
    db.commit()
    db.refresh(db_eq)
    return db_eq

@router.delete("/{id}")
async def delete_equipo(id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_eq = db.query(Equipo).filter(Equipo.id_equipo == id).first()
    if not db_eq:
        raise HTTPException(404, "Equipo no encontrado")
    db_eq.estatus = 1
    db.commit()
    return {"msg": "Equipo eliminado (soft delete)"}