from db import conectar, random_id
from datetime import datetime
import bcrypt
import os
import jwt
import base64
import secrets
from datetime import timedelta
import smtplib
from email.message import EmailMessage


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
        print("Error al registrar usuario:", e)
        return None  # ← devolvemos None en lugar de lanzar excepción
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

def obtener_usuario_por_id(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, email, rol, creado_en FROM usuarios WHERE id = ?
    """, (usuario_id,))
    usuario = cursor.fetchone()
    conn.close()
    if usuario:
        return {
            "id": usuario[0],
            "nombre": usuario[1],
            "email": usuario[2],
            "rol": usuario[3],
            "creado_en": usuario[4]
        }
    return None


def _enviar_email_smtp(to_email, subject, body):
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    email_from = os.getenv('EMAIL_FROM', smtp_user)

    if not smtp_host or not smtp_user or not smtp_pass:
        print('SMTP no configurado. Mensaje:')
        print(body)
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.send_message(msg)
        return True
    except Exception as e:
        print('Error enviando SMTP:', e)
        return False


def iniciar_registro_con_verificacion(nombre, email, password, rol='estudiante', expires_minutes=15):
    """
    Genera un token JWT temporal que contiene los datos necesarios (incluye password_hash codificado en base64)
    y un código numérico. Envía el código al email. Devuelve el token.
    """
    # generar codigo
    codigo = str(secrets.randbelow(10**6)).zfill(6)

    # crear hash de password y codificarlo para meterlo en el token
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    password_b64 = base64.b64encode(password_hash).decode()

    payload = {
        'nombre': nombre,
        'email': email,
        'password_b64': password_b64,
        'rol': rol,
        'codigo': codigo,
        'exp': datetime.utcnow() + timedelta(minutes=expires_minutes)
    }

    secret = os.getenv('SECRET_KEY')
    token = jwt.encode(payload, secret, algorithm='HS256')

    # enviar email con el codigo
    subject = 'Código de verificación'
    body = f'Hola {nombre},\n\nTu código de verificación es: {codigo}\nEste código expira en {expires_minutes} minutos.\n\nSaludos.'
    _enviar_email_smtp(email, subject, body)

    return token


def confirmar_registro_con_token(token, codigo):
    """
    Verifica el token y el código, crea el usuario y devuelve user_id o None.
    """
    secret = os.getenv('SECRET_KEY')
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
    except Exception as e:
        print('Token inválido o expirado:', e)
        return None

    if payload.get('codigo') != codigo:
        return None

    nombre = payload.get('nombre')
    email = payload.get('email')
    rol = payload.get('rol')
    password_b64 = payload.get('password_b64')
    if not (nombre and email and password_b64):
        return None

    password_hash = base64.b64decode(password_b64)

    # crear usuario usando hash directamente
    conn = conectar()
    cursor = conn.cursor()
    usuario_id = random_id('usuarios')
    creado_en = datetime.now().isoformat()
    try:
        cursor.execute('''
            INSERT INTO usuarios (id, nombre, email, password_hash, rol, creado_en)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (usuario_id, nombre, email, password_hash, rol, creado_en))
        conn.commit()
        return usuario_id
    except Exception as e:
        conn.rollback()
        print('Error al crear usuario desde token:', e)
        return None
    finally:
        conn.close()