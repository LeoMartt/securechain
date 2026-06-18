import argparse
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

from blockchain.blockchain import adicionar_bloco


BASE_DIR = Path(__file__).resolve().parent
DOCUMENTOS_DIR = BASE_DIR / "documentos"
HASHES_FILE = BASE_DIR / "logs" / "hashes_documentos.json"


def agora():
    return datetime.now().isoformat(timespec="seconds")


def calcular_hash_arquivo(caminho):
    sha256 = hashlib.sha256()

    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(4096), b""):
            sha256.update(bloco)

    return sha256.hexdigest()


def varrer_documentos():
    DOCUMENTOS_DIR.mkdir(parents=True, exist_ok=True)

    hashes = {}

    for caminho in DOCUMENTOS_DIR.rglob("*"):
        if caminho.is_file():
            caminho_relativo = str(caminho.relative_to(DOCUMENTOS_DIR))
            hashes[caminho_relativo] = calcular_hash_arquivo(caminho)

    return hashes


def salvar_hashes(hashes):
    HASHES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(HASHES_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(hashes, arquivo, ensure_ascii=False, indent=4)


def carregar_hashes():
    if not HASHES_FILE.exists() or HASHES_FILE.stat().st_size == 0:
        return {}

    with open(HASHES_FILE, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def inicializar_monitoramento():
    hashes = varrer_documentos()
    salvar_hashes(hashes)

    adicionar_bloco(
        evento="Monitoramento de integridade inicializado",
        dados={
            "total_arquivos": len(hashes),
            "diretorio": str(DOCUMENTOS_DIR)
        }
    )

    print("Hashes iniciais salvos.")
    print(f"Total de arquivos monitorados: {len(hashes)}")


def verificar_integridade():
    hashes_antigos = carregar_hashes()
    hashes_atuais = varrer_documentos()

    arquivos_antigos = set(hashes_antigos.keys())
    arquivos_atuais = set(hashes_atuais.keys())

    incluidos = arquivos_atuais - arquivos_antigos
    excluidos = arquivos_antigos - arquivos_atuais
    possivelmente_alterados = arquivos_atuais & arquivos_antigos

    alterados = {
        arquivo
        for arquivo in possivelmente_alterados
        if hashes_atuais[arquivo] != hashes_antigos[arquivo]
    }

    eventos = []

    for arquivo in sorted(incluidos):
        eventos.append(("Arquivo incluído", arquivo))

    for arquivo in sorted(excluidos):
        eventos.append(("Arquivo excluído", arquivo))

    for arquivo in sorted(alterados):
        eventos.append(("Arquivo alterado", arquivo))

    if not eventos:
        print("Nenhuma alteração detectada.")
    else:
        print("ALERTA: inconsistências detectadas.")

        for tipo_evento, arquivo in eventos:
            print(f"- {tipo_evento}: {arquivo}")

            adicionar_bloco(
                evento=tipo_evento,
                dados={
                    "arquivo": arquivo,
                    "detectado_em": agora()
                }
            )

    salvar_hashes(hashes_atuais)


def monitorar_periodicamente(intervalo):
    print(f"Monitorando documentos a cada {intervalo} segundos.")
    print("Pressione Ctrl + C para parar.")

    try:
        while True:
            verificar_integridade()
            time.sleep(intervalo)
    except KeyboardInterrupt:
        print("\nMonitoramento encerrado.")


def main():
    parser = argparse.ArgumentParser(description="Monitor de integridade SecureChain")
    parser.add_argument(
        "acao",
        choices=["init", "check", "watch"],
        help="init cria hashes iniciais, check verifica uma vez, watch monitora periodicamente"
    )
    parser.add_argument(
        "--intervalo",
        type=int,
        default=10,
        help="Intervalo em segundos para o modo watch"
    )

    args = parser.parse_args()

    if args.acao == "init":
        inicializar_monitoramento()
    elif args.acao == "check":
        verificar_integridade()
    elif args.acao == "watch":
        monitorar_periodicamente(args.intervalo)


if __name__ == "__main__":
    main()
