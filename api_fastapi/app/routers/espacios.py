from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data.database import get_db
from app.models.SAGE_BD import Espacio
from app.schemas.espacio import EspacioCreate, EspacioUpdate, EspacioResponse
from app.auth import get_current_admin

router = APIRouter(prefix="/espacios", tags=["Espacios"])

@router.get("/", response_model=list[EspacioResponse])
async def list_espacios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Espacio).filter(Espacio.estatus == 0).offset(skip).limit(limit).all()

@router.get("/{id}", response_model=EspacioResponse)
async def get_espacio(id: int, db: Session = Depends(get_db)):
    espacio = db.query(Espacio).filter(Espacio.id_espacio == id, Espacio.estatus == 0).first()
    if not espacio:
        raise HTTPException(404, "Espacio no encontrado")
    return espacio

@router.post("/", response_model=EspacioResponse)
async def create_espacio(esp: EspacioCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_esp = Espacio(**esp.dict())
    db.add(db_esp)
    db.commit()
    db.refresh(db_esp)
    return db_esp

@router.put("/{id}", response_model=EspacioResponse)
async def update_espacio(id: int, esp: EspacioUpdate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_esp = db.query(Espacio).filter(Espacio.id_espacio == id, Espacio.estatus == 0).first()
    if not db_esp:
        raise HTTPException(404, "Espacio no encontrado")
    for key, value in esp.dict(exclude_unset=True).items():
        setattr(db_esp, key, value)
    db.commit()
    db.refresh(db_esp)
    return db_esp

@router.delete("/{id}")
async def delete_espacio(id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_esp = db.query(Espacio).filter(Espacio.id_espacio == id).first()
    if not db_esp:
        raise HTTPException(404, "Espacio no encontrado")
    db_esp.estatus = 1
    db.commit()
    return {"msg": "Espacio eliminado (soft delete)"}