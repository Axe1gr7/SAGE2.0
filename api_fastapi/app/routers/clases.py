from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.data.database import get_db
from app.models.SAGE_BD import Clase, HorarioClase, Reserva, Espacio, Modulo, TipoReserva, EstadoReserva, Administrador
from app.schemas.clase import ClaseCreate, ClaseUpdate, ClaseResponse
from app.schemas.horario_clase import HorarioClaseCreate, HorarioClaseResponse
from app.auth import get_current_admin
from app.utils.fechas import generar_fechas_semestre

router = APIRouter(prefix="/clases", tags=["Clases"])

# CRUD básico de clases (ya lo tenías, lo incluimos completo)
@router.get("/", response_model=list[ClaseResponse])
async def list_clases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return db.query(Clase).filter(Clase.estatus == 0).offset(skip).limit(limit).all()

@router.post("/", response_model=ClaseResponse)
async def create_clase(clase: ClaseCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_clase = Clase(**clase.dict())
    db.add(db_clase)
    db.commit()
    db.refresh(db_clase)
    return db_clase

@router.get("/{id}", response_model=ClaseResponse)
async def get_clase(id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    clase = db.query(Clase).filter(Clase.id_clase == id, Clase.estatus == 0).first()
    if not clase:
        raise HTTPException(404, "Clase no encontrada")
    return clase

@router.put("/{id}", response_model=ClaseResponse)
async def update_clase(id: int, clase_update: ClaseUpdate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_clase = db.query(Clase).filter(Clase.id_clase == id, Clase.estatus == 0).first()
    if not db_clase:
        raise HTTPException(404, "Clase no encontrada")
    for key, value in clase_update.dict(exclude_unset=True).items():
        setattr(db_clase, key, value)
    db.commit()
    db.refresh(db_clase)
    return db_clase

@router.delete("/{id}")
async def delete_clase(id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_clase = db.query(Clase).filter(Clase.id_clase == id).first()
    if not db_clase:
        raise HTTPException(404, "Clase no encontrada")
    db_clase.estatus = 1
    db.commit()
    return {"msg": "Clase eliminada (soft delete)"}

# Nuevo endpoint: crear horario recurrente para una clase
@router.post("/{id_clase}/horarios", response_model=HorarioClaseResponse)
async def crear_horario_clase(
    id_clase: int,
    horario: HorarioClaseCreate,
    db: Session = Depends(get_db),
    admin: Administrador = Depends(get_current_admin)
):
    # Verificar que la clase existe
    clase = db.query(Clase).filter(Clase.id_clase == id_clase, Clase.estatus == 0).first()
    if not clase:
        raise HTTPException(404, "Clase no encontrada")

    # Verificar módulo existe
    modulo = db.query(Modulo).filter(Modulo.id_modulo == horario.id_modulo, Modulo.estatus == 0).first()
    if not modulo:
        raise HTTPException(404, "Módulo no encontrado")

    # Verificar espacio existe y está activo
    espacio = db.query(Espacio).filter(Espacio.id_espacio == horario.id_espacio, Espacio.estatus == 0).first()
    if not espacio:
        raise HTTPException(404, "Espacio no encontrado")

    # Validar dia_semana (0=lunes, 6=domingo)
    if not 0 <= horario.dia_semana <= 6:
        raise HTTPException(400, "Día de semana debe ser entre 0 (lunes) y 6 (domingo)")

    # Validar fechas del semestre
    if horario.fecha_inicio_semestre > horario.fecha_fin_semestre:
        raise HTTPException(400, "La fecha de inicio del semestre debe ser anterior a la fecha de fin")

    # Crear el registro de horario
    db_horario = HorarioClase(
        id_clase=id_clase,
        id_modulo=horario.id_modulo,
        id_espacio=horario.id_espacio,
        dia_semana=horario.dia_semana,
        fecha_inicio_semestre=horario.fecha_inicio_semestre,
        fecha_fin_semestre=horario.fecha_fin_semestre,
        id_administrador_creador=admin.id_administrador,
        estatus=0
    )
    db.add(db_horario)
    db.flush()  # para obtener id_horario

    # Generar las fechas de todas las semanas dentro del semestre
    fechas_clase = generar_fechas_semestre(
        horario.fecha_inicio_semestre,
        horario.fecha_fin_semestre,
        horario.dia_semana
    )

    # Para cada fecha, crear una reserva
    for fecha in fechas_clase:
        inicio = datetime.combine(fecha, modulo.hora_inicio)
        fin = datetime.combine(fecha, modulo.hora_fin)

        # Verificar disponibilidad del espacio en ese día y horario
        conflicto = db.query(Reserva).filter(
            Reserva.id_espacio == horario.id_espacio,
            Reserva.estado == EstadoReserva.ACTIVA,
            Reserva.estatus == 0,
            Reserva.fecha_hora_inicio < fin,
            Reserva.fecha_hora_fin > inicio
        ).first()
        if conflicto:
            db.rollback()
            raise HTTPException(409, f"Conflicto de horario en {fecha} con reserva {conflicto.id_reserva}")

        # Crear la reserva para la clase
        reserva = Reserva(
            id_espacio=horario.id_espacio,
            tipo_reserva=TipoReserva.CLASE,
            id_clase=id_clase,
            id_administrador_creador=admin.id_administrador,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=fin,
            estado=EstadoReserva.ACTIVA,
            estatus=0
        )
        db.add(reserva)

    db.commit()
    db.refresh(db_horario)
    return db_horario