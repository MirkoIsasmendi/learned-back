"""
Module to handle file storage operations for tasks.
Manages file uploads, storage links, and downloads.
"""

import os
import tempfile
from datetime import datetime
from db import conectar, random_id

# Directory for persistent file storage
STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(STORAGE_DIR, exist_ok=True)


def create_file_storage_table():
    """Create the trabajos_archivos table if it doesn't exist."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trabajos_archivos (
            id TEXT PRIMARY KEY,
            trabajo_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trabajo_id) REFERENCES trabajos(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_trabajos_archivos_trabajo_id 
        ON trabajos_archivos(trabajo_id)
    """)
    conn.commit()
    conn.close()


def save_file_for_task(trabajo_id, file_obj):
    """
    Save a file and associate it with a task.
    
    Args:
        trabajo_id (str): ID of the task
        file_obj: FileStorage object from request.files
    
    Returns:
        dict: File record with id, filename, and status
    """
    if not file_obj or file_obj.filename == '':
        return None

    try:
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        safe_filename = timestamp + os.path.basename(file_obj.filename)
        filepath = os.path.join(STORAGE_DIR, safe_filename)

        # Save file to disk
        file_obj.save(filepath)

        # Register in database
        file_id = random_id('trabajos_archivos')
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trabajos_archivos (id, trabajo_id, filename, filepath)
            VALUES (?, ?, ?, ?)
        """, (file_id, trabajo_id, safe_filename, filepath))
        conn.commit()
        conn.close()

        return {
            'id': file_id,
            'filename': safe_filename,
            'trabajo_id': trabajo_id,
            'status': 'ok'
        }
    except Exception as e:
        print(f"Error saving file for task {trabajo_id}: {e}")
        return None


def get_task_files(trabajo_id):
    """
    Get all files associated with a task.
    
    Args:
        trabajo_id (str): ID of the task
    
    Returns:
        list: List of file records
    """
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, trabajo_id, uploaded_at
            FROM trabajos_archivos
            WHERE trabajo_id = ?
            ORDER BY uploaded_at DESC
        """, (trabajo_id,))
        rows = cursor.fetchall()
        conn.close()

        files = [
            {
                'id': r[0],
                'filename': r[1],
                'trabajo_id': r[2],
                'uploaded_at': r[3]
            }
            for r in rows
        ]
        return files
    except Exception as e:
        print(f"Error fetching files for task {trabajo_id}: {e}")
        return []


def get_file_path(filename):
    """
    Get the full file path for a given filename.
    
    Args:
        filename (str): Name of the file (as stored in DB)
    
    Returns:
        str: Full path to file or None if not found
    """
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT filepath FROM trabajos_archivos WHERE filename = ?
        """, (filename,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return row[0]
        return None
    except Exception as e:
        print(f"Error getting file path for {filename}: {e}")
        return None


def delete_file_from_task(file_id):
    """
    Delete a file from a task and the file system.
    
    Args:
        file_id (str): ID of the file record
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Get file path before deletion
        cursor.execute("SELECT filepath FROM trabajos_archivos WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        filepath = row[0]
        
        # Delete from database
        cursor.execute("DELETE FROM trabajos_archivos WHERE id = ?", (file_id,))
        conn.commit()
        conn.close()

        # Delete from filesystem
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return True
    except Exception as e:
        print(f"Error deleting file {file_id}: {e}")
        return False
