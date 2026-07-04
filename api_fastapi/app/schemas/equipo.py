from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.SAGE_BD import EstadoOperativo

class EquipoBase(BaseModel):
    id_espacio: int
    nombre_equipo: str
    tipo_equipo: str
    estado_operativo: EstadoOperativo = EstadoOperativo.OPERATIVO

class EquipoCreate(EquipoBase):
    pass

class EquipoUpdate(BaseModel):
    nombre_equipo: Optional[str] = None
    tipo_equipo: Optional[str] = None
    estado_operativo: Optional[EstadoOperativo] = None

class EquipoResponse(EquipoBase):
    id_equipo: int
    estatus: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True