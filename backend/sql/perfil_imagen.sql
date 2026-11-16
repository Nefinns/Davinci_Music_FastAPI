-- PostgreSQL: ejecutar una vez en pgAdmin antes de iniciar el backend actualizado.
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS imagen_perfil_public_id VARCHAR(255);
