import os
from flask_migrate import upgrade
from app import app, db
from sqlalchemy import text
import sys

print("==========================================")
print(" EXECUTING MIGRATION SCRIPT (DIAGNOSTIC)  ")
print("==========================================")

# 1. Verificar se a variável de ambiente existe no build
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("FATAL ERROR: A variável DATABASE_URL não foi encontrada no ambiente de build.")
    sys.exit(1) # Sai com código de erro para falhar o build
else:
    # Imprime a URL de forma segura, escondendo a senha
    print(f"Build environment encontrou a DATABASE_URL.")

# 2. Tentar conectar e executar uma query simples
with app.app_context():
    try:
        print("Tentando conectar ao banco de dados...")
        db.session.execute(text('SELECT 1'))
        print(">>> Conexão com o banco de dados BEM-SUCEDIDA.")

        # 3. Se a conexão funcionou, aplicar as migrações
        print("Aplicando migrações com upgrade()...")
        upgrade()
        print(">>> Comando upgrade() finalizado com sucesso.")

    except Exception as e:
        print(f"\nFATAL ERROR: Ocorreu um erro durante a conexão ou migração.")
        print(f"--> ERRO: {e}\n")
        sys.exit(1) # Sai com código de erro para falhar o build

print("==========================================")
print(" SCRIPT DE MIGRAÇÃO FINALIZADO COM SUCESSO ")
print("==========================================")