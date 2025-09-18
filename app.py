from flask import Flask, request, jsonify
from flask_cors import CORS
from notificaciones import crear_tablas, crear_notificacion, asignar_a_usuario, marcar_vista, listar_por_usuario
from clases import crear_clases, unirse_clase, clases_por_usuario
from db import random_id, conectar
from usuarios import registrar_usuario, login_usuario
from login import comp_login, comp_reg_alum, comp_reg_prof

app = Flask(__name__)
CORS(app)
crear_tablas()

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
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.id, u.nombre, u.estado
        FROM usuarios u
        JOIN clases_usuarios cu ON cu.usuario_id = u.id
        WHERE cu.clase_id = ?
    """, (clase_id,))
    
    usuarios = cursor.fetchall()
    conn.close()

    usuarios_con_foto = []
    for i, u in enumerate(usuarios):
        usuarios_con_foto.append({
            "id": u[0],
            "nombre": u[1],
            "estado": u[2],
            "foto": f"`https://tse1.mm.bing.net/th/id/OIP.mV1jXnbl-N9OGjpKzIVGzwHaHk?pid=Api&P=0&h=180`"
        })

    return jsonify(usuarios_con_foto)


# Registro de profesor con validaciones
@app.route("/api/register/profesor", methods=["POST"])
def register_profesor():
    body = request.json
    required = ["nombre", "email", "password"]
    if not all(k in body for k in required):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    resultado = comp_reg_prof(body["nombre"], body["password"], body["email"])
    if isinstance(resultado, str):
        # Si retorna un string, es un error
        return jsonify({"error": resultado}), 400
    return jsonify({"status": "ok", "usuario_id": resultado, "rol": "profesor"})


# Registro de alumno con validaciones
@app.route("/api/register/alumno", methods=["POST"])
def register_alumno():
    body = request.json
    required = ["nombre", "email", "password"]
    if not all(k in body for k in required):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    resultado = comp_reg_alum(body["nombre"], body["password"], body["email"])
    if isinstance(resultado, str):
        return jsonify({"error": resultado}), 400
    return jsonify({"status": "ok", "usuario_id": resultado, "rol": "estudiante"})


# Login con validaciones
@app.route("/api/login", methods=["POST"])
def login():
    body = request.json
    required = ["email", "password"]
    if not all(k in body for k in required):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    resultado = comp_login(body["password"], body["email"])
    if isinstance(resultado, str):
        return jsonify({"error": resultado}), 400
    if resultado:
        return jsonify({"status": "ok", "usuario": resultado})
    else:
        return jsonify({"error": "Credenciales incorrectas"}), 401

if __name__ == "__main__":
    app.run(debug=True)
