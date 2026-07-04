from typing import Optional
from pydantic import BaseModel
from datetime import datetime, time

class EspacioBase(BaseModel):
    tipo_espacio: str
    nombre: str
    ubicacion: str
    capacidad: int
    horario_apertura: time
    horario_cierre: time
    disponible: bool = True

class EspacioCreate(EspacioBase):
    pass

class EspacioUpdate(BaseModel):
    tipo_espacio: Optional[str] = None
    nombre: Optional[str] = None
    ubicacion: Optional[str] = None
    capacidad: Optional[int] = None
    horario_apertura: Optional[time] = None
    horario_cierre: Optional[time] = None
    disponible: Optional[bool] = None

class EspacioResponse(EspacioBase):
    id_espacio: int
    estatus: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True