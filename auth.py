import getpass
import hashlib
import json
import secrets
from datetime import datetime
from pathlib import Path

from blockchain.blockchain import adicionar_bloco


BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "usuarios" / "usuarios.json"

PERFIS_VALIDOS = {"admin", "analista", "visitante"}


def agora():
    return datetime.now().isoformat(timespec="seconds")


def carregar_usuarios():
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not USERS_FILE.exists() or USERS_FILE.stat().st_size == 0:
        return {}

    with open(USERS_FILE, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_usuarios(usuarios):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(USERS_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, ensure_ascii=False, indent=4)


def gerar_salt():
    return secrets.token_hex(16)


def gerar_hash_senha(senha, salt):
    conteudo = f"{salt}:{senha}"
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()


def cadastrar_usuario():
    usuarios = carregar_usuarios()

    nome = input("Nome do usuário: ").strip()
    perfil = input("Perfil [admin/analista/visitante]: ").strip().lower()

    if not nome:
        print("Nome de usuário inválido.")
        return

    if perfil not in PERFIS_VALIDOS:
        print("Perfil inválido.")
        return

    if nome in usuarios:
        print("Usuário já existe.")
        return

    senha = getpass.getpass("Senha: ")
    confirmar = getpass.getpass("Confirmar senha: ")

    if senha != confirmar:
        print("As senhas não conferem.")
        return

    if len(senha) < 6:
        print("A senha deve ter pelo menos 6 caracteres.")
        return

    salt = gerar_salt()
    senha_hash = gerar_hash_senha(senha, salt)

    usuarios[nome] = {
        "perfil": perfil,
        "salt": salt,
        "senha_hash": senha_hash,
        "criado_em": agora()
    }

    salvar_usuarios(usuarios)

    adicionar_bloco(
        evento="Usuário cadastrado no sistema Python",
        dados={
            "usuario": nome,
            "perfil": perfil
        }
    )

    print("Usuário cadastrado com sucesso.")


def login():
    usuarios = carregar_usuarios()

    nome = input("Usuário: ").strip()
    senha = getpass.getpass("Senha: ")

    if nome not in usuarios:
        adicionar_bloco(
            evento="Tentativa de login negada",
            dados={
                "usuario": nome,
                "motivo": "usuario inexistente"
            }
        )
        print("Acesso negado.")
        return None

    usuario = usuarios[nome]
    senha_hash = gerar_hash_senha(senha, usuario["salt"])

    if senha_hash != usuario["senha_hash"]:
        adicionar_bloco(
            evento="Tentativa de login negada",
            dados={
                "usuario": nome,
                "motivo": "senha incorreta"
            }
        )
        print("Acesso negado.")
        return None

    sessao = {
        "usuario": nome,
        "perfil": usuario["perfil"],
        "login_em": agora()
    }

    adicionar_bloco(
        evento="Login realizado com sucesso",
        dados={
            "usuario": nome,
            "perfil": usuario["perfil"]
        }
    )

    print("Login realizado com sucesso.")
    print(f"Usuário ativo: {sessao['usuario']}")
    print(f"Perfil ativo: {sessao['perfil']}")

    return sessao


def listar_usuarios():
    usuarios = carregar_usuarios()

    if not usuarios:
        print("Nenhum usuário cadastrado.")
        return

    print("Usuários cadastrados:")

    for nome, dados in usuarios.items():
        print(f"- {nome} | perfil: {dados['perfil']} | criado em: {dados['criado_em']}")


def menu():
    while True:
        print("\n=== SecureChain Auth ===")
        print("1 - Cadastrar usuário")
        print("2 - Login")
        print("3 - Listar usuários")
        print("0 - Sair")

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            cadastrar_usuario()
        elif opcao == "2":
            login()
        elif opcao == "3":
            listar_usuarios()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
