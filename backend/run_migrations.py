from flask_migrate import upgrade
from app import app

print("===================================")
print("EXECUTING MIGRATION SCRIPT...")
print("===================================")

# O "contexto da aplicação" é necessário para que as extensões do Flask saibam
# como se conectar ao banco de dados e encontrar os arquivos de migração.
with app.app_context():
    try:
        # A função upgrade() é o coração do Flask-Migrate.
        # Ela aplica todas as migrações pendentes.
        upgrade()
        print("Database migrations applied successfully.")
    except Exception as e:
        print(f"An error occurred while applying migrations: {e}")
        # Levanta o erro para fazer o build do Render falhar se a migração falhar.
        raise e

print("===================================")
print("MIGRATION SCRIPT FINISHED.")
print("===================================")