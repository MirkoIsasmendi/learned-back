from db import conectar, random_id
from datetime import datetime

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS notificaciones (
        id TEXT PRIMARY KEY,
        tipo TEXT NOT NULL CHECK (tipo IN ('tarea', 'invitacion', 'mensaje', 'otro')),
        clase_id TEXT,
        titulo TEXT,
        descripcion TEXT,
        creado_por TEXT,
        creada_en DATETIME,
        FOREIGN KEY (clase_id) REFERENCES clases(id),
        FOREIGN KEY (creado_por) REFERENCES usuarios(id)
    );

    CREATE TABLE IF NOT EXISTS notificaciones_usuarios (
        id TEXT PRIMARY KEY,
        notificacion_id TEXT NOT NULL,
        usuario_id TEXT NOT NULL,
        vista BOOLEAN DEFAULT 0,
        respondida BOOLEAN DEFAULT 0,
        recibida_en DATETIME,
        FOREIGN KEY (notificacion_id) REFERENCES notificaciones(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    """)
    conn.commit()
    conn.close()

def crear_notificacion(id, tipo, clase_id, titulo, descripcion, creado_por):
    conn = conectar()
    cursor = conn.cursor()
    creada_en = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO notificaciones (id, tipo, clase_id, titulo, descripcion, creado_por, creada_en)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (id, tipo, clase_id, titulo, descripcion, creado_por, creada_en))
    conn.commit()
    conn.close()

def asignar_a_usuario(noti_id, usuario_id, asignacion_id):
    conn = conectar()
    cursor = conn.cursor()
    recibida_en = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO notificaciones_usuarios (id, notificacion_id, usuario_id, recibida_en)
        VALUES (?, ?, ?, ?)
    """, (asignacion_id, noti_id, usuario_id, recibida_en))
    conn.commit()
    conn.close()

def marcar_vista(asignacion_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notificaciones_usuarios
        SET vista = 1
        WHERE id = ?
    """, (asignacion_id,))
    conn.commit()
    conn.close()

def listar_por_usuario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nu.id, n.titulo, n.descripcion, nu.vista, nu.respondida, n.tipo, n.creada_en
        FROM notificaciones_usuarios nu
        JOIN notificaciones n ON nu.notificacion_id = n.id
        WHERE nu.usuario_id = ?
        ORDER BY n.creada_en DESC
    """, (usuario_id,))
    resultados = cursor.fetchall()
    conn.close()
    return resultados
