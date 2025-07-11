
import os
from typing import List, Dict, Optional
from datetime import datetime 

from fastapi import FastAPI, Request, Depends, Form, HTTPException, status # <-- status está importado
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, configure_mappers 

# Importações do seu projeto
from app.auth import login_user, get_password_hash
from app.database import create_db_and_tables, get_db
from app.models import User, Resource, Alert, AreaRestrita, Comunicado, Solicitacao


# --- Configuração da Aplicação FastAPI ---
app = FastAPI()

# Configuração de templates e arquivos estáticos
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Funções Auxiliares para Autenticação e Autorização ---

async def get_current_user_from_cookies(request: Request) -> Optional[Dict[str, str]]:
    """Obtém o ID, nome completo e a role do usuário dos cookies."""
    user_id = request.cookies.get("user_id")
    user_full_name = request.cookies.get("user")
    user_role = request.cookies.get("role")
    
    if not user_id or not user_full_name or not user_role:
        return None
    try:
        return {"id": int(user_id), "full_name": user_full_name, "role": user_role}
    except ValueError:
        return None


async def get_authenticated_user_db(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Verifica se o usuário está autenticado via cookies e retorna o objeto User completo do banco de dados.
    Redireciona para a página de login se o usuário não estiver autenticado ou não for encontrado no DB.
    """
    user_info = await get_current_user_from_cookies(request)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, # <-- Uso correto
            detail="Não autenticado. Por favor, faça login.",
            headers={"Location": "/"}
        )
    
    user = db.query(User).filter(
        User.id == user_info["id"],
        User.full_name == user_info["full_name"],
        User.role == user_info["role"]
    ).first()

    if not user or not user.is_active:
        response = RedirectResponse(url="/logout", status_code=status.HTTP_302_FOUND) # <-- Uso correto
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, # <-- Uso correto
            detail="Sessão inválida ou usuário inativo. Faça login novamente.",
            headers={"Location": response.headers["location"]}
        )
    return user


async def admin_required(current_user: User = Depends(get_authenticated_user_db)):
    """Verifica se o usuário é um administrador e retorna o objeto User."""
    if current_user.role != "administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Apenas administradores podem acessar esta funcionalidade.")
    return current_user


async def manager_or_admin_required(current_user: User = Depends(get_authenticated_user_db)):
    """Verifica se o usuário é um gerente ou administrador e retorna o objeto User."""
    if current_user.role not in ["administrador", "gerente"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Apenas administradores e gerentes podem acessar esta funcionalidade.")
    return current_user


# --- Evento de Inicialização (Popula o DB com usuários e comunicados de exemplo) ---

@app.on_event("startup")
def startup_event():
    """Cria o banco de dados e insere usuários e comunicados de exemplo se não existirem."""
    create_db_and_tables()
    db = next(get_db())

    configure_mappers() 

    example_users = [
        {"email": "bruce@wayne.com", "full_name": "Bruce Wayne", "password": "batman123", "role": "administrador"},
        {"email": "dick@grayson.com", "full_name": "Dick Grayson", "password": "asanoturna123", "role": "gerente"},
        {"email": "damian@wayne.com", "full_name": "Damian Wayne", "password": "robin123", "role": "usuario"}
    ]

    for user_data in example_users:
        user = db.query(User).filter(User.email == user_data["email"]).first()
        if not user:
            new_user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                is_active=True
            )
            db.add(new_user)
    
    example_comunicado = db.query(Comunicado).filter(Comunicado.titulo == "Comunicado de Boas-Vindas").first()
    if not example_comunicado:
        new_comunicado = Comunicado(
            titulo="Comunicado de Boas-Vindas",
            descricao="Bem-vindo(a) ao sistema! Explore as novas funcionalidades.",
            criado_por="Sistema"
        )
        db.add(new_comunicado)
    
    example_area = db.query(AreaRestrita).filter(AreaRestrita.nome == "Sala de Servidores").first()
    if not example_area:
        new_area = AreaRestrita(
            nome="Sala de Servidores",
            descricao="Acesso a servidores críticos.",
            acesso_liberado_para="administrador,gerente"
        )
        db.add(new_area)
    
    db.commit()

    bruce = db.query(User).filter(User.full_name == "Bruce Wayne").first()
    servidores = db.query(AreaRestrita).filter(AreaRestrita.nome == "Sala de Servidores").first()

    if bruce and servidores and 'Solicitacao' in globals():
        example_solicitacao = db.query(Solicitacao).filter(
            Solicitacao.usuario_id == bruce.id, 
            Solicitacao.area_solicitada == servidores.nome
        ).first()
        if not example_solicitacao:
            new_solicitacao = Solicitacao(
                usuario_id=bruce.id,
                usuario_nome=bruce.full_name,
                area_solicitada=servidores.nome,
                justificativa="Necessário para manutenção de rotina.",
                status="pendente"
            )
            db.add(new_solicitacao)
            db.commit()

    db.close()


# --- Rotas de Autenticação ---

@app.get("/", response_class=HTMLResponse)
async def get_login(request: Request):
    """Página de login."""
    return templates.TemplateResponse("login.html", {"request": request, "message": ""})


@app.post("/login")
async def post_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Processa o formulário de login."""
    user = login_user(db, email, password)
    if user:
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND) # <-- Uso correto
        response.set_cookie(key="user", value=user.full_name, httponly=True)
        response.set_cookie(key="role", value=user.role, httponly=True)
        response.set_cookie(key="user_id", value=str(user.id), httponly=True)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "message": "Credenciais inválidas. Verifique seu email e senha."})


@app.get("/logout")
async def logout():
    """Realiza o logout do usuário, removendo os cookies de sessão."""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND) # <-- Uso correto
    response.delete_cookie("user")
    response.delete_cookie("role")
    response.delete_cookie("user_id")
    return response


# --- Rotas do Dashboard ---

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request, current_user: User = Depends(get_authenticated_user_db)):
    """Página do dashboard."""
    role = current_user.role
    user_full_name = current_user.full_name
    current_server_time = datetime.now() 

    resources_by_role = {
        "administrador": [
            {"nome": "Visualizar Alertas de Segurança", "url": "/alertas"},
            {"nome": "Acessar Comunicados", "url": "/comunicados"},
            {"nome": "Gerenciar Usuários", "url": "/usuarios"},
            {"nome": "Gerenciar Equipe", "url": "/equipe"},
            {"nome": "Configurar Permissões", "url": "/permissoes"},
            {"nome": "Relatórios e Análises", "url": "/relatorios"},
            {"nome": "Gerenciar Recursos", "url": "/recursos"},
            {"nome": "Gerenciar Áreas Restritas", "url": "/areas"},
            {"nome": "Gerenciar Solicitações de Acesso", "url": "/solicitacoes"}
        ],
        "gerente": [
            {"nome": "Visualizar Alertas de Segurança", "url": "/alertas"},
            {"nome": "Acessar Comunicados", "url": "/comunicados"},
            {"nome": "Gerenciar Equipe", "url": "/equipe"},
            {"nome": "Gerar Relatórios", "url": "/relatorios"},
            {"nome": "Visualizar Recursos", "url": "/recursos"},
            {"nome": "Visualizar Áreas Restritas", "url": "/areas"},
            {"nome": "Gerenciar Solicitações de Acesso", "url": "/solicitacoes"}
        ],
        "usuario": [
            {"nome": "Visualizar Alertas de Segurança", "url": "/alertas"},
            {"nome": "Acessar Comunicados", "url": "/comunicados"},
            {"nome": "Solicitar Acesso a Áreas", "url": "/solicitacoes"},
            {"nome": "Ver Áreas Restritas Disponíveis", "url": "/areas"}
        ]
    }
    recursos = resources_by_role.get(role, [])

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user_full_name,
        "recursos": recursos,
        "role": role,
        "current_time": current_server_time 
    })


# --- CRUD de Áreas Restritas ---

@app.get("/areas", response_class=HTMLResponse)
async def listar_areas(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_authenticated_user_db)):
    """Lista todas as áreas restritas."""
    areas = db.query(AreaRestrita).all()
    return templates.TemplateResponse("areas.html", {"request": request, "areas": areas, "role": current_user.role})


@app.get("/areas/nova", response_class=HTMLResponse)
async def nova_area_form(request: Request, current_user: User = Depends(admin_required)):
    """Formulário para criar uma nova área restrita (apenas admin)."""
    return templates.TemplateResponse("nova_area.html", {"request": request})


@app.post("/areas/nova")
async def criar_area(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(""),
    acesso_liberado_para: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Cria uma nova área restrita."""
    new_area = AreaRestrita(
        nome=nome,
        descricao=descricao,
        acesso_liberado_para=acesso_liberado_para
    )
    db.add(new_area)
    db.commit()
    db.refresh(new_area)
    return RedirectResponse(url="/areas", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.get("/areas/{area_id}/editar", response_class=HTMLResponse)
async def editar_area_form(area_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    """Formulário de edição de área restrita (apenas admin)."""
    area = db.query(AreaRestrita).filter(AreaRestrita.id == area_id).first()
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Área não encontrada.")
    return templates.TemplateResponse("editar_area.html", {"request": request, "area": area})


@app.post("/areas/{area_id}/editar")
async def editar_area(
    area_id: int,
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(...),
    acesso_liberado_para: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Salva as edições de uma área restrita."""
    area = db.query(AreaRestrita).filter(AreaRestrita.id == area_id).first()
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Área não encontrada.")
    
    area.nome = nome
    area.descricao = descricao
    area.acesso_liberado_para = acesso_liberado_para
    db.commit()
    db.refresh(area)
    return RedirectResponse(url="/areas", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.post("/areas/{area_id}/excluir")
async def excluir_area(area_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    """Exclui uma área restrita."""
    area = db.query(AreaRestrita).filter(AreaRestrita.id == area_id).first()
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Área não encontrada.")
    db.delete(area)
    db.commit()
    return RedirectResponse(url="/areas", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.get("/areas/{area_id}/entrar", response_class=HTMLResponse)
async def entrar_area(area_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_authenticated_user_db)):
    """Permite que um usuário entre em uma área restrita se tiver a role necessária."""
    area = db.query(AreaRestrita).filter(AreaRestrita.id == area_id).first()
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Área não encontrada.")

    allowed_roles = [role.strip() for role in area.acesso_liberado_para.split(",")]
    if current_user.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Acesso não autorizado a esta área para a sua role ({current_user.role}). Roles permitidas: {', '.join(allowed_roles)}.")

    return templates.TemplateResponse("area_detalhe.html", {"request": request, "area": area, "user": current_user.full_name})


# --- CRUD de Recursos ---

@app.get("/recursos", response_class=HTMLResponse)
async def listar_recursos(request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_or_admin_required)):
    """Lista todos os recursos (apenas gerente e admin)."""
    recursos = db.query(Resource).all()
    current_user_info_for_template = await get_current_user_from_cookies(request) 
    return templates.TemplateResponse("resources.html", {"request": request, "recursos": recursos, "role": current_user_info_for_template["role"]})


@app.get("/recursos/novo", response_class=HTMLResponse)
async def novo_recurso_form(request: Request, current_user: User = Depends(admin_required)):
    """Formulário para criar um novo recurso (apenas admin)."""
    return templates.TemplateResponse("novo_recurso.html", {"request": request})


@app.post("/recursos/novo")
async def criar_recurso(
    request: Request,
    name: str = Form(...),
    type: str = Form(...),
    description: str = Form(""),
    quantity: int = Form(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Cria um novo recurso."""
    recurso = Resource(name=name, type=type, description=description, quantity=quantity, is_active=True)
    db.add(recurso)
    db.commit()
    db.refresh(recurso)
    return RedirectResponse(url="/recursos", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.get("/recursos/{resource_id}/editar", response_class=HTMLResponse)
async def editar_recurso_form(resource_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    """Formulário de edição de recurso (apenas admin)."""
    recurso = db.query(Resource).filter(Resource.id == resource_id).first()
    if not recurso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso não encontrado.")
    return templates.TemplateResponse("editar_recurso.html", {"request": request, "recurso": recurso})


@app.post("/recursos/{resource_id}/editar")
async def salvar_edicao_recurso(
    resource_id: int,
    request: Request,
    name: str = Form(...),
    type: str = Form(...),
    description: str = Form(""),
    quantity: int = Form(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Salva as edições de um recurso."""
    recurso = db.query(Resource).filter(Resource.id == resource_id).first()
    if not recurso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso não encontrado.")

    recurso.name = name
    recurso.type = type
    recurso.description = description
    recurso.quantity = quantity
    db.commit()
    db.refresh(recurso)
    return RedirectResponse(url="/recursos", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.post("/recursos/{resource_id}/excluir")
async def excluir_recurso(resource_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    """Exclui um recurso."""
    recurso = db.query(Resource).filter(Resource.id == resource_id).first()
    if not recurso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso não encontrado.")

    db.delete(recurso)
    db.commit()
    return RedirectResponse(url="/recursos", status_code=status.HTTP_302_FOUND) # <-- Uso correto


# --- CRUD de Alertas ---

@app.get("/alertas", response_class=HTMLResponse)
async def alertas(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_authenticated_user_db)):
    """Lista todos os alertas."""
    alertas_list = db.query(Alert).order_by(Alert.data_criacao.desc()).all()
    return templates.TemplateResponse(
        "alertas.html", 
        {"request": request, "alertas": alertas_list, "role": current_user.role}
    )


@app.get("/criar-alerta", response_class=HTMLResponse)
async def get_criar_alerta(request: Request, current_user: User = Depends(manager_or_admin_required)):
    """Formulário para criar um novo alerta (apenas gerente e admin)."""
    return templates.TemplateResponse("criar_alerta.html", {"request": request})


@app.post("/criar-alerta")
async def post_criar_alerta(
    request: Request,
    titulo: str = Form(...),
    descricao: str = Form(...),
    nivel: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_or_admin_required)
):
    """Cria um novo alerta."""
    alerta = Alert(
        titulo=titulo,
        descricao=descricao,
        nivel=nivel,
        criado_por=current_user.full_name
    )
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return RedirectResponse(url="/alertas", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.get("/alertas/{alerta_id}/editar", response_class=HTMLResponse)
async def editar_alerta_form(alerta_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_or_admin_required)):
    """Formulário de edição de alerta (apenas gerente e admin)."""
    alerta = db.query(Alert).filter(Alert.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta não encontrado.")
    return templates.TemplateResponse("editar_alerta.html", {"request": request, "alerta": alerta})


@app.post("/alertas/{alerta_id}/editar")
async def editar_alerta(
    alerta_id: int,
    titulo: str = Form(...),
    descricao: str = Form(...),
    nivel: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_or_admin_required)
):
    """Salva as edições de um alerta."""
    alerta = db.query(Alert).filter(Alert.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta não encontrado.")

    alerta.titulo = titulo
    alerta.descricao = descricao
    alerta.nivel = nivel
    db.commit()
    db.refresh(alerta)
    return RedirectResponse(url="/alertas", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.post("/alertas/{alerta_id}/excluir")
async def excluir_alerta(alerta_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_or_admin_required)):
    """Exclui um alerta."""
    alerta = db.query(Alert).filter(Alert.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta não encontrado.")
    db.delete(alerta)
    db.commit()
    return RedirectResponse(url="/alertas", status_code=status.HTTP_302_FOUND) # <-- Uso correto


# --- CRUD de Usuários e Permissões ---

@app.get("/usuarios", response_class=HTMLResponse)
async def usuarios(request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    """Lista todos os usuários (apenas admin)."""
    users = db.query(User).all()
    return templates.TemplateResponse("usuarios.html", {"request": request, "usuarios": users, "role": current_user.role, "usuario_logado_id": current_user.id})


@app.get("/adicionar-usuario", response_class=HTMLResponse)
async def get_add_user(request: Request, current_user: User = Depends(admin_required)):
    """Formulário para adicionar um novo usuário (apenas admin)."""
    return templates.TemplateResponse("add_user.html", {"request": request, "message": ""})


@app.post("/adicionar-usuario")
async def post_add_user(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Adiciona um novo usuário."""
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("add_user.html", {"request": request, "message": "Já existe um usuário com este e-mail."})

    new_user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/usuarios", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.post("/usuarios/{user_id}/desativar")
async def desativar_usuario(user_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    """Desativa um usuário."""
    user_to_deactivate = db.query(User).filter(User.id == user_id).first()
    if not user_to_deactivate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    if user_to_deactivate.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Você não pode desativar sua própria conta.")

    user_to_deactivate.is_active = False
    db.commit()
    db.refresh(user_to_deactivate)
    return RedirectResponse(url="/usuarios", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.post("/usuarios/{user_id}/ativar")
async def ativar_usuario(user_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    """Ativa um usuário."""
    user_to_activate = db.query(User).filter(User.id == user_id).first()
    if not user_to_activate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    user_to_activate.is_active = True
    db.commit()
    db.refresh(user_to_activate)
    return RedirectResponse(url="/usuarios", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.post("/usuarios/{user_id}/excluir")
async def excluir_usuario(user_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    """Exclui um usuário."""
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    if user_to_delete.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Você não pode excluir sua própria conta.")

    db.delete(user_to_delete)
    db.commit()
    return RedirectResponse(url="/usuarios", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.get("/permissoes", response_class=HTMLResponse)
async def configurar_permissoes(request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    """Exibe a página para configurar permissões de usuário (apenas admin)."""
    usuarios_list = db.query(User).all()
    return templates.TemplateResponse("permissoes.html", {"request": request, "usuarios": usuarios_list, "role": current_user.role, "usuario_logado_id": current_user.id})


@app.post("/permissoes/{user_id}/alterar")
async def alterar_permissao(user_id: int, novo_role: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    """Altera a role de um usuário."""
    user_to_update = db.query(User).filter(User.id == user_id).first()
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    
    if novo_role not in ["usuario", "gerente", "administrador"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de usuário inválido. Roles válidas: usuario, gerente, administrador.")

    if user_to_update.id == current_user.id and novo_role != "administrador" and current_user.role == "administrador":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Você não pode remover seu próprio acesso de administrador.")

    user_to_update.role = novo_role
    db.commit()
    db.refresh(user_to_update)
    return RedirectResponse(url="/permissoes", status_code=status.HTTP_302_FOUND) # <-- Uso correto


# --- Rotas de Relatórios ---

@app.get("/relatorios", response_class=HTMLResponse)
async def relatorios(request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_or_admin_required)):
    """Página de relatórios (apenas gerente e admin)."""
    total_alertas = db.query(Alert).count()
    alertas_criticos = db.query(Alert).filter(Alert.nivel == "crítico").count()
    total_recursos = db.query(Resource).count()
    total_usuarios = db.query(User).count()
    total_areas = db.query(AreaRestrita).count()

    current_user_info_for_template = await get_current_user_from_cookies(request) 

    return templates.TemplateResponse("relatorios.html", {
        "request": request,
        "total_alertas": total_alertas,
        "alertas_criticos": alertas_criticos,
        "total_recursos": total_recursos,
        "total_usuarios": total_usuarios,
        "total_areas": total_areas,
        "role": current_user_info_for_template["role"]
    })


# --- Gerenciamento de Equipe ---

@app.get("/equipe", response_class=HTMLResponse)
async def equipe(request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_or_admin_required)):
    """Página de equipe com informações de todos os usuários (visível por gerentes e administradores)."""
    if current_user.role not in ["administrador", "gerente"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito.")
    
    equipe_list = db.query(User).all()
    return templates.TemplateResponse("equipe.html", {
        "request": request,
        "equipe": equipe_list,
        "role": current_user.role,
        "usuario_logado_id": current_user.id
    })


@app.post("/equipe/{user_id}/alternar-status")
async def alternar_status_usuario_equipe(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_or_admin_required)
):
    """Ativa ou desativa um membro da equipe (permitido para gerentes e admins, menos eles mesmos)."""
    usuario_to_update = db.query(User).filter(User.id == user_id).first()
    if not usuario_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    
    if usuario_to_update.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Você não pode alterar seu próprio status.")

    usuario_to_update.is_active = not usuario_to_update.is_active
    db.commit()
    db.refresh(usuario_to_update)
    return RedirectResponse(url="/equipe", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.post("/equipe/{user_id}/excluir")
async def excluir_membro_equipe(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    usuario_to_delete = db.query(User).filter(User.id == user_id).first()
    if not usuario_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    
    if usuario_to_delete.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Você não pode excluir sua própria conta.")

    db.delete(usuario_to_delete)
    db.commit()
    return RedirectResponse(url="/equipe", status_code=status.HTTP_302_FOUND) # <-- Uso correto


# --- CRUD de Comunicados ---

@app.get("/comunicados", response_class=HTMLResponse)
async def listar_comunicados(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_authenticated_user_db)):
    """Lista comunicados - aberto para qualquer usuário autenticado."""
    comunicados = db.query(Comunicado).order_by(Comunicado.data_criacao.desc()).all()
    return templates.TemplateResponse("comunicados.html", {
        "request": request,
        "comunicados": comunicados,
        "role": current_user.role
    })


@app.get("/comunicados/novo", response_class=HTMLResponse)
async def novo_comunicado_form(request: Request, current_user: User = Depends(manager_or_admin_required)):
    """Formulário para novo comunicado - só gerente e administrador."""
    return templates.TemplateResponse("novo_comunicado.html", {"request": request})


@app.post("/comunicados/novo")
async def criar_comunicado(
    request: Request,
    titulo: str = Form(...),
    descricao: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_or_admin_required)
):
    """Cria comunicado - só gerente e administrador."""
    comunicado_obj = Comunicado(
        titulo=titulo,
        descricao=descricao,
        criado_por=current_user.full_name
    )
    db.add(comunicado_obj)
    db.commit()
    db.refresh(comunicado_obj)
    return RedirectResponse(url="/comunicados", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.get("/comunicados/{comunicado_id}/editar", response_class=HTMLResponse)
async def editar_comunicado_form(comunicado_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    """Formulário para editar comunicado - só administrador."""
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunicado não encontrado.")
    
    return templates.TemplateResponse("editar_comunicado.html", {"request": request, "comunicado": comunicado})


@app.post("/comunicados/{comunicado_id}/editar")
async def editar_comunicado(
    comunicado_id: int,
    request: Request,
    titulo: str = Form(...),
    descricao: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Salvar edição do comunicado - só administrador."""
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunicado não encontrado.")
    
    comunicado.titulo = titulo
    comunicado.descricao = descricao
    db.commit()
    db.refresh(comunicado)
    return RedirectResponse(url="/comunicados", status_code=status.HTTP_302_FOUND) # <-- Uso correto

@app.post("/comunicados/{comunicado_id}/excluir")
async def excluir_comunicado(
    comunicado_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    comunicado = db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
    if not comunicado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunicado não encontrado.")
    
    db.delete(comunicado)
    db.commit()
    return RedirectResponse(url="/comunicados", status_code=status.HTTP_302_FOUND) # <-- Uso correto


# --- Gerenciamento de Solicitações de Acesso ---

@app.get("/solicitacoes", response_class=HTMLResponse)
async def get_solicitacoes(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user_db)
):
    """
    Página para usuários solicitarem acesso ou para admins/gerentes gerenciarem solicitações.
    Apresenta o formulário de solicitação para "usuario" e a lista de solicitações para "gerente" e "administrador".
    """
    
    areas_disponiveis = db.query(AreaRestrita).all()

    if current_user.role == "usuario":
        return templates.TemplateResponse("solicitacoes.html", {
            "request": request,
            "areas_disponiveis": areas_disponiveis,
            "role": current_user.role,
            "message": "",
            "message_type": ""
        })
    elif current_user.role in ["administrador", "gerente"]:
        if 'Solicitacao' in globals():
            solicitacoes_list = db.query(Solicitacao).order_by(Solicitacao.data_criacao.desc()).all()
        else:
            solicitacoes_list = []
            print("WARNING: Solicitacao model not available. Check app/models.py import.")

        return templates.TemplateResponse("solicitacoes_admin.html", {
            "request": request,
            "solicitacoes": solicitacoes_list,
            "role": current_user.role
        })
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado para esta página.")


@app.post("/solicitacoes/nova", response_class=HTMLResponse)
async def create_solicitacao(
    request: Request,
    area_id: int = Form(...),
    justificativa: str = Form(...),
    current_user: User = Depends(get_authenticated_user_db),
    db: Session = Depends(get_db)
):
    """Processa a submissão de uma nova solicitação de acesso de um usuário."""
    area = db.query(AreaRestrita).filter(AreaRestrita.id == area_id).first()
    if not area:
        areas = db.query(AreaRestrita).all()
        return templates.TemplateResponse("solicitacoes.html", {
            "request": request,
            "areas_disponiveis": areas,
            "role": current_user.role,
            "message": "Área selecionada não encontrada ou inválida.",
            "message_type": "error"
        })

    allowed_roles_for_area = [r.strip() for r in area.acesso_liberado_para.split(",")]
    if current_user.role in allowed_roles_for_area:
        areas = db.query(AreaRestrita).all()
        return templates.TemplateResponse("solicitacoes.html", {
            "request": request,
            "areas_disponiveis": areas,
            "role": current_user.role,
            "message": f"Você já tem acesso à área '{area.nome}'.",
            "message_type": "info"
        })

    existing_solicitation = db.query(Solicitacao).filter(
        Solicitacao.usuario_id == current_user.id,
        Solicitacao.area_solicitada == area.nome,
        Solicitacao.status == "pendente"
    ).first()

    if existing_solicitation:
        areas = db.query(AreaRestrita).all()
        return templates.TemplateResponse("solicitacoes.html", {
            "request": request,
            "areas_disponiveis": areas,
            "role": current_user.role,
            "message": f"Você já tem uma solicitação pendente para a área '{area.nome}'.",
            "message_type": "warning"
        })

    nova_solicitacao = Solicitacao(
        usuario_id=current_user.id,
        usuario_nome=current_user.full_name,
        area_solicitada=area.nome,
        justificativa=justificativa,
        status="pendente"
    )
    db.add(nova_solicitacao)
    db.commit()
    db.refresh(nova_solicitacao)

    areas = db.query(AreaRestrita).all()
    return templates.TemplateResponse("solicitacoes.html", {
        "request": request,
        "areas_disponiveis": areas,
        "role": current_user.role,
        "message": f"Solicitação para a área '{area.nome}' enviada com sucesso! Aguarde aprovação.",
        "message_type": "success"
    })


@app.post("/solicitacoes/{solicitacao_id}/aprovar")
async def aprovar_solicitacao(
    solicitacao_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_or_admin_required)
):
    """Aprova uma solicitação de acesso."""
    solicitacao = db.query(Solicitacao).filter(Solicitacao.id == solicitacao_id).first()
    if not solicitacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")
    
    if solicitacao.status != "pendente":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A solicitação já foi processada.")

    solicitacao.status = "aprovada"
    db.commit()
    db.refresh(solicitacao)
    return RedirectResponse(url="/solicitacoes", status_code=status.HTTP_302_FOUND) # <-- Uso correto


@app.post("/solicitacoes/{solicitacao_id}/rejeitar")
async def rejeitar_solicitacao(
    solicitacao_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_or_admin_required)
):
    """Rejeita uma solicitação de acesso."""
    solicitacao = db.query(Solicitacao).filter(Solicitacao.id == solicitacao_id).first()
    if not solicitacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")
    
    if solicitacao.status != "pendente":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A solicitação já foi processada.")

    solicitacao.status = "rejeitada"
    db.commit()
    db.refresh(solicitacao)
    return RedirectResponse(url="/solicitacoes", status_code=status.HTTP_302_FOUND) # <-- Uso correto
