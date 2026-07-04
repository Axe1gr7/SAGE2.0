from pydantic import BaseModel
from datetime import date

class HorarioClaseBase(BaseModel):
    id_clase: int
    id_modulo: int
    id_espacio: int
    dia_semana: int          # 0=lunes, 1=martes, ..., 6=domingo
    fecha_inicio_semestre: date
    fecha_fin_semestre: date

class HorarioClaseCreate(HorarioClaseBase):
    pass

class HorarioClaseResponse(HorarioClaseBase):
    id_horario: int
    estatus: int

    class Config:
        from_attributes = True