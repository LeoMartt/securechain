# SecureChain Audit

Plataforma de auditoria baseada em blockchain desenvolvida para a disciplina **Segurança de Sistemas com Blockchain, Criptografia e Auditoria de Eventos**.

O projeto foi implementado em uma Máquina Virtual Debian, utilizando **Python 3**, **Bash Script**, **Git** e **GitHub**.

## Objetivo do Projeto

O SecureChain Audit tem como objetivo criar uma solução integrada de segurança e auditoria capaz de:

* Gerenciar usuários com controle de acesso;
* Separar permissões por função;
* Registrar eventos de segurança em uma blockchain;
* Monitorar a integridade de arquivos por hash SHA-256;
* Detectar inclusão, alteração e exclusão de documentos;
* Gerar relatórios de auditoria do sistema operacional;
* Executar backup compactado e criptografado;
* Validar a integridade da blockchain;
* Aplicar conceitos de Zero Trust, menor privilégio e trilha de auditoria imutável.

## Tecnologias Utilizadas

* Sistema Operacional: Debian em Máquina Virtual
* Linguagem principal: Python 3
* Scripts de automação: Bash Script
* Versionamento: Git + GitHub
* Criptografia e hashing:

  * SHA-256 para hashes de arquivos;
  * SHA-256 com salt para senhas;
  * SHA-256 para hashes dos blocos da blockchain;
  * AES-256-CBC com PBKDF2 via OpenSSL para backup criptografado.

## Estrutura do Projeto

```text
securechain/
├── blockchain/
│   ├── __init__.py
│   ├── blockchain.py
│   └── chain.json
├── auditoria/
│   ├── auditor.py
│   └── relatorios/
├── backup/
│   └── backup.sh
├── logs/
├── documentos/
├── usuarios/
├── auth.py
├── monitor.py
├── README.md
└── .gitignore
```

## Descrição dos Diretórios

| Diretório / Arquivo        | Função                                                 |
| -------------------------- | ------------------------------------------------------ |
| `blockchain/`              | Contém a lógica da blockchain de auditoria             |
| `blockchain/blockchain.py` | Criação, listagem, persistência e validação dos blocos |
| `blockchain/chain.json`    | Arquivo de persistência da blockchain                  |
| `auditoria/`               | Módulo de auditoria do sistema operacional             |
| `auditoria/auditor.py`     | Coleta dados com `who`, `last`, `ss -tulpn` e `ip a`   |
| `auditoria/relatorios/`    | Armazena relatórios gerados automaticamente            |
| `backup/`                  | Contém o script de backup seguro                       |
| `backup/backup.sh`         | Compacta e criptografa os documentos                   |
| `logs/`                    | Armazena logs locais do sistema                        |
| `documentos/`              | Diretório monitorado por integridade                   |
| `usuarios/`                | Armazena dados dos usuários do sistema Python          |
| `auth.py`                  | Sistema de autenticação com perfis e senha com hash    |
| `monitor.py`               | Monitoramento de integridade dos arquivos              |

## Instalação das Dependências

Atualizar o sistema:

```bash
sudo apt update
sudo apt upgrade -y
```

Instalar ferramentas necessárias:

```bash
sudo apt install -y git python3 python3-pip python3-venv openssl gpg nmap net-tools acl curl nano
```

## Usuários e Grupos do Sistema Operacional

Foram criados três usuários no Debian:

| Usuário         | Permissão                                       |
| --------------- | ----------------------------------------------- |
| `administrador` | Acesso total ao sistema SecureChain             |
| `analista`      | Leitura e execução dos módulos                  |
| `visitante`     | Acesso restrito, somente leitura dos relatórios |

Também foram criados grupos específicos:

```bash
securechain_admin
securechain_analista
securechain_visitante
```

A configuração de permissões utiliza:

* `chmod`;
* `chown`;
* grupos do Linux;
* ACLs com `setfacl`.

Essa separação aplica o princípio do menor privilégio, garantindo que cada usuário tenha apenas os acessos necessários para sua função.

## Blockchain de Auditoria

A blockchain é responsável por registrar eventos relevantes do sistema.

Eventos registrados:

* Bloco gênesis;
* Cadastro de usuário;
* Login realizado com sucesso;
* Tentativa de login negada;
* Arquivo incluído;
* Arquivo alterado;
* Arquivo excluído;
* Backup executado;
* Relatório de auditoria gerado.

Cada bloco possui:

| Campo           | Descrição                         |
| --------------- | --------------------------------- |
| `id`            | Identificador sequencial do bloco |
| `timestamp`     | Data e hora em formato ISO 8601   |
| `evento`        | Descrição do evento ocorrido      |
| `dados`         | Dados adicionais do evento        |
| `hash_anterior` | Hash SHA-256 do bloco anterior    |
| `hash_atual`    | Hash SHA-256 do bloco atual       |

### Validar a blockchain

```bash
python3 blockchain/blockchain.py validate
```

Saída esperada quando a cadeia estiver íntegra:

```text
Blockchain válida. Nenhuma adulteração encontrada.
```

### Listar os blocos

```bash
python3 blockchain/blockchain.py list
```

### Adicionar um evento manual

```bash
python3 blockchain/blockchain.py add "Evento de teste"
```

## Sistema de Autenticação

O arquivo `auth.py` implementa:

* Cadastro de usuários;
* Perfis `admin`, `analista` e `visitante`;
* Login com verificação de senha;
* Registro dos acessos na blockchain;
* Senhas protegidas com SHA-256 e salt.

Executar:

```bash
python3 auth.py
```

Menu principal:

```text
=== SecureChain Auth ===
1 - Cadastrar usuário
2 - Login
3 - Listar usuários
0 - Sair
```

Exemplo de usuários internos do sistema Python:

| Usuário      | Perfil      |
| ------------ | ----------- |
| `admin1`     | `admin`     |
| `analista1`  | `analista`  |
| `visitante1` | `visitante` |

As senhas não são armazenadas em texto puro. O arquivo `usuarios/usuarios.json` armazena apenas:

* perfil;
* salt;
* hash da senha;
* data de criação.

## Monitoramento de Integridade de Arquivos

O arquivo `monitor.py` monitora o diretório `documentos/`.

Funcionalidades:

* Calcula hash SHA-256 dos arquivos;
* Armazena os hashes iniciais;
* Compara os hashes atuais com os anteriores;
* Detecta arquivos incluídos;
* Detecta arquivos alterados;
* Detecta arquivos excluídos;
* Registra eventos na blockchain;
* Gera alerta no terminal quando há inconsistência.

### Inicializar hashes

```bash
python3 monitor.py init
```

### Verificar alterações uma vez

```bash
python3 monitor.py check
```

### Monitorar periodicamente

```bash
python3 monitor.py watch --intervalo 10
```

### Exemplo de teste

```bash
echo "Documento inicial" > documentos/teste.txt
python3 monitor.py init

echo "Alteração no documento" >> documentos/teste.txt
python3 monitor.py check
```

A alteração será detectada e registrada na blockchain.

## Auditoria do Sistema Operacional

O arquivo `auditoria/auditor.py` coleta dados do sistema operacional usando os comandos:

```bash
who
last
ss -tulpn
ip a
```

Executar:

```bash
python3 auditoria/auditor.py
```

Os relatórios são salvos em:

```text
auditoria/relatorios/
```

Cada relatório contém:

* usuários conectados;
* histórico recente de logins;
* portas e serviços em escuta;
* interfaces de rede e endereços IP.

## Backup Seguro Automatizado

O arquivo `backup/backup.sh` executa:

* Compactação do diretório `documentos/` em `.tar.gz`;
* Criptografia simétrica com AES-256-CBC usando OpenSSL;
* Derivação de chave com PBKDF2;
* Registro local em `logs/backup.log`;
* Registro do evento de backup na blockchain.

Executar:

```bash
./backup/backup.sh
```

O script solicitará uma senha para criptografar o backup.

Os backups criptografados são gerados em:

```text
backup/backups/
```

O log local é salvo em:

```text
logs/backup.log
```

## Criptografia Aplicada

| Contexto                | Técnica utilizada                  |
| ----------------------- | ---------------------------------- |
| Senhas                  | SHA-256 com salt                   |
| Integridade de arquivos | SHA-256                            |
| Hash dos blocos         | SHA-256                            |
| Backup                  | AES-256-CBC com PBKDF2 via OpenSSL |

## Zero Trust Security

O projeto aplica conceitos de Zero Trust da seguinte forma:

1. A identidade dos usuários é verificada por login e senha.
2. As senhas não são armazenadas em texto puro.
3. Cada usuário possui um perfil de acesso.
4. O sistema operacional separa permissões por usuários e grupos.
5. O princípio do menor privilégio é aplicado com permissões restritas.
6. Eventos relevantes são registrados na blockchain.
7. A integridade dos documentos é verificada por hash.
8. Backups são criptografados antes do armazenamento.

## Hacking Ético e Análise da VM

A análise de segurança da VM pode ser feita com:

```bash
nmap -sV localhost
ss -tulpn
ip a
who
last
getfacl /home/leonardo/securechain
getfacl /home/leonardo/securechain/auditoria/relatorios
getfacl /home/leonardo/securechain/documentos
```

Esses comandos permitem verificar:

* portas abertas;
* serviços em escuta;
* conexões;
* usuários conectados;
* histórico de login;
* permissões aplicadas aos diretórios críticos.

A análise detalhada, os riscos encontrados e as melhorias propostas devem ser documentados no relatório técnico.

## Teste Geral do Sistema

Sequência recomendada para validar o funcionamento:

```bash
cd /home/leonardo/securechain

python3 blockchain/blockchain.py validate

python3 auth.py

echo "Documento inicial" > documentos/contrato_teste.txt
python3 monitor.py init

echo "Alteração de segurança" >> documentos/contrato_teste.txt
python3 monitor.py check

python3 auditoria/auditor.py

./backup/backup.sh

python3 blockchain/blockchain.py list
python3 blockchain/blockchain.py validate
```

## Teste de Adulteração da Blockchain

Para demonstrar a validação da blockchain:

1. Fazer backup temporário da chain:

```bash
cp blockchain/chain.json blockchain/chain_backup.json
```

2. Editar manualmente um evento:

```bash
nano blockchain/chain.json
```

3. Validar a blockchain:

```bash
python3 blockchain/blockchain.py validate
```

O sistema deve exibir alerta de inconsistência.

4. Restaurar a chain original:

```bash
mv blockchain/chain_backup.json blockchain/chain.json
python3 blockchain/blockchain.py validate
```

## Entregáveis

### Repositório GitHub

O repositório contém:

* Código-fonte completo;
* Scripts Bash;
* Blockchain persistida em `chain.json`;
* README com instruções;
* Estrutura de diretórios do projeto.

### Relatório Técnico

O relatório técnico é um entregável separado e deve conter:

* Arquitetura da solução;
* Conceitos aplicados;
* Capturas de tela;
* Justificativas de criptografia;
* Respostas sobre Zero Trust;
* Análise de segurança da VM;
* Vulnerabilidades encontradas;
* Melhorias aplicadas ou propostas.

### Vídeo Demonstrativo

O vídeo demonstrativo é um entregável separado e deve mostrar:

* VM Debian em execução;
* Login no sistema;
* Geração de blocos na blockchain;
* Monitoramento de arquivo;
* Validação da blockchain;
* Execução do backup criptografado.

## Roteiro Sugerido para o Vídeo

1. Mostrar o projeto no Debian.
2. Mostrar a estrutura de diretórios.
3. Executar `python3 auth.py` e realizar login.
4. Listar blocos da blockchain.
5. Criar ou alterar um arquivo em `documentos/`.
6. Executar `python3 monitor.py check`.
7. Mostrar o novo bloco gerado.
8. Executar `python3 blockchain/blockchain.py validate`.
9. Executar `python3 auditoria/auditor.py`.
10. Executar `./backup/backup.sh`.
11. Mostrar arquivo `.enc` gerado e log do backup.

## Boas Práticas de Segurança

* Não armazenar senhas em texto puro.
* Não versionar tokens pessoais.
* Não versionar backups criptografados gerados em execução.
* Aplicar menor privilégio aos usuários.
* Registrar eventos relevantes na blockchain.
* Validar periodicamente a integridade da cadeia.
* Monitorar alterações em documentos sensíveis.
* Manter histórico de commits significativo no Git.

## Autor

Leonardo Martins

## Suporte tecnico e co autores

Vinicius Calefo
Guilherme Fabretti

## Status

Projeto desenvolvido como prova prática da disciplina Segurança de Sistemas com Blockchain, Criptografia e Auditoria de Eventos.
