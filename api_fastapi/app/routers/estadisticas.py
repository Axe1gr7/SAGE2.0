from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_api_key, limiter
from app.data.database import get_db
from app.models.SAGE_BD import Espacio, Modulo, Reserva, EstadoReserva

router = APIRouter(
    prefix="/estadisticas", 
    tags=["Estadísticas"], 
    dependencies=[Depends(get_api_key)]
)

@router.get("/espacios-mas-reservados")
@limiter.limit("20/minute")
def espacios_mas_reservados(request: Request, db: Session = Depends(get_db)):
    """
    Devuelve los 5 espacios con más reservas activas (no canceladas).
    """
    resultados = db.query(
        Espacio.nombre,
        func.count(Reserva.id_reserva).label("total")
    ).join(Reserva, Espacio.id_espacio == Reserva.id_espacio)\
     .filter(Reserva.estado == EstadoReserva.ACTIVA, Reserva.estatus == 0)\
     .group_by(Espacio.id_espacio)\
     .order_by(func.count(Reserva.id_reserva).desc())\
     .limit(5).all()
    
    # Convertir a lista de diccionarios
    return [{"nombre": nombre, "total": total} for nombre, total in resultados]

@router.get("/horarios-demanda")
@limiter.limit("20/minute")
def horarios_demanda(request: Request, db: Session = Depends(get_db)):
    """
    Devuelve los módulos horarios más reservados (por cantidad de reservas activas).
    Asume que la tabla `modulos` existe y está relacionada con `reservas` a través de `id_modulo`.
    """
    # Si tienes una tabla de módulos y una relación (ej. Reserva.id_modulo)
    resultados = db.query(
        Modulo.nombre,
        func.count(Reserva.id_reserva).label("total")
    ).join(Reserva, Modulo.id_modulo == Reserva.id_modulo)\
     .filter(Reserva.estado == EstadoReserva.ACTIVA, Reserva.estatus == 0)\
     .group_by(Modulo.id_modulo)\
     .order_by(func.count(Reserva.id_reserva).desc())\
     .all()
    
    return [{"hora": nombre, "total": total} for nombre, total in resultados]

    # Si NO tienes una tabla de módulos, puedes agrupar por hora de inicio (ejemplo comentado):
    # resultados = db.query(
    #     func.extract('hour', Reserva.fecha_hora_inicio).label("hora"),
    #     func.count(Reserva.id_reserva).label("total")
    # ).filter(Reserva.estado == "activa", Reserva.estatus == 0)\
    #  .group_by("hora")\
    #  .order_by(func.count(Reserva.id_reserva).desc())\
    #  .all()
    # return [{"hora": f"{int(hora)}:00", "total": total} for hora, total in resultados]