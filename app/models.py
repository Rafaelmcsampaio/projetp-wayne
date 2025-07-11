from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base # app.database é importado, isso é correto

# --- Modelo de Usuário ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="usuario")

    solicitacoes = relationship("Solicitacao", back_populates="solicitante")


# --- Modelo de Recurso ---
class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text)
    quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

# --- Modelo de Alerta ---
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False) # Mantido como Text para descrições longas
    nivel = Column(String(20), nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now()) # Usando func.now() para timezone
    criado_por = Column(String(100), nullable=False)

# --- Modelo de Área Restrita ---
class AreaRestrita(Base):
    __tablename__ = "areas_restritas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)
    acesso_liberado_para = Column(String(100), nullable=False)  # Ex: "administrador,gerente"
    is_ativa = Column(Boolean, default=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now()) # Usando func.now() para timezone

# --- Modelo de Comunicado ---
class Comunicado(Base):
    __tablename__ = "comunicados"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False) # Alterado para Text para permitir descrições maiores
    criado_por = Column(String(100), nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now()) # Usando func.now() para timezone

# --- Modelo de Solicitação de Acesso ---
class Solicitacao(Base):
    __tablename__ = "solicitacoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    area_solicitada = Column(String(100), nullable=False)
    justificativa = Column(Text, nullable=True)
    status = Column(String(20), default="pendente", nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_atualizacao = Column(DateTime(timezone=True), onupdate=func.now())

    solicitante = relationship("User", back_populates="solicitacoes")
