"""
Script de inicialización de datos para SAGE.
Inserta módulos, administrador, estudiantes, espacios, equipos y eventos.
"""

import sys
from app.data.database import SessionLocal, engine
from datetime import datetime, timedelta, time
from app.data.database import SessionLocal, engine

# Asegúrate de que esta ruta coincida con la ubicación de tus modelos
from app.models.SAGE_BD import (
    Base, Estudiante, Administrador, Espacio, Equipo, Evento, Modulo,
    CarreraEnum, EstadoOperativo, EstatusTinyInt
)
# Asumiendo que esta función existe en tu proyecto
from app.auth import get_password_hash

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # ==================================================
    # 1. MÓDULOS (8 módulos de 100 minutos)
    # ==================================================
    modulos = [
        {"nombre": "Módulo 1 (7:00-8:40)", "hora_inicio": time(7, 0), "hora_fin": time(8, 40), "orden": 1},
        {"nombre": "Módulo 2 (8:40-10:20)", "hora_inicio": time(8, 40), "hora_fin": time(10, 20), "orden": 2},
        {"nombre": "Módulo 3 (10:20-12:00)", "hora_inicio": time(10, 20), "hora_fin": time(12, 0), "orden": 3},
        {"nombre": "Módulo 4 (12:00-13:40)", "hora_inicio": time(12, 0), "hora_fin": time(13, 40), "orden": 4},
        {"nombre": "Módulo 5 (14:00-15:40)", "hora_inicio": time(14, 0), "hora_fin": time(15, 40), "orden": 5},
        {"nombre": "Módulo 6 (15:40-17:20)", "hora_inicio": time(15, 40), "hora_fin": time(17, 20), "orden": 6},
        {"nombre": "Módulo 7 (17:20-19:00)", "hora_inicio": time(17, 20), "hora_fin": time(19, 0), "orden": 7},
        {"nombre": "Módulo 8 (19:00-20:40)", "hora_inicio": time(19, 0), "hora_fin": time(20, 40), "orden": 8},
    ]
    for m_data in modulos:
        if not db.query(Modulo).filter(Modulo.orden == m_data["orden"]).first():
            modulo = Modulo(**m_data)
            db.add(modulo)
    db.flush()
    print("Módulos revisados/insertados.")

    # ==================================================
    # 2. ADMINISTRADOR
    # ==================================================
    # CORRECCIÓN: Validación para evitar IntegrityError por correo duplicado
    correo_admin = "axelgr@upq.mx"
    if not db.query(Administrador).filter(Administrador.correo == correo_admin).first():
        admin = Administrador(
            nombre_completo="Axel GR",
            puesto="Coordinador de Sistemas",
            correo=correo_admin,
            contrasena=get_password_hash("axel13"),
            estatus=EstatusTinyInt.ACTIVO
        )
        db.add(admin)
        db.flush()
        print("Administrador insertado.")
    else:
        print("El administrador ya existe.")

    # ==================================================
    # 3. ESTUDIANTES
    # ==================================================
    estudiantes_data = [
        {"nombre_completo": "Andres badillo", "matricula": "A001", "correo": "andres.badillo@upq.edu.mx", "carrera": CarreraEnum.SISTEMAS},
        {"nombre_completo": "Antonio Hernandez", "matricula": "A002", "correo": "antonio.hernandez@upq.edu.mx", "carrera": CarreraEnum.MECATRONICA},
        {"nombre_completo": "Edith Uribe", "matricula": "A003", "correo": "edith.uribe@upq.edu.mx", "carrera": CarreraEnum.INGENIERIA_DATOS},
    ]
    for est_data in estudiantes_data:
        if not db.query(Estudiante).filter(Estudiante.matricula == est_data["matricula"]).first():
            estudiante = Estudiante(
                nombre_completo=est_data["nombre_completo"],
                matricula=est_data["matricula"],
                correo=est_data["correo"],
                contrasena=get_password_hash("estudiante123"),
                carrera=est_data["carrera"],
                estatus=EstatusTinyInt.ACTIVO
            )
            db.add(estudiante)
    db.flush()
    print("Estudiantes revisados/insertados.")

    # ==================================================
    # 4. ESPACIOS
    # ==================================================
    espacios_data = [
        {"tipo_espacio": "Laboratorio", "nombre": "Laboratorio A1", "ubicacion": "Edificio A, Planta 1", "capacidad": 30, "horario_apertura": time(7,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Laboratorio", "nombre": "Laboratorio A2", "ubicacion": "Edificio A, Planta 1", "capacidad": 30, "horario_apertura": time(7,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Laboratorio", "nombre": "Laboratorio B1", "ubicacion": "Edificio B, Planta 1", "capacidad": 25, "horario_apertura": time(7,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Laboratorio", "nombre": "Laboratorio B2", "ubicacion": "Edificio B, Planta 1", "capacidad": 25, "horario_apertura": time(7,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Laboratorio", "nombre": "Laboratorio C1", "ubicacion": "Edificio C, Planta 2", "capacidad": 20, "horario_apertura": time(7,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Laboratorio", "nombre": "Laboratorio C2", "ubicacion": "Edificio C, Planta 2", "capacidad": 20, "horario_apertura": time(7,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Laboratorio", "nombre": "Laboratorio D1", "ubicacion": "Edificio D, Planta 1", "capacidad": 35, "horario_apertura": time(7,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Laboratorio", "nombre": "Laboratorio Capta", "ubicacion": "Edificio Innovación", "capacidad": 40, "horario_apertura": time(7,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Laboratorio", "nombre": "Laboratorio Cidea", "ubicacion": "Edificio Innovación", "capacidad": 45, "horario_apertura": time(7,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Sala", "nombre": "Isoptica-C", "ubicacion": "Edificio Central", "capacidad": 80, "horario_apertura": time(8,0), "horario_cierre": time(20,0), "disponible": True},
        {"tipo_espacio": "Sala", "nombre": "Isoptica-B", "ubicacion": "Edificio Central", "capacidad": 60, "horario_apertura": time(8,0), "horario_cierre": time(20,0), "disponible": True},
        {"tipo_espacio": "Sala", "nombre": "Sala 3D", "ubicacion": "Edificio Multimedia", "capacidad": 50, "horario_apertura": time(9,0), "horario_cierre": time(19,0), "disponible": True},
        {"tipo_espacio": "Deportivo", "nombre": "Cancha de Basquetbol", "ubicacion": "Área Deportiva", "capacidad": 100, "horario_apertura": time(6,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Deportivo", "nombre": "Cancha de Fútbol 11", "ubicacion": "Área Deportiva", "capacidad": 300, "horario_apertura": time(6,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Deportivo", "nombre": "Cancha de Fútbol 7", "ubicacion": "Área Deportiva", "capacidad": 150, "horario_apertura": time(6,0), "horario_cierre": time(22,0), "disponible": True},
        {"tipo_espacio": "Servicios", "nombre": "Cafetería", "ubicacion": "Edificio Central", "capacidad": 80, "horario_apertura": time(7,0), "horario_cierre": time(20,0), "disponible": True},
        {"tipo_espacio": "Servicios", "nombre": "Biblioteca", "ubicacion": "Edificio Cultural", "capacidad": 200, "horario_apertura": time(8,0), "horario_cierre": time(21,0), "disponible": True},
    ]

    espacios_creados = {}
    for esp_data in espacios_data:
        # CORRECCIÓN: Buscamos el espacio. Si existe, guardamos su ID. Si no, lo creamos y luego guardamos su ID.
        espacio = db.query(Espacio).filter(Espacio.nombre == esp_data["nombre"]).first()
        if not espacio:
            espacio = Espacio(**esp_data, estatus=EstatusTinyInt.ACTIVO)
            db.add(espacio)
            db.flush()
        
        # Ahora siempre tendremos un ID válido para el diccionario
        espacios_creados[esp_data["nombre"]] = espacio.id_espacio
        
    print("Espacios revisados/insertados.")

    # ==================================================
    # 5. EQUIPOS PARA LABORATORIOS (10 PCs cada uno)
    # ==================================================
    nombres_laboratorios = [
        "Laboratorio A1", "Laboratorio A2", "Laboratorio B1", "Laboratorio B2",
        "Laboratorio C1", "Laboratorio C2", "Laboratorio D1", "Laboratorio Capta", "Laboratorio Cidea"
    ]
    for lab_nombre in nombres_laboratorios:
        espacio_id = espacios_creados.get(lab_nombre)
        if not espacio_id:
            continue
            
        # Verificar si ya existen equipos en este espacio
        if db.query(Equipo).filter(Equipo.id_espacio == espacio_id).first():
            continue
            
        for i in range(1, 11):
            equipo = Equipo(
                id_espacio=espacio_id,
                nombre_equipo=f"PC-{i:02d}",
                tipo_equipo="PC",
                estado_operativo=EstadoOperativo.OPERATIVO,
                estatus=EstatusTinyInt.ACTIVO
            )
            db.add(equipo)
    db.flush()
    print("Equipos insertados.")

    # ==================================================
    # 6. EVENTOS (en espacios no reservables, fechas futuras)
    # ==================================================
    eventos_data = [
        {"nombre": "Conferencia de Inteligencia Artificial", "descripcion": "Evento anual de IA con invitados internacionales.", "fecha_inicio": datetime.now() + timedelta(days=30), "fecha_fin": datetime.now() + timedelta(days=30, hours=8)},
        {"nombre": "Torneo de Basquetbol Intercarreras", "descripcion": "Competencia entre equipos de diferentes carreras.", "fecha_inicio": datetime.now() + timedelta(days=15), "fecha_fin": datetime.now() + timedelta(days=15, hours=4)},
        {"nombre": "Taller de Impresión 3D", "descripcion": "Introducción a la impresión 3D y modelado.", "fecha_inicio": datetime.now() + timedelta(days=7), "fecha_fin": datetime.now() + timedelta(days=7, hours=3)},
        {"nombre": "Feria de Emprendimiento", "descripcion": "Exposición de proyectos de estudiantes y startups.", "fecha_inicio": datetime.now() + timedelta(days=45), "fecha_fin": datetime.now() + timedelta(days=45, hours=10)},
        {"nombre": "Noche de Café Literario", "descripcion": "Lectura de poesía y café en la cafetería universitaria.", "fecha_inicio": datetime.now() + timedelta(days=20, hours=19), "fecha_fin": datetime.now() + timedelta(days=20, hours=22)},
    ]
    for evt_data in eventos_data:
        if not db.query(Evento).filter(Evento.nombre == evt_data["nombre"]).first():
            evento = Evento(
                nombre=evt_data["nombre"],
                descripcion=evt_data["descripcion"],
                fecha_inicio=evt_data["fecha_inicio"],
                fecha_fin=evt_data["fecha_fin"],
                estatus=EstatusTinyInt.ACTIVO
            )
            db.add(evento)
            
    # Finalmente aplicamos el commit general
    db.commit()
    print("Eventos revisados/insertados.")
    print("\n¡Todos los datos se han procesado correctamente!")

except Exception as e:
    db.rollback()
    print(f"Error al insertar datos: {e}", file=sys.stderr)
    raise
finally:
    db.close()