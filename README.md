# Projeto Wayne – Sistema de Gerenciamento de Segurança

## Descrição

Este projeto é um sistema web robusto e completo, desenvolvido como trabalho final de um curso de Python. Ele foi projetado para oferecer controle de acesso avançado, gerenciamento eficiente de recursos e visualização de dados de segurança para as Indústrias Wayne, uma entidade fictícia do universo Batman.

O sistema é construído com uma arquitetura moderna, utilizando **FastAPI** no backend para uma API de alta performance, **HTML/CSS com Jinja2** para um frontend dinâmico e responsivo, e **MySQL** como banco de dados para persistência de dados.

## Funcionalidades

O Projeto Wayne oferece um conjunto abrangente de funcionalidades, categorizadas por tipo de usuário e área de gerenciamento:

### 1. Autenticação e Autorização
* **Login Seguro**: Autenticação de usuários utilizando JWT (JSON Web Tokens) para sessões seguras.
* **Controle de Acesso Baseado em Papéis (RBAC)**: Diferenciação de funcionalidades e acesso com base em três perfis de usuário: `usuário`, `gerente` e `administrador`.
* **Gerenciamento de Sessão**: Logout funcional que remove os cookies de sessão.

### 2. Dashboard Interativo
* **Visão Geral Personalizada**: Cada usuário tem um dashboard que exibe recursos e opções relevantes à sua função (`administrador`, `gerente`, `usuário`), incluindo a hora atual do servidor.

### 3. Gerenciamento de Áreas Restritas
* **Listagem de Áreas**: Visualização de todas as áreas restritas da indústria.
* **Criação de Novas Áreas**: Administradores podem adicionar novas áreas com nome, descrição e perfis de acesso permitidos.
* **Edição de Áreas**: Administradores podem modificar detalhes de áreas existentes.
* **Exclusão de Áreas**: Administradores podem remover áreas do sistema.
* **Acesso Controlado**: Usuários podem "entrar" em áreas restritas, com validação da sua permissão de acesso.

### 4. Gerenciamento de Recursos
* **Listagem de Recursos**: Gerentes e administradores podem visualizar todos os equipamentos, veículos e dispositivos de segurança.
* **Criação de Recursos**: Administradores podem adicionar novos recursos, especificando nome, tipo, descrição e quantidade.
* **Edição de Recursos**: Administradores podem atualizar as informações de recursos existentes.
* **Exclusão de Recursos**: Administradores podem remover recursos.

### 5. Gerenciamento de Alertas de Segurança
* **Listagem de Alertas**: Visualização de todos os alertas de segurança.
* **Criação de Alertas**: Gerentes e administradores podem criar novos alertas com título, descrição e nível de severidade (baixo, médio, alto, crítico).
* **Edição de Alertas**: Gerentes e administradores podem modificar alertas existentes.
* **Exclusão de Alertas**: Gerentes e administradores podem remover alertas.

### 6. Gerenciamento de Usuários e Permissões
* **Listagem de Usuários**: Administradores podem visualizar todos os usuários do sistema.
* **Adição de Usuários**: Administradores podem registrar novos usuários com e-mail, nome completo, senha e função inicial.
* **Ativação/Desativação de Usuários**: Administradores podem ativar ou desativar contas de usuários (exceto a própria).
* **Exclusão de Usuários**: Administradores podem excluir contas de usuários (exceto a própria).
* **Configuração de Permissões**: Administradores podem alterar a função (role) de qualquer usuário.

### 7. Gerenciamento da Equipe
* **Visão da Equipe**: Gerentes e administradores têm acesso a uma visão geral de todos os membros da equipe, incluindo status e função.
* **Alternar Status de Membro**: Gerentes e administradores podem ativar ou desativar membros da equipe (exceto a própria conta).
* **Excluir Membro da Equipe**: Administradores podem remover membros da equipe (exceto a própria conta).

### 8. Gerenciamento de Comunicados
* **Listagem de Comunicados**: Todos os usuários autenticados podem visualizar comunicados importantes.
* **Criação de Comunicados**: Gerentes e administradores podem criar novos comunicados com título e descrição.
* **Edição de Comunicados**: Administradores podem modificar comunicados existentes.
* **Exclusão de Comunicados**: Administradores podem remover comunicados.

### 9. Gerenciamento de Solicitações de Acesso
* **Solicitar Acesso**: Usuários podem solicitar acesso a áreas restritas, fornecendo uma justificativa.
* **Revisão de Solicitações**: Gerentes e administradores podem visualizar todas as solicitações pendentes, aprovadas ou rejeitadas.
* **Aprovar/Rejeitar Solicitações**: Gerentes e administradores podem aprovar ou rejeitar solicitações de acesso pendentes.

### 10. Relatórios e Análises
* **Dados Agregados**: Gerentes e administradores podem visualizar um resumo de alertas, recursos, usuários e áreas restritas.
* **Gráficos de Dados**: Integração com Chart.js para visualização gráfica dos dados do sistema.

## Tecnologias Utilizadas

* **Backend**:
    * Python 3.11
    * [FastAPI](https://fastapi.tiangolo.com/) (Framework web)
    * [SQLAlchemy](https://www.sqlalchemy.org/) (ORM - Object-Relational Mapper)
    * MySQL (Banco de Dados - configurado via `mysql+mysqlconnector`)
    * [python-jose](https://python-jose.readthedocs.io/en/latest/) (Para JWT - JSON Web Tokens)
    * [Passlib](https://passlib.readthedocs.io/en/stable/) (Para hashing de senhas, utilizando `bcrypt`)
    * [Uvicorn](https://www.uvicorn.org/) (Servidor ASGI)
* **Frontend**:
    * HTML5
    * CSS3 (Com variáveis CSS para melhor manutenibilidade e responsividade)
    * [Jinja2](https://jinja.palletsprojects.com/) (Sistema de templates)
    * [Chart.js](https://www.chartjs.org/) (Biblioteca JavaScript para gráficos)
    * JavaScript (Para interações no frontend e confirmação de ações)

## Estrutura do Projeto

projetp-wayne/
├── app/
│   ├── auth.py                  # Funções de autenticação e hashing de senha
│   ├── create_resources.py      # Script para popular recursos iniciais
│   ├── create_user.py           # Script para criar um usuário administrador inicial
│   ├── database.py              # Configuração do banco de dados (MySQL) e sessão
│   ├── main.py                  # Aplicação FastAPI principal e rotas
│   ├── models.py                # Definições dos modelos de dados (SQLAlchemy)
│   └── templates/               # Arquivos HTML (Jinja2)
│       ├── add_user.html
│       ├── alertas.html
│       ├── area_detalhe.html
│       ├── areas.html
│       ├── comunicados.html
│       ├── criar_alerta.html
│       ├── dashboard.html
│       ├── editar_alerta.html
│       ├── editar_area.html
│       ├── editar_comunicado.html
│       ├── editar_recurso.html
│       ├── equipe.html
│       ├── login.html
│       ├── nova_area.html
│       ├── novo_comunicado.html
│       ├── novo_recurso.html
│       ├── permissoes.html
│       ├── relatorios.html
│       ├── resources.html
│       ├── solicitacoes_admin.html
│       └── solicitacoes.html
├── static/
│   ├── css/
│   │   └── style.css            # Folha de estilos CSS
│   └── js/
│       ├── confirm_actions.js   # Funções JS para confirmações
│       └── relatorios.js        # Script JS para renderização de gráficos Chart.js
└── requirements.txt             # Dependências do projeto


## Como executar o projeto localmente

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local:

```bash
# Clone o repositório
git clone [https://github.com/rafaelmcsampaio/projetp-wayne.git](https://github.com/rafaelmcsampaio/projetp-wayne.git)
cd projetp-wayne

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
Configuração do Banco de Dados (MySQL):

Este projeto está configurado para usar MySQL. Antes de rodar a aplicação, você precisará ter um servidor MySQL em execução e criar um banco de dados com as seguintes credenciais (conforme definido em app/database.py):

Nome do Banco de Dados: wayne_security

Usuário: wayne_user

Senha: senha_forte

Você pode configurar isso manualmente ou usar ferramentas como MySQL Workbench ou linha de comando. Exemplo de comandos SQL para criar o banco de dados e usuário (se seu MySQL já estiver rodando):

SQL

CREATE DATABASE wayne_security;
CREATE USER 'wayne_user'@'localhost' IDENTIFIED BY 'senha_forte';
GRANT ALL PRIVILEGES ON wayne_security.* TO 'wayne_user'@'localhost';
FLUSH PRIVILEGES;
Bash

# Rode o servidor
uvicorn app.main:app --reload
Após executar o comando uvicorn, o sistema estará acessível no seu navegador, geralmente em http://127.0.0.1:8000.