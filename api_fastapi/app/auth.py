import hashlib
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.data.database import get_db
# Importamos EstatusTinyInt para validar correctamente el estatus activo
from app.models.SAGE_BD import Estudiante, Administrador, EstatusTinyInt 
from app.schemas.token import TokenData

SECRET_KEY = "tu-clave-secreta-cambiala-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

from fastapi.security.api_key import APIKeyHeader
from fastapi import Security
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_scheme)):
    if api_key_header == "SAGE_SECRET_API_KEY_2026":
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="No se pudo validar la API KEY"
    )


# --- FUNCIONES DE ENCRIPTACIÓN NATIVAS (Sin librerías externas) ---
def verify_password(plain_password: str, hashed_password: str):
    # Encriptamos la contraseña ingresada y la comparamos con la guardada
    hashed_plain = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return hashed_plain == hashed_password

def get_password_hash(password: str):
    # Generamos un hash SHA-256 estándar
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
# -----------------------------------------------------------------

def authenticate_user(db: Session, email: str, password: str, role: str):
    if role == "admin":
        user = db.query(Administrador).filter(
            Administrador.correo == email, 
            Administrador.estatus == EstatusTinyInt.ACTIVO
        ).first()
    elif role == "estudiante":
        user = db.query(Estudiante).filter(
            Estudiante.correo == email, 
            Estudiante.estatus == EstatusTinyInt.ACTIVO
        ).first()
    else:
        return None

    if not user or not verify_password(password, user.contrasena):
        return None
        
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        role: str = payload.get("role")
        
        if user_id_str is None or role is None:
            raise credentials_exception
            
        # Convertimos el string de vuelta a int para buscar en la base de datos
        token_data = TokenData(id=int(user_id_str), role=role)
    except (JWTError, ValueError):
        raise credentials_exception
        
    if token_data.role == "admin":
        user = db.query(Administrador).filter(Administrador.id_administrador == token_data.id).first()
    else:
        user = db.query(Estudiante).filter(Estudiante.id_estudiante == token_data.id).first()
        
    if user is None:
        raise credentials_exception
        
    return user

def get_current_admin(current_user = Depends(get_current_user)):
    if current_user.__class__.__name__ != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Se requieren privilegios de administrador"
        )
    return current_user