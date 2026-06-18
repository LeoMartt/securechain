import subprocess
import sys
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
RELATORIOS_DIR = BASE_DIR / "auditoria" / "relatorios"

sys.path.insert(0, str(BASE_DIR))

from blockchain.blockchain import adicionar_bloco


COMANDOS = {
    "who": ["who"],
    "last": ["last", "-n", "10"],
    "ss -tulpn": ["ss", "-tulpn"],
    "ip a": ["ip", "a"],
}


def agora_nome_arquivo():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def agora_texto():
    return datetime.now().isoformat(timespec="seconds")


def executar_comando(comando):
    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=20
        )

        saida = resultado.stdout.strip()

        if resultado.stderr.strip():
            saida += "\n\n[STDERR]\n" + resultado.stderr.strip()

        return saida if saida else "(sem saída)"

    except Exception as erro:
        return f"Erro ao executar comando: {erro}"


def gerar_relatorio():
    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)

    nome_relatorio = f"auditoria_{agora_nome_arquivo()}.txt"
    caminho_relatorio = RELATORIOS_DIR / nome_relatorio

    conteudo = []
    conteudo.append("RELATÓRIO DE AUDITORIA DO SISTEMA OPERACIONAL")
    conteudo.append(f"Gerado em: {agora_texto()}")
    conteudo.append("=" * 70)

    for titulo, comando in COMANDOS.items():
        conteudo.append(f"\n\n### Comando: {titulo}")
        conteudo.append("-" * 70)
        conteudo.append(executar_comando(comando))

    with open(caminho_relatorio, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(conteudo))

    adicionar_bloco(
        evento="Relatório de auditoria do sistema operacional gerado",
        dados={
            "arquivo": str(caminho_relatorio.relative_to(BASE_DIR))
        }
    )

    print(f"Relatório criado em: {caminho_relatorio}")


if __name__ == "__main__":
    gerar_relatorio()
