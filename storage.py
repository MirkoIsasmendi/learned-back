import os
import uuid
from flask import request, jsonify, send_from_directory
from werkzeug.utils import secure_filename


BASE_DIR = os.path.dirname(__file__)
UPLOAD_ROOT = os.path.join(BASE_DIR, "uploads")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def register_storage(app):
    # Ensure base uploads dir exists
    ensure_dir(UPLOAD_ROOT)

    @app.route('/api/trabajos/<trabajo_id>/archivos', methods=['GET'])
    def list_trabajo_files(trabajo_id):
        dir_path = os.path.join(UPLOAD_ROOT, 'trabajos', str(trabajo_id))
        if not os.path.isdir(dir_path):
            return jsonify([])
        files = []
        for fname in os.listdir(dir_path):
            # skip hidden
            if fname.startswith('.'):
                continue
            url = request.host_url.rstrip('/') + f"/api/uploads/trabajos/{trabajo_id}/{fname}"
            files.append({"filename": fname, "url": url})
        return jsonify(files)

    @app.route('/api/trabajos/<trabajo_id>/archivos', methods=['POST'])
    def upload_trabajo_files(trabajo_id):
        # Accept multiple files under key 'files'
        if 'files' not in request.files:
            # if no 'files' key, maybe single file keys: handle all request.files
            if len(request.files) == 0:
                return jsonify({"error": "No files provided"}), 400

        dir_path = os.path.join(UPLOAD_ROOT, 'trabajos', str(trabajo_id))
        ensure_dir(dir_path)

        saved = []
        # support both 'files' array and arbitrary file keys
        file_items = request.files.getlist('files') if 'files' in request.files else list(request.files.values())
        for f in file_items:
            if f and f.filename:
                filename = secure_filename(f.filename)
                unique = f"{uuid.uuid4().hex}_{filename}"
                dest = os.path.join(dir_path, unique)
                f.save(dest)
                url = request.host_url.rstrip('/') + f"/api/uploads/trabajos/{trabajo_id}/{unique}"
                saved.append({"filename": unique, "original_name": filename, "url": url})

        return jsonify({"status": "ok", "files": saved})

    @app.route('/api/uploads/trabajos/<trabajo_id>/<path:filename>')
    def serve_trabajo_file(trabajo_id, filename):
        dir_path = os.path.join(UPLOAD_ROOT, 'trabajos', str(trabajo_id))
        return send_from_directory(dir_path, filename, as_attachment=True)
