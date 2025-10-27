from flask import Flask, request, jsonify
from flask_cors import CORS
from notificaciones import crear_tablas, crear_notificacion, asignar_a_usuario, marcar_vista, listar_por_usuario
from clases import crear_clases, eliminar_clase, dejar_clase, unirse_clase, clases_por_usuario
from db import random_id, conectar
from usuarios import obtener_usuario_por_id
from login import comp_login, comp_reg_alum, comp_reg_prof
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
import traceback
import jwt
from flask_socketio import SocketIO
from call_signaling import register_signaling
from storage import register_storage

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "A99GJFJKSLKJi129873@#$$%&&/()=?¿")

app = Flask(__name__)
CORS(app)
crear_tablas()

# Socket.IO (Flask integration)
socketio = SocketIO(app, cors_allowed_origins='*')

# Registrar los manejadores de señalización de llamadas
register_signaling(socketio)

# Registrar endpoints de storage (subida/descarga)
register_storage(app)

@app.route("/api/notificaciones/<usuario_id>", methods=["GET"])
def obtener_notificaciones(usuario_id):
    data = listar_por_usuario(usuario_id)
    notis = [
        {
            "asignacion_id": r[0],
            "titulo": r[1],
            "descripcion": r[2],
            "vista": bool(r[3]),
            "respondida": bool(r[4]),
            "tipo": r[5],
            "creada_en": r[6]
        }
        for r in data
    ]
    return jsonify(notis)

@app.route("/api/notificaciones", methods=["POST"])
def nueva_notificacion():
    body = request.json
    noti_id = random_id("notificaciones")
    crear_notificacion(
        id=noti_id,
        tipo=body["tipo"],
        clase_id=body.get("clase_id"),
        titulo=body["titulo"],
        descripcion=body["descripcion"],
        creado_por=body["creado_por"]
    )
    return jsonify({"status": "ok", "id": noti_id})

@app.route("/api/notificaciones/asignar", methods=["POST"])
def asignar():
    body = request.json
    asignacion_id = random_id("notificaciones_usuarios")
    asignar_a_usuario(
        noti_id=body["notificacion_id"],
        usuario_id=body["usuario_id"],
        asignacion_id=asignacion_id
    )
    return jsonify({"status": "ok", "asignacion_id": asignacion_id})

@app.route("/api/notificaciones/vista/<asignacion_id>", methods=["POST"])
def marcar_como_vista(asignacion_id):
    marcar_vista(asignacion_id)
    return jsonify({"status": "ok", "vista": True})

@app.route("/api/notificaciones/crear", methods=["POST"])
def crear_y_asignar():
    body = request.json

    if not all(k in body for k in ["tipo", "titulo", "descripcion", "creado_por", "usuarios"]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    noti_id = random_id("notificaciones")
    crear_notificacion(
        id=noti_id,
        tipo=body["tipo"],
        clase_id=body.get("clase_id"),
        titulo=body["titulo"],
        descripcion=body["descripcion"],
        creado_por=body["creado_por"]
    )

    asignaciones = []
    for usuario_id in body["usuarios"]:
        asignacion_id = random_id("notificaciones_usuarios")
        asignar_a_usuario(noti_id, usuario_id, asignacion_id)
        asignaciones.append({"usuario_id": usuario_id, "asignacion_id": asignacion_id})

    return jsonify({
        "status": "ok",
        "notificacion_id": noti_id,
        "asignaciones": asignaciones
    })

@app.route("/api/clases", methods=["POST"])
def nueva_clase():
    body = request.json

    if not all(k in body for k in ["nombre", "descripcion", "profesor_id"]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    clase_id = crear_clases(
        nombre=body["nombre"],
        descripcion=body["descripcion"],
        profesor_id=body["profesor_id"]
    )

    return jsonify({"status": "ok", "clase_id": clase_id})

@app.route("/api/clases/unirse", methods=["POST"])
def unirse():
    body = request.json

    if not all(k in body for k in ["usuario_id", "clase_id"]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    unirse_clase(body["usuario_id"], body["clase_id"])
    return jsonify({"status": "ok", "mensaje": "Usuario unido a la clase"})

@app.route("/api/clases/abandonar", methods=["POST"])
def abandonar_clase():
    body = request.json
    if not all(k in body for k in ["usuario_id", "clase_id"]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    dejar_clase(body["usuario_id"], body["clase_id"])
    return jsonify({"status": "ok", "mensaje": "Usuario ha abandonado la clase"})

@app.route("/api/clases/eliminar", methods=["POST"])
def eliminar_clase_api():
    body = request.json
    if not body or "clase_id" not in body:
        return jsonify({"error": "Falta el campo clase_id"}), 400

    eliminar_clase(body["clase_id"])
    return jsonify({"status": "ok", "mensaje": "Clase eliminada correctamente"})

@app.route("/api/clases/<usuario_id>", methods=["GET"])
def obtener_clases(usuario_id):
    data = clases_por_usuario(usuario_id)
    clases = [
        {
            "id": r[0],
            "nombre": r[1],
            "descripcion": r[2],
            "profesor_id": r[3],
            "creado_en": r[4],
            "profesor_nombre": r[5]
        }
        for r in data
    ]
    return jsonify(clases)

@app.route("/api/clase/<clase_id>", methods=["GET"])
def obtener_clase_por_id(clase_id):
    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT 
            id,
            nombre,
            descripcion,
            profesor_id,
            creado_en
        FROM clases
        WHERE id = ?
    """
    cursor.execute(query, (clase_id,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        clase = {
            "id": resultado[0],
            "nombre": resultado[1],
            "descripcion": resultado[2],
            "profesor_id": resultado[3],
            "creado_en": resultado[4]
        }
        return jsonify(clase)
    else:
        return jsonify({"error": "Clase no encontrada"}), 404

@app.route("/api/trabajos/<clase_id>/<alumno_id>", methods=["GET"])
def obtener_trabajos_por_clase(clase_id, alumno_id):
    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT 
            t.id,
            t.titulo,
            t.descripcion,
            ta.estado
        FROM trabajos t
        LEFT JOIN trabajos_alumnos ta ON t.id = ta.trabajo_id AND ta.alumno_id = ?
        WHERE t.clase_id = ?
        ORDER BY t.titulo
    """
    cursor.execute(query, (alumno_id, clase_id))
    resultados = cursor.fetchall()
    conn.close()

    tareas = {
        "sin_hacer": [],
        "en_proceso": [],
        "realizado": []
    }

    for r in resultados:
        tarea = {
            "id": r[0],
            "titulo": r[1],
            "descripcion": r[2]
        }
        estado = r[3] or "sin_hacer"
        tareas[estado].append(tarea)

    return jsonify(tareas)

@app.route("/api/trabajos/<clase_id>", methods=["POST"])
def crear_trabajo(clase_id):
    body = request.json
    required = ["titulo", "descripcion"]

    if not all(k in body for k in required):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    trabajo_id = random_id("trabajos")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trabajos (id, titulo, descripcion, clase_id)
        VALUES (?, ?, ?, ?)
    """, (trabajo_id, body["titulo"], body["descripcion"], clase_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok", "trabajo_id": trabajo_id})

@app.route("/api/clases/<clase_id>/usuarios")
def obtener_usuarios_de_clase(clase_id):
    try:
        print("DEBUG: obtener_usuarios_de_clase llamado con clase_id:", clase_id)
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.id, u.nombre
            FROM usuarios u
            JOIN participaciones p ON p.usuario_id = u.id
            WHERE p.clase_id = ?
        """, (clase_id,))
        
        filas = cursor.fetchall()
        conn.close()

        usuarios_con_foto = []
        for i, u in enumerate(filas):
            usuarios_con_foto.append({
                "id": u[0],
                "nombre": u[1],
                "estado": "desconectado",   # valor por defecto; adaptá si querés otro comportamiento
                "foto": "https://static.vecteezy.com/system/resources/previews/036/594/092/non_2x/man-empty-avatar-photo-placeholder-for-social-networks-resumes-forums-and-dating-sites-male-and-female-no-photo-images-for-unfilled-user-profile-free-vector.jpg"
            })

        print("DEBUG: usuarios encontrados:", len(usuarios_con_foto))
        return jsonify(usuarios_con_foto)
    except Exception as e:
        print("Error en obtener_usuarios_de_clase:", e)
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor", "detail": str(e)}), 500

# Registro de profesor con validaciones
@app.route("/api/register/profesor", methods=["POST"])
def register_profesor():
    body = request.json
    required = ["nombre", "email", "password"]
    if not all(k in body for k in required):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    # iniciamos el flujo de verificación que envía un código al email
    from usuarios import iniciar_registro_con_verificacion
    token = iniciar_registro_con_verificacion(body["nombre"], body["email"], body["password"], rol="profesor")
    if not token:
        return jsonify({"error": "No se pudo iniciar la verificación"}), 500
    return jsonify({"status": "ok", "token": token}), 200


# Registro de alumno con validaciones
@app.route("/api/register/alumno", methods=["POST"])
def register_alumno():
    body = request.json
    required = ["nombre", "email", "password"]
    if not all(k in body for k in required):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    from usuarios import iniciar_registro_con_verificacion
    token = iniciar_registro_con_verificacion(body["nombre"], body["email"], body["password"], rol="estudiante")
    if not token:
        return jsonify({"error": "No se pudo iniciar la verificación"}), 500
    return jsonify({"status": "ok", "token": token}), 200


@app.route('/api/register/confirm', methods=['POST'])
def register_confirm():
    body = request.json or {}
    if not all(k in body for k in ('token', 'codigo')):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    from usuarios import confirmar_registro_con_token
    usuario_id = confirmar_registro_con_token(body['token'], body['codigo'])
    if not usuario_id:
        return jsonify({'error': 'Token inválido o código incorrecto/expirado'}), 400
    return jsonify({'status': 'ok', 'usuario_id': usuario_id}), 200

# Login con validaciones
@app.route("/api/login", methods=["POST"])
def login():
    body = request.json
    required = ["email", "password"]
    if not all(k in body for k in required):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    usuario = comp_login(body["password"], body["email"])
    if isinstance(usuario, str):  
        # Error de validación
        return jsonify({"error": usuario}), 400
    if not usuario:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    token = jwt.encode({
        "usuario_id": usuario["id"],
        "rol": usuario["rol"],
        "nombre": usuario["nombre"],  # ← Agregado aquí
        "exp": datetime.now(timezone.utc) + timedelta(hours=36000)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "status": "ok",
        "usuario": usuario,
        "token": token
    })


@app.route("/api/usuarios/<usuario_id>", methods=["GET"])
def obtener_usuario(usuario_id):
    usuario = obtener_usuario_por_id(usuario_id)
    if usuario:
        return jsonify({"status": "ok", "usuario": usuario})
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
@app.route("/api/usuarios/email/<email>", methods=["GET"])
def obtener_usuario_por_email(email):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email, rol FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    conn.close()
    if usuario:
        return jsonify({"usuario": {
            "id": usuario[0],
            "nombre": usuario[1],
            "email": usuario[2],
            "rol": usuario[3]
        }})
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404

@app.route("/api/notificaciones/respond/<asignacion_id>", methods=["POST"])
def responder_notificacion(asignacion_id):
    """
    Acciones:
      - aceptar: une al usuario a la clase asociada y elimina la asignación (la notificación desaparece)
      - rechazar: elimina la asignación (la notificación desaparece)
    Body: { "action": "aceptar" | "rechazar" }
    """
    body = request.json or {}
    action = body.get("action")
    if action not in ("aceptar", "rechazar"):
        return jsonify({"error": "Acción no válida"}), 400

    try:
        conn = conectar()
        cursor = conn.cursor()

        # Obtener la asignación: id (asignacion) -> notificacion_id, usuario_id
        cursor.execute("SELECT notificacion_id, usuario_id FROM notificaciones_usuarios WHERE id = ?", (asignacion_id,))
        asign = cursor.fetchone()
        if not asign:
            conn.close()
            return jsonify({"error": "Asignación no encontrada"}), 404

        noti_id, usuario_id = asign[0], asign[1]

        if action == "aceptar":
            # obtener clase asociada a la notificación
            cursor.execute("SELECT clase_id FROM notificaciones WHERE id = ?", (noti_id,))
            fila = cursor.fetchone()
            if fila and fila[0]:
                clase_id = fila[0]
                try:
                    # unirse_clase debe crear la relación en clases_usuarios
                    unirse_clase(usuario_id, clase_id)
                except Exception as e:
                    # ignorar si ya estaba unido o similar, solo loguear
                    print("Warning al unir usuario a clase:", e)

        # En ambos casos (aceptar o rechazar) eliminamos la asignación para que no aparezca más
        cursor.execute("DELETE FROM notificaciones_usuarios WHERE id = ?", (asignacion_id,))
        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error en responder_notificacion:", e)
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/notificaciones/asignacion/<asignacion_id>", methods=["DELETE"])
def eliminar_asignacion(asignacion_id):
    """
    Elimina una asignación de notificación (borrar notificación para el usuario).
    Usado para cerrar notificaciones normales o rechazar invitaciones (si se prefiere llamada directa).
    """
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM notificaciones_usuarios WHERE id = ?", (asignacion_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Error al eliminar asignacion:", e)
        return jsonify({"error": "Error interno del servidor"}), 500

@socketio.on('connect')
def handle_connect():
    print('🔌 Cliente conectado')


@socketio.on('chat_message')
def handle_chat_message(data):
    print(f'Mensaje recibido: {data}')
    # Reenviamos el mensaje a todos los clientes conectados
    # flask-socketio.server.emit no acepta broadcast kwarg en algunas versiones;
    # llamar emit(event, data) enviará a todos en namespace global.
    socketio.emit('chat_message', data)


@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Cliente desconectado')


if __name__ == '__main__':
    # usamos eventlet/uWSGI/gunicorn en producción; para desarrollo socketio.run funciona bien
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)