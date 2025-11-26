#!/bin/bash

# Script para iniciar o sistema de inspeção final no Docker

# Função para cleanup
cleanup() {
    echo "Parando serviços..."
    kill $APP_PID 2>/dev/null
    exit 0
}

# Capturar sinais para cleanup
trap cleanup SIGTERM SIGINT

echo "Iniciando Sistema de Inspeção Final na porta 9020..."
python app.py &
APP_PID=$!

echo "Sistema iniciado com PID: $APP_PID"
echo "Acesse: http://localhost:9020"

# Aguardar o processo
wait $APP_PID