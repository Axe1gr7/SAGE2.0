from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.SAGE_BD import AccionAuditoriaEnum

class AuditoriaReservaBase(BaseModel):
    id_reserva: int
    accion: AccionAuditoriaEnum
    fecha_hora: datetime
    id_administrador: Optional[int] = None
    id_estudiante: Optional[int] = None

class AuditoriaReservaResponse(AuditoriaReservaBase):
    id_auditoria: int
    estatus: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True