
from db import conectar, random_id
from datetime import datetime
import bcrypt


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def registrar_usuario(nombre, email, password, rol):
    conn = conectar()
    cursor = conn.cursor()
    usuario_id = random_id("usuarios")
    creado_en = datetime.now().isoformat()
    password_hash = hash_password(password)
    try:
        cursor.execute("""
            INSERT INTO usuarios (id, nombre, email, password_hash, rol, creado_en)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (usuario_id, nombre, email, password_hash, rol, creado_en))
        conn.commit()
        return usuario_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def login_usuario(email, password):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, rol, password_hash FROM usuarios WHERE email = ?
    """, (email,))
    usuario = cursor.fetchone()
    conn.close()
    if usuario and bcrypt.checkpw(password.encode(), usuario[3]):
        return usuario[:3]
    return None
