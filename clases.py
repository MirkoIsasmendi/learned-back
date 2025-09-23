from db import conectar, random_id
from datetime import datetime
from usuarios import obtener_usuario_por_id

def crear_clases(nombre, descripcion, profesor_id):
    conn = conectar()
    cursor = conn.cursor()
    clase_id = random_id("clases")
    creada_en = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO clases (id, nombre, descripcion, profesor_id, creado_en)
        VALUES (?, ?, ?, ?, ?)
    """, (clase_id, nombre, descripcion, profesor_id, creada_en))
    conn.commit()
    conn.close()
    unirse_clase(profesor_id, clase_id)
    return clase_id

def unirse_clase(usuario_id, clase_id):
    conn = conectar()
    cursor = conn.cursor()
    participacion_id = random_id("participaciones")
    unido_en = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO participaciones (id, usuario_id, clase_id, unido_en)
        VALUES (?, ?, ?, ?)
    """, (participacion_id, usuario_id, clase_id, unido_en))
    conn.commit()
    conn.close()

def clases_por_usuario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    query = """
        SELECT 
            c.id,
            c.nombre,
            c.descripcion,
            c.profesor_id,
            c.creado_en,
            u.nombre AS profesor_nombre
        FROM clases c
        JOIN participaciones p ON c.id = p.clase_id
        JOIN usuarios u ON c.profesor_id = u.id
        WHERE p.usuario_id = ?
    """
    cursor.execute(query, (usuario_id,))
    clases = cursor.fetchall()
    conn.close()
    return clases
