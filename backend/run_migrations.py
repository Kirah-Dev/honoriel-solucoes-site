import os
from app import app, db
from flask_migrate import stamp
from sqlalchemy import text
import sys

print("==========================================")
print("  EXECUTING DATABASE SETUP SCRIPT (FORCE)  ")
print("==========================================")

with app.app_context():
    try:
        print("Connecting to the database...")
        db.session.execute(text('SELECT 1'))
        print(">>> Database connection successful.")

        # FORÇA a criação de todas as tabelas a partir dos models.
        print("Running db.create_all() to ensure all tables exist...")
        db.create_all()
        print(">>> db.create_all() completed.")

        # CARIMBA o banco de dados com a versão mais recente da migração.
        # Isso informa ao Alembic que o banco já está atualizado.
        print("Stamping the database with the 'head' revision...")
        stamp()
        print(">>> Database stamped successfully.")

    except Exception as e:
        print(f"\nFATAL ERROR: An error occurred during database setup.")
        print(f"--> ERRO: {e}\n")
        sys.exit(1) # Falha o build se qualquer coisa der errado.

print("==========================================")
print("  DATABASE SETUP SCRIPT FINISHED  ")
print("==========================================")