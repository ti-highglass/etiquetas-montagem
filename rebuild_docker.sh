#!/bin/bash
echo "=========================================="
echo "RECONSTRUINDO IMAGEM DOCKER"
echo "=========================================="
echo ""
echo "Parando containers..."
docker-compose down

echo ""
echo "Reconstruindo imagem..."
docker-compose build --no-cache

echo ""
echo "Iniciando containers..."
docker-compose up -d

echo ""
echo "Verificando logs..."
docker-compose logs -f
