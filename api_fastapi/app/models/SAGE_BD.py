import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, DateTime, Time,Date,
    Enum as SQLEnum, Text, TIMESTAMP, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.data.database import Base

# ==================================================
# Enumeraciones y constantes (Corregidas para SQLAlchemy)
# ==================================================

class EstatusTinyInt:
    ACTIVO = 0
    ELIMINADO = 1

# Al heredar de enum.Enum, PostgreSQL entiende que esto es un tipo ENUM nativo
class EstadoReserva(enum.Enum):
    ACTIVA = 'activa'
    CANCELADA = 'cancelada'

class TipoReserva(enum.Enum):
    ESTUDIANTE = 'estudiante'
    CLASE = 'clase'
    EVENTO = 'evento'

class EstadoOperativo(enum.Enum):
    OPERATIVO = 'operativo'
    MANTENIMIENTO = 'mantenimiento'

class CarreraEnum(enum.Enum):
    SISTEMAS = 'sistemas'
    MECATRONICA = 'mecatronica'
    INGENIERIA_DATOS = 'ingenieria de datos'
    AUTOMOTRIZ = 'automotriz'
    NEGOCIOS_INTERNACIONALES = 'negocios internacionales'
    ADMINISTRACION = 'administracion '
    MANUFACTURA = 'manufactura'

class AccionAuditoriaEnum(enum.Enum):
    INSERT = 'INSERT'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'

# ==================================================
# Modelos
# ==================================================

class Estudiante(Base):
    __tablename__ = "estudiantes"

    id_estudiante = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(200), nullable=False)
    matricula = Column(String(20), unique=True, nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    # Ahora usamos la sintaxis limpia para los Enums
    carrera = Column(SQLEnum(CarreraEnum), nullable=False)
    estatus = Column(Integer, default=EstatusTinyInt.ACTIVO, comment='0=activo, 1=eliminado')
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relaciones
    reservas_beneficiario = relationship("Reserva", foreign_keys="Reserva.id_estudiante", back_populates="estudiante_beneficiario")
    reservas_creador = relationship("Reserva", foreign_keys="Reserva.id_estudiante_creador", back_populates="estudiante_creador")
    auditorias = relationship("AuditoriaReserva", foreign_keys="AuditoriaReserva.id_estudiante", back_populates="estudiante")


class Administrador(Base):
    __tablename__ = "administradores"

    id_administrador = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(200), nullable=False)
    puesto = Column(String(100))
    correo = Column(String(100), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    estatus = Column(Integer, default=EstatusTinyInt.ACTIVO)
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relaciones
    reservas_creador = relationship("Reserva", foreign_keys="Reserva.id_administrador_creador", back_populates="administrador_creador")
    auditorias = relationship("AuditoriaReserva", foreign_keys="AuditoriaReserva.id_administrador", back_populates="administrador")


class Espacio(Base):
    __tablename__ = "espacios"

    id_espacio = Column(Integer, primary_key=True, index=True)
    tipo_espacio = Column(String(50), nullable=False)
    nombre = Column(String(100), nullable=False)
    ubicacion = Column(String(255), nullable=False)
    capacidad = Column(Integer, nullable=False)
    horario_apertura = Column(Time, nullable=False)
    horario_cierre = Column(Time, nullable=False)
    disponible = Column(Boolean, default=True)
    estatus = Column(Integer, default=EstatusTinyInt.ACTIVO)
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relaciones
    equipos = relationship("Equipo", back_populates="espacio")
    reservas = relationship("Reserva", back_populates="espacio")
    clases_asignadas = relationship("Clase", back_populates="espacio_asignado")  # para clases que tengan espacio fijo


class Equipo(Base):
    __tablename__ = "equipos"

    id_equipo = Column(Integer, primary_key=True, index=True)
    id_espacio = Column(Integer, ForeignKey("espacios.id_espacio"), nullable=False)
    nombre_equipo = Column(String(50), nullable=False)
    tipo_equipo = Column(String(50), nullable=False)
    estado_operativo = Column(SQLEnum(EstadoOperativo), default=EstadoOperativo.OPERATIVO)
    estatus = Column(Integer, default=EstatusTinyInt.ACTIVO)
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relaciones
    espacio = relationship("Espacio", back_populates="equipos")
    reservas = relationship("Reserva", back_populates="equipo")


class Clase(Base):
    __tablename__ = "clases"

    id_clase = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    materia = Column(String(100), nullable=False)
    grupo = Column(String(20), nullable=False)
    docente = Column(String(100), nullable=False)
    correo_docente = Column(String(100))
    horario = Column(String(255), comment="Información textual del horario")
    estatus = Column(Integer, default=EstatusTinyInt.ACTIVO)
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relaciones
    reservas = relationship("Reserva", back_populates="clase_beneficiario")
    # Opcional: un administrador puede ser responsable de la clase
    id_administrador = Column(Integer, ForeignKey("administradores.id_administrador"), nullable=True)
    administrador = relationship("Administrador")
    # Opcional: espacio fijo asignado a la clase (para uso recurrente)
    id_espacio_asignado = Column(Integer, ForeignKey("espacios.id_espacio"), nullable=True)
    espacio_asignado = relationship("Espacio", back_populates="clases_asignadas")
    
    horarios = relationship("HorarioClase", back_populates="clase")

class Evento(Base):
    __tablename__ = "eventos"

    id_evento = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    estatus = Column(Integer, default=EstatusTinyInt.ACTIVO)
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relaciones
    reservas = relationship("Reserva", back_populates="evento_beneficiario")


class Reserva(Base):
    __tablename__ = "reservas"

    id_reserva = Column(Integer, primary_key=True, index=True)
    id_espacio = Column(Integer, ForeignKey("espacios.id_espacio"), nullable=False)
    id_equipo = Column(Integer, ForeignKey("equipos.id_equipo"), nullable=True)   # reserva de equipo específico
    tipo_reserva = Column(SQLEnum(TipoReserva), nullable=False)

    # Beneficiario según tipo_reserva
    id_estudiante = Column(Integer, ForeignKey("estudiantes.id_estudiante"), nullable=True)
    id_clase = Column(Integer, ForeignKey("clases.id_clase"), nullable=True)
    id_evento = Column(Integer, ForeignKey("eventos.id_evento"), nullable=True)

    # Creador de la reserva
    id_administrador_creador = Column(Integer, ForeignKey("administradores.id_administrador"), nullable=True)
    id_estudiante_creador = Column(Integer, ForeignKey("estudiantes.id_estudiante"), nullable=True)

    fecha_hora_inicio = Column(DateTime, nullable=False)
    fecha_hora_fin = Column(DateTime, nullable=False)
    estado = Column(SQLEnum(EstadoReserva), default=EstadoReserva.ACTIVA)
    motivo_cancelacion = Column(String(255), nullable=True)
    observaciones = Column(Text, nullable=True)

    estatus = Column(Integer, default=EstatusTinyInt.ACTIVO, comment="0=activa, 1=eliminada")
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relaciones
    espacio = relationship("Espacio", back_populates="reservas")
    equipo = relationship("Equipo", back_populates="reservas")
    estudiante_beneficiario = relationship("Estudiante", foreign_keys=[id_estudiante], back_populates="reservas_beneficiario")
    clase_beneficiario = relationship("Clase", foreign_keys=[id_clase], back_populates="reservas")
    evento_beneficiario = relationship("Evento", foreign_keys=[id_evento], back_populates="reservas")
    administrador_creador = relationship("Administrador", foreign_keys=[id_administrador_creador], back_populates="reservas_creador")
    estudiante_creador = relationship("Estudiante", foreign_keys=[id_estudiante_creador], back_populates="reservas_creador")

    # Auditoría
    auditorias = relationship("AuditoriaReserva", back_populates="reserva")


class AuditoriaReserva(Base):
    __tablename__ = "auditoria_reservas"

    id_auditoria = Column(Integer, primary_key=True, index=True)
    id_reserva = Column(Integer, ForeignKey("reservas.id_reserva", ondelete="CASCADE"), nullable=False)
    id_administrador = Column(Integer, ForeignKey("administradores.id_administrador", ondelete="SET NULL"), nullable=True)
    id_estudiante = Column(Integer, ForeignKey("estudiantes.id_estudiante", ondelete="SET NULL"), nullable=True)
    accion = Column(SQLEnum(AccionAuditoriaEnum), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    estatus = Column(Integer, default=EstatusTinyInt.ACTIVO)
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relaciones
    reserva = relationship("Reserva", back_populates="auditorias")
    administrador = relationship("Administrador", foreign_keys=[id_administrador], back_populates="auditorias")
    estudiante = relationship("Estudiante", foreign_keys=[id_estudiante], back_populates="auditorias") 
    
class Modulo(Base):
    __tablename__ = "modulos"

    id_modulo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)          # ej. "Módulo 1 (7:00-8:40)"
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    orden = Column(Integer, nullable=False)              # para ordenar
    estatus = Column(Integer, default=EstatusTinyInt.ACTIVO)
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relaciones
    horarios_clase = relationship("HorarioClase", back_populates="modulo")
    # No relación directa con reservas, pero se puede usar para validación


class HorarioClase(Base):
    __tablename__ = "horarios_clase"

    id_horario = Column(Integer, primary_key=True, index=True)
    id_clase = Column(Integer, ForeignKey("clases.id_clase"), nullable=False)
    id_modulo = Column(Integer, ForeignKey("modulos.id_modulo"), nullable=False)
    id_espacio = Column(Integer, ForeignKey("espacios.id_espacio"), nullable=False)
    dia_semana = Column(Integer, nullable=False)          # 0 = lunes, 1 = martes, ..., 6 = domingo
    fecha_inicio_semestre = Column(Date, nullable=False)
    fecha_fin_semestre = Column(Date, nullable=False)
    id_administrador_creador = Column(Integer, ForeignKey("administradores.id_administrador"), nullable=False)
    estatus = Column(Integer, default=EstatusTinyInt.ACTIVO)
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relaciones
    clase = relationship("Clase", back_populates="horarios")
    modulo = relationship("Modulo", back_populates="horarios_clase")
    espacio = relationship("Espacio")
    administrador = relationship("Administrador")

    # Para facilitar la generación de reservas, se puede añadir un método