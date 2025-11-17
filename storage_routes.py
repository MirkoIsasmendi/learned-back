"""
Storage endpoints for Flask app.
Handles file uploads, downloads, and file management for tasks.
"""

from flask import request, jsonify, send_file
from file_storage import (
    create_file_storage_table,
    save_file_for_task,
    get_task_files,
    get_file_path,
    delete_file_from_task
)


def register_storage(app):
    """Register storage endpoints."""
    
    # Initialize storage table on startup
    create_file_storage_table()

    @app.route("/api/trabajos/<trabajo_id>/archivos", methods=["GET"])
    def get_task_files_endpoint(trabajo_id):
        """Get all files for a specific task."""
        files = get_task_files(trabajo_id)
        return jsonify(files), 200

    @app.route("/api/trabajos/<trabajo_id>/archivos", methods=["POST"])
    def upload_task_files(trabajo_id):
        """Upload one or more files and associate with a task."""
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400

        files_list = request.files.getlist('files')
        if not files_list:
            return jsonify({"error": "No files provided"}), 400

        uploaded = []
        errors = []

        for file_obj in files_list:
            result = save_file_for_task(trabajo_id, file_obj)
            if result:
                uploaded.append(result)
            else:
                errors.append(f"Failed to upload {file_obj.filename}")

        response = {
            "status": "ok" if uploaded else "error",
            "uploaded": uploaded,
            "errors": errors if errors else None
        }
        
        status_code = 200 if uploaded else 400
        return jsonify(response), status_code

    @app.route("/api/trabajos/archivos/download/<filename>", methods=["GET"])
    def download_file(filename):
        """Download a file by filename."""
        filepath = get_file_path(filename)
        
        if not filepath:
            return jsonify({"error": "File not found"}), 404

        try:
            return send_file(filepath, as_attachment=True, download_name=filename)
        except Exception as e:
            print(f"Error downloading file {filename}: {e}")
            return jsonify({"error": "Error downloading file"}), 500

    @app.route("/api/trabajos/archivos/<file_id>", methods=["DELETE"])
    def delete_task_file(file_id):
        """Delete a file from a task."""
        if delete_file_from_task(file_id):
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"error": "File not found"}), 404
