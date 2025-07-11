from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Configuração do banco de dados
DATABASE_URL = "mysql+mysqlconnector://wayne_user:senha_forte@localhost/wayne_security"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Criação das tabelas com base nos modelos
def create_db_and_tables():
    from app.models import User, Resource  # Importa ambos os modelos aqui
    Base.metadata.create_all(bind=engine)

# Dependência para injeção do DB no FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Consulta auxiliar: buscar usuário pelo email
def get_user_by_email(email: str, db: Session):  # recebe sessão como parâmetro
    from app.models import User
    return db.query(User).filter(User.email == email).first()
