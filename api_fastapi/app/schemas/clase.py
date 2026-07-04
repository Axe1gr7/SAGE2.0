from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ClaseBase(BaseModel):
    nombre: str
    materia: str
    grupo: str
    docente: str
    correo_docente: Optional[str] = None
    horario: Optional[str] = None
    id_administrador: Optional[int] = None
    id_espacio_asignado: Optional[int] = None

class ClaseCreate(ClaseBase):
    pass

class ClaseUpdate(BaseModel):
    nombre: Optional[str] = None
    materia: Optional[str] = None
    grupo: Optional[str] = None
    docente: Optional[str] = None
    correo_docente: Optional[str] = None
    horario: Optional[str] = None
    id_administrador: Optional[int] = None
    id_espacio_asignado: Optional[int] = None

class ClaseResponse(ClaseBase):
    id_clase: int
    estatus: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True