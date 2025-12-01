#!/bin/bash

# Script para iniciar o sistema de etiquetas montagem no Docker

# Configurações do Gunicorn
WORKERS=${GUNICORN_WORKERS:-2}
WORKER_CLASS=${GUNICORN_WORKER_CLASS:-gthread}
THREADS=${GUNICORN_THREADS:-4}
TIMEOUT=${GUNICORN_TIMEOUT:-120}

echo "=========================================="
echo "Sistema de Etiquetas Montagem"
echo "=========================================="
echo "Workers: $WORKERS"
echo "Worker Class: $WORKER_CLASS"
echo "Threads: $THREADS"
echo "Timeout: $TIMEOUT"
echo "Porta: 9020"
echo "=========================================="

# Iniciar aplicação com Gunicorn
exec gunicorn \
    --bind 0.0.0.0:9020 \
    --workers $WORKERS \
    --worker-class $WORKER_CLASS \
    --threads $THREADS \
    --timeout $TIMEOUT \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level info \
    --certfile /app/cert.pem \
    --keyfile /app/key.pem \
    app:app