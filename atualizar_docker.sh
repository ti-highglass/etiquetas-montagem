#!/bin/bash

echo "=========================================="
echo "ATUALIZANDO APLICAÇÃO DOCKER"
echo "=========================================="

# Parar container
echo ""
echo "1. Parando container..."
docker-compose down

# Rebuildar imagem
echo ""
echo "2. Rebuildando imagem (sem cache)..."
docker-compose build --no-cache

# Subir container
echo ""
echo "3. Subindo container..."
docker-compose up -d

# Aguardar inicialização
echo ""
echo "4. Aguardando inicialização..."
sleep 5

# Verificar logs
echo ""
echo "5. Verificando logs..."
docker-compose logs --tail=50

echo ""
echo "=========================================="
echo "✓ ATUALIZAÇÃO CONCLUÍDA"
echo "=========================================="
echo ""
echo "Acesse: https://10.150.16.45:9020"
echo ""
echo "Para ver logs em tempo real:"
echo "  docker-compose logs -f"
