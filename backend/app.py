from flask import send_from_directory
from flask import send_from_directory
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Mail, Message
from dotenv import load_dotenv
import re # Para expressões regulares
from markupsafe import Markup, escape # Biblioteca de segurança do Jinja2
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import os

load_dotenv()

# --- CRIAÇÃO DO FILTRO NL2BR (VERSÃO MODERNA) ---
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

def nl2br(value):
    # Escapa o valor para segurança, depois processa
    escaped_value = escape(value)
    # Converte quebras de linha duplas em parágrafos e simples em <br>
    result = u'\n\n'.join(f'<p>{p.replace(chr(10), "<br>\\n")}</p>' for p in _paragraph_re.split(escaped_value))
    return Markup(result)

app = Flask(__name__, template_folder='../templates', static_folder='../static')

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Se um user não logado tentar acessar uma pág. protegida, será redirecionado para a rota 'login'
# login_manager.login_message = 'Por favor, faça o login para acessar esta página.'
# login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    """Redireciona usuários não autorizados para a página de login."""
    flash("Por favor, faça o login para acessar esta página.", "warning")
    return redirect(url_for('login'))

@app.cli.command("create-admin")
def create_admin():
    """Cria o usuário administrador inicial."""
    username = input("Digite o nome de usuário do admin: ")
    password = input("Digite a senha do admin: ")
    
    user_exists = User.query.filter_by(username=username).first()
    if user_exists:
        print(f"Usuário '{username}' já existe.")
        return

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    print(f"Usuário admin '{username}' criado com sucesso!")

# --- REGISTRA O FILTRO NO AMBIENTE JINJA2 ---
app.jinja_env.filters['nl2br'] = nl2br

# --- CONFIGURAÇÕES ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '#Honoriel123456'
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# --- CONFIGURAÇÕES DO FLASK-MAIL ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# Usa as variáveis de ambiente que carregamos do .env
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# --- CONFIGURAÇÕES DO BD DOS ESPECIALISTAS - Dicionário que mapeia áreas a ícones.
# A CHAVE é o que será salvo no banco, o VALOR é o nome amigável.
ESPECIALISTA_AREAS = {
    'psicologia': 'Psicologia',
    'direito': 'Direito',
    'desenvolvimento': 'Desenvolvimento',
    'medicina': 'Medicina',
    'nutricao': 'Nutrição',
    'financeiro': 'Finança',
    'contabilidade': 'Contabilidade', # Adicione mais áreas conforme necessário
    'outro': 'Outro'
}

# Dicionário que mapeia a chave da área para a classe do ícone.
AREA_ICONS = {
    'psicologia': 'fa-solid fa-brain',
    'direito': 'fa-solid fa-gavel',
    'desenvolvimento': 'fa-solid fa-code',
    'medicina': 'fa-solid fa-user-doctor',
    'nutricao': 'fa-solid fa-apple-whole',
    'financeiro': 'fa-solid fa-money-bill-trend-up',
    'contabilidade': 'fa-solid fa-calculator',
    'outro': 'fa-solid fa-handshake' # Ícone padrão
}


db = SQLAlchemy(app)
mail = Mail(app) # Inicializa a extensão Mail
migrate = Migrate(app, db)


# --- FIM DAS CONFIGURAÇÕES ---


# --- MODELS ---
class Pessoa(db.Model):
    __tablename__ = 'pessoa' # Nome da tabela no banco
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(150), nullable=False)
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    telefone1 = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    linkedin_url = db.Column(db.String(200))
    competencias_tecnicas = db.Column(db.Text)
    
    # NOVOS E ANTIGOS RELACIONAMENTOS ATUALIZADOS
    candidaturas = db.relationship('Candidatura', backref='pessoa', lazy=True, cascade="all, delete-orphan")
    formacoes = db.relationship('Formacao', backref='pessoa', lazy=True, cascade="all, delete-orphan")
    experiencias = db.relationship('Experiencia', backref='pessoa', lazy=True, cascade="all, delete-orphan")
    idiomas = db.relationship('Idioma', backref='pessoa', lazy=True, cascade="all, delete-orphan")
    cursos = db.relationship('Curso', backref='pessoa', lazy=True, cascade="all, delete-orphan")
    
class Candidatura(db.Model):
    __tablename__ = 'candidatura' # Nome da tabela no banco
    id = db.Column(db.Integer, primary_key=True)
    vaga_objetivo = db.Column(db.String(255), nullable=False)
    resumo_profissional = db.Column(db.Text)
    curriculo_pdf_path = db.Column(db.String(255))
    data_candidatura = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # A "ponte" que liga esta candidatura a uma pessoa
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)

class Formacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    curso = db.Column(db.String(150), nullable=False)
    instituicao = db.Column(db.String(150), nullable=False)
    ano_conclusao = db.Column(db.String(10))
    conclusao_prevista = db.Column(db.String(10))
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)

class Experiencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(150), nullable=False)
    cargo = db.Column(db.String(150), nullable=False)
    data_inicio = db.Column(db.String(20))
    data_fim = db.Column(db.String(20))
    atividades = db.Column(db.Text)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)

class Idioma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    nivel = db.Column(db.String(50), nullable=False)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)

class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    instituicao = db.Column(db.String(150))
    carga_horaria = db.Column(db.String(20))
    ano_conclusao = db.Column(db.String(10))
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    autor = db.Column(db.String(100), nullable=True, default='Equipe Honoriel')
    data_publicacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    imagem_destaque_path = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Post('{self.titulo}', '{self.data_publicacao}')"
    
# ===== NOVO MODELO PARA OS ESPECIALISTAS =====
class Especialista(db.Model):
    __tablename__ = 'especialista'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    foto_path = db.Column(db.String(255), nullable=True)
    
    bio_intro = db.Column(db.Text, nullable=True)     # "Especialista em gestão..."
    bio_lista_titulo = db.Column(db.String(255), nullable=True) # "Nossa expertise elimina..."
    bio_lista_itens = db.Column(db.Text, nullable=True) # Os itens da lista, um por linha
    bio_conclusao = db.Column(db.Text, nullable=True) # "Oferecemos um serviço..."

    contato_whatsapp = db.Column(db.String(50), nullable=True)
    contato_email = db.Column(db.String(150), nullable=True)
    contato_linkedin = db.Column(db.String(255), nullable=True) # Para a URL completa
    contato_instagram = db.Column(db.String(100), nullable=True) # Apenas para o @usuario
    contato_extra = db.Column(db.String(150), nullable=True) # "Atendimento a todo o Brasil"

    ativo = db.Column(db.Boolean, default=True, nullable=False)
    ordem = db.Column(db.Integer, default=0)
    
    area = db.Column(db.String(50), nullable=False, default='outro')

    def __repr__(self):
        return f'<Especialista {self.nome}>'
# ============================================

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"



# --- FUNÇÕES AUXILIARES ---
# (Sem alterações aqui)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


# --- ROTAS PÚBLICAS ---
@app.route('/')
def home():
    # BUSCA OS 3 POSTS MAIS RECENTES
    # Ordena por data de publicação em ordem decrescente e pega os 3 primeiros
    posts_recentes = Post.query.order_by(Post.data_publicacao.desc()).limit(3).all()
    
    # PASSA OS POSTS PARA O TEMPLATE
    return render_template('index.html', posts=posts_recentes)

@app.route('/empresas')
def empresas():
    especialistas = Especialista.query.filter_by(ativo=True).order_by(Especialista.ordem).all()
    # Envia a lista de especialistas E o dicionário de ícones para o template
    return render_template('empresas.html', especialistas=especialistas, area_icons=AREA_ICONS)

@app.route('/contato-empresa', methods=['POST'])
def contato_empresa():
    # Como este formulário só envia dados, ele só precisa do método 'POST'.
    if request.method == 'POST':
        # --- Pega os dados específicos deste formulário ---
        nome = request.form.get('nome')
        empresa = request.form.get('empresa')
        cnpj_cpf = request.form.get('cnpj_cpf')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        mensagem = request.form.get('mensagem')

        # Validação
        if not nome or not empresa or not email or not mensagem:
            flash('Todos os campos, exceto CPF/CNPJ e Telefone, são obrigatórios.', 'warning')
            # Redireciona de volta para a página de onde veio
            return redirect(url_for('empresas'))
        
        try:
            # Cria um e-mail com assunto e corpo específicos
            msg = Message(
                subject=f"Novo Contato de Empresa: {empresa}",
                sender=app.config['MAIL_USERNAME'],
                recipients=['wellensouza@gmail.com'] # E-mail da Renata
            )

            # Corpo do e-mail em formato HTML, com os campos corretos
            msg.html = f"""
                <h3>Nova Solicitação de Contato (Empresa) Recebida</h3>
                <p><strong>Nome do Contato:</strong> {nome}</p>
                <p><strong>Empresa:</strong> {empresa}</p>
                <p><strong>CPF/CNPJ:</strong> {cnpj_cpf}</p>
                <p><strong>E-mail:</strong> {email}</p>
                <p><strong>Telefone:</strong> {telefone}</p>
                <hr>
                <p><strong>Mensagem:</strong></p>
                <p>{mensagem.replace('\n', '<br>')}</p>
            """

            # Envia o e-mail
            mail.send(msg)

            flash('Sua solicitação foi enviada com sucesso! Nossa equipe entrará em contato em breve.', 'success')
            # Redireciona para a própria página de empresas, onde o usuário estava
            return redirect(url_for('empresas'))

        except Exception as e:
            print(f"ERRO AO ENVIAR E-MAIL (EMPRESA): {e}")
            flash('Ocorreu um erro ao tentar enviar sua solicitação. Por favor, tente novamente mais tarde.', 'danger')
            return redirect(url_for('empresas'))


@app.route('/candidatos')
def candidatos():
    return render_template('candidatos.html')

@app.route('/cadastro-curriculo/', methods=['GET', 'POST'])
def cadastro_curriculo():
    if request.method == 'POST':
        # 1. Validação de consentimento
        if not request.form.get('consent'):
            flash('Você precisa ler e aceitar os termos para continuar.', 'danger')
            return redirect(url_for('cadastro_curriculo'))

        email_enviado = request.form.get('email')
        
        try:
            # 2. Procura pela Pessoa usando o e-mail
            pessoa = Pessoa.query.filter_by(email=email_enviado).first()
            flash_message = ''

            if pessoa:
                # --- A: PESSOA JÁ EXISTE -> ATUALIZA O PERFIL ---
                flash_message = 'Seu perfil foi atualizado e sua nova candidatura foi registrada com sucesso!'
                
                # Atualiza todos os dados fixos da Pessoa com as informações mais recentes do formulário
                pessoa.nome_completo = request.form.get('nome_completo')
                pessoa.bairro = request.form.get('bairro')
                pessoa.cidade = request.form.get('cidade')
                pessoa.uf = request.form.get('uf')
                pessoa.telefone1 = request.form.get('telefone1')
                pessoa.linkedin_url = request.form.get('linkedin_url')
                pessoa.competencias_tecnicas = request.form.get('competencias_tecnicas')

                # Limpa as listas antigas para substituí-las pelas novas.
                # Isso garante que o perfil reflita exatamente o que foi enviado agora.
                pessoa.formacoes = []
                pessoa.experiencias = []
                pessoa.idiomas = []
                pessoa.cursos = []
                
            else:
                # --- B: PESSOA É NOVA -> CRIA O PERFIL ---
                flash_message = 'Sua candidatura foi enviada com sucesso! Boa sorte!'
                
                pessoa = Pessoa(
                    nome_completo=request.form.get('nome_completo'),
                    email=email_enviado,
                    bairro=request.form.get('bairro'),
                    cidade=request.form.get('cidade'),
                    uf=request.form.get('uf'),
                    telefone1=request.form.get('telefone1'),
                    linkedin_url=request.form.get('linkedin_url'),
                    competencias_tecnicas=request.form.get('competencias_tecnicas')
                )
                db.session.add(pessoa)

            # 3. LÓGICA COMUM (executada para pessoas novas E existentes)
            # Preenche/repreenche as listas de Formação, Experiência, etc.

            # Formações
            cursos_formacao = request.form.getlist('form_curso[]')
            for i in range(len(cursos_formacao)):
                nova_formacao = Formacao(
                    curso=cursos_formacao[i],
                    instituicao=request.form.getlist('form_instituicao[]')[i],
                    ano_conclusao=request.form.getlist('form_ano_conclusao[]')[i],
                    conclusao_prevista=request.form.getlist('form_conclusao_prevista[]')[i]
                )
                pessoa.formacoes.append(nova_formacao)

            # Experiências
            empresas_exp = request.form.getlist('exp_empresa[]')
            for i in range(len(empresas_exp)):
                nova_experiencia = Experiencia(
                    empresa=empresas_exp[i],
                    cargo=request.form.getlist('exp_cargo[]')[i],
                    data_inicio=request.form.getlist('exp_data_inicio[]')[i],
                    data_fim=request.form.getlist('exp_data_fim[]')[i],
                    atividades=request.form.getlist('exp_atividades[]')[i]
                )
                pessoa.experiencias.append(nova_experiencia)

            # Idiomas
            nomes_idioma = request.form.getlist('idioma_nome[]')
            for i in range(len(nomes_idioma)):
                novo_idioma = Idioma(
                    nome=nomes_idioma[i],
                    nivel=request.form.getlist('idioma_nivel[]')[i]
                )
                pessoa.idiomas.append(novo_idioma)

            # Cursos Complementares
            nomes_curso = request.form.getlist('curso_nome[]')
            for i in range(len(nomes_curso)):
                novo_curso = Curso(
                    nome=nomes_curso[i],
                    instituicao=request.form.getlist('curso_instituicao[]')[i],
                    carga_horaria=request.form.getlist('curso_carga_horaria[]')[i],
                    ano_conclusao=request.form.getlist('curso_ano_conclusao[]')[i]
                )
                pessoa.cursos.append(novo_curso)

            # 4. Cria a nova CANDIDATURA com os dados específicos da vaga
            nova_candidatura = Candidatura(
                vaga_objetivo=request.form.get('objetivo'),
                resumo_profissional=request.form.get('resumo_profissional'),
                pessoa=pessoa 
            )

            # Processa o upload do PDF para ESTA candidatura
            if 'curriculo_pdf' in request.files:
                file = request.files['curriculo_pdf']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Cria um nome de arquivo único para evitar conflitos
                    curriculo_filename = f"cv_{pessoa.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], curriculo_filename))
                    nova_candidatura.curriculo_pdf_path = curriculo_filename
            
            # 5. Salva tudo no banco de dados
            db.session.add(nova_candidatura)
            db.session.commit()

            # 6. Dispara a mensagem de sucesso e redireciona
            flash(flash_message, 'success')
            return redirect(url_for('cadastro_curriculo'))

        except Exception as e:
            db.session.rollback()
            print("="*50)
            print(f"ERRO NO CADASTRO/ATUALIZAÇÃO: {e}")
            import traceback
            traceback.print_exc()
            print("="*50)
            flash('Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente.', 'danger')
            return redirect(url_for('cadastro_curriculo'))
        
    return render_template('cadastro-curriculo.html')

@app.route('/servicos')
def servicos():
    return render_template('servicos.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

# ==================================================================
# INÍCIO DA MODIFICAÇÃO: Rota do Blog para Listagem de Posts
# ==================================================================
@app.route('/blog')
def blog_list():
    """
    Busca os posts de forma paginada e os exibe na página pública do blog.
    """
    try:
        # 1. Pega o número da página da URL (ex: /blog?page=2). Se não houver, o padrão é 1.
        page = request.args.get('page', 1, type=int)

        # 2. Em vez de .all(), usamos .paginate().
        #    - page=page: informa a página atual.
        #    - per_page=5: define quantos posts você quer por página. Altere este número como quiser.
        posts_pagination = Post.query.order_by(Post.data_publicacao.desc()).paginate(page=page, per_page=6)
        
        # 3. Passamos o objeto de paginação completo para o template.
        #    Ele contém não só os posts da página atual, mas também informações
        #    sobre outras páginas, total de posts, etc.
        return render_template('blog_list.html', pagination=posts_pagination)

    except Exception as e:
        flash('Não foi possível carregar os posts do blog. Tente novamente mais tarde.', 'warning')
        print(f"Erro ao buscar posts: {e}")
        return redirect(url_for('home'))
# ==================================================================
# FIM DA MODIFICAÇÃO
# ==================================================================

# ==================================================================
# INÍCIO ROTA: Página de Post Individual
# ==================================================================
@app.route('/blog/post/<int:post_id>')
def blog_post(post_id):
    """
    Busca um post específico pelo seu ID e exibe seu conteúdo completo.
    """
    try:
        post = Post.query.get_or_404(post_id)
        return render_template('blog_post.html', post=post)
    except Exception as e:
        flash('Post não encontrado ou ocorreu um erro.', 'danger')
        print(f"Erro ao buscar post individual: {e}") # Log do erro
        return redirect(url_for('blog_list'))
# ==================================================================
# FIM DA ROTA
# ==================================================================

# ==================================================================
# INÍCIO ROTA: Página de Contato
# ==================================================================
@app.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        assunto = request.form.get('assunto')
        mensagem = request.form.get('mensagem')

        if not nome or not email or not mensagem:
            flash('Nome, e-mail e mensagem são campos obrigatórios.', 'warning')
            return render_template('contato.html')
        
        try:
            # Cria o corpo do e-mail
            msg = Message(
                subject=f"Nova Mensagem de Contato de {nome}",
                sender=app.config['MAIL_USERNAME'], # O remetente é o seu e-mail configurado
                recipients=['wellensouza@gmail.com'] # O destinatário (e-mail da Renata)
            )

            # Corpo do e-mail em formato HTML para ficar mais bonito
            msg.html = f"""
                <h3>Nova Mensagem Recebida do Site Honoriel</h3>
                <p><strong>Nome:</strong> {nome}</p>
                <p><strong>E-mail:</strong> {email}</p>
                <p><strong>Telefone:</strong> {telefone}</p>
                <p><strong>Assunto:</strong> {assunto}</p>
                <hr>
                <p><strong>Mensagem:</strong></p>
                <p>{mensagem.replace('\n', '<br>')}</p>
            """

            # Envia o e-mail
            mail.send(msg)

            flash('Sua mensagem foi enviada com sucesso! Entraremos em contato em breve.', 'success')
            return redirect(url_for('contato'))

        except Exception as e:
            print(f"ERRO AO ENVIAR E-MAIL: {e}") # Loga o erro no terminal
            flash('Ocorreu um erro ao tentar enviar sua mensagem. Por favor, tente novamente mais tarde.', 'danger')
            return redirect(url_for('contato'))

    return render_template('contato.html')
# ==================================================================
# FIM DA ROTA
# ==================================================================

# ==================================================================
# INICIO DA ROTA: Termos Legais
# ==================================================================

@app.route('/politica-de-privacidade')
def politica_privacidade():
    return render_template('politica_privacidade.html') # Supondo que você criará este template

@app.route('/termos-de-uso')
def termos_de_uso():
# Vamos unificar a Isenção de Responsabilidade aqui
    return render_template('termos_de_uso.html')

@app.route('/termo-dos-parceiros')
def termos_parceiros():
    # Esta rota renderiza o template 'termos_parceiros.html'
    return render_template('termo_parceiros.html')

@app.route('/codigo-de-etica')
def codigo_de_etica():
    return render_template('codigo-de-etica.html') # Supondo que você criará este template
# ==================================================================
# FIM DA ROTA
# ==================================================================

# ==================================================================
# INICIO DA ROTA: ADMINISTRAÇÃO
# ==================================================================
@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # =================================================================
    #   LINHA DE LIMPEZA: Consome e descarta quaisquer mensagens antigas
    # =================================================================
    get_flashed_messages() 
    # =================================================================

    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
        else:
            flash('Login falhou. Verifique o usuário e a senha.', 'danger')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
@login_required # Garante que apenas usuários logados possam acessar esta rota
def logout():
    logout_user() # Função do Flask-Login para deslogar o usuário
    flash('Você foi desconectado com segurança.', 'success')
    return redirect(url_for('login')) # Redireciona para a página de login


# --- ADMIN CANDIDATOS ---
@app.route('/admin/candidatos')
@login_required
def admin_candidatos():
    # A lógica de busca que implementamos antes já funciona com esta nova estrutura!
    filtro_por = request.args.get('filtro_por', 'pessoa')
    termo_busca = request.args.get('termo_busca', '')

    query = Candidatura.query # A consulta base agora é em Candidatura

    if termo_busca:
        if filtro_por == 'candidatura':
            query = query.filter(Candidatura.vaga_objetivo.ilike(f'%{termo_busca}%'))
        elif filtro_por == 'pessoa':
            query = query.join(Pessoa).filter(
                or_(
                    Pessoa.nome_completo.ilike(f'%{termo_busca}%'),
                    Pessoa.email.ilike(f'%{termo_busca}%')
                )
            )
    
    # A variável agora contém candidaturas, não pessoas/candidatos
    todas_as_candidaturas = query.order_by(Candidatura.data_candidatura.desc()).all()
    return render_template('admin_candidatos.html', candidaturas=todas_as_candidaturas)


@app.route('/pessoa/<int:pessoa_id>') # Rota agora por ID da Pessoa
@login_required
def detalhe_candidato(pessoa_id):
    # Busca a Pessoa para ver o perfil completo
    pessoa = Pessoa.query.get_or_404(pessoa_id)
    
    # --- LÓGICA ADICIONADA ---
    # Busca a candidatura mais recente daquela pessoa
    candidatura_recente = Candidatura.query.filter_by(pessoa_id=pessoa.id).order_by(Candidatura.data_candidatura.desc()).first()
    
    # Passa AMBAS as variáveis para o template
    return render_template('detalhe_candidato.html', pessoa=pessoa, candidatura_recente=candidatura_recente)


@app.route('/candidatura/excluir/<int:candidatura_id>', methods=['POST'])
@login_required
def excluir_candidatura(candidatura_id):
    # Agora excluímos uma candidatura específica, não o perfil inteiro
    candidatura_para_excluir = Candidatura.query.get_or_404(candidatura_id)
    try:
        # Apaga o PDF se existir
        if candidatura_para_excluir.curriculo_pdf_path:
            caminho_do_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], candidatura_para_excluir.curriculo_pdf_path)
            if os.path.exists(caminho_do_arquivo):
                os.remove(caminho_do_arquivo)
        
        db.session.delete(candidatura_para_excluir)
        db.session.commit()
        flash('Candidatura excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao excluir a candidatura: {e}', 'danger')
    return redirect(url_for('admin_candidatos'))


# --- ADMIN ESPECIALISTAS (CRUD COMPLETO) ---

@app.route('/admin/especialistas')
@login_required
def admin_especialistas_list():
    """Exibe a lista de todos os especialistas cadastrados."""
    try:
        especialistas = Especialista.query.order_by(Especialista.ordem, Especialista.nome).all()
        return render_template('admin_especialistas_list.html', especialistas=especialistas)
    except Exception as e:
        print(f"Erro ao carregar especialistas: {e}")
        flash('Erro ao carregar a lista de especialistas. Verifique o banco de dados.', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/especialistas/novo', methods=['GET', 'POST'])
@login_required
def admin_especialistas_novo():
    if request.method == 'POST':
        try:
            # Pega todos os dados dos campos do formulário
            nome = request.form.get('nome')
            titulo = request.form.get('titulo')
            bio_intro = request.form.get('bio_intro')
            bio_lista_titulo = request.form.get('bio_lista_titulo')
            bio_lista_itens = request.form.get('bio_lista_itens')
            bio_conclusao = request.form.get('bio_conclusao')
            contato_whatsapp = request.form.get('contato_whatsapp')
            contato_email = request.form.get('contato_email')
            contato_extra = request.form.get('contato_extra')
            ordem = request.form.get('ordem', 0, type=int)
            ativo = 'ativo' in request.form

            # Validação básica
            if not nome or not titulo:
                flash('Nome e Título são campos obrigatórios.', 'warning')
                return render_template('admin_especialistas_form.html', title="Adicionar Novo Especialista", especialista=request.form)

            # Lógica para salvar a foto
            foto_filename = None
            if 'foto' in request.files:
                file = request.files['foto']
                if file and file.filename and allowed_image_file(file.filename):
                    filename = secure_filename(file.filename)
                    foto_filename = f"especialista_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))

            # Cria o novo objeto Especialista com todos os campos
            novo_especialista = Especialista(
                area=request.form.get('area'),
                nome=nome,
                titulo=titulo,
                bio_intro=bio_intro,
                bio_lista_titulo=bio_lista_titulo,
                bio_lista_itens=bio_lista_itens,
                bio_conclusao=bio_conclusao,
                contato_whatsapp=contato_whatsapp,
                contato_email=contato_email,
                contato_linkedin=request.form.get('contato_linkedin'),   
                contato_instagram=request.form.get('contato_instagram'), 
                contato_extra=contato_extra,
                ordem=ordem,
                ativo=ativo,
                foto_path=foto_filename
            )
            
            db.session.add(novo_especialista)
            db.session.commit()
            flash('Novo especialista adicionado com sucesso!', 'success')
            return redirect(url_for('admin_especialistas_list'))

        except Exception as e:
            db.session.rollback()
            print(f"ERRO AO CRIAR ESPECIALISTA: {e}")
            flash('Ocorreu um erro ao criar o especialista. Verifique o terminal para detalhes.', 'danger')
            return redirect(url_for('admin_especialistas_novo'))
    
    return render_template('admin_especialistas_form.html', title="Adicionar Novo Especialista", areas=ESPECIALISTA_AREAS)


@app.route('/admin/especialistas/editar/<int:especialista_id>', methods=['GET', 'POST'])
@login_required
def admin_especialistas_editar(especialista_id):
    especialista = Especialista.query.get_or_404(especialista_id)
    if request.method == 'POST':
        try:
            # Atualiza todos os campos do objeto 'especialista' com os dados do formulário
            especialista.area = request.form.get('area')
            especialista.nome = request.form.get('nome')
            especialista.titulo = request.form.get('titulo')
            especialista.bio_intro = request.form.get('bio_intro')
            especialista.bio_lista_titulo = request.form.get('bio_lista_titulo')
            especialista.bio_lista_itens = request.form.get('bio_lista_itens')
            especialista.bio_conclusao = request.form.get('bio_conclusao')
            especialista.contato_whatsapp = request.form.get('contato_whatsapp')
            especialista.contato_email = request.form.get('contato_email')
            especialista.contato_linkedin = request.form.get('contato_linkedin')
            especialista.contato_instagram = request.form.get('contato_instagram')
            especialista.contato_extra = request.form.get('contato_extra')
            especialista.ordem = request.form.get('ordem', 0, type=int)
            especialista.ativo = 'ativo' in request.form

            # Lógica para atualizar a foto
            if 'foto' in request.files:
                file = request.files['foto']
                if file and file.filename and allowed_image_file(file.filename):
                    # Apaga a foto antiga do disco se ela existir
                    if especialista.foto_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], especialista.foto_path)):
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], especialista.foto_path))
                    
                    # Salva a nova foto e atualiza o caminho no banco
                    filename = secure_filename(file.filename)
                    foto_filename = f"especialista_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
                    especialista.foto_path = foto_filename
            
            db.session.commit()
            flash('Especialista atualizado com sucesso!', 'success')
            return redirect(url_for('admin_especialistas_list'))

        except Exception as e:
            db.session.rollback()
            print(f"ERRO AO EDITAR ESPECIALISTA: {e}")
            flash('Ocorreu um erro ao atualizar o especialista. Verifique o terminal para detalhes.', 'danger')
            return redirect(url_for('admin_especialistas_editar', especialista_id=especialista.id))

    return render_template('admin_especialistas_form.html', title="Editar Especialista", especialista=especialista, areas=ESPECIALISTA_AREAS)

@app.route('/admin/especialistas/excluir/<int:especialista_id>', methods=['POST'])
@login_required
def admin_especialistas_excluir(especialista_id):
    """Processa a exclusão de um especialista."""
    especialista = Especialista.query.get_or_404(especialista_id)
    try:
        if especialista.foto_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], especialista.foto_path)):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], especialista.foto_path))
        
        db.session.delete(especialista)
        db.session.commit()
        flash('Especialista excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao excluir o especialista: {e}', 'danger')
    
    return redirect(url_for('admin_especialistas_list'))

# --- ADMIN BLOG ---
@app.route('/admin/blog')
@login_required
def admin_blog_list():
    posts = Post.query.order_by(Post.data_publicacao.desc()).all()
    return render_template('admin_blog_list.html', posts=posts)

@app.route('/admin/blog/novo', methods=['GET', 'POST'])
def admin_blog_novo():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        conteudo = request.form.get('conteudo')
        autor = request.form.get('autor')
        if not titulo or not conteudo:
            flash('Título e Conteúdo são campos obrigatórios.', 'warning')
            return render_template('admin_blog_form.html', titulo=titulo, conteudo=conteudo, autor=autor)
        imagem_filename = None
        if 'imagem_destaque' in request.files:
            file = request.files['imagem_destaque']
            if file and file.filename and allowed_image_file(file.filename):
                filename = secure_filename(file.filename)
                imagem_filename = f"post_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                caminho_para_salvar = os.path.join(app.config['UPLOAD_FOLDER'], imagem_filename)
                file.save(caminho_para_salvar)
        novo_post = Post(titulo=titulo, conteudo=conteudo, autor=autor, imagem_destaque_path=imagem_filename)
        try:
            db.session.add(novo_post)
            db.session.commit()
            flash('Novo post criado com sucesso!', 'success')
            return redirect(url_for('admin_blog_list'))
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro interno. Verifique o terminal do servidor para detalhes.', 'danger')
            return redirect(url_for('admin_blog_novo'))
    return render_template('admin_blog_form.html')

@app.route('/admin/blog/editar/<int:post_id>', methods=['GET', 'POST'])
@login_required
def admin_blog_editar(post_id):
    post_para_editar = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post_para_editar.titulo = request.form.get('titulo')
        post_para_editar.conteudo = request.form.get('conteudo')
        post_para_editar.autor = request.form.get('autor')
        if 'imagem_destaque' in request.files:
            file = request.files['imagem_destaque']
            if file and file.filename and allowed_image_file(file.filename):
                if post_para_editar.imagem_destaque_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], post_para_editar.imagem_destaque_path)):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post_para_editar.imagem_destaque_path))
                filename = secure_filename(file.filename)
                imagem_filename = f"post_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                caminho_para_salvar = os.path.join(app.config['UPLOAD_FOLDER'], imagem_filename)
                file.save(caminho_para_salvar)
                post_para_editar.imagem_destaque_path = imagem_filename
        try:
            db.session.commit()
            flash('Post atualizado com sucesso!', 'success')
            return redirect(url_for('admin_blog_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar o post: {e}', 'danger')
    return render_template('admin_blog_form.html', post=post_para_editar)

@app.route('/admin/blog/excluir/<int:post_id>', methods=['POST'])
@login_required
def admin_blog_excluir(post_id):
    post_para_excluir = Post.query.get_or_404(post_id)
    try:
        if post_para_excluir.imagem_destaque_path:
            caminho_do_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], post_para_excluir.imagem_destaque_path)
            if os.path.exists(caminho_do_arquivo):
                os.remove(caminho_do_arquivo)
        db.session.delete(post_para_excluir)
        db.session.commit()
        flash('Post excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao excluir o post: {e}', 'danger')
    return redirect(url_for('admin_blog_list'))
# ==================================================================
# FIM DA ROTA
# ==================================================================

# --- ROTAS PARA SERVIR ARQUIVOS ---
@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/uploads/view/<path:filename>')
def view_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# --- TERMOS LEGAIS ---

# @app.route('/politica-de-privacidade')
# def politica_privacidade():
#     return render_template('politica_privacidade.html')

# @app.route('/termos-de-uso')
# def termos_de_uso():
#     # Vamos unificar a Isenção de Responsabilidade aqui
#     return render_template('termos_de_uso.html')

# # O Código de Ética já deve ter uma rota similar
# @app.route('/codigo-de-etica')
# def codigo_de_etica():
#     return render_template('codigo_de_etica.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)