from app.database import SessionLocal, create_db_and_tables
from app.models import User
from app.auth import get_password_hash

def main():
    create_db_and_tables()
    db = SessionLocal()

    user = User(
        email="bruce@wayne.com",
        full_name="Bruce Wayne",
        hashed_password=get_password_hash("batman123"),
        role="administrador",
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    print(f"Usuário criado: {user.email}")

if __name__ == "__main__":
    main()
