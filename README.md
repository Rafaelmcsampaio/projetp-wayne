#  Projeto Wayne – Sistema de Gerenciamento de Segurança

##  Descrição

Projeto final do curso de Python, com objetivo de desenvolver um sistema web completo para controle de acesso, gestão de recursos e visualização de dados de segurança para as Indústrias Wayne (empresa fictícia do universo Batman).

Este sistema foi construído com Python (FastAPI) no backend, HTML/CSS no frontend, e banco de dados SQLite para persistência local.

---

##  Funcionalidades

-  Autenticação com JWT (login seguro)
-  Controle de acesso por tipo de usuário: funcionário, gerente, administrador
-  Gerenciamento de recursos: equipamentos, veículos e dispositivos de segurança
-  Dashboard HTML com dados da operação
-  Interface organizada com HTML5, CSS3 e templates Jinja2
-  Backend em Python com FastAPI, SQLAlchemy e SQLite

---

##  Tecnologias Utilizadas

- Python 3.11
- FastAPI
- SQLite + SQLAlchemy
- Jinja2
- JWT (via python-jose)
- Passlib (bcrypt)
- HTML5 + CSS3

---

##  Como executar o projeto localmente

```bash
# Clone o repositório
git clone https://github.com/rafaelmcsampaio/projetp-wayne.git
cd projetp-wayne

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Rode o servidor
uvicorn app.main:app --reload
