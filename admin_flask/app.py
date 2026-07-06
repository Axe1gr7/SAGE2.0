from flask import Flask, redirect, url_for, request, flash, session, jsonify, render_template
import os
from functools import wraps
from datetime import date, timedelta, datetime

from api_service import api_request

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'sage_admin_secret')

# ==========================================
# DECORADOR DE AUTENTICACIÓN
# ==========================================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_access_token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# RUTAS PÚBLICAS
# ==========================================
@app.route('/')
def index():
    if 'admin_access_token' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        data = {'username': email, 'password': password, 'scope': 'admin'}
        resp = api_request('/auth/login', method='POST', data=data)
        print("RESPUESTA LOGIN:", resp) 

        if not isinstance(resp, dict) or 'error' in resp:
            flash('Credenciales inválidas o sin permisos de administrador', 'danger')
            return redirect(url_for('login'))

        session['admin_access_token'] = resp.get('access_token')
        session['admin_email'] = email
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==========================================
# DASHBOARD
# ==========================================
@app.route('/dashboard')
@admin_required
def dashboard():
    espacios = api_request('/espacios', method='GET')
    equipos = api_request('/equipos', method='GET')
    reservas = api_request('/reservas', method='GET')
    eventos = api_request('/eventos/proximos', method='GET')

    total_espacios = len(espacios) if isinstance(espacios, list) else 0
    total_equipos = len(equipos) if isinstance(equipos, list) else 0
    total_reservas = len(reservas) if isinstance(reservas, list) else 0
    total_eventos = len(eventos) if isinstance(eventos, list) else 0

    # Obtener estadísticas reales
    espacios_top = api_request('/estadisticas/espacios-mas-reservados', method='GET')
    if not isinstance(espacios_top, list): espacios_top = []
    horarios_top = api_request('/estadisticas/horarios-demanda', method='GET')
    if not isinstance(horarios_top, list): horarios_top = []

    return render_template('dashboard.html',
                           espacios=total_espacios,
                           equipos=total_equipos,
                           reservas=total_reservas,
                           eventos=total_eventos,
                           espacios_top=espacios_top,
                           horarios_top=horarios_top)

@app.route('/usuarios/update/<int:id>', methods=['POST'])
@admin_required
def usuarios_update(id):
    data = {
        "nombre_completo": request.form.get("nombre_completo"),
        "carrera": request.form.get("carrera")
    }
    if request.form.get("contrasena"):
        data["contrasena"] = request.form.get("contrasena")
    resp = api_request(f'/estudiantes/{id}', method='PUT', data=data)
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al actualizar usuario: {resp["error"]}', 'danger')
    else:
        flash('Usuario actualizado correctamente.', 'success')
    return redirect(url_for('usuarios'))

@app.route('/usuarios/delete/<int:id>', methods=['POST'])
@admin_required
def usuarios_delete(id):
    resp = api_request(f'/estudiantes/{id}', method='DELETE')
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al eliminar usuario: {resp["error"]}', 'danger')
    else:
        flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('usuarios'))

@app.route('/espacios')
@admin_required
def espacios():
    q = request.args.get('q')
    tipo_espacio = request.args.get('tipo_espacio')

    espacios_data = api_request('/espacios', method='GET')
    if not isinstance(espacios_data, list):
        espacios_data = []

    if tipo_espacio:
        espacios_data = [e for e in espacios_data if str(e.get('tipo_espacio', '')).lower() == str(tipo_espacio).lower()]
    if q:
        ql = q.lower()
        espacios_data = [e for e in espacios_data if ql in str(e.get('nombre', '')).lower() or ql in str(e.get('descripcion', '')).lower()]

    return render_template('espacios.html', espacios=espacios_data)

@app.route('/espacios/create', methods=['POST'])
@admin_required
def espacios_create():
    data = {
        "tipo_espacio": request.form.get("tipo_espacio"),
        "nombre": request.form.get("nombre"),
        "ubicacion": request.form.get("ubicacion"),
        "capacidad": int(request.form.get("capacidad") or 0),
        "horario_apertura": request.form.get("horario_apertura") + ":00" if len(request.form.get("horario_apertura", "")) == 5 else request.form.get("horario_apertura"),
        "horario_cierre": request.form.get("horario_cierre") + ":00" if len(request.form.get("horario_cierre", "")) == 5 else request.form.get("horario_cierre"),
        "disponible": request.form.get("disponible") == 'on'
    }
    resp = api_request('/espacios/', method='POST', json=data)
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al crear espacio: {resp["error"]}', 'danger')
    else:
        flash('Espacio creado correctamente.', 'success')
    return redirect(url_for('espacios'))

@app.route('/espacios/update/<int:id>', methods=['POST'])
@admin_required
def espacios_update(id):
    data = {
        "tipo_espacio": request.form.get("tipo_espacio"),
        "nombre": request.form.get("nombre"),
        "ubicacion": request.form.get("ubicacion"),
        "capacidad": int(request.form.get("capacidad") or 0),
        "horario_apertura": request.form.get("horario_apertura") + ":00" if len(request.form.get("horario_apertura", "")) == 5 else request.form.get("horario_apertura"),
        "horario_cierre": request.form.get("horario_cierre") + ":00" if len(request.form.get("horario_cierre", "")) == 5 else request.form.get("horario_cierre"),
        "disponible": request.form.get("disponible") == 'on'
    }
    resp = api_request(f'/espacios/{id}', method='PUT', json=data)
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al actualizar espacio: {resp["error"]}', 'danger')
    else:
        flash('Espacio actualizado correctamente.', 'success')
    return redirect(url_for('espacios'))

@app.route('/espacios/delete/<int:id>', methods=['POST'])
@admin_required
def espacios_delete(id):
    resp = api_request(f'/espacios/{id}', method='DELETE')
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al eliminar espacio: {resp["error"]}', 'danger')
    else:
        flash('Espacio eliminado correctamente.', 'success')
    return redirect(url_for('espacios'))


# ==========================================
# EQUIPOS
# ==========================================
@app.route('/equipos')
@admin_required
def equipos():
    espacio_id = request.args.get('espacio_id')
    estado = request.args.get('estado')

    if espacio_id and espacio_id.isdigit():
        equipos_data = api_request('/equipos', method='GET', data={'espacio_id': int(espacio_id)})
    else:
        equipos_data = api_request('/equipos', method='GET')

    if not isinstance(equipos_data, list):
        equipos_data = []

    espacios_data = api_request('/espacios', method='GET')
    if not isinstance(espacios_data, list): espacios_data = []

    if estado:
        estl = str(estado).lower()
        equipos_data = [e for e in equipos_data if estl in str(e.get('estado', '')).lower() or estl in str(e.get('estado_operativo', '')).lower()]

    return render_template('equipos.html', equipos=equipos_data, espacios=espacios_data)

@app.route('/equipos/create', methods=['POST'])
@admin_required
def equipos_create():
    id_espacio = request.form.get("id_espacio")
    data = {
        "nombre_equipo": request.form.get("nombre_equipo"),
        "tipo_equipo": request.form.get("tipo_equipo"),
        "estado_operativo": request.form.get("estado_operativo") or 'Operativo'
    }
    resp = api_request(f'/equipos/?id_espacio={id_espacio}', method='POST', data=data)
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al crear equipo: {resp["error"]}', 'danger')
    else:
        flash('Equipo registrado correctamente.', 'success')
    return redirect(url_for('equipos'))

@app.route('/equipos/update/<int:id>', methods=['POST'])
@admin_required
def equipos_update(id):
    data = {
        "nombre_equipo": request.form.get("nombre_equipo"),
        "tipo_equipo": request.form.get("tipo_equipo"),
        "estado_operativo": request.form.get("estado_operativo")
    }
    resp = api_request(f'/equipos/{id}', method='PUT', data=data)
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al actualizar equipo: {resp["error"]}', 'danger')
    else:
        flash('Equipo actualizado correctamente.', 'success')
    return redirect(url_for('equipos'))

@app.route('/equipos/delete/<int:id>', methods=['POST'])
@admin_required
def equipos_delete(id):
    resp = api_request(f'/equipos/{id}', method='DELETE')
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al eliminar equipo: {resp["error"]}', 'danger')
    else:
        flash('Equipo eliminado correctamente.', 'success')
    return redirect(url_for('equipos'))

# ==========================================
# RESERVAS
# ==========================================
@app.route('/reservas')
@admin_required
def reservas():
    reservas_data = api_request('/reservas', method='GET')
    if not isinstance(reservas_data, list):
        reservas_data = []
    espacios_data = api_request('/espacios', method='GET')
    if not isinstance(espacios_data, list):
        espacios_data = []
    clases_data = api_request('/clases', method='GET')
    if not isinstance(clases_data, list):
        clases_data = []
    estudiantes_data = api_request('/estudiantes', method='GET')
    if not isinstance(estudiantes_data, list):
        estudiantes_data = []
    return render_template('reservas.html',
                           reservas=reservas_data,
                           espacios=espacios_data,
                           clases=clases_data,
                           estudiantes=estudiantes_data)

# ==========================================
# EVENTOS
# ==========================================
@app.route('/eventos')
@admin_required
def eventos():
    eventos_data = api_request('/eventos/proximos', method='GET')
    if not isinstance(eventos_data, list):
        eventos_data = []
    return render_template('eventos.html', eventos=eventos_data)

@app.route('/eventos/create', methods=['POST'])
@admin_required
def crear_evento():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    if not nombre:
        flash('El nombre del evento es obligatorio.', 'danger')
        return redirect(url_for('eventos'))

    payload = {
        'nombre': nombre,
        'descripcion': descripcion
    }
    if fecha_inicio:
        payload['fecha_inicio'] = fecha_inicio
    if fecha_fin:
        payload['fecha_fin'] = fecha_fin

    resp = api_request('/eventos', method='POST', json=payload)
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al crear evento: {resp.get("error", "Error desconocido")}', 'danger')
    else:
        flash('Evento creado exitosamente.', 'success')

    return redirect(url_for('eventos'))

@app.route('/eventos/update/<int:id>', methods=['POST'])
@admin_required
def editar_evento(id):
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    payload = {}
    if nombre:
        payload['nombre'] = nombre
    if descripcion is not None:
        payload['descripcion'] = descripcion
    if fecha_inicio:
        payload['fecha_inicio'] = fecha_inicio
    if fecha_fin:
        payload['fecha_fin'] = fecha_fin

    if not payload:
        flash('No se proporcionaron cambios para actualizar.', 'warning')
        return redirect(url_for('eventos'))

    resp = api_request(f'/eventos/{id}', method='PUT', json=payload)
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al actualizar evento: {resp.get("error", "Error desconocido")}', 'danger')
    else:
        flash('Evento actualizado exitosamente.', 'success')

    return redirect(url_for('eventos'))

@app.route('/eventos/delete/<int:id>', methods=['POST'])
@admin_required
def eliminar_evento(id):
    resp = api_request(f'/eventos/{id}', method='DELETE')
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al eliminar evento: {resp.get("error", "Error desconocido")}', 'danger')
    else:
        flash('Evento eliminado correctamente.', 'success')
    return redirect(url_for('eventos'))

# ==========================================
# GESTIÓN DE USUARIOS
# ==========================================
@app.route('/usuarios')
@admin_required
def usuarios():
    token = session.get('admin_access_token')
    print("=== USUARIOS ===")
    print("Token presente:", token[:20] + "..." if token else "NINGUNO")
    resp_est = api_request('/estudiantes', method='GET')
    print("Respuesta /estudiantes:", resp_est)
    resp_adm = api_request('/administradores', method='GET')
    print("Respuesta /administradores:", resp_adm)
    estudiantes_data = api_request('/estudiantes', method='GET')
    if not isinstance(estudiantes_data, list):
        estudiantes_data = []
    administradores_data = api_request('/administradores', method='GET')
    if not isinstance(administradores_data, list):
        administradores_data = []
    return render_template('usuarios.html',
                           estudiantes=estudiantes_data,
                           administradores=administradores_data)

@app.route('/usuarios/crear_admin', methods=['POST'])
@admin_required
def crear_administrador():
    payload = {
        'nombre_completo': request.form.get('nombre_completo'),
        'puesto': request.form.get('puesto', ''),
        'correo': request.form.get('correo'),
        'contrasena': request.form.get('contrasena')
    }
    resp = api_request('/administradores', method='POST', json=payload)
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al crear administrador: {resp.get("error", "Desconocido")}', 'danger')
    else:
        flash('Administrador creado exitosamente', 'success')
    return redirect(url_for('usuarios'))

@app.route('/usuarios/crear_estudiante', methods=['POST'])
@admin_required
def crear_estudiante():
    payload = {
        'nombre_completo': request.form.get('nombre_completo'),
        'matricula': request.form.get('matricula'),
        'correo': request.form.get('correo'),
        'contrasena': request.form.get('contrasena'),
        'carrera': request.form.get('carrera')
    }
    resp = api_request('/estudiantes', method='POST', json=payload)
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al crear estudiante: {resp.get("error", "Desconocido")}', 'danger')
    else:
        flash('Estudiante creado exitosamente', 'success')
    return redirect(url_for('usuarios'))

@app.route('/usuarios/eliminar_estudiante/<int:id>', methods=['POST'])
@admin_required
def eliminar_estudiante(id):
    resp = api_request(f'/estudiantes/{id}', method='DELETE')
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al eliminar estudiante: {resp.get("error", "Desconocido")}', 'danger')
    else:
        flash('Estudiante eliminado exitosamente', 'success')
    return redirect(url_for('usuarios'))

@app.route('/usuarios/eliminar_admin/<int:id>', methods=['POST'])
@admin_required
def eliminar_admin(id):
    resp = api_request(f'/administradores/{id}', method='DELETE')
    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al eliminar administrador: {resp.get("error", "Desconocido")}', 'danger')
    else:
        flash('Administrador eliminado exitosamente', 'success')
    return redirect(url_for('usuarios'))

# ==========================================
# RESERVAS - CREAR CLASE RECURRENTE (16 SEMANAS)
# ==========================================
@app.route('/reservas/nueva_clase', methods=['POST'])
@admin_required
def crear_reserva_clase():
    id_clase = request.form.get('id_clase')
    id_espacio = request.form.get('id_espacio')
    dia_semana = request.form.get('dia_semana')
    hora_inicio = request.form.get('hora_inicio')
    hora_fin = request.form.get('hora_fin')

    if not all([id_clase, id_espacio, dia_semana, hora_inicio, hora_fin]):
        flash('Todos los campos son obligatorios', 'danger')
        return redirect(url_for('reservas'))

    id_clase = int(id_clase)
    id_espacio = int(id_espacio)
    dia_semana = int(dia_semana)

    hoy = date.today()
    dias_hasta = (dia_semana - hoy.weekday()) % 7
    if dias_hasta == 0:
        dias_hasta = 7
    fecha_inicio = hoy + timedelta(days=dias_hasta)

    total_semanas = 16
    exitos = 0
    errores = []

    for semana in range(total_semanas):
        fecha_reserva = fecha_inicio + timedelta(weeks=semana)
        fecha_str = fecha_reserva.isoformat()
        payload = {
            'id_espacio': id_espacio,
            'id_equipo': None,
            'tipo_reserva': 'clase',
            'id_clase_beneficiario': id_clase,
            'fecha_hora_inicio': f"{fecha_str}T{hora_inicio}:00",
            'fecha_hora_fin': f"{fecha_str}T{hora_fin}:00",
            'observaciones': f'Reserva automática semana {semana + 1}/16'
        }
        resp = api_request('/reservas', method='POST', json=payload)
        if isinstance(resp, dict) and 'error' in resp:
            errores.append(f'Semana {semana + 1} ({fecha_str}): {resp.get("error", "Error")}')
        else:
            exitos += 1

    if exitos > 0:
        flash(f'Se crearon {exitos} de {total_semanas} reservas semanales exitosamente.', 'success')
    if errores:
        resumen = '; '.join(errores[:3])
        if len(errores) > 3:
            resumen += f' ... y {len(errores) - 3} más'
        flash(f'Errores en algunas semanas: {resumen}', 'warning')

    return redirect(url_for('reservas'))

# ==========================================
# RESERVAS - CREAR INDIVIDUAL
# ==========================================
@app.route('/reservas/nueva_individual', methods=['POST'])
@admin_required
def crear_reserva_individual():
    id_espacio = request.form.get('id_espacio')
    tipo_beneficiario = request.form.get('tipo_beneficiario')
    id_beneficiario = request.form.get('id_beneficiario')
    fecha = request.form.get('fecha')
    hora_inicio = request.form.get('hora_inicio')
    hora_fin = request.form.get('hora_fin')

    if not all([id_espacio, tipo_beneficiario, id_beneficiario, fecha, hora_inicio, hora_fin]):
        flash('Todos los campos son obligatorios', 'danger')
        return redirect(url_for('reservas'))

    inicio_dt = f"{fecha}T{hora_inicio}:00"
    fin_dt = f"{fecha}T{hora_fin}:00"

    payload = {
        'id_espacio': int(id_espacio),
        'id_equipo': int(request.form.get('id_equipo')) if request.form.get('id_equipo') else None,
        'tipo_reserva': tipo_beneficiario,
        'fecha_hora_inicio': inicio_dt,
        'fecha_hora_fin': fin_dt,
        'observaciones': request.form.get('observaciones', 'Reserva creada por administrador')
    }

    if tipo_beneficiario == 'clase':
        payload['id_clase_beneficiario'] = int(id_beneficiario)
    elif tipo_beneficiario == 'estudiante':
        payload['id_estudiante_beneficiario'] = int(id_beneficiario)
    elif tipo_beneficiario == 'evento':
        payload['id_evento_beneficiario'] = int(id_beneficiario)

    resp = api_request('/reservas', method='POST', json=payload)

    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al crear la reserva: {resp.get("error", "Error desconocido")}', 'danger')
    else:
        flash('Reserva individual creada exitosamente.', 'success')

    return redirect(url_for('reservas'))

# ==========================================
# CANCELAR RESERVA
# ==========================================
@app.route('/reservas/<int:id>/cancelar', methods=['POST'])
@admin_required
def cancelar_reserva(id):
    motivo = request.form.get('motivo', 'Cancelada por administrador')
    resp = api_request(f'/reservas/{id}/cancelar', method='PUT', json={'motivo': motivo})

    if isinstance(resp, dict) and 'error' in resp:
        flash(f'Error al cancelar: {resp.get("error", "Desconocido")}', 'danger')
    else:
        flash('Reserva cancelada exitosamente', 'success')

    return redirect(url_for('reservas'))

# ==========================================
# API PROXY - EQUIPOS POR ESPACIO (usado por JS)
# ==========================================
@app.route('/api/equipos_por_espacio/<int:espacio_id>')
@admin_required
def api_equipos_por_espacio(espacio_id):
    equipos_data = api_request(f'/equipos?espacio_id={espacio_id}', method='GET')
    if not isinstance(equipos_data, list):
        return jsonify([])
    return jsonify(equipos_data)

# ==========================================
# TALLERES Y COCURRICULARES
# ==========================================
@app.route('/talleres')
@admin_required
def talleres():
    clases_data = api_request('/clases', method='GET')
    if not isinstance(clases_data, list):
        clases_data = []
    cocurriculares = [c for c in clases_data if c.get('materia', '').lower().startswith('cocurricular')]

    eventos_data = api_request('/eventos/proximos', method='GET')
    if not isinstance(eventos_data, list):
        eventos_data = []
    talleres_especiales = [e for e in eventos_data if 'taller' in e.get('nombre', '').lower() or 'workshop' in e.get('nombre', '').lower()]
    if not talleres_especiales:
        talleres_especiales = eventos_data

    espacios_data = api_request('/espacios', method='GET')
    if not isinstance(espacios_data, list):
        espacios_data = []

    return render_template('talleres.html',
                           cocurriculares=cocurriculares,
                           talleres_especiales=talleres_especiales,
                           espacios=espacios_data)

@app.route('/talleres/cocurricular', methods=['POST'])
@admin_required
def crear_cocurricular():
    nombre = request.form.get('nombre')
    docente = request.form.get('docente')
    grupo = request.form.get('grupo', 'COCURR')
    id_espacio = request.form.get('id_espacio')
    dia_semana = request.form.get('dia_semana')
    hora_inicio = request.form.get('hora_inicio')
    hora_fin = request.form.get('hora_fin')

    if not all([nombre, docente, id_espacio, dia_semana, hora_inicio, hora_fin]):
        flash('Todos los campos son obligatorios', 'danger')
        return redirect(url_for('talleres'))

    dias_nombre = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    clase_payload = {
        'nombre': nombre,
        'materia': f'Cocurricular: {nombre}',
        'grupo': grupo,
        'docente': docente,
        'correo_docente': '',
        'horario': f'{dias_nombre[int(dia_semana)]} {hora_inicio}-{hora_fin}'
    }
    resp_clase = api_request('/clases', method='POST', json=clase_payload)

    if isinstance(resp_clase, dict) and 'error' in resp_clase:
        flash(f'Error al crear cocurricular: {resp_clase.get("error", "Error")}', 'danger')
        return redirect(url_for('talleres'))

    id_clase = resp_clase.get('id_clase')
    if not id_clase:
        flash('Cocurricular creado, pero no se pudo obtener su ID para generar reservas.', 'warning')
        return redirect(url_for('talleres'))

    id_espacio = int(id_espacio)
    dia_semana = int(dia_semana)
    hoy = date.today()
    dias_hasta = (dia_semana - hoy.weekday()) % 7
    if dias_hasta == 0:
        dias_hasta = 7
    fecha_inicio = hoy + timedelta(days=dias_hasta)

    total_semanas = 16
    exitos = 0
    for semana in range(total_semanas):
        fecha_reserva = fecha_inicio + timedelta(weeks=semana)
        fecha_str = fecha_reserva.isoformat()
        payload = {
            'id_espacio': id_espacio,
            'id_equipo': None,
            'tipo_reserva': 'clase',
            'id_clase_beneficiario': id_clase,
            'fecha_hora_inicio': f"{fecha_str}T{hora_inicio}:00",
            'fecha_hora_fin': f"{fecha_str}T{hora_fin}:00",
            'observaciones': f'Cocurricular: {nombre} - Semana {semana+1}/16'
        }
        resp = api_request('/reservas', method='POST', json=payload)
        if not (isinstance(resp, dict) and 'error' in resp):
            exitos += 1

    flash(f'Cocurricular "{nombre}" creado con {exitos}/{total_semanas} reservas semanales.', 'success')
    return redirect(url_for('talleres'))

@app.route('/talleres/especial', methods=['POST'])
@admin_required
def crear_taller_especial():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion', '')
    id_espacio = request.form.get('id_espacio')
    fecha = request.form.get('fecha')
    hora_inicio = request.form.get('hora_inicio')
    hora_fin = request.form.get('hora_fin')

    if not all([nombre, id_espacio, fecha, hora_inicio, hora_fin]):
        flash('Todos los campos son obligatorios', 'danger')
        return redirect(url_for('talleres'))

    inicio_dt = f"{fecha}T{hora_inicio}:00"
    fin_dt = f"{fecha}T{hora_fin}:00"
    evento_payload = {
        'nombre': f'Taller: {nombre}',
        'descripcion': descripcion,
        'fecha_inicio': inicio_dt,
        'fecha_fin': fin_dt
    }
    resp_evento = api_request('/eventos', method='POST', json=evento_payload)

    if isinstance(resp_evento, dict) and 'error' in resp_evento:
        flash(f'Error al crear taller especial: {resp_evento.get("error", "Error")}', 'danger')
        return redirect(url_for('talleres'))

    id_evento = resp_evento.get('id_evento')
    if not id_evento:
        flash('Taller especial creado como evento, pero no se pudo generar la reserva automática.', 'warning')
        return redirect(url_for('talleres'))

    reserva_payload = {
        'id_espacio': int(id_espacio),
        'id_equipo': None,
        'tipo_reserva': 'evento',
        'id_evento_beneficiario': id_evento,
        'fecha_hora_inicio': inicio_dt,
        'fecha_hora_fin': fin_dt,
        'observaciones': f'Taller especial: {nombre}'
    }
    resp_reserva = api_request('/reservas', method='POST', json=reserva_payload)

    if isinstance(resp_reserva, dict) and 'error' in resp_reserva:
        flash(f'Evento creado pero error en reserva: {resp_reserva.get("error", "")}', 'warning')
    else:
        flash(f'Taller especial "{nombre}" creado con su reserva de espacio.', 'success')

    return redirect(url_for('talleres'))

# ==========================================
# ARRANCAR SERVIDOR
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)