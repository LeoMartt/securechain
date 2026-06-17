#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCUMENTOS_DIR="$BASE_DIR/documentos"
BACKUP_DIR="$BASE_DIR/backup/backups"
LOG_FILE="$BASE_DIR/logs/backup.log"

mkdir -p "$DOCUMENTOS_DIR"
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
ARQUIVO_COMPACTADO="$BACKUP_DIR/documentos_$TIMESTAMP.tar.gz"
ARQUIVO_CRIPTOGRAFADO="$ARQUIVO_COMPACTADO.enc"

echo "Iniciando backup seguro..."
echo "Diretório de origem: $DOCUMENTOS_DIR"

tar -czf "$ARQUIVO_COMPACTADO" -C "$BASE_DIR" documentos

read -rsp "Digite a senha para criptografar o backup: " BACKUP_PASS
echo ""

openssl enc -aes-256-cbc \
    -salt \
    -pbkdf2 \
    -iter 100000 \
    -in "$ARQUIVO_COMPACTADO" \
    -out "$ARQUIVO_CRIPTOGRAFADO" \
    -pass "pass:$BACKUP_PASS"

rm -f "$ARQUIVO_COMPACTADO"

TAMANHO="$(stat -c%s "$ARQUIVO_CRIPTOGRAFADO")"
STATUS="OK"

echo "$(date +'%Y-%m-%d %H:%M:%S') | arquivo=$(basename "$ARQUIVO_CRIPTOGRAFADO") | tamanho=${TAMANHO} bytes | status=$STATUS" >> "$LOG_FILE"

python3 - "$BASE_DIR" "$ARQUIVO_CRIPTOGRAFADO" "$TAMANHO" <<'PY'
import os
import sys
from pathlib import Path

base_dir = Path(sys.argv[1])
arquivo = Path(sys.argv[2])
tamanho = int(sys.argv[3])

sys.path.insert(0, str(base_dir))

from blockchain.blockchain import adicionar_bloco

adicionar_bloco(
    evento="Backup seguro executado",
    dados={
        "arquivo": str(arquivo.relative_to(base_dir)),
        "tamanho_bytes": tamanho,
        "criptografia": "AES-256-CBC com PBKDF2",
        "status": "OK"
    }
)
PY

echo "Backup criptografado criado com sucesso:"
echo "$ARQUIVO_CRIPTOGRAFADO"
