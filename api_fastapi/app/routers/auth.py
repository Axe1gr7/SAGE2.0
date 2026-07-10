from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import authenticate_user, create_access_token, get_current_user, get_password_hash, limiter
from app.data.database import get_db
from app.models.SAGE_BD import Administrador, Estudiante
from app.schemas.estudiante import EstudianteCreate, EstudianteResponse
from app.schemas.token import Token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    # 1. Intentamos buscarlo primero como estudiante
    role = "estudiante"
    user = authenticate_user(db, form_data.username, form_data.password, role)
    
    # 2. Si no lo encontramos como estudiante, intentamos como admin
    if not user:
        role = "admin"
        user = authenticate_user(db, form_data.username, form_data.password, role)
        
    # 3. Si de plano no existe en ninguna de las dos tablas (o la contraseña está mal)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 4. Generamos el token usando el ID correcto según su rol
    access_token = create_access_token(
        data={
            "sub": str(user.id_administrador) if role == "admin" else str(user.id_estudiante),
            "role": role
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/registro", response_model=EstudianteResponse)
@limiter.limit("3/minute")
async def registrar_estudiante(request: Request, estudiante: EstudianteCreate, db: Session = Depends(get_db)):
    if db.query(Estudiante).filter(Estudiante.matricula == estudiante.matricula).first():
        raise HTTPException(status_code=400, detail="Matrícula ya registrada")
    if db.query(Estudiante).filter(Estudiante.correo == estudiante.correo).first():
        raise HTTPException(status_code=400, detail="Correo ya registrado")
        
    hashed = get_password_hash(estudiante.contrasena)
    db_est = Estudiante(
        nombre_completo=estudiante.nombre_completo,
        matricula=estudiante.matricula,
        correo=estudiante.correo,
        contrasena=hashed,
        carrera=estudiante.carrera
    )
    db.add(db_est)
    db.commit()
    db.refresh(db_est)
    return db_est

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    """Devuelve datos del usuario autenticado para el cliente móvil."""

    # El móvil espera una estructura con keys como nombre_completo, correo,
    # y en caso de estudiante: matricula y carrera.
    if isinstance(current_user, Administrador):
        return {
            "id": current_user.id_administrador,
            "role": "admin",
            "nombre_completo": current_user.nombre_completo,
            "correo": current_user.correo,
            "puesto": current_user.puesto,
        }

    return {
        "id": current_user.id_estudiante,
        "role": "estudiante",
        "id_estudiante": current_user.id_estudiante,
        "nombre_completo": current_user.nombre_completo,
        "correo": current_user.correo,
        "matricula": current_user.matricula,
        # Si viene null, regresamos null; si es Enum, devolvemos su string.
        "carrera": current_user.carrera.value if current_user.carrera else None,
    }
