import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyHeader
from jose import JWTError, jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.data.database import get_db
from app.models.SAGE_BD import Administrador, Estudiante, EstatusTinyInt
from app.schemas.token import TokenData

load_dotenv()

SECRET_KEY = os.getenv("SAGE_JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("SAGE_JWT_SECRET must be set in environment variables")

ALGORITHM = os.getenv("SAGE_JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("SAGE_JWT_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
limiter = Limiter(key_func=get_remote_address)
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key(api_key_header: str = Security(api_key_scheme)):
    api_key_value = os.getenv("SAGE_API_KEY")
    if not api_key_value:
        raise ValueError("SAGE_API_KEY must be set in environment variables")
        
    if api_key_header and api_key_header == api_key_value:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No se pudo validar la API KEY",
    )


def verify_password(plain_password: str, hashed_password: str):
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def authenticate_user(db: Session, email: str, password: str, role: str):
    if role == "admin":
        user = db.query(Administrador).filter(
            Administrador.correo == email,
            Administrador.estatus == EstatusTinyInt.ACTIVO,
        ).first()
    elif role == "estudiante":
        user = db.query(Estudiante).filter(
            Estudiante.correo == email,
            Estudiante.estatus == EstatusTinyInt.ACTIVO,
        ).first()
    else:
        return None

    if not user or not verify_password(password, user.contrasena):
        return None

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


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


def get_current_admin(current_user=Depends(get_current_user)):
    if not isinstance(current_user, Administrador):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador",
        )
    return current_user


def get_current_student(current_user=Depends(get_current_user)):
    if not isinstance(current_user, Estudiante):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de estudiante",
        )
    return current_user