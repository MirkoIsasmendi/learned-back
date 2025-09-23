import bcrypt
import re
from usuarios import login_usuario, registrar_usuario

def comp_login(password, mail):
    resultado_pass = validar_password(password)
    if not resultado_pass[0]:
        return resultado_pass[1]

    resultado_mail = validar_email(mail)
    if not resultado_mail[0]:
        return resultado_mail[1]

    usuario = login_usuario(mail, password)
    if usuario:
        return {"id": usuario[0], "nombre": usuario[1], "rol": usuario[2]}
    return None

def comp_reg_alum(nombre, password, mail):
    resultado_nombre = validar_nombre(nombre)
    if not resultado_nombre[0]:
        return resultado_nombre[1]

    resultado_pass = validar_password(password)
    if not resultado_pass[0]:
        return resultado_pass[1]

    resultado_mail = validar_email(mail)
    if not resultado_mail[0]:
        return resultado_mail[1]

    return registrar_usuario(nombre.strip(), mail.strip(), password, "estudiante")

def comp_reg_prof(nombre, password, mail):
    resultado_nombre = validar_nombre(nombre)
    if not resultado_nombre[0]:
        return resultado_nombre[1]

    resultado_pass = validar_password(password)
    if not resultado_pass[0]:
        return resultado_pass[1]

    resultado_mail = validar_email(mail)
    if not resultado_mail[0]:
        return resultado_mail[1]

    return registrar_usuario(nombre.strip(), mail.strip(), password, "profesor")

def validar_password(password):
    if not password or len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."

    if not re.search(r"[A-Z]", password):
        return False, "Debe contener al menos una letra mayúscula."

    if not re.search(r"[a-z]", password):
        return False, "Debe contener al menos una letra minúscula."

    if not re.search(r"\d", password):
        return False, "Debe contener al menos un número."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Debe contener al menos un carácter especial."

    return True, "Contraseña válida."

def validar_nombre(nombre):
    if not nombre or nombre.strip() == "":
        return False, "El nombre no puede estar vacío."

    if len(nombre.strip()) < 2:
        return False, "El nombre debe tener al menos 2 caracteres."

    if len(nombre.strip()) > 50:
        return False, "El nombre no puede tener más de 50 caracteres."

    if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", nombre.strip()):
        return False, "El nombre solo puede contener letras y espacios."

    return True, "Nombre válido."

def validar_email(email):
    if not email or email.strip() == "":
        return False, "El email no puede estar vacío."

    if len(email.strip()) > 254:
        return False, "El email no puede tener más de 254 caracteres."

    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(regex, email.strip()):
        return False, "El formato del email no es válido."

    return True, "Email válido."
