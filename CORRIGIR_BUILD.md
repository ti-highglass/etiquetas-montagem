# ✅ CORREÇÃO APLICADA - Build Docker

## O que foi corrigido?

1. ✅ Removido `pywin32` do `requirements.txt` (só funciona no Windows)
2. ✅ Adicionado `gunicorn` para produção
3. ✅ Criado `requirements-windows.txt` separado
4. ✅ Atualizado `start.sh` para usar Gunicorn
5. ✅ Ajustado `app.py` para gerar certificados SSL

## 🚀 Execute AGORA:

```bash
cd /opt/apps/etiquetas-montagem

# Build e iniciar
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## ✅ Resultado Esperado:

```
✔ Container etiquetas-montagem  Started
```

Logs devem mostrar:
```
==========================================
Sistema de Etiquetas Montagem
==========================================
Workers: 2
Worker Class: gthread
Threads: 4
Timeout: 120
Porta: 9020
==========================================
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: https://0.0.0.0:9020
```

## 🔍 Testar:

```bash
# Teste de conexão
curl -k https://10.150.20.123:9020/

# Teste de busca
curl -k -X POST https://10.150.20.123:9020/buscar \
  -H "Content-Type: application/json" \
  -d '{"codigoBarras":"PBS20418"}'
```

## 📋 Arquivos Modificados:

- ✅ `requirements.txt` - Removido pywin32, adicionado gunicorn
- ✅ `requirements-windows.txt` - Criado para Windows
- ✅ `start.sh` - Atualizado para usar Gunicorn
- ✅ `app.py` - Ajustado geração de certificados
- ✅ `INSTALACAO.md` - Guia completo criado

## ⚠️ Importante:

**Linux/Docker**: Use `requirements.txt`
**Windows**: Use `requirements-windows.txt`

---

**Status**: ✅ Pronto para build  
**Tempo estimado**: 2-3 minutos
