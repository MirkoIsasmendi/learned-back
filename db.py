import sqlite3
import os
from datetime import datetime
import secrets

DB_PATH = "./db/app.db"
SCHEMA_PATH = "./db/schema.sql"

def ejecutar_schema(path_sql, db_name=DB_PATH):
    with open(path_sql, "r", encoding="utf-8") as f:
        schema = f.read()
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()

def conectar():
    if not os.path.exists(DB_PATH):
        ejecutar_schema(SCHEMA_PATH)
    return sqlite3.connect(DB_PATH)

def random_id(tabla, campo="id"):
    conn = conectar()
    cursor = conn.cursor()
    while True:
        nuevo_id = secrets.token_hex(10)
        cursor.execute(f"SELECT 1 FROM {tabla} WHERE {campo} = ?", (nuevo_id,))
        if not cursor.fetchone():
            conn.close()
            return nuevo_id
