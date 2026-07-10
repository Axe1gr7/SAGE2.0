from datetime import datetime, date as date_type
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import Date, cast
from sqlalchemy.orm import Session

from app.auth import get_current_admin, get_current_user, limiter
from app.data.database import get_db
from app.models.SAGE_BD import (
    AccionAuditoriaEnum,
    Administrador,
    AuditoriaReserva,
    Clase,
    Equipo,
    Espacio,
    EstadoReserva,
    Estudiante,
    Evento,
    Modulo,
    Reserva,
    TipoReserva,
)
from app.schemas.reserva import ReservaCreate, ReservaResponse, ReservaUpdate

router = APIRouter(prefix="/reservas", tags=["Reservas"])

# Nuevo esquema para reserva de estudiante
class ReservaEstudianteCreate(BaseModel):
    id_espacio: int
    id_equipo: Optional[int] = None
    id_modulo: int
    fecha: date_type          # solo el día (YYYY-MM-DD)
    observaciones: Optional[str] = None

def verificar_disponibilidad(
    db: Session,
    id_espacio: int,
    id_equipo: Optional[int],
    inicio: datetime,
    fin: datetime,
    exclude_id: int = None
) -> bool:
    q = db.query(Reserva).filter(
        Reserva.id_espacio == id_espacio,
        Reserva.estado == EstadoReserva.ACTIVA,
        Reserva.estatus == 0,
        Reserva.fecha_hora_inicio < fin,
        Reserva.fecha_hora_fin > inicio
    )
    if id_equipo:
        q = q.filter(Reserva.id_equipo == id_equipo)
    if exclude_id:
        q = q.filter(Reserva.id_reserva != exclude_id)
    return q.count() == 0

def validar_beneficiario_segun_tipo(
    db: Session,
    tipo: TipoReserva,
    estudiante_id: Optional[int],
    clase_id: Optional[int],
    evento_id: Optional[int]
):
    if tipo == TipoReserva.ESTUDIANTE:
        if not estudiante_id or clase_id or evento_id:
            raise HTTPException(400, "Para reserva de estudiante debe indicar id_estudiante_beneficiario")
        estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == estudiante_id, Estudiante.estatus == 0).first()
        if not estudiante:
            raise HTTPException(404, "Estudiante no encontrado")
    elif tipo == TipoReserva.CLASE:
        if not clase_id or estudiante_id or evento_id:
            raise HTTPException(400, "Para reserva de clase debe indicar id_clase_beneficiario")
        clase = db.query(Clase).filter(Clase.id_clase == clase_id, Clase.estatus == 0).first()
        if not clase:
            raise HTTPException(404, "Clase no encontrada")
    elif tipo == TipoReserva.EVENTO:
        if not evento_id or estudiante_id or clase_id:
            raise HTTPException(400, "Para reserva de evento debe indicar id_evento_beneficiario")
        evento = db.query(Evento).filter(Evento.id_evento == evento_id, Evento.estatus == 0).first()
        if not evento:
            raise HTTPException(404, "Evento no encontrado")
    else:
        raise HTTPException(400, "Tipo de reserva inválido")

# ==========================================
# ENDPOINTS PARA MAPA INTERACTIVO
# ==========================================

@router.get("/ocupacion")
@limiter.limit("30/minute")
async def get_ocupacion(
    request: Request,
    fecha: date_type = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Devuelve la ocupación de los equipos para una fecha específica.
    """
    reservas = db.query(Reserva).filter(
        cast(Reserva.fecha_hora_inicio, Date) == fecha,
        Reserva.estado == EstadoReserva.ACTIVA,
        Reserva.estatus == 0
    ).all()

    ocupacion = {}
    for r in reservas:
        if not r.id_equipo:
            continue
            
        eq_id = str(r.id_equipo)
        if eq_id not in ocupacion:
            ocupacion[eq_id] = []
        
        ocupacion[eq_id].append({
            "inicio": r.fecha_hora_inicio.strftime("%H:%M"),
            "fin": r.fecha_hora_fin.strftime("%H:%M")
        })

    return {"ocupacion": ocupacion}

@router.get("/espacios/{espacio_id}/modulos-disponibles")
async def get_modulos_disponibles_espacio(
    espacio_id: int,
    fecha: date_type = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Devuelve los módulos libres para un espacio (cuando se reserva el espacio completo, sin equipo).
    """
    espacio = db.query(Espacio).filter(Espacio.id_espacio == espacio_id, Espacio.estatus == 0).first()
    if not espacio:
        raise HTTPException(404, "Espacio no encontrado")

    modulos_db = db.query(Modulo).filter(Modulo.estatus == 0).order_by(Modulo.hora_inicio).all()
    reservas = db.query(Reserva).filter(
        Reserva.id_espacio == espacio_id,
        Reserva.id_equipo == None, # Buscamos reservas de espacio completo
        cast(Reserva.fecha_hora_inicio, Date) == fecha,
        Reserva.estado == EstadoReserva.ACTIVA,
        Reserva.estatus == 0
    ).all()

    modulos_libres = []
    for mod in modulos_db:
        inicio_mod = datetime.combine(fecha, mod.hora_inicio)
        fin_mod = datetime.combine(fecha, mod.hora_fin)
        ocupado = any(r.fecha_hora_inicio < fin_mod and r.fecha_hora_fin > inicio_mod for r in reservas)
        
        if not ocupado:
            modulos_libres.append({
                "id_modulo": mod.id_modulo,
                "nombre": getattr(mod, 'nombre', f"Módulo {mod.id_modulo}"),
                "hora_inicio": mod.hora_inicio.strftime("%H:%M"),
                "hora_fin": mod.hora_fin.strftime("%H:%M")
            })

    return {"modulos": modulos_libres}

@router.get("/modulos")
async def get_todos_modulos(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Devuelve todos los módulos configurados en el sistema.
    """
    modulos = db.query(Modulo).filter(Modulo.estatus == 0).order_by(Modulo.hora_inicio).all()
    return [{"id_modulo": mod.id_modulo, "nombre": mod.nombre, "hora_inicio": mod.hora_inicio.strftime("%H:%M"), "hora_fin": mod.hora_fin.strftime("%H:%M")} for mod in modulos]

@router.get("/equipos/{equipo_id}/modulos-disponibles")
async def get_modulos_disponibles(
    equipo_id: int,
    fecha: date_type = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Devuelve los módulos dinámicos libres para un equipo específico en una fecha.
    """
    # 1. Validar que el equipo exista
    equipo = db.query(Equipo).filter(Equipo.id_equipo == equipo_id, Equipo.estatus == 0).first()
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")

    # 2. Obtener todos los módulos activos de la base de datos
    modulos_db = db.query(Modulo).filter(Modulo.estatus == 0).order_by(Modulo.hora_inicio).all()

    # 3. Obtener las reservas activas del equipo para ese día
    reservas = db.query(Reserva).filter(
        Reserva.id_equipo == equipo_id,
        cast(Reserva.fecha_hora_inicio, Date) == fecha,
        Reserva.estado == EstadoReserva.ACTIVA,
        Reserva.estatus == 0
    ).all()

    modulos_libres = []
    
    # 4. Cruzar módulos con reservas
    for mod in modulos_db:
        inicio_mod = datetime.combine(fecha, mod.hora_inicio)
        fin_mod = datetime.combine(fecha, mod.hora_fin)
        
        ocupado = False
        for r in reservas:
            # Lógica de solapamiento de horarios
            if r.fecha_hora_inicio < fin_mod and r.fecha_hora_fin > inicio_mod:
                ocupado = True
                break
                
        if not ocupado:
            # Se asume que tu modelo Modulo tiene un campo 'nombre' o descriptivo.
            # Si se llama diferente (ej. 'descripcion'), cámbialo aquí.
            nombre_modulo = getattr(mod, 'nombre', f"Módulo {mod.id_modulo}")
            
            modulos_libres.append({
                "id_modulo": mod.id_modulo,
                "nombre": nombre_modulo,
                "hora_inicio": mod.hora_inicio.strftime("%H:%M"),
                "hora_fin": mod.hora_fin.strftime("%H:%M")
            })

    return {"modulos": modulos_libres}

# ==========================================
# RUTAS ESTÁNDAR CRUD
# ==========================================

@router.post("/", response_model=ReservaResponse)
@limiter.limit("15/minute")
async def crear_reserva(
    request: Request,
    reserva: ReservaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    espacio = db.query(Espacio).filter(Espacio.id_espacio == reserva.id_espacio, Espacio.estatus == 0).first()
    if not espacio:
        raise HTTPException(404, "Espacio no encontrado")

    if reserva.id_equipo:
        equipo = db.query(Equipo).filter(
            Equipo.id_equipo == reserva.id_equipo,
            Equipo.id_espacio == espacio.id_espacio,
            Equipo.estatus == 0
        ).first()
        if not equipo:
            raise HTTPException(404, "Equipo no encontrado en este espacio")
        if equipo.estado_operativo.value != "operativo":
            raise HTTPException(400, "Equipo en mantenimiento, no se puede reservar")

    if reserva.fecha_hora_inicio.time() < espacio.horario_apertura or \
       reserva.fecha_hora_fin.time() > espacio.horario_cierre:
        raise HTTPException(400, f"Horario fuera del rango del espacio ({espacio.horario_apertura} - {espacio.horario_cierre})")

    if reserva.fecha_hora_inicio >= reserva.fecha_hora_fin:
        raise HTTPException(400, "La hora de inicio debe ser anterior a la de fin")

    if not verificar_disponibilidad(db, espacio.id_espacio, reserva.id_equipo,
                                    reserva.fecha_hora_inicio, reserva.fecha_hora_fin):
        raise HTTPException(409, "Conflicto: el espacio/equipo ya está reservado en ese horario")

    validar_beneficiario_segun_tipo(db, reserva.tipo_reserva,
                                    reserva.id_estudiante_beneficiario,
                                    reserva.id_clase_beneficiario,
                                    reserva.id_evento_beneficiario)

    if isinstance(current_user, Administrador):
        creador_admin_id = current_user.id_administrador
        creador_est_id = None
    else:
        creador_admin_id = None
        creador_est_id = current_user.id_estudiante

    db_reserva = Reserva(
        id_espacio=reserva.id_espacio,
        id_equipo=reserva.id_equipo,
        tipo_reserva=reserva.tipo_reserva,
        id_estudiante=reserva.id_estudiante_beneficiario,
        id_clase=reserva.id_clase_beneficiario,
        id_evento=reserva.id_evento_beneficiario,
        id_administrador_creador=creador_admin_id,
        id_estudiante_creador=creador_est_id,
        fecha_hora_inicio=reserva.fecha_hora_inicio,
        fecha_hora_fin=reserva.fecha_hora_fin,
        observaciones=reserva.observaciones
    )
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)

    auditoria = AuditoriaReserva(
        id_reserva=db_reserva.id_reserva,
        id_administrador=creador_admin_id,
        id_estudiante=creador_est_id,
        accion=AccionAuditoriaEnum.INSERT,
        fecha_hora=datetime.utcnow()
    )
    db.add(auditoria)
    db.commit()
    return db_reserva

@router.post("/estudiante", response_model=ReservaResponse)
@limiter.limit("15/minute")
async def crear_reserva_estudiante(
    request: Request,
    reserva: ReservaEstudianteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not isinstance(current_user, Estudiante):
        raise HTTPException(403, "Solo estudiantes pueden usar este endpoint")

    modulo = db.query(Modulo).filter(Modulo.id_modulo == reserva.id_modulo, Modulo.estatus == 0).first()
    if not modulo:
        raise HTTPException(404, "Módulo no encontrado")

    espacio = db.query(Espacio).filter(Espacio.id_espacio == reserva.id_espacio, Espacio.estatus == 0).first()
    if not espacio:
        raise HTTPException(404, "Espacio no encontrado")

    if not espacio.disponible:
        raise HTTPException(400, "Espacio no disponible para reservas")

    if modulo.hora_inicio < espacio.horario_apertura or modulo.hora_fin > espacio.horario_cierre:
        raise HTTPException(400, f"Módulo fuera del horario del espacio ({espacio.horario_apertura} - {espacio.horario_cierre})")

    inicio = datetime.combine(reserva.fecha, modulo.hora_inicio)
    fin = datetime.combine(reserva.fecha, modulo.hora_fin)

    if inicio < datetime.now():
        raise HTTPException(400, "No se puede reservar en el pasado")

    if reserva.id_equipo:
        equipo = db.query(Equipo).filter(
            Equipo.id_equipo == reserva.id_equipo,
            Equipo.id_espacio == espacio.id_espacio,
            Equipo.estatus == 0
        ).first()
        if not equipo:
            raise HTTPException(404, "Equipo no encontrado en este espacio")
        if equipo.estado_operativo.value != "operativo":
            raise HTTPException(400, "Equipo en mantenimiento, no se puede reservar")

    if not verificar_disponibilidad(db, espacio.id_espacio, reserva.id_equipo, inicio, fin):
        raise HTTPException(409, "El espacio/equipo ya está reservado en ese horario")

    db_reserva = Reserva(
        id_espacio=reserva.id_espacio,
        id_equipo=reserva.id_equipo,
        tipo_reserva=TipoReserva.ESTUDIANTE,
        id_estudiante=current_user.id_estudiante,
        id_estudiante_creador=current_user.id_estudiante,
        fecha_hora_inicio=inicio,
        fecha_hora_fin=fin,
        observaciones=reserva.observaciones
    )
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@router.get("/", response_model=list[ReservaResponse])
@limiter.limit("30/minute")
async def listar_reservas(
    request: Request,
    fecha_inicio: datetime = None,
    fecha_fin: datetime = None,
    espacio_id: int = None,
    equipo_id: int = None,
    estado: EstadoReserva = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Reserva).filter(Reserva.estatus == 0)
    if isinstance(current_user, Estudiante):
        query = query.filter(
            (Reserva.id_estudiante == current_user.id_estudiante) |
            (Reserva.id_estudiante_creador == current_user.id_estudiante)
        )
    if fecha_inicio:
        query = query.filter(Reserva.fecha_hora_inicio >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Reserva.fecha_hora_fin <= fecha_fin)
    if espacio_id:
        query = query.filter(Reserva.id_espacio == espacio_id)
    if equipo_id:
        query = query.filter(Reserva.id_equipo == equipo_id)
    if estado:
        query = query.filter(Reserva.estado == estado)
    query = query.order_by(Reserva.fecha_hora_inicio.desc())
    return query.offset(skip).limit(limit).all()

@router.get("/{id}", response_model=ReservaResponse)
async def get_reserva(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    reserva = db.query(Reserva).filter(Reserva.id_reserva == id, Reserva.estatus == 0).first()
    if not reserva:
        raise HTTPException(404, "Reserva no encontrada")
    if isinstance(current_user, Estudiante):
        if reserva.id_estudiante != current_user.id_estudiante and reserva.id_estudiante_creador != current_user.id_estudiante:
            raise HTTPException(403, "No tienes permiso para ver esta reserva")
    return reserva

@router.put("/{id}/cancelar", response_model=ReservaResponse)
async def cancelar_reserva(
    id: int,
    motivo: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    reserva = db.query(Reserva).filter(Reserva.id_reserva == id, Reserva.estatus == 0).first()
    if not reserva:
        raise HTTPException(404, "Reserva no encontrada")
    if isinstance(current_user, Estudiante):
        if reserva.id_estudiante_creador != current_user.id_estudiante and reserva.id_estudiante != current_user.id_estudiante:
            raise HTTPException(403, "No tienes permiso para cancelar esta reserva")
    if reserva.estado == EstadoReserva.CANCELADA:
        raise HTTPException(400, "La reserva ya está cancelada")
    reserva.estado = EstadoReserva.CANCELADA
    reserva.motivo_cancelacion = motivo
    db.commit()
    auditoria = AuditoriaReserva(
        id_reserva=id,
        id_administrador=current_user.id_administrador if isinstance(current_user, Administrador) else None,
        id_estudiante=current_user.id_estudiante if isinstance(current_user, Estudiante) else None,
        accion=AccionAuditoriaEnum.UPDATE,
        fecha_hora=datetime.utcnow()
    )
    db.add(auditoria)
    db.commit()
    db.refresh(reserva)
    return reserva

@router.put("/{id}", response_model=ReservaResponse)
async def update_reserva(
    id: int,
    reserva_update: ReservaUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    db_reserva = db.query(Reserva).filter(Reserva.id_reserva == id, Reserva.estatus == 0).first()
    if not db_reserva:
        raise HTTPException(404, "Reserva no encontrada")
    data = reserva_update.dict(exclude_unset=True)
    if "fecha_hora_inicio" in data or "fecha_hora_fin" in data:
        new_inicio = data.get("fecha_hora_inicio", db_reserva.fecha_hora_inicio)
        new_fin = data.get("fecha_hora_fin", db_reserva.fecha_hora_fin)
        if new_inicio >= new_fin:
            raise HTTPException(400, "La hora de inicio debe ser anterior a la de fin")
        if not verificar_disponibilidad(db, db_reserva.id_espacio, db_reserva.id_equipo,
                                        new_inicio, new_fin, exclude_id=id):
            raise HTTPException(409, "Conflicto de horario con otra reserva")
        db_reserva.fecha_hora_inicio = new_inicio
        db_reserva.fecha_hora_fin = new_fin
    if "observaciones" in data:
        db_reserva.observaciones = data["observaciones"]
    if "estado" in data and data["estado"] == EstadoReserva.CANCELADA:
        db_reserva.estado = EstadoReserva.CANCELADA
        db_reserva.motivo_cancelacion = data.get("motivo_cancelacion")
        auditoria = AuditoriaReserva(
            id_reserva=id,
            id_administrador=current_admin.id_administrador,
            accion=AccionAuditoriaEnum.UPDATE,
            fecha_hora=datetime.utcnow()
        )
        db.add(auditoria)
    elif "estado" in data:
        db_reserva.estado = data["estado"]
    db.commit()
    db.refresh(db_reserva)
    return db_reserva