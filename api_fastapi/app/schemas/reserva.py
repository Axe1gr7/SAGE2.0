from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.SAGE_BD import TipoReserva, EstadoReserva

class ReservaBase(BaseModel):
    id_espacio: int
    id_equipo: Optional[int] = None
    tipo_reserva: TipoReserva
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    observaciones: Optional[str] = None

class ReservaCreate(ReservaBase):
    id_estudiante_beneficiario: Optional[int] = None
    id_clase_beneficiario: Optional[int] = None
    id_evento_beneficiario: Optional[int] = None

class ReservaUpdate(BaseModel):
    fecha_hora_inicio: Optional[datetime] = None
    fecha_hora_fin: Optional[datetime] = None
    observaciones: Optional[str] = None
    estado: Optional[EstadoReserva] = None
    motivo_cancelacion: Optional[str] = None

class ReservaResponse(ReservaBase):
    id_reserva: int
    estado: EstadoReserva
    motivo_cancelacion: Optional[str] = None
    id_estudiante: Optional[int] = None
    id_clase: Optional[int] = None
    id_evento: Optional[int] = None
    id_administrador_creador: Optional[int] = None
    id_estudiante_creador: Optional[int] = None
    estatus: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True