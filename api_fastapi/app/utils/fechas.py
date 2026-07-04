from datetime import date, timedelta
from typing import List

def generar_fechas_semestre(fecha_inicio: date, fecha_fin: date, dia_semana: int) -> List[date]:
    fechas = []
    if fecha_inicio.weekday() <= dia_semana:
        primera_fecha = fecha_inicio + timedelta(days=(dia_semana - fecha_inicio.weekday()))
    else:
        primera_fecha = fecha_inicio + timedelta(days=(7 - fecha_inicio.weekday() + dia_semana))
    
    fecha_actual = primera_fecha
    while fecha_actual <= fecha_fin:
        fechas.append(fecha_actual)
        fecha_actual += timedelta(days=7)
    return fechas