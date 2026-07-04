import hashlib
from app.data.database import SessionLocal
from app.models.SAGE_BD import Administrador, EstatusTinyInt

# Inicializamos la sesión de la base de datos
db = SessionLocal()

try:
    # 1. Definimos los datos del administrador
    correo_admin = "admin.sage@upq.edu.mx"
    contrasena_plana = "1234"
    
    # 2. Encriptamos la contraseña usando la librería nativa de Python (cero instalaciones)
    contrasena_encriptada = hashlib.sha256(contrasena_plana.encode('utf-8')).hexdigest()
    
    # 3. Verificamos si ya existe
    admin_existente = db.query(Administrador).filter(Administrador.correo == correo_admin).first()

    if admin_existente:
        # Si existe, ACTUALIZAMOS su contraseña por la nueva versión encriptada
        admin_existente.contrasena = contrasena_encriptada
        db.commit()
        print(f"🔄 ¡Actualizado! El administrador '{correo_admin}' ya existía. Se actualizó su contraseña con encriptación nativa.")
    else:
        # Si no existe, creamos el nuevo registro
        nuevo_admin = Administrador(
            nombre_completo="Administrador General SAGE",
            puesto="Coordinador de Laboratorios",
            correo=correo_admin,
            contrasena=contrasena_encriptada,
            estatus=EstatusTinyInt.ACTIVO
        )
        
        # Guardamos en la base de datos
        db.add(nuevo_admin)
        db.commit()
        
        print(f"✅ ¡Éxito! Administrador registrado correctamente con la contraseña encriptada.")

except Exception as e:
    db.rollback() # Si hay un error, deshacemos los cambios para proteger la BD
    print(f"❌ Error crítico al registrar el administrador: {e}")
finally:
    db.close() # Siempre cerramos la conexión