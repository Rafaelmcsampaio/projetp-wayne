from app.database import get_db, create_db_and_tables
from app.models import Resource

def main():
    create_db_and_tables()  # garante que as tabelas estejam criadas

    db = next(get_db())  # pega a sessão do banco

    # Recursos iniciais
    recursos_iniciais = [
        Resource(name="Câmera de Segurança", type="equipamento", description="Câmera 8k para monitoramento", quantity=10, is_active=True),
        Resource(name="Veículo de Patrulha", type="veículo", description="Veículo utilitário para ronda", quantity=3, is_active=True),
        Resource(name="Detector de Incêndio", type="dispositivo", description="Sensor de fumaça e calor", quantity=15, is_active=True),
    ]

    # Checa se já tem recursos para não duplicar
    if db.query(Resource).count() == 0:
        db.add_all(recursos_iniciais)
        db.commit()
        print("Recursos criados com sucesso!")
    else:
        print("Recursos já existem no banco.")

if __name__ == "__main__":
    main()
