"""Modelo de dados multi-tenant da Plataforma LGPD.

Conceitos centrais:
  - Empresa  ........ o *tenant*. Tudo é escopado por empresa_id.
  - Usuario  ........ pessoa que loga (papéis: encarregado / gestor / colaborador).
  - Setor    ........ unidade da empresa (RH, Financeiro, ...), mapeada a uma ÁREA
                      canônica para reaproveitar o conteúdo curado.
  - Trilha / Questao  conteúdo educacional e banco de questões, chaveados por ÁREA.
                      Quando empresa_id é NULL = biblioteca global (curada por nós);
                      quando preenchido = conteúdo próprio daquele tenant.
  - Prova / ProvaItem  uma aplicação de avaliação + as questões sorteadas.
  - Certificado ..... emitido quando a prova é aprovada; tem validade e código.
"""
import secrets
from datetime import datetime, timedelta

from flask_login import UserMixin
from sqlalchemy import false, text
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from utils import agora_utc

# ── Áreas canônicas ────────────────────────────────────────────────────────
# Desacoplam o conteúdo curado dos setores específicos de cada empresa: a área
# "RH" serve tanto para um setor chamado "Recursos Humanos" quanto "Gente e Gestão".
AREAS = [
    ("RH", "Recursos Humanos"),
    ("FINANCEIRO", "Financeiro"),
    ("MARKETING", "Marketing e Vendas"),
    ("TI", "TI e Segurança da Informação"),
    ("ATENDIMENTO", "Atendimento e SAC"),
    ("JURIDICO", "Jurídico e Compras"),
    ("GERAL", "Geral (toda a empresa)"),
]
AREA_CODES = [code for code, _ in AREAS]
AREA_LABELS = dict(AREAS)


def label_area(code: str) -> str:
    return AREA_LABELS.get(code, code)


# ── Dimensões do diagnóstico de maturidade em privacidade ───────────────────
DIMENSOES = [
    ("GOVERNANCA", "Governança e cultura"),
    ("BASES_LEGAIS", "Bases legais e finalidade"),
    ("SEGURANCA", "Segurança da informação"),
    ("DIREITOS", "Direitos do titular"),
    ("INCIDENTES", "Resposta a incidentes"),
]
DIM_LABELS = dict(DIMENSOES)


def label_dimensao(code: str) -> str:
    return DIM_LABELS.get(code, code)


# ── Bases legais (Art. 7º e 11) — usadas no ROPA ────────────────────────────
BASES_LEGAIS = [
    ("CONSENTIMENTO", "Consentimento (Art. 7º, I)"),
    ("OBRIGACAO_LEGAL", "Obrigação legal/regulatória (Art. 7º, II)"),
    ("CONTRATO", "Execução de contrato (Art. 7º, V)"),
    ("LEGITIMO_INTERESSE", "Legítimo interesse (Art. 7º, IX)"),
    ("PROTECAO_CREDITO", "Proteção ao crédito (Art. 7º, X)"),
    ("EXERCICIO_DIREITOS", "Exercício de direitos em processo (Art. 7º, VI)"),
    ("PROTECAO_VIDA", "Proteção da vida (Art. 7º, VII)"),
    ("TUTELA_SAUDE", "Tutela da saúde (Art. 7º, VIII)"),
    ("DADO_SENSIVEL", "Hipótese de dado sensível (Art. 11)"),
]
BASE_LEGAL_LABELS = dict(BASES_LEGAIS)


def label_base_legal(code: str) -> str:
    return BASE_LEGAL_LABELS.get(code, code)


# ── Direitos do titular (Art. 18) e status dos pedidos ──────────────────────
TIPOS_DIREITO = [
    ("CONFIRMACAO", "Confirmação de tratamento (Art. 18, I)"),
    ("ACESSO", "Acesso aos dados (Art. 18, II)"),
    ("CORRECAO", "Correção (Art. 18, III)"),
    ("ANONIMIZACAO", "Anonimização/bloqueio (Art. 18, IV)"),
    ("PORTABILIDADE", "Portabilidade (Art. 18, V)"),
    ("ELIMINACAO", "Eliminação de dados consentidos (Art. 18, VI)"),
    ("INFO_COMPARTILHAMENTO", "Informação sobre compartilhamento (Art. 18, VII)"),
    ("REVOGACAO", "Revogação do consentimento (Art. 18, IX)"),
]
TIPO_DIREITO_LABELS = dict(TIPOS_DIREITO)

STATUS_PEDIDO = [
    ("recebido", "Recebido"),
    ("em_andamento", "Em andamento"),
    ("concluido", "Concluído"),
    ("recusado", "Recusado"),
]
STATUS_PEDIDO_LABELS = dict(STATUS_PEDIDO)


def label_tipo_direito(code: str) -> str:
    return TIPO_DIREITO_LABELS.get(code, code)


def label_status_pedido(code: str) -> str:
    return STATUS_PEDIDO_LABELS.get(code, code)


# ── Risco (RIPD/incidentes) e status de incidentes ──────────────────────────
RISCO_NIVEIS = [("baixo", "Baixo"), ("medio", "Médio"), ("alto", "Alto")]
RISCO_LABELS = dict(RISCO_NIVEIS)

STATUS_INCIDENTE = [("aberto", "Aberto"), ("em_tratamento", "Em tratamento"), ("encerrado", "Encerrado")]
STATUS_INCIDENTE_LABELS = dict(STATUS_INCIDENTE)


def label_risco(code: str) -> str:
    return RISCO_LABELS.get(code, code or "—")


def label_status_incidente(code: str) -> str:
    return STATUS_INCIDENTE_LABELS.get(code, code)


def nivel_risco_de(valor: int) -> str:
    """Mapeia probabilidade × impacto (1–9) para baixo/médio/alto."""
    if valor <= 2:
        return "baixo"
    if valor <= 4:
        return "medio"
    return "alto"


# ── Papéis ──────────────────────────────────────────────────────────────────
PAPEL_ENCARREGADO = "encarregado"  # DPO: administra toda a empresa
PAPEL_GESTOR = "gestor"            # responsável por um setor
PAPEL_COLABORADOR = "colaborador"  # faz trilhas e provas
PAPEIS = [PAPEL_ENCARREGADO, PAPEL_GESTOR, PAPEL_COLABORADOR]
PAPEL_LABELS = {
    PAPEL_ENCARREGADO: "Encarregado (DPO)",
    PAPEL_GESTOR: "Gestor de setor",
    PAPEL_COLABORADOR: "Colaborador",
}


class Empresa(db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(160), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    mfa_obrigatorio = db.Column(db.Boolean, default=False, nullable=False, server_default=false())
    email_remetente = db.Column(db.String(255))  # remetente das notificações; None = MAIL_FROM
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)

    setores = db.relationship("Setor", back_populates="empresa", cascade="all, delete-orphan")
    usuarios = db.relationship("Usuario", back_populates="empresa", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Empresa {self.slug}>"


class Setor(db.Model):
    __tablename__ = "setores"
    __table_args__ = (db.UniqueConstraint("empresa_id", "slug", name="uq_setor_empresa_slug"),)

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    nome = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), nullable=False)
    area = db.Column(db.String(20), nullable=False, default="GERAL")
    descricao = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)

    empresa = db.relationship("Empresa", back_populates="setores")
    usuarios = db.relationship("Usuario", back_populates="setor")

    @property
    def area_label(self):
        return label_area(self.area)

    def __repr__(self):
        return f"<Setor {self.slug} area={self.area}>"


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    setor_id = db.Column(db.Integer, db.ForeignKey("setores.id"), nullable=True, index=True)
    nome = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    papel = db.Column(db.String(20), nullable=False, default=PAPEL_COLABORADOR)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)
    ultimo_login = db.Column(db.DateTime)

    # 2FA (TOTP)
    totp_secret = db.Column(db.String(64))
    mfa_ativo = db.Column(db.Boolean, default=False, nullable=False, server_default=false())
    # Bloqueio por tentativas de login
    tentativas_falhas = db.Column(db.Integer, default=0, nullable=False, server_default=text("0"))
    bloqueado_ate = db.Column(db.DateTime)
    # Quando o usuário foi anonimizado (nome/e-mail removidos; histórico estatístico mantido).
    anonimizado_em = db.Column(db.DateTime)

    empresa = db.relationship("Empresa", back_populates="usuarios")
    setor = db.relationship("Setor", back_populates="usuarios")
    provas = db.relationship("Prova", back_populates="usuario", cascade="all, delete-orphan")
    certificados = db.relationship("Certificado", back_populates="usuario", cascade="all, delete-orphan")
    recovery_codes = db.relationship("RecoveryCode", cascade="all, delete-orphan", backref="usuario")

    # -- senha --
    def definir_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def conferir_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)

    # -- papéis --
    @property
    def is_encarregado(self):
        return self.papel == PAPEL_ENCARREGADO

    @property
    def is_gestor(self):
        return self.papel == PAPEL_GESTOR

    @property
    def is_colaborador(self):
        return self.papel == PAPEL_COLABORADOR

    @property
    def papel_label(self):
        return PAPEL_LABELS.get(self.papel, self.papel)

    @property
    def esta_bloqueado(self):
        return self.bloqueado_ate is not None and agora_utc() < self.bloqueado_ate

    def __repr__(self):
        return f"<Usuario {self.email} ({self.papel})>"


class Trilha(db.Model):
    """Conteúdo educacional em Markdown, chaveado por área."""
    __tablename__ = "trilhas"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    area = db.Column(db.String(20), nullable=False, index=True)
    titulo = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(120), nullable=False, index=True)
    resumo = db.Column(db.String(300))
    conteudo_md = db.Column(db.Text, nullable=False, default="")
    ordem = db.Column(db.Integer, default=0, nullable=False)
    publicada = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=agora_utc, onupdate=agora_utc)

    @property
    def area_label(self):
        return label_area(self.area)

    def __repr__(self):
        return f"<Trilha {self.slug} area={self.area}>"


class Questao(db.Model):
    """Questão de múltipla escolha do banco curado, ancorada em um artigo da lei."""
    __tablename__ = "questoes"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    area = db.Column(db.String(20), nullable=False, index=True)
    enunciado = db.Column(db.Text, nullable=False)
    artigo = db.Column(db.String(120))         # ex.: "Art. 7º" / "Art. 18"
    explicacao = db.Column(db.Text)            # mostrada na correção
    dificuldade = db.Column(db.Integer, default=1, nullable=False)  # 1=fácil 2=média 3=difícil
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)

    alternativas = db.relationship(
        "Alternativa", back_populates="questao",
        cascade="all, delete-orphan", order_by="Alternativa.ordem",
    )

    @property
    def area_label(self):
        return label_area(self.area)

    def __repr__(self):
        return f"<Questao {self.id} area={self.area}>"


class Alternativa(db.Model):
    __tablename__ = "alternativas"

    id = db.Column(db.Integer, primary_key=True)
    questao_id = db.Column(db.Integer, db.ForeignKey("questoes.id"), nullable=False, index=True)
    texto = db.Column(db.String(500), nullable=False)
    correta = db.Column(db.Boolean, default=False, nullable=False)
    ordem = db.Column(db.Integer, default=0, nullable=False)

    questao = db.relationship("Questao", back_populates="alternativas")

    def __repr__(self):
        return f"<Alternativa {self.id} correta={self.correta}>"


class Prova(db.Model):
    """Uma aplicação de avaliação para um colaborador, em um setor/área."""
    __tablename__ = "provas"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    setor_id = db.Column(db.Integer, db.ForeignKey("setores.id"), nullable=True, index=True)
    area = db.Column(db.String(20), nullable=False)
    nota_corte = db.Column(db.Integer, nullable=False, default=70)
    nota = db.Column(db.Float)
    aprovado = db.Column(db.Boolean)
    status = db.Column(db.String(20), nullable=False, default="em_andamento")  # em_andamento / concluida
    tempo_limite_min = db.Column(db.Integer)  # None = sem limite
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)
    finalizado_em = db.Column(db.DateTime)

    usuario = db.relationship("Usuario", back_populates="provas")
    setor = db.relationship("Setor")
    itens = db.relationship(
        "ProvaItem", back_populates="prova",
        cascade="all, delete-orphan", order_by="ProvaItem.ordem",
    )
    certificado = db.relationship("Certificado", back_populates="prova", uselist=False)

    @property
    def area_label(self):
        return label_area(self.area)

    @property
    def total_questoes(self):
        return len(self.itens)

    @property
    def acertos(self):
        return sum(1 for i in self.itens if i.correta)

    @property
    def expira_em(self):
        if not self.tempo_limite_min:
            return None
        return self.criado_em + timedelta(minutes=self.tempo_limite_min)

    def __repr__(self):
        return f"<Prova {self.id} status={self.status} nota={self.nota}>"


class ProvaItem(db.Model):
    """Questão sorteada para uma prova + a resposta dada.

    ``ordem_alternativas`` guarda a ordem embaralhada dos ids das alternativas,
    para que a apresentação seja estável entre o carregamento e o envio.
    """
    __tablename__ = "prova_itens"

    id = db.Column(db.Integer, primary_key=True)
    prova_id = db.Column(db.Integer, db.ForeignKey("provas.id"), nullable=False, index=True)
    questao_id = db.Column(db.Integer, db.ForeignKey("questoes.id"), nullable=False)
    ordem = db.Column(db.Integer, default=0, nullable=False)
    ordem_alternativas = db.Column(db.String(120))  # ex.: "12,9,15,10"
    alternativa_escolhida_id = db.Column(db.Integer, db.ForeignKey("alternativas.id"))
    correta = db.Column(db.Boolean)

    prova = db.relationship("Prova", back_populates="itens")
    questao = db.relationship("Questao")
    alternativa_escolhida = db.relationship("Alternativa")

    def alternativas_ordenadas(self):
        """Alternativas na ordem embaralhada armazenada."""
        if not self.ordem_alternativas:
            return list(self.questao.alternativas)
        ids = [int(x) for x in self.ordem_alternativas.split(",") if x]
        por_id = {a.id: a for a in self.questao.alternativas}
        return [por_id[i] for i in ids if i in por_id]


class Certificado(db.Model):
    __tablename__ = "certificados"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    prova_id = db.Column(db.Integer, db.ForeignKey("provas.id"), nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey("setores.id"), nullable=True)
    area = db.Column(db.String(20), nullable=False)
    codigo = db.Column(db.String(40), unique=True, nullable=False, index=True)
    nota = db.Column(db.Float, nullable=False)
    emitido_em = db.Column(db.DateTime, default=agora_utc, nullable=False)
    valido_ate = db.Column(db.DateTime, nullable=False)

    usuario = db.relationship("Usuario", back_populates="certificados")
    prova = db.relationship("Prova", back_populates="certificado")
    setor = db.relationship("Setor")

    @property
    def area_label(self):
        return label_area(self.area)

    @property
    def valido(self):
        return agora_utc() <= self.valido_ate

    @property
    def dias_para_vencer(self):
        return (self.valido_ate - agora_utc()).days

    @staticmethod
    def validade_padrao(dias: int) -> datetime:
        return agora_utc() + timedelta(days=dias)

    def __repr__(self):
        return f"<Certificado {self.codigo} valido={self.valido}>"


# ── Diagnóstico de maturidade em privacidade (fase 2) ───────────────────────
class DiagnosticoPergunta(db.Model):
    """Afirmação avaliada numa escala 0 (não) / 1 (parcial) / 2 (sim)."""
    __tablename__ = "diagnostico_perguntas"

    id = db.Column(db.Integer, primary_key=True)
    dimensao = db.Column(db.String(20), nullable=False, index=True)
    texto = db.Column(db.Text, nullable=False)
    peso = db.Column(db.Integer, default=1, nullable=False)
    ordem = db.Column(db.Integer, default=0, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    @property
    def dimensao_label(self):
        return label_dimensao(self.dimensao)


class Diagnostico(db.Model):
    __tablename__ = "diagnosticos"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    setor_id = db.Column(db.Integer, db.ForeignKey("setores.id"), nullable=True, index=True)
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)
    finalizado_em = db.Column(db.DateTime)
    score = db.Column(db.Float)
    nivel = db.Column(db.String(40))
    status = db.Column(db.String(20), nullable=False, default="em_andamento")

    usuario = db.relationship("Usuario")
    setor = db.relationship("Setor")
    respostas = db.relationship(
        "DiagnosticoResposta", back_populates="diagnostico", cascade="all, delete-orphan",
    )

    @property
    def setor_label(self):
        return self.setor.nome if self.setor else "Empresa toda"


class DiagnosticoResposta(db.Model):
    __tablename__ = "diagnostico_respostas"

    id = db.Column(db.Integer, primary_key=True)
    diagnostico_id = db.Column(db.Integer, db.ForeignKey("diagnosticos.id"), nullable=False, index=True)
    pergunta_id = db.Column(db.Integer, db.ForeignKey("diagnostico_perguntas.id"), nullable=False)
    valor = db.Column(db.Integer, nullable=False, default=0)  # 0, 1 ou 2

    diagnostico = db.relationship("Diagnostico", back_populates="respostas")
    pergunta = db.relationship("DiagnosticoPergunta")


# ── Trilha de auditoria (fase 4 — segurança/accountability) ─────────────────
class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True, index=True)
    acao = db.Column(db.String(120), nullable=False)
    detalhe = db.Column(db.String(255))
    ip = db.Column(db.String(45))
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False, index=True)
    # SHA-256 deste registro encadeado ao anterior — adulteração quebra a cadeia
    # (conferível com `flask auditoria-verificar`). None = registro anterior à cadeia.
    hash = db.Column(db.String(64))

    usuario = db.relationship("Usuario")


class RecoveryCode(db.Model):
    """Código de recuperação de uso único para o 2FA."""
    __tablename__ = "recovery_codes"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    code_hash = db.Column(db.String(255), nullable=False)
    usado = db.Column(db.Boolean, default=False, nullable=False, server_default=false())
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)


# ── Caixa de saída de e-mails ───────────────────────────────────────────────
class EmailEnviado(db.Model):
    """Cópia de todo e-mail que a plataforma tentou enviar.

    Em modo dry-run (sem MAIL_SERVER) é a única forma de *ver* as notificações —
    reset de senha, reavaliações, pedidos — o que torna a demo demonstrável sem
    SMTP. Com SMTP real, vira histórico de envios (``enviado`` = entregue ao servidor).
    """
    __tablename__ = "emails_enviados"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    remetente = db.Column(db.String(255))
    destinatario = db.Column(db.String(255), nullable=False)
    assunto = db.Column(db.String(255), nullable=False)
    corpo = db.Column(db.Text)
    enviado = db.Column(db.Boolean, default=False, nullable=False, server_default=false())
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False, index=True)


# ── Anexos (evidências) de RIPD, incidente e pedido do titular ──────────────
class Anexo(db.Model):
    """Arquivo anexado como evidência (contrato com operador, print, resposta enviada...).

    O binário fica em disco (ANEXOS_DIR ou instance/uploads/<empresa_id>/), fora do
    git; aqui só os metadados. ``alvo_tipo``/``alvo_id`` apontam para o registro dono.
    """
    __tablename__ = "anexos"
    __table_args__ = (db.Index("ix_anexos_alvo", "empresa_id", "alvo_tipo", "alvo_id"),)

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    alvo_tipo = db.Column(db.String(20), nullable=False)   # ripd / incidente / pedido
    alvo_id = db.Column(db.Integer, nullable=False)
    nome_original = db.Column(db.String(255), nullable=False)
    nome_arquivo = db.Column(db.String(80), nullable=False)  # uuid + extensão, no disco
    mime = db.Column(db.String(100))
    tamanho = db.Column(db.Integer)
    enviado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)

    enviado_por = db.relationship("Usuario")


# ── ROPA — Registro das operações de tratamento (Art. 37) ───────────────────
class RopaRegistro(db.Model):
    __tablename__ = "ropa_registros"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    setor_id = db.Column(db.Integer, db.ForeignKey("setores.id"), nullable=True, index=True)
    atividade = db.Column(db.String(200), nullable=False)
    titulares = db.Column(db.String(255))          # ex.: colaboradores, clientes
    categorias_dados = db.Column(db.Text)          # quais dados são tratados
    finalidade = db.Column(db.Text)
    base_legal = db.Column(db.String(40))
    retencao = db.Column(db.String(255))
    compartilhamento = db.Column(db.Text)          # com quem se compartilha
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=agora_utc, onupdate=agora_utc)

    setor = db.relationship("Setor")

    @property
    def setor_label(self):
        return self.setor.nome if self.setor else "Toda a empresa"

    @property
    def base_legal_label(self):
        return label_base_legal(self.base_legal) if self.base_legal else "—"


# ── Pedidos do titular (Art. 18) ────────────────────────────────────────────
class PedidoTitular(db.Model):
    __tablename__ = "pedidos_titular"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    nome_titular = db.Column(db.String(160), nullable=False)
    contato = db.Column(db.String(255))
    tipo = db.Column(db.String(40), nullable=False)
    descricao = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="recebido")
    responsavel_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)
    prazo = db.Column(db.DateTime)
    concluido_em = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)
    # Protocolo público (ex.: LGPD-3F9A21C0): o titular acompanha o pedido sem login.
    protocolo = db.Column(db.String(20), unique=True, index=True)
    origem = db.Column(db.String(20))  # "portal" (aberto pelo titular) ou "interno"

    responsavel = db.relationship("Usuario")

    @staticmethod
    def gerar_protocolo() -> str:
        while True:
            codigo = "LGPD-" + secrets.token_hex(4).upper()
            if not PedidoTitular.query.filter_by(protocolo=codigo).first():
                return codigo

    @property
    def tipo_label(self):
        return label_tipo_direito(self.tipo)

    @property
    def status_label(self):
        return label_status_pedido(self.status)

    @property
    def atrasado(self):
        return (self.status not in ("concluido", "recusado")
                and self.prazo is not None and agora_utc() > self.prazo)

    @property
    def dias_para_prazo(self):
        return (self.prazo - agora_utc()).days if self.prazo else None


# ── RIPD — Relatório de Impacto à Proteção de Dados (Art. 38) ────────────────
class Ripd(db.Model):
    __tablename__ = "ripd"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    ropa_id = db.Column(db.Integer, db.ForeignKey("ropa_registros.id"), nullable=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao_tratamento = db.Column(db.Text)
    probabilidade = db.Column(db.Integer, default=1, nullable=False)  # 1–3
    impacto = db.Column(db.Integer, default=1, nullable=False)        # 1–3
    medidas = db.Column(db.Text)
    risco_residual = db.Column(db.String(20))                        # baixo/medio/alto
    conclusao = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="rascunho")
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=agora_utc, onupdate=agora_utc)

    ropa = db.relationship("RopaRegistro")

    @property
    def risco_inerente(self):
        return (self.probabilidade or 1) * (self.impacto or 1)

    @property
    def risco_inerente_nivel(self):
        return label_risco(nivel_risco_de(self.risco_inerente))

    @property
    def risco_residual_label(self):
        return label_risco(self.risco_residual) if self.risco_residual else "—"


# ── Incidentes de segurança (Art. 48) ───────────────────────────────────────
class Incidente(db.Model):
    __tablename__ = "incidentes"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    titulo = db.Column(db.String(200), nullable=False)
    ocorrido_em = db.Column(db.DateTime)
    descricao = db.Column(db.Text)
    dados_afetados = db.Column(db.Text)
    num_titulares = db.Column(db.Integer)
    risco = db.Column(db.String(20))
    comunicado_anpd = db.Column(db.Boolean, default=False, nullable=False, server_default=false())
    comunicado_anpd_em = db.Column(db.DateTime)
    comunicado_titulares = db.Column(db.Boolean, default=False, nullable=False, server_default=false())
    comunicado_titulares_em = db.Column(db.DateTime)
    medidas = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="aberto")
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)

    @property
    def risco_label(self):
        return label_risco(self.risco)

    @property
    def status_label(self):
        return label_status_incidente(self.status)
