-- Ejecutar una sola vez en la base PostgreSQL actual desde pgAdmin.
ALTER TABLE instrumento
    ADD COLUMN IF NOT EXISTS imagen_public_id VARCHAR(255);
