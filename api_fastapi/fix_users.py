from datetime import datetime, timedelta
from app.data.database import SessionLocal
from app.models.SAGE_BD import (
    Reserva, Estudiante, Espacio, Equipo, 
    TipoReserva, EstadoReserva, EstatusTinyInt
)

db = SessionLocal()

try:
    edith = db.query(Estudiante).filter(Estudiante.correo == "edith.uribe@upq.edu.mx").first()
    espacio = db.query(Espacio).first()
    equipo = db.query(Equipo).first()

    if not edith or not espacio or not equipo:
        print("❌ Error: No se encontró a Edith o los recursos.")
        exit()

    # Limpiamos para evitar duplicados
    db.query(Reserva).filter(Reserva.id_estudiante == edith.id_estudiante).delete()

    ahora = datetime.now()

    # Intentamos detectar los nombres correctos del Enum, si fallan usamos el string
    def get_estado(nombre):
        try:
            return getattr(EstadoReserva, nombre)
        except AttributeError:
            # Si 'FINALIZADA' no existe, intentamos 'CONCLUIDA' o devolvemos 'ACTIVA' por defecto
            return EstadoReserva.ACTIVA 

    # Definición de las 4 reservas
    reservas_a_crear = [
        {"estado": EstadoReserva.ACTIVA, "fecha": ahora + timedelta(days=1)},
        {"estado": EstadoReserva.ACTIVA, "fecha": ahora + timedelta(hours=5)},
        {"estado": get_estado("CANCELADA"), "fecha": ahora - timedelta(days=1)},
        {"estado": get_estado("FINALIZADA"), "fecha": ahora - timedelta(days=2)},
    ]

    for data in reservas_a_crear:
        nueva = Reserva(
            id_estudiante=edith.id_estudiante,
            id_espacio=espacio.id_espacio,
            id_equipo=equipo.id_equipo,
            fecha_hora_inicio=data["fecha"],
            fecha_hora_fin=data["fecha"] + timedelta(hours=1),
            tipo_reserva=TipoReserva.ESTUDIANTE,
            estado=data["estado"],
            estatus=EstatusTinyInt.ACTIVO
        )
        db.add(nueva)

    db.commit()
    print("✅ ¡Éxito! Se generaron 4 reservas para Edith.")
    print("Revisa ahora el historial en el navegador.")

except Exception as e:
    db.rollback()
    print(f"❌ Error crítico: {e}")
finally:
    db.close()