from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.SAGE_BD import CarreraEnum

class EstudianteBase(BaseModel):
    nombre_completo: str
    matricula: str
    correo: EmailStr
    carrera: CarreraEnum

class EstudianteCreate(EstudianteBase):
    contrasena: str

class EstudianteUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    matricula: Optional[str] = None
    correo: Optional[EmailStr] = None
    carrera: Optional[CarreraEnum] = None
    contrasena: Optional[str] = None

class EstudianteResponse(EstudianteBase):
    id_estudiante: int
    estatus: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True