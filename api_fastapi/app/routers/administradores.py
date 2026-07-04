from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.data.database import get_db
from app.models.SAGE_BD import Administrador
from app.schemas.administrador import AdministradorCreate, AdministradorUpdate, AdministradorResponse
from app.auth import get_current_admin, get_password_hash

router = APIRouter(prefix="/administradores", tags=["Administradores (admin)"])

@router.get("/", response_model=list[AdministradorResponse])
async def list_administradores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    return db.query(Administrador).filter(Administrador.estatus == 0).offset(skip).limit(limit).all()

@router.post("/", response_model=AdministradorResponse)
async def create_administrador(
    admin: AdministradorCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    if db.query(Administrador).filter(Administrador.correo == admin.correo).first():
        raise HTTPException(400, "Correo ya existe")
    hashed = get_password_hash(admin.contrasena)
    db_admin = Administrador(
        nombre_completo=admin.nombre_completo,
        puesto=admin.puesto,
        correo=admin.correo,
        contrasena=hashed
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.get("/{id}", response_model=AdministradorResponse)
async def get_administrador(
    id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    admin = db.query(Administrador).filter(Administrador.id_administrador == id, Administrador.estatus == 0).first()
    if not admin:
        raise HTTPException(404, "Administrador no encontrado")
    return admin

@router.put("/{id}", response_model=AdministradorResponse)
async def update_administrador(
    id: int,
    admin_update: AdministradorUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    db_admin = db.query(Administrador).filter(Administrador.id_administrador == id, Administrador.estatus == 0).first()
    if not db_admin:
        raise HTTPException(404, "Administrador no encontrado")
    data = admin_update.dict(exclude_unset=True)
    if "contrasena" in data and data["contrasena"]:
        data["contrasena"] = get_password_hash(data["contrasena"])
    for key, value in data.items():
        setattr(db_admin, key, value)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.delete("/{id}")
async def delete_administrador(
    id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    db_admin = db.query(Administrador).filter(Administrador.id_administrador == id).first()
    if not db_admin:
        raise HTTPException(404, "Administrador no encontrado")
    db_admin.estatus = 1
    db.commit()
    return {"msg": "Administrador eliminado (soft delete)"}