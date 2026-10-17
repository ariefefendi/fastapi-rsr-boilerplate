#!/bin/sh
set -e

echo "Menunggu database di ${DB_HOST}:${DB_PORT}..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "Database siap."

# Jika nanti memakai Alembic, aktifkan baris ini:
# alembic upgrade head

# Jalankan CMD dari Dockerfile (uvicorn / gunicorn)
exec "$@"
