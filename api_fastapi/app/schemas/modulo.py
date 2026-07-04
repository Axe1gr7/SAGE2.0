from pydantic import BaseModel
from datetime import time

class ModuloBase(BaseModel):
    nombre: str
    hora_inicio: time
    hora_fin: time
    orden: int

class ModuloCreate(ModuloBase):
    pass

class ModuloResponse(ModuloBase):
    id_modulo: int
    estatus: int

    class Config:
        from_attributes = True