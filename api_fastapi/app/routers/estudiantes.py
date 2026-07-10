from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.auth import get_current_admin, get_current_user, get_password_hash, limiter
from app.data.database import get_db
from app.models.SAGE_BD import Estudiante
from app.schemas.estudiante import EstudianteCreate, EstudianteResponse, EstudianteUpdate

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes (admin)"])

@router.get("/", response_model=list[EstudianteResponse])
@limiter.limit("20/minute")
async def list_estudiantes(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    return db.query(Estudiante).filter(Estudiante.estatus == 0).offset(skip).limit(limit).all()

@router.post("/", response_model=EstudianteResponse)
@limiter.limit("20/minute")
async def create_estudiante(
    request: Request,
    est: EstudianteCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    if db.query(Estudiante).filter(Estudiante.matricula == est.matricula).first():
        raise HTTPException(400, "Matrícula ya existe")
    if db.query(Estudiante).filter(Estudiante.correo == est.correo).first():
        raise HTTPException(400, "Correo ya existe")
    hashed = get_password_hash(est.contrasena)
    db_est = Estudiante(
        nombre_completo=est.nombre_completo,
        matricula=est.matricula,
        correo=est.correo,
        contrasena=hashed,
        carrera=est.carrera
    )
    db.add(db_est)
    db.commit()
    db.refresh(db_est)
    return db_est

@router.get("/{id}", response_model=EstudianteResponse)
async def get_estudiante(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if isinstance(current_user, Estudiante) and current_user.id_estudiante != id:
        raise HTTPException(403, "No tienes permiso para acceder a este recurso")

    est = db.query(Estudiante).filter(Estudiante.id_estudiante == id, Estudiante.estatus == 0).first()
    if not est:
        raise HTTPException(404, "Estudiante no encontrado")
    return est

@router.put("/{id}", response_model=EstudianteResponse)
async def update_estudiante(
    id: int,
    est_update: EstudianteUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if isinstance(current_user, Estudiante) and current_user.id_estudiante != id:
        raise HTTPException(403, "No tienes permiso para actualizar este recurso")

    db_est = db.query(Estudiante).filter(Estudiante.id_estudiante == id, Estudiante.estatus == 0).first()
    if not db_est:
        raise HTTPException(404, "Estudiante no encontrado")
    data = est_update.dict(exclude_unset=True)
    if "contrasena" in data and data["contrasena"]:
        data["contrasena"] = get_password_hash(data["contrasena"])
    for key, value in data.items():
        setattr(db_est, key, value)
    db.commit()
    db.refresh(db_est)
    return db_est

@router.delete("/{id}")
async def delete_estudiante(
    id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    db_est = db.query(Estudiante).filter(Estudiante.id_estudiante == id).first()
    if not db_est:
        raise HTTPException(404, "Estudiante no encontrado")
    db_est.estatus = 1
    db.commit()
    return {"msg": "Estudiante eliminado (soft delete)"}