import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CHAIN_FILE = BASE_DIR / "chain.json"


def agora_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def calcular_hash_bloco(bloco):
    bloco_sem_hash = {
        chave: bloco[chave]
        for chave in sorted(bloco.keys())
        if chave != "hash_atual"
    }

    bloco_json = json.dumps(
        bloco_sem_hash,
        ensure_ascii=False,
        sort_keys=True
    )

    return hashlib.sha256(bloco_json.encode("utf-8")).hexdigest()


def criar_bloco(id_bloco, evento, hash_anterior, dados=None):
    bloco = {
        "id": id_bloco,
        "timestamp": agora_iso(),
        "evento": evento,
        "dados": dados or {},
        "hash_anterior": hash_anterior,
    }

    bloco["hash_atual"] = calcular_hash_bloco(bloco)
    return bloco


def criar_bloco_genesis():
    return criar_bloco(
        id_bloco=0,
        evento="Bloco genesis da blockchain de auditoria",
        hash_anterior="0" * 64,
        dados={"sistema": "SecureChain Audit"}
    )


def salvar_cadeia(cadeia):
    CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(CHAIN_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(cadeia, arquivo, ensure_ascii=False, indent=4)


def carregar_cadeia():
    if not CHAIN_FILE.exists() or CHAIN_FILE.stat().st_size == 0:
        cadeia = [criar_bloco_genesis()]
        salvar_cadeia(cadeia)
        return cadeia

    try:
        with open(CHAIN_FILE, "r", encoding="utf-8") as arquivo:
            cadeia = json.load(arquivo)

        if not isinstance(cadeia, list) or len(cadeia) == 0:
            raise ValueError("chain.json vazio ou inválido")

        return cadeia

    except Exception:
        cadeia = [criar_bloco_genesis()]
        salvar_cadeia(cadeia)
        return cadeia


def adicionar_bloco(evento, dados=None):
    cadeia = carregar_cadeia()

    bloco_anterior = cadeia[-1]
    novo_bloco = criar_bloco(
        id_bloco=len(cadeia),
        evento=evento,
        hash_anterior=bloco_anterior["hash_atual"],
        dados=dados or {}
    )

    cadeia.append(novo_bloco)
    salvar_cadeia(cadeia)

    return novo_bloco


def validar_cadeia():
    cadeia = carregar_cadeia()
    erros = []

    for indice, bloco in enumerate(cadeia):
        hash_recalculado = calcular_hash_bloco(bloco)

        if hash_recalculado != bloco.get("hash_atual"):
            erros.append(
                f"Bloco {bloco.get('id')} adulterado: hash armazenado diferente do hash recalculado."
            )

        if indice == 0:
            if bloco.get("hash_anterior") != "0" * 64:
                erros.append("Bloco genesis possui hash_anterior inválido.")
        else:
            bloco_anterior = cadeia[indice - 1]

            if bloco.get("hash_anterior") != bloco_anterior.get("hash_atual"):
                erros.append(
                    f"Quebra de encadeamento no bloco {bloco.get('id')}: "
                    f"hash_anterior não corresponde ao hash_atual do bloco anterior."
                )

        if bloco.get("id") != indice:
            erros.append(
                f"ID inconsistente no índice {indice}: encontrado id={bloco.get('id')}."
            )

    return len(erros) == 0, erros


def listar_blocos():
    cadeia = carregar_cadeia()

    for bloco in cadeia:
        print("-" * 60)
        print(f"ID: {bloco['id']}")
        print(f"Timestamp: {bloco['timestamp']}")
        print(f"Evento: {bloco['evento']}")
        print(f"Hash anterior: {bloco['hash_anterior']}")
        print(f"Hash atual: {bloco['hash_atual']}")


def main():
    parser = argparse.ArgumentParser(description="Blockchain de auditoria SecureChain")
    subparsers = parser.add_subparsers(dest="comando")

    parser_add = subparsers.add_parser("add", help="Adiciona evento na blockchain")
    parser_add.add_argument("evento", help="Descrição do evento")

    subparsers.add_parser("validate", help="Valida a integridade da blockchain")
    subparsers.add_parser("list", help="Lista os blocos da blockchain")

    args = parser.parse_args()

    if args.comando == "add":
        bloco = adicionar_bloco(args.evento)
        print(f"Bloco criado com sucesso. ID: {bloco['id']}")

    elif args.comando == "validate":
        valida, erros = validar_cadeia()

        if valida:
            print("Blockchain válida. Nenhuma adulteração encontrada.")
        else:
            print("ALERTA: blockchain inválida.")
            for erro in erros:
                print(f"- {erro}")

    elif args.comando == "list":
        listar_blocos()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
