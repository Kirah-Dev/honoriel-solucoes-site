# Honoriel Soluções - Site Institucional e Plataforma de RH

![Honoriel Logo](backend/static/images/anjo_honoriel.png)

Repositório oficial do site institucional e sistema de gestão para a consultoria de RH **Honoriel Soluções**. Este é um projeto full-stack desenvolvido para fortalecer a presença online da empresa e otimizar seus processos de recrutamento e gerenciamento de conteúdo.

---

## 🚀 Status do Projeto

**Em Produção** | O site está pronto para o deploy e uso real.

---

## 🛠️ Tecnologias Utilizadas

### Backend
*   **Linguagem:** Python 3
*   **Framework:** Flask
*   **Banco de Dados:** PostgreSQL
*   **ORM:** SQLAlchemy com Flask-SQLAlchemy
*   **Migrações:** Flask-Migrate (Alembic)
*   **Autenticação:** Flask-Login & Flask-Bcrypt
*   **Envio de E-mail:** Flask-Mail

### Frontend
*   **Estrutura:** HTML5
*   **Estilização:** CSS3 (com Flexbox e Grid)
*   **Interatividade:** JavaScript (Vanilla ES6+)
*   **Motor de Templates:** Jinja2

---

## ✨ Funcionalidades Principais

### Site Público
- [x] **Páginas Institucionais:** Home, Sobre, Serviços e Contato.
- [x] **Sistema de Candidatura:** Formulário dinâmico para cadastro de perfil completo, permitindo que a mesma pessoa se candidate a múltiplas vagas.
- [x] **Blog Dinâmico:** Listagem de posts com paginação e página de detalhes para cada artigo.
- [x] **Exibição de Especialistas:** Cards e modais com perfis de especialistas parceiros, gerenciados via painel de admin.
- [x] **Design Responsivo:** Adaptado para desktops, tablets e celulares.

### Painel Administrativo
- [x] **Autenticação Segura:** Sistema de login e senha para acesso restrito.
- [x] **CRUD de Blog:** Funcionalidades para Criar, Ler, Atualizar e Excluir posts.
- [x] **CRUD de Especialistas:** Gerenciamento completo dos perfis de parceiros, incluindo fotos e ordem de exibição.
- [x] **Gestão de Candidaturas:** Visualização e busca avançada de todas as candidaturas recebidas, com acesso ao perfil detalhado de cada pessoa.

---

## 📋 Como Rodar o Projeto Localmente

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/Kirah-Dev/honoriel-solucoes-site.git
    cd honoriel-solucoes-site
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    - Crie um arquivo `.env` dentro da pasta `backend/`.
    - Adicione as seguintes variáveis com seus valores (exemplo):
      ```
      DATABASE_URL="postgresql://user:password@host:port/database_name"
      SECRET_KEY="uma_chave_secreta_muito_longa_e_aleatoria"
      MAIL_USERNAME="seu_email@gmail.com"
      MAIL_PASSWORD="sua_senha_de_app_do_gmail"
      ```

5.  **Configure o banco de dados:**
    - Certifique-se de que o PostgreSQL está rodando e que o banco de dados especificado na `DATABASE_URL` existe.
    - Aplique as migrações:
      ```bash
      cd backend
      flask db upgrade
      ```

6.  **Crie o usuário administrador (se for a primeira vez):**
    ```bash
    flask create-admin
    ```

7.  **Inicie o servidor:**
    ```bash
    python app.py
    ```

O site estará disponível em `http://127.0.0.1:5000`.

---
```    *   **Importante:** Na linha `![Honoriel Logo](...)`, eu apontei para o caminho relativo da imagem do anjo. O GitHub deve conseguir exibi-la. Na linha `git clone ...`, não se esqueça de substituir `seu-usuario/honoriel-solucoes-site.git` pela URL real do seu repositório.