-- Create table to store file associations with tasks
CREATE TABLE IF NOT EXISTS trabajos_archivos (
    id TEXT PRIMARY KEY,
    trabajo_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trabajo_id) REFERENCES trabajos(id) ON DELETE CASCADE
);

-- Create index for faster lookups by task
CREATE INDEX IF NOT EXISTS idx_trabajos_archivos_trabajo_id ON trabajos_archivos(trabajo_id);
