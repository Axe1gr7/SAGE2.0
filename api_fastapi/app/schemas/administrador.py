from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class AdministradorBase(BaseModel):
    nombre_completo: str
    puesto: Optional[str] = None
    correo: EmailStr

class AdministradorCreate(AdministradorBase):
    contrasena: str

class AdministradorUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    puesto: Optional[str] = None
    correo: Optional[EmailStr] = None
    contrasena: Optional[str] = None

class AdministradorResponse(AdministradorBase):
    id_administrador: int
    estatus: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True