import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import certifi
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_email_abastecimento(quem_abasteceu, veiculo, valor):
    """Envia email notificando o outro usuario sobre abastecimento"""
    try:
        # Puxa configuracoes do secrets.toml (secao [smtp])
        smtp_section = st.secrets.get("smtp", {})
        smtp_config = {
            "host": smtp_section.get("smtp_host", "smtp.gmail.com"),
            "port": smtp_section.get("smtp_port", 587),
            "user": smtp_section.get("smtp_user", ""),
            "password": smtp_section.get("smtp_password", ""),
            "from_email": smtp_section.get("smtp_from_email", ""),
            "from_name": smtp_section.get("smtp_from_name", "Financas")
        }

        emails_usuarios = {
            "Susanna": smtp_section.get("email_susanna", "susannazk004@gmail.com"),
            "Pietrah": smtp_section.get("email_pietrah", "pietrahofc@gmail.com")
        }

        # Define destinatario (o outro usuario)
        if quem_abasteceu == "Susanna":
            destinatario = emails_usuarios["Pietrah"]
            nome_dest = "Pietrah"
        else:
            destinatario = emails_usuarios["Susanna"]
            nome_dest = "Susanna"

        # Verifica se tem configuracao
        if not smtp_config["user"] or not smtp_config["password"] or not destinatario:
            print("Configuracao de email incompleta no secrets.toml")
            return False

        # Formata valor
        valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # Artigo correto para o veiculo
        artigo = "a" if veiculo == "Moto" else "o"
        emoji_veiculo = "🏍️" if veiculo == "Moto" else "🚗"

        # Cria mensagem
        msg = MIMEMultipart()
        msg["From"] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
        msg["To"] = destinatario
        msg["Subject"] = f"{quem_abasteceu} abasteceu {artigo} {veiculo}!"

        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #1a1a2e; color: white; padding: 20px;">
            <div style="max-width: 400px; margin: 0 auto; background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%); border-radius: 12px; padding: 20px; border: 1px solid #333;">
                <h2 style="color: #ff9800; margin-bottom: 15px; text-align: center;">{emoji_veiculo} Abastecimento!</h2>

                <p style="font-size: 16px; color: #ccc; text-align: center;">Oi <strong style="color: #e91e63;">{nome_dest}</strong>! 👋</p>

                <p style="font-size: 15px; color: white; text-align: center; margin: 15px 0;">
                    <strong>{quem_abasteceu}</strong> acabou de abastecer {artigo} <strong>{veiculo}</strong>!
                </p>

                <div style="background: rgba(76, 175, 80, 0.15); padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; border: 1px solid #4caf50;">
                    <span style="font-size: 12px; color: #888;">💵 Valor</span><br>
                    <span style="font-size: 28px; color: #4caf50; font-weight: bold;">{valor_fmt}</span>
                </div>

                <div style="background: rgba(233, 30, 99, 0.1); padding: 12px; border-radius: 8px; text-align: center; margin-top: 15px;">
                    <p style="font-size: 14px; color: #e91e63; margin: 0;">
                        😜 Agora é sua vez de abastecer, hein!
                    </p>
                </div>

                <p style="font-size: 11px; color: #666; text-align: center; margin-top: 20px;">
                    Enviado automaticamente pelo app Financas
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(corpo, "html"))

        # Envia email
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            server.starttls()
            server.login(smtp_config["user"], smtp_config["password"])
            server.sendmail(smtp_config["from_email"], destinatario, msg.as_string())

        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

# Configuracao da pagina
st.set_page_config(
    page_title="Financas",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS otimizado para mobile 6.7"
st.markdown("""
<style>
    * {
        box-sizing: border-box;
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }
    .block-container {
        padding: 0.5rem 0.75rem !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        min-width: 180px;
        max-width: 200px;
    }
    [data-testid="stSidebar"] .block-container {
        padding: 0.5rem !important;
    }
    div[data-testid="stSidebar"] .stRadio > div > label {
        padding: 8px 10px;
        font-size: 13px;
        border-radius: 8px;
        margin: 2px 0;
        background: rgba(255,255,255,0.05);
    }

    .page-title {
        font-size: 13px;
        text-align: center;
        margin: 2px 0 6px 0;
        font-weight: 600;
    }
    .section-title {
        font-size: 10px;
        text-align: center;
        margin: 4px 0 2px 0;
        font-weight: 500;
    }

    .su-card {
        background: linear-gradient(135deg, #c2185b 0%, #e91e63 100%);
        padding: 4px 6px;
        border-radius: 6px;
        color: white;
        margin: 1px 0;
        border-left: 2px solid #f48fb1;
        display: inline-block;
        width: 100%;
    }
    .su-card h4 { margin: 0; font-size: 8px; opacity: 0.9; }
    .su-card h2 { margin: 0; font-size: 11px; font-weight: 600; }
    .su-card small { font-size: 7px; opacity: 0.8; display: block; }
    .su-label { color: #f48fb1; font-size: 9px; font-weight: 500; margin: 1px 0; }

    .pi-card {
        background: linear-gradient(135deg, #0277bd 0%, #03a9f4 100%);
        padding: 4px 6px;
        border-radius: 6px;
        color: white;
        margin: 1px 0;
        border-left: 2px solid #4fc3f7;
        display: inline-block;
        width: 100%;
    }
    .pi-card h4 { margin: 0; font-size: 8px; opacity: 0.9; }
    .pi-card h2 { margin: 0; font-size: 11px; font-weight: 600; }
    .pi-card small { font-size: 7px; opacity: 0.8; display: block; }
    .pi-label { color: #4fc3f7; font-size: 9px; font-weight: 500; margin: 1px 0; }

    .ok-box {
        background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
        padding: 6px;
        border-radius: 6px;
        text-align: center;
        color: white;
        margin: 2px 0;
    }
    .ok-box h3 { margin: 0; font-size: 11px; }

    .su-deve {
        background: linear-gradient(135deg, #880e4f 0%, #c2185b 100%);
        padding: 6px;
        border-radius: 6px;
        text-align: center;
        color: white;
        margin: 2px 0;
    }
    .su-deve p { margin: 0; font-size: 8px; }
    .su-deve h2 { margin: 1px 0; font-size: 12px; }

    .pi-deve {
        background: linear-gradient(135deg, #01579b 0%, #0277bd 100%);
        padding: 6px;
        border-radius: 6px;
        text-align: center;
        color: white;
        margin: 2px 0;
    }
    .pi-deve p { margin: 0; font-size: 8px; }
    .pi-deve h2 { margin: 1px 0; font-size: 12px; }

    .info-box {
        background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%);
        padding: 6px;
        border-radius: 6px;
        text-align: center;
        color: white;
        margin: 2px 0;
    }
    .info-box p { margin: 0; font-size: 8px; }
    .info-box h2 { margin: 1px 0; font-size: 12px; }

    div[data-testid="stExpander"] {
        border-radius: 6px;
        border: 1px solid #333;
    }
    div[data-testid="stExpander"] summary {
        font-size: 10px;
        padding: 5px;
    }

    .stSelectbox, .stTextInput, .stNumberInput { font-size: 11px; }
    .stButton > button { font-size: 11px; padding: 5px 10px; border-radius: 6px; }
    .stProgress > div > div { height: 5px; border-radius: 3px; }

    [data-testid="column"] { padding: 0 1px !important; }

    /* Forca colunas lado a lado em mobile */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 !important;
    }

    /* Container flexbox para cards */
    .cards-row {
        display: flex !important;
        flex-direction: row !important;
        gap: 6px;
        width: 100%;
    }
    .cards-row > div {
        flex: 1;
        min-width: 0;
    }
    .stCaption { font-size: 9px !important; }

    .user-selector {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        padding: 40px 20px;
    }
    .user-btn {
        padding: 30px 40px;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .user-btn:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def connect_mongodb():
    """Conexao cacheada com MongoDB - persiste entre reruns."""
    URI = st.secrets["uri"]

    try:
        client = MongoClient(URI, tls=True, tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=30000, connectTimeoutMS=30000, socketTimeoutMS=30000, maxPoolSize=10, retryWrites=True)
        client.admin.command('ping')
        return client
    except: pass

    try:
        client = MongoClient(URI, tls=True, tlsAllowInvalidCertificates=True, tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=30000, connectTimeoutMS=30000, socketTimeoutMS=30000, maxPoolSize=10, retryWrites=True)
        client.admin.command('ping')
        return client
    except: pass

    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=30000, connectTimeoutMS=30000, socketTimeoutMS=30000, maxPoolSize=10, retryWrites=True)
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f"Conexao falhou: {e}")
        raise


def get_collections(client):
    URI = st.secrets["uri"]
    try:
        db_name = URI.split("/")[-1].split("?")[0] or "financas"
    except:
        db_name = "financas"
    db = client[db_name]
    return {"despesas": db["despesas"], "emprestimos": db["emprestimos"], "metas": db["metas"], "quitacoes": db["quitacoes"], "contas_fixas": db["contas_fixas"], "emprestimos_terceiros": db["emprestimos_terceiros"], "dividas_terceiros": db["dividas_terceiros"], "config": db["config"]}


def limpar_cache_dados():
    """Limpa cache de dados para refletir alteracoes."""
    st.cache_data.clear()


@st.cache_data(ttl=300)
def carregar_despesas(_colls):
    """Carrega despesas com cache de 5 minutos."""
    return list(_colls["despesas"].find({}))


@st.cache_data(ttl=300)
def carregar_emprestimos(_colls):
    """Carrega emprestimos com cache de 5 minutos."""
    return list(_colls["emprestimos"].find({}))


@st.cache_data(ttl=300)
def carregar_quitacoes(_colls):
    """Carrega quitacoes com cache de 5 minutos."""
    return list(_colls["quitacoes"].find({}))


@st.cache_data(ttl=300)
def carregar_metas(_colls, user):
    """Carrega metas do usuario com cache de 5 minutos."""
    return list(_colls["metas"].find({"ativo": True, "pessoa": user}))


@st.cache_data(ttl=300)
def carregar_contas_fixas(_colls):
    """Carrega contas fixas com cache de 5 minutos."""
    return list(_colls["contas_fixas"].find({"ativo": True}))


@st.cache_data(ttl=300)
def carregar_emprestimos_terceiros(_colls, user):
    """Carrega emprestimos a terceiros do usuario (todos em aberto)."""
    return list(_colls["emprestimos_terceiros"].find({"credor": user, "status": "em aberto"}))


@st.cache_data(ttl=300)
def carregar_emprestimos_terceiros_periodo(_colls, user, data_inicio, data_fim):
    """Carrega emprestimos a terceiros do usuario filtrados por periodo."""
    from datetime import datetime
    # Converte date para datetime se necessario
    if hasattr(data_inicio, 'year') and not hasattr(data_inicio, 'hour'):
        data_inicio = datetime(data_inicio.year, data_inicio.month, data_inicio.day)
    if hasattr(data_fim, 'year') and not hasattr(data_fim, 'hour'):
        data_fim = datetime(data_fim.year, data_fim.month, data_fim.day, 23, 59, 59)
    return list(_colls["emprestimos_terceiros"].find({
        "credor": user,
        "status": "em aberto",
        "data_emprestimo": {"$gte": data_inicio, "$lte": data_fim}
    }))


@st.cache_data(ttl=300)
def carregar_dividas_terceiros(_colls, user):
    """Carrega dividas a terceiros do usuario."""
    return list(_colls["dividas_terceiros"].find({"devedor": user, "status": "em aberto"}))


@st.cache_data(ttl=300)
def carregar_pagamentos_contas_fixas(_colls, user, mes_ano):
    """Carrega pagamentos de contas fixas do usuario no mes."""
    return list(_colls["quitacoes"].find({"tipo": "conta_fixa", "pagador": user, "mes_ano": mes_ano}))


@st.cache_data(ttl=300)
def carregar_fechamento_fatura(_colls, user):
    """Carrega configuracao de fechamento de fatura do usuario."""
    return list(_colls["config"].find({"tipo": "fechamento_fatura", "user": user}))


def get_fechamento_mes(colls, ano, mes, user):
    """Retorna o dia de fechamento da fatura para o mes/ano especificado do usuario."""
    fechamentos = carregar_fechamento_fatura(colls, user)
    mes_ano = f"{ano}-{mes:02d}"
    for f in fechamentos:
        if f.get("mes_ano") == mes_ano:
            return f.get("dia_fechamento", 7)  # Default dia 7
    return 7  # Default se nao configurado


def get_periodo_fatura(colls, user):
    """Retorna data_inicio e data_fim do periodo atual baseado no fechamento da fatura do usuario."""
    hoje = date.today()

    # Pega fechamento do mes atual e proximo
    fechamento_atual = get_fechamento_mes(colls, hoje.year, hoje.month, user)

    if hoje.month == 12:
        prox_ano, prox_mes = hoje.year + 1, 1
    else:
        prox_ano, prox_mes = hoje.year, hoje.month + 1

    if hoje.month == 1:
        ant_ano, ant_mes = hoje.year - 1, 12
    else:
        ant_ano, ant_mes = hoje.year, hoje.month - 1

    fechamento_prox = get_fechamento_mes(colls, prox_ano, prox_mes, user)
    fechamento_ant = get_fechamento_mes(colls, ant_ano, ant_mes, user)

    # Data de fechamento do mes atual
    try:
        data_fechamento_atual = date(hoje.year, hoje.month, fechamento_atual)
    except:
        data_fechamento_atual = date(hoje.year, hoje.month, 28)

    if hoje >= data_fechamento_atual:
        # Estamos apos o fechamento - periodo atual vai do fechamento ate proximo fechamento
        data_inicio = data_fechamento_atual
        try:
            data_fim = date(prox_ano, prox_mes, fechamento_prox) - timedelta(days=1)
        except:
            data_fim = date(prox_ano, prox_mes, 28) - timedelta(days=1)
    else:
        # Estamos antes do fechamento - periodo eh do fechamento anterior ate o atual
        try:
            data_inicio = date(ant_ano, ant_mes, fechamento_ant)
        except:
            data_inicio = date(ant_ano, ant_mes, 28)
        data_fim = data_fechamento_atual - timedelta(days=1)

    return data_inicio, data_fim


def get_feriados(ano):
    """Retorna lista de feriados nacionais e de SP para o ano."""
    from datetime import date
    feriados = [
        # Feriados nacionais fixos
        date(ano, 1, 1),    # Confraternizacao Universal
        date(ano, 4, 21),   # Tiradentes
        date(ano, 5, 1),    # Dia do Trabalho
        date(ano, 9, 7),    # Independencia
        date(ano, 10, 12),  # Nossa Senhora Aparecida
        date(ano, 11, 2),   # Finados
        date(ano, 11, 15),  # Proclamacao da Republica
        date(ano, 12, 25),  # Natal
        # Feriado estadual SP
        date(ano, 7, 9),    # Revolucao Constitucionalista
        # Feriado municipal Paulinia
        date(ano, 2, 28),   # Aniversario de Paulinia
    ]
    # Carnaval e Corpus Christi (moveis) - calcular baseado na Pascoa
    # Pascoa 2025: 20/04, 2026: 05/04, 2027: 28/03
    pascoas = {2025: date(2025, 4, 20), 2026: date(2026, 4, 5), 2027: date(2027, 3, 28), 2028: date(2028, 4, 16)}
    if ano in pascoas:
        pascoa = pascoas[ano]
        feriados.append(pascoa - timedelta(days=47))  # Carnaval (terca)
        feriados.append(pascoa - timedelta(days=48))  # Carnaval (segunda)
        feriados.append(pascoa - timedelta(days=2))   # Sexta-feira Santa
        feriados.append(pascoa + timedelta(days=60))  # Corpus Christi
    return set(feriados)


def get_5o_dia_util(ano, mes):
    """Calcula o 5o dia util do mes considerando feriados de Paulinia-SP."""
    from calendar import monthrange
    feriados = get_feriados(ano)
    dias_uteis = 0
    for dia in range(1, monthrange(ano, mes)[1] + 1):
        d = date(ano, mes, dia)
        # Dia util = segunda a sexta E nao eh feriado
        if d.weekday() < 5 and d not in feriados:
            dias_uteis += 1
            if dias_uteis == 5:
                return d
    return date(ano, mes, 1)


def fmt(valor):
    return f"R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def get_user():
    """Retorna o usuario selecionado ou None se nao selecionado."""
    return st.session_state.get("usuario_atual")


def get_outro_user():
    """Retorna o outro usuario."""
    user = get_user()
    return "Pietrah" if user == "Susanna" else "Susanna"


def show_user_selector():
    """Mostra tela de selecao de usuario."""
    st.markdown("""
    <div style="text-align: center; padding: 50px 0 30px 0;">
        <h1 style="font-size: 64px; margin-bottom: 0;">💰</h1>
        <h2 style="color: #FF6B6B; margin-bottom: 30px;">Financas</h2>
        <p style="color: #888; font-size: 14px;">Quem esta usando?</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⚡ Susanna", use_container_width=True, type="primary"):
        st.session_state.usuario_atual = "Susanna"
        st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if st.button("👩 Pietrah", use_container_width=True, type="secondary"):
        st.session_state.usuario_atual = "Pietrah"
        st.rerun()


def show_user_badge():
    """Mostra badge do usuario na sidebar com opcao de trocar."""
    user = get_user()
    cor = "#e91e63" if user == "Susanna" else "#03a9f4"

    st.markdown(f"""
    <div style="text-align: center; padding: 10px; background: {cor}20; border-radius: 8px; margin-bottom: 10px;">
        <span style="font-size: 20px;">⚡</span>
        <p style="margin: 5px 0 0 0; font-weight: bold; color: {cor};">{user}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Trocar", use_container_width=True, key="trocar_user"):
        del st.session_state["usuario_atual"]
        st.rerun()


def main():
    client = connect_mongodb()
    if not client:
        st.stop()

    colls = get_collections(client)
    user = get_user()
    outro = get_outro_user()
    cor_card = "su-card" if user == "Susanna" else "pi-card"
    cor_outro = "pi-card" if user == "Susanna" else "su-card"
    cores_user = ['#e91e63', '#f48fb1', '#f06292', '#ec407a', '#d81b60', '#c2185b', '#ad1457', '#880e4f', '#ff80ab', '#ff4081'] if user == "Susanna" else ['#03a9f4', '#4fc3f7', '#29b6f6', '#0288d1', '#039be5', '#0277bd', '#01579b', '#81d4fa', '#00bcd4', '#26c6da']

    with st.sidebar:
        show_user_badge()
        st.markdown("### Menu")

        # Inicializa menu selecionado
        if "menu_selecionado" not in st.session_state:
            st.session_state.menu_selecionado = "🏠 Inicio"

        menu_opcoes = ["🏠 Inicio", "➕ Novo", "🤝 Acerto", "📊 Relatorio", "⛽", "🎯 Metas", "👯 Ambas", "📈 Evolucao", "⚙️ Config"]

        for opcao in menu_opcoes:
            tipo_btn = "primary" if st.session_state.menu_selecionado == opcao else "secondary"
            if st.button(opcao, use_container_width=True, key=f"menu_{opcao}", type=tipo_btn):
                st.session_state.menu_selecionado = opcao
                st.rerun()

        menu = st.session_state.menu_selecionado

    # ========== INICIO ==========
    if menu == "🏠 Inicio":
        st.markdown(f'<p class="page-title">💰 Ola, {user}!</p>', unsafe_allow_html=True)

        df = pd.DataFrame(carregar_despesas(colls))
        df_emp = pd.DataFrame(carregar_emprestimos(colls))
        df_contas_fixas_inicio = pd.DataFrame(carregar_contas_fixas(colls))

        if not df.empty:
            df["createdAt"] = pd.to_datetime(df["createdAt"])

            # Periodo baseado no fechamento da fatura
            data_inicio, data_fim = get_periodo_fatura(colls, user)

            # Filtra registros do periodo da fatura
            meus_registros = df[
                (df["buyer"] == user) &
                (df["createdAt"].dt.date >= data_inicio) &
                (df["createdAt"].dt.date <= data_fim)
            ]

            # Mostra periodo
            st.markdown(f'<p style="font-size: 10px; text-align: center; color: #888; margin-bottom: 8px;">Fatura: {data_inicio.strftime("%d/%m")} a {data_fim.strftime("%d/%m")}</p>', unsafe_allow_html=True)

            # === DASHBOARD - 3 CARDS ===
            # Card 1: Gastos (tudo que JA FOI gasto - credito, parcelamentos, contas fixas PAGAS e contas fixas no credito)
            # Inclui despesas com origem="conta_fixa" porque significa que foi paga
            df_gastos_card = meus_registros[~meus_registros["label"].str.contains("Cofrinho|Renda Variavel", na=False)] if not meus_registros.empty else pd.DataFrame()
            gastos_reais = df_gastos_card["total_value"].sum() if not df_gastos_card.empty else 0

            # Soma contas fixas no credito (ja estao comprometidas automaticamente)
            contas_fixas_credito_inicio = 0
            if not df_contas_fixas_inicio.empty:
                for _, conta in df_contas_fixas_inicio.iterrows():
                    if conta.get("cartao_credito", False):
                        if conta["responsavel"] == user:
                            contas_fixas_credito_inicio += conta["valor"]
                        elif conta["responsavel"] == "Dividido":
                            contas_fixas_credito_inicio += conta["valor"] / 2
            gastos_reais += contas_fixas_credito_inicio

            # Soma emprestimos a terceiros (dinheiro que saiu do bolso) - apenas do periodo atual
            df_emprestimos_terceiros_inicio = pd.DataFrame(carregar_emprestimos_terceiros_periodo(colls, user, data_inicio, data_fim))
            if not df_emprestimos_terceiros_inicio.empty:
                gastos_reais += df_emprestimos_terceiros_inicio["valor"].sum()

            # Card 2: Cofrinho
            df_cofrinho_card = meus_registros[meus_registros["label"].str.contains("Cofrinho", na=False)] if not meus_registros.empty else pd.DataFrame()
            cofrinho = df_cofrinho_card["total_value"].sum() if not df_cofrinho_card.empty else 0

            # Card 3: Renda Variavel
            df_extra_card = meus_registros[meus_registros["label"].str.contains("Renda Variavel", na=False)] if not meus_registros.empty else pd.DataFrame()
            renda_variavel = df_extra_card["total_value"].sum() if not df_extra_card.empty else 0

            # Exibir os 3 cards com flexbox (garante lado a lado em mobile)
            cor_gastos = "linear-gradient(135deg, #c2185b 0%, #e91e63 100%)" if user == "Susanna" else "linear-gradient(135deg, #0277bd 0%, #03a9f4 100%)"
            borda_gastos = "#f48fb1" if user == "Susanna" else "#4fc3f7"

            st.markdown(f'''
            <div style="display: flex; flex-direction: row; gap: 6px; width: 100%;">
                <div style="flex: 1; background: {cor_gastos}; padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid {borda_gastos};">
                    <span style="font-size: 14px; opacity: 0.9;">💸 Gastos</span><br>
                    <span style="font-size: 12px; font-weight: 600;">{fmt(gastos_reais)}</span>
                </div>
                <div style="flex: 1; background: linear-gradient(135deg, #388e3c 0%, #66bb6a 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #81c784;">
                    <span style="font-size: 14px; opacity: 0.9;">🐷 Cofrinho</span><br>
                    <span style="font-size: 12px; font-weight: 600;">{fmt(cofrinho)}</span>
                </div>
                <div style="flex: 1; background: linear-gradient(135deg, #f57c00 0%, #ffb74d 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #ffcc80;">
                    <span style="font-size: 14px; opacity: 0.9;">💵 Extra</span><br>
                    <span style="font-size: 12px; font-weight: 600;">{fmt(renda_variavel)}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            st.markdown("")
            st.markdown("")

            # === GRAFICO POR CATEGORIA (incluindo Cofrinho e Contas Fixas) ===
            st.markdown('<p class="section-title">📊 Gastos por Categoria</p>', unsafe_allow_html=True)

            # Exclui apenas Renda Variavel do grafico
            gastos_para_grafico = meus_registros[~meus_registros["label"].str.contains("Renda Variavel", na=False)]
            user_cat_series = gastos_para_grafico.groupby("label")["total_value"].sum() if not gastos_para_grafico.empty else pd.Series(dtype=float)

            # Adiciona contas fixas de credito ao grafico
            if not df_contas_fixas_inicio.empty:
                for _, conta in df_contas_fixas_inicio.iterrows():
                    if conta.get("cartao_credito", False):
                        valor_meu = conta["valor"] if conta["responsavel"] == user else (conta["valor"] / 2 if conta["responsavel"] == "Dividido" else 0)
                        if valor_meu > 0:
                            cat_original = conta.get("categoria", "📄 Contas")
                            # Mapeia categoria da conta fixa para categoria de despesa
                            if "Saude" in str(cat_original) or "saude" in str(cat_original).lower():
                                cat_label = "💊 Saude"
                            elif cat_original in ["📄 Contas", "💊 Saude", "📦 Outros"]:
                                cat_label = cat_original
                            else:
                                cat_label = "📄 Contas"

                            if cat_label in user_cat_series.index:
                                user_cat_series[cat_label] += valor_meu
                            else:
                                user_cat_series[cat_label] = valor_meu

            # Adiciona emprestimos a terceiros (do periodo atual) como categoria
            df_emprestimos_terceiros = pd.DataFrame(carregar_emprestimos_terceiros_periodo(colls, user, data_inicio, data_fim))
            if not df_emprestimos_terceiros.empty:
                total_emprestei = df_emprestimos_terceiros["valor"].sum()
                if total_emprestei > 0:
                    if "🤝 Emprestei" in user_cat_series.index:
                        user_cat_series["🤝 Emprestei"] += total_emprestei
                    else:
                        user_cat_series["🤝 Emprestei"] = total_emprestei

            user_cat = user_cat_series.reset_index()
            user_cat.columns = ["label", "total_value"]
            user_cat = user_cat.sort_values("total_value", ascending=False)

            if not user_cat.empty:
                # Cores bem distintas para mobile
                cores_distintas = ['#e91e63', '#2196f3', '#4caf50', '#ff9800', '#9c27b0', '#00bcd4', '#ffeb3b', '#f44336', '#8bc34a', '#673ab7', '#ff5722', '#03a9f4']

                # Calcula porcentagem baseada no maior valor (100%)
                max_valor = user_cat["total_value"].max()
                total_geral = user_cat["total_value"].sum()

                # Gera barras de progresso em HTML
                barras_html = ""
                for i, (_, row) in enumerate(user_cat.iterrows()):
                    cor = cores_distintas[i % len(cores_distintas)]
                    pct_barra = (row["total_value"] / max_valor) * 100
                    pct_total = (row["total_value"] / total_geral) * 100

                    barras_html += f'''
                    <div style="margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                            <span style="font-size: 12px; color: white;">{row["label"]}</span>
                            <span style="font-size: 11px; color: #aaa;">{fmt(row["total_value"])} ({pct_total:.1f}%)</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); border-radius: 4px; height: 8px; overflow: hidden;">
                            <div style="background: {cor}; width: {pct_barra}%; height: 100%; border-radius: 4px; transition: width 0.3s;"></div>
                        </div>
                    </div>
                    '''

                st.markdown(barras_html, unsafe_allow_html=True)
            else:
                st.caption("Sem gastos ainda")

            st.markdown("---")

            # ========== SITUACAO FINANCEIRA ==========
            # Calcula pendencias entre usuarios
            user_deve = df[(df["devedor"] == user) & (df["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            outro_deve = df[(df["devedor"] == outro) & (df["status_pendencia"] == "em aberto")]["valor_pendente"].sum()

            if not df_emp.empty:
                df_emp["createdAt"] = pd.to_datetime(df_emp["createdAt"])
                user_deve += df_emp[(df_emp["devedor"] == user) & (df_emp["status"] == "em aberto")]["valor"].sum()
                outro_deve += df_emp[(df_emp["devedor"] == outro) & (df_emp["status"] == "em aberto")]["valor"].sum()

            saldo = outro_deve - user_deve

            # Busca dividas a terceiros (separando emprestimos pessoais)
            df_dividas_terceiros = pd.DataFrame(carregar_dividas_terceiros(colls, user))
            if not df_dividas_terceiros.empty:
                if "emprestimo_conta" not in df_dividas_terceiros.columns:
                    df_dividas_terceiros["emprestimo_conta"] = False
                df_dividas_terceiros["emprestimo_conta"] = df_dividas_terceiros["emprestimo_conta"].fillna(False)

                df_dividas_pessoas = df_dividas_terceiros[df_dividas_terceiros["emprestimo_conta"] == False]
                total_dividas = df_dividas_pessoas["valor"].sum() if not df_dividas_pessoas.empty else 0
                df_emp_pessoal = df_dividas_terceiros[df_dividas_terceiros["emprestimo_conta"] == True]
                total_emp_pessoal = df_emp_pessoal["valor"].sum() if not df_emp_pessoal.empty else 0
            else:
                total_dividas = 0
                total_emp_pessoal = 0

            # Mostra situacao se houver algo
            tem_alguma_divida = abs(saldo) >= 0.01 or total_dividas > 0 or total_emp_pessoal > 0
            if tem_alguma_divida:
                st.markdown("")
                st.markdown('<p class="section-title" style="font-size: 14px;">💫 Situacao</p>', unsafe_allow_html=True)

                cor_user = "linear-gradient(135deg, #c2185b 0%, #e91e63 100%)" if user == "Susanna" else "linear-gradient(135deg, #0277bd 0%, #03a9f4 100%)"
                borda_user = "#f48fb1" if user == "Susanna" else "#4fc3f7"

                # Monta lista de cards
                cards_situacao = []

                # Card saldo com a outra pessoa
                if saldo > 0:
                    cards_situacao.append(f'<div style="flex: 1; background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #81c784;"><span style="font-size: 14px; opacity: 0.9;">🤑 {outro} te deve</span><br><span style="font-size: 12px; font-weight: 600;">{fmt(saldo)}</span></div>')
                elif saldo < 0:
                    cards_situacao.append(f'<div style="flex: 1; background: {cor_user}; padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid {borda_user};"><span style="font-size: 14px; opacity: 0.9;">Devo pra {outro}</span><br><span style="font-size: 12px; font-weight: 600;">{fmt(abs(saldo))}</span></div>')

                # Card dividas a terceiros
                if total_dividas > 0:
                    cards_situacao.append(f'<div style="flex: 1; background: linear-gradient(135deg, #c62828 0%, #f44336 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #ef9a9a;"><span style="font-size: 14px; opacity: 0.9;">💸 Devo (terceiros)</span><br><span style="font-size: 12px; font-weight: 600;">{fmt(total_dividas)}</span></div>')

                # Card emprestimos pessoais
                if total_emp_pessoal > 0:
                    cards_situacao.append(f'<div style="flex: 1; background: linear-gradient(135deg, #5d4037 0%, #8d6e63 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #bcaaa4;"><span style="font-size: 14px; opacity: 0.9;">🏦 Emp. Pessoal</span><br><span style="font-size: 12px; font-weight: 600;">{fmt(total_emp_pessoal)}</span></div>')

                if cards_situacao:
                    html_cards = "".join(cards_situacao)
                    st.markdown(f'<div style="display: flex; flex-direction: row; gap: 6px; width: 100%;">{html_cards}</div>', unsafe_allow_html=True)
        else:
            st.info("📝 Sem registros ainda. Va em '➕ Novo'!")

    # ========== NOVO ==========
    elif menu == "➕ Novo":
        st.markdown('<p class="page-title">➕ Novo Registro</p>', unsafe_allow_html=True)

        # Inicializa estado do formulario selecionado
        if "form_selecionado" not in st.session_state:
            st.session_state.form_selecionado = None
        
        st.markdown("")

        # Botoes empilhados
        if st.button("💸 Gasto", use_container_width=True, type="primary" if st.session_state.form_selecionado == "gasto" else "secondary"):
            st.session_state.form_selecionado = "gasto"
            st.rerun()
        if st.button("🤝 Emprestei", use_container_width=True, type="primary" if st.session_state.form_selecionado == "emprestei" else "secondary"):
            st.session_state.form_selecionado = "emprestei"
            st.rerun()
        if st.button("💳 Devo", use_container_width=True, type="primary" if st.session_state.form_selecionado == "devo" else "secondary"):
            st.session_state.form_selecionado = "devo"
            st.rerun()
        if st.button("📋 Conta Fixa", use_container_width=True, type="primary" if st.session_state.form_selecionado == "conta_fixa" else "secondary"):
            st.session_state.form_selecionado = "conta_fixa"
            st.rerun()

        st.markdown("")

        # ===== ABASTECIMENTO RAPIDO =====
        st.markdown('<p style="font-size: 12px; color: #888; margin-bottom: 4px;">⛽ Abastecimento rapido</p>', unsafe_allow_html=True)

        with st.expander("🏍️ Moto", expanded=False):
            with st.form("form_moto", clear_on_submit=True):
                valor_moto = st.number_input("💵 Valor", min_value=0.01, value=30.00, format="%.2f", key="valor_moto")
                pagamento_moto = st.selectbox("💳 Pagamento", ["Debito", "Credito", "Pix", "Dinheiro"], key="pag_moto")
                moto_submitted = st.form_submit_button("✅ Registrar", use_container_width=True)

            if moto_submitted:
                colls["despesas"].insert_one({
                    "label": "⛽ Combustivel",
                    "buyer": user,
                    "item": "Moto",
                    "description": "",
                    "quantity": 1,
                    "total_value": valor_moto,
                    "payment_method": pagamento_moto,
                    "installment": 0,
                    "createdAt": datetime.now(),
                    "pagamento_compartilhado": "👤 Pra mim",
                    "tem_pendencia": False,
                    "devedor": None,
                    "valor_pendente": None,
                    "status_pendencia": None
                })
                limpar_cache_dados()
                # Envia email para o outro usuario
                if enviar_email_abastecimento(user, "Moto", valor_moto):
                    st.success(f"✅ Abastecimento moto {fmt(valor_moto)} registrado! 📧 Email enviado!")
                else:
                    st.success(f"✅ Abastecimento moto {fmt(valor_moto)} registrado!")
                st.balloons()

        with st.expander("🚗 Carro", expanded=False):
            with st.form("form_carro", clear_on_submit=True):
                valor_carro = st.number_input("💵 Valor", min_value=0.01, value=60.00, format="%.2f", key="valor_carro")
                pagamento_carro = st.selectbox("💳 Pagamento", ["Debito", "Credito", "Pix", "Dinheiro"], key="pag_carro")
                carro_submitted = st.form_submit_button("✅ Registrar", use_container_width=True)

            if carro_submitted:
                colls["despesas"].insert_one({
                    "label": "⛽ Combustivel",
                    "buyer": user,
                    "item": "Carro",
                    "description": "",
                    "quantity": 1,
                    "total_value": valor_carro,
                    "payment_method": pagamento_carro,
                    "installment": 0,
                    "createdAt": datetime.now(),
                    "pagamento_compartilhado": "👤 Pra mim",
                    "tem_pendencia": False,
                    "devedor": None,
                    "valor_pendente": None,
                    "status_pendencia": None
                })
                limpar_cache_dados()
                # Envia email para o outro usuario
                if enviar_email_abastecimento(user, "Carro", valor_carro):
                    st.success(f"✅ Abastecimento carro {fmt(valor_carro)} registrado! 📧 Email enviado!")
                else:
                    st.success(f"✅ Abastecimento carro {fmt(valor_carro)} registrado!")
                st.balloons()

        st.markdown("---")

        # ===== FORMULARIO GASTO =====
        if st.session_state.form_selecionado == "gasto":
            st.markdown('<p style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">💸 Registrar Gasto</p>', unsafe_allow_html=True)
            with st.form("form_novo_gasto", clear_on_submit=True):

                label = st.selectbox("🏷️ Categoria", ["🍔 Comida", "⛽ Combustivel", "🚗 Automoveis", "🍺 Bebidas", "👗 Vestuario", "💊 Saude", "🎮 Lazer", "📄 Contas", "👨‍👩‍👧 Boa pra familia", "🐷 Cofrinho", "💵 Renda Variavel", "📦 Outros"])
                item = st.text_input("📝 Item")
                description = st.text_input("💬 Descricao")

                quantidade = st.number_input("🔢 Quantidade", min_value=1, value=1)
                preco = st.number_input("💵 Preco", min_value=0.01, value=1.00, format="%.2f")

                pagamento = st.selectbox("💳 Pagamento", ["VR", "Debito", "Credito", "Pix", "Dinheiro"])
                tipo_despesa = st.selectbox("🤝 Tipo de compra", ["👤 Pra mim", "👯 Dividido (me deve metade)", "🎁 Pra outra (me deve tudo)"])
                parcelas = st.number_input("📅 Parcelas", min_value=0, value=0)

                submitted = st.form_submit_button("✅ Salvar Gasto", use_container_width=True)

            if submitted:
                try:
                    valor_total = quantidade * preco

                    pend = {"tem_pendencia": False, "devedor": None, "valor_pendente": None, "status_pendencia": None}

                    if "Dividido" in tipo_despesa:
                        pend = {"tem_pendencia": True, "devedor": outro, "valor_pendente": round(valor_total / 2, 2), "status_pendencia": "em aberto"}
                    elif "Pra outra" in tipo_despesa:
                        pend = {"tem_pendencia": True, "devedor": outro, "valor_pendente": valor_total, "status_pendencia": "em aberto"}

                    doc = {
                        "label": label, "buyer": user, "item": item, "description": description,
                        "quantity": quantidade, "total_value": valor_total, "payment_method": pagamento,
                        "installment": parcelas, "createdAt": datetime.now(), "pagamento_compartilhado": tipo_despesa, **pend
                    }

                    result = colls["despesas"].insert_one(doc)

                    if pend["tem_pendencia"]:
                        colls["quitacoes"].insert_one({
                            "tipo": "despesa_compartilhada", "despesa_id": result.inserted_id, "data": datetime.now(),
                            "credor": user, "devedor": pend["devedor"], "valor": pend["valor_pendente"],
                            "descricao": f"{label} - {item}" if item else label, "observacao": description, "status": "em aberto"
                        })

                    limpar_cache_dados()
                    st.success(f"✅ Gasto de {fmt(valor_total)} salvo!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Erro: {e}")

        # ===== FORMULARIO EMPRESTEI =====
        elif st.session_state.form_selecionado == "emprestei":
            st.markdown('<p style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">🤝 Emprestei pra Alguem</p>', unsafe_allow_html=True)
            with st.form("form_emprestimo_terceiro", clear_on_submit=True):
                pessoa_terceiro = st.text_input("👤 Pessoa", placeholder="Nome de quem te deve")
                valor_terceiro = st.number_input("💵 Valor", min_value=0.01, value=10.00, format="%.2f", key="valor_emp_terceiro")
                desc_terceiro = st.text_input("📝 Descricao", placeholder="Do que se trata")
                data_devolucao = st.date_input("📅 Previsao de devolucao", value=date.today() + timedelta(days=30), format="DD/MM/YYYY")

                emp_terceiro_submitted = st.form_submit_button("✅ Registrar", use_container_width=True)

            if emp_terceiro_submitted and pessoa_terceiro:
                colls["emprestimos_terceiros"].insert_one({
                    "credor": user,
                    "devedor": pessoa_terceiro,
                    "valor": valor_terceiro,
                    "descricao": desc_terceiro,
                    "data_emprestimo": datetime.now(),
                    "data_devolucao": datetime.combine(data_devolucao, datetime.min.time()),
                    "status": "em aberto"
                })
                limpar_cache_dados()
                st.success(f"✅ Emprestimo de {fmt(valor_terceiro)} pra {pessoa_terceiro} registrado!")
                st.balloons()

        # ===== FORMULARIO DEVO =====
        elif st.session_state.form_selecionado == "devo":
            st.markdown('<p style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">💳 Devo pra Alguem</p>', unsafe_allow_html=True)
            with st.form("form_divida_terceiro", clear_on_submit=True):
                pessoa_credor = st.text_input("👤 Pra quem devo", placeholder="Nome de quem te emprestou")
                valor_divida = st.number_input("💵 Valor", min_value=0.01, value=10.00, format="%.2f", key="valor_divida_terceiro")
                desc_divida = st.text_input("📝 Descricao", placeholder="Do que se trata", key="desc_divida")
                data_pagamento = st.date_input("📅 Previsao de pagamento", value=date.today() + timedelta(days=30), format="DD/MM/YYYY", key="data_pagamento")
                emprestimo_conta = st.checkbox("🏦 Emprestimo da minha conta", value=False, help="Marque se e um emprestimo de uma conta pessoal sua (ex: poupanca, reserva)")

                divida_submitted = st.form_submit_button("✅ Registrar", use_container_width=True)

            if divida_submitted and pessoa_credor:
                colls["dividas_terceiros"].insert_one({
                    "devedor": user,
                    "credor": pessoa_credor,
                    "valor": valor_divida,
                    "descricao": desc_divida,
                    "data_emprestimo": datetime.now(),
                    "data_pagamento": datetime.combine(data_pagamento, datetime.min.time()),
                    "status": "em aberto",
                    "emprestimo_conta": emprestimo_conta
                })
                limpar_cache_dados()
                st.success(f"✅ Divida de {fmt(valor_divida)} com {pessoa_credor} registrada!")
                st.balloons()

        # ===== FORMULARIO CONTA FIXA =====
        elif st.session_state.form_selecionado == "conta_fixa":
            st.markdown('<p style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">📋 Cadastrar Conta Fixa</p>', unsafe_allow_html=True)
            with st.form("form_conta_fixa", clear_on_submit=True):
                nome_conta = st.text_input("📝 Nome da conta", placeholder="Ex: Aluguel, Internet...")
                valor_conta = st.number_input("💵 Valor", min_value=0.01, value=100.00, format="%.2f")
                dia_vencimento = st.number_input("📅 Dia vencimento", min_value=1, max_value=31, value=10)
                responsavel = st.selectbox("👤 Responsavel", [user, outro, "Dividido"])
                categoria_conta = st.selectbox("🏷️ Categoria", ["📄 Contas", "💊 Saude", "📦 Outros"])
                cartao_credito = st.checkbox("💳 Conta no cartao de credito", value=False, help="Marque se essa conta e paga no cartao de credito")
                obs_conta = st.text_input("💬 Observacao")

                cf_submitted = st.form_submit_button("✅ Cadastrar", use_container_width=True)

            if cf_submitted:
                conta_fixa = {
                    "nome": nome_conta, "valor": valor_conta, "dia_vencimento": dia_vencimento,
                    "responsavel": responsavel, "categoria": categoria_conta, "observacao": obs_conta,
                    "cartao_credito": cartao_credito,
                    "ativo": True, "createdAt": datetime.now()
                }
                colls["contas_fixas"].insert_one(conta_fixa)
                limpar_cache_dados()
                st.success("✅ Conta fixa cadastrada!")
                st.balloons()

        # Mensagem se nenhum selecionado
        else:
            st.markdown('''
            <div style="text-align: center; padding: 30px; color: #888;">
                <span style="font-size: 32px;">👆</span><br>
                <span style="font-size: 12px;">Selecione o tipo de registro</span>
            </div>
            ''', unsafe_allow_html=True)

    # ========== ACERTO DE CONTAS ==========
    elif menu == "🤝 Acerto":
        st.markdown('<p class="page-title">🤝 Acerto de Contas</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(carregar_despesas(colls))
        df_emp = pd.DataFrame(carregar_emprestimos(colls))
        df_logs = pd.DataFrame(carregar_quitacoes(colls))

        # Calcula totais brutos (o que cada uma deve)
        user_deve_desp, outro_deve_desp = 0, 0
        if not df_desp.empty:
            user_deve_desp = df_desp[(df_desp["devedor"] == user) & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            outro_deve_desp = df_desp[(df_desp["devedor"] == outro) & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()

        user_deve_emp, outro_deve_emp = 0, 0
        if not df_emp.empty:
            user_deve_emp = df_emp[(df_emp["devedor"] == user) & (df_emp["status"] == "em aberto")]["valor"].sum()
            outro_deve_emp = df_emp[(df_emp["devedor"] == outro) & (df_emp["status"] == "em aberto")]["valor"].sum()

        user_deve_bruto = user_deve_desp + user_deve_emp
        outro_deve_bruto = outro_deve_desp + outro_deve_emp

        # SALDO LIQUIDO (ja abatido)
        saldo_liquido = outro_deve_bruto - user_deve_bruto

        # Minha situacao - SALDO LIQUIDO
        st.markdown('<p class="section-title">💰 Saldo</p>', unsafe_allow_html=True)

        if abs(saldo_liquido) < 0.01:
            st.markdown('<div class="ok-box"><h3>✨ Voces estao quites!</h3></div>', unsafe_allow_html=True)
        elif saldo_liquido > 0:
            # Ela me deve (saldo positivo = ela deve pra mim)
            st.markdown(f'<div class="ok-box"><h3>🤑 {outro} te deve {fmt(saldo_liquido)}</h3></div>', unsafe_allow_html=True)
        else:
            # Eu devo pra ela (saldo negativo = eu devo)
            st.markdown(f'<div class="{cor_card}"><h4>Voce deve pra {outro}</h4><h2>{fmt(abs(saldo_liquido))}</h2></div>', unsafe_allow_html=True)

        # Botao de acertar (so aparece pra quem deve)
        if abs(saldo_liquido) >= 0.01:
            st.markdown("")
            quem_paga = user if saldo_liquido < 0 else outro
            quem_recebe = outro if saldo_liquido < 0 else user

            if quem_paga == user and st.button(f"✅ Acertar (Pagar {fmt(abs(saldo_liquido))} pra {quem_recebe})", use_container_width=True, type="primary"):
                # Registra o acerto
                colls["quitacoes"].insert_one({
                    "tipo": "acerto",
                    "data": datetime.now(),
                    "de": quem_paga,
                    "para": quem_recebe,
                    "valor": abs(saldo_liquido),
                    "itens_quitados": {
                        "user_devia": user_deve_bruto,
                        "outro_devia": outro_deve_bruto
                    }
                })

                # Quita TODOS os itens em aberto (de ambas)
                colls["despesas"].update_many(
                    {"status_pendencia": "em aberto"},
                    {"$set": {"status_pendencia": "quitado", "data_quitacao": datetime.now()}}
                )
                colls["emprestimos"].update_many(
                    {"status": "em aberto"},
                    {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                )
                colls["quitacoes"].update_many(
                    {"status": "em aberto", "tipo": "despesa_compartilhada"},
                    {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                )

                limpar_cache_dados()
                st.success(f"✅ Acertado! {quem_paga} pagou {fmt(abs(saldo_liquido))} pra {quem_recebe}")
                st.balloons()
                st.rerun()

        st.markdown("")


        # Mostra resumo
        st.markdown(f'''
        <div style="display: flex; gap: 8px; margin-bottom: 10px;">
            <div style="flex: 1; background: rgba(233,30,99,0.2); padding: 6px; border-radius: 6px; text-align: center;">
                <span style="font-size: 11px; color: #f48fb1;">Voce deve</span><br>
                <span style="font-size: 14px; color: white; font-weight: 600;">{fmt(user_deve_bruto)}</span>
            </div>
            <div style="flex: 1; background: rgba(3,169,244,0.2); padding: 6px; border-radius: 6px; text-align: center;">
                <span style="font-size: 11px; color: #4fc3f7;">{outro} deve</span><br>
                <span style="font-size: 14px; color: white; font-weight: 600;">{fmt(outro_deve_bruto)}</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # Lista de itens pendentes (todos juntos para referencia)
        todas_pendencias = []

        # Minhas pendencias
        if not df_logs.empty and "tipo" in df_logs.columns and "status" in df_logs.columns:
            logs_user = df_logs[(df_logs["tipo"] == "despesa_compartilhada") & (df_logs["status"] == "em aberto") & (df_logs["devedor"] == user)]
            for _, log in logs_user.iterrows():
                todas_pendencias.append({
                    "quem": "Voce",
                    "descricao": log.get("descricao", "-"),
                    "valor": log["valor"],
                    "data": log["data"].strftime("%d/%m") if pd.notna(log.get("data")) else ""
                })

        # Pendencias da outra
        if not df_logs.empty and "tipo" in df_logs.columns and "status" in df_logs.columns:
            logs_outro = df_logs[(df_logs["tipo"] == "despesa_compartilhada") & (df_logs["status"] == "em aberto") & (df_logs["devedor"] == outro)]
            for _, log in logs_outro.iterrows():
                todas_pendencias.append({
                    "quem": outro,
                    "descricao": log.get("descricao", "-"),
                    "valor": log["valor"],
                    "data": log["data"].strftime("%d/%m") if pd.notna(log.get("data")) else ""
                })

        # Emprestimos
        if not df_emp.empty:
            emp_user = df_emp[(df_emp["status"] == "em aberto") & (df_emp["devedor"] == user)]
            for _, emp in emp_user.iterrows():
                todas_pendencias.append({
                    "quem": "Voce",
                    "descricao": f"Emp: {emp.get('motivo', '-')}",
                    "valor": emp["valor"],
                    "data": emp["createdAt"].strftime("%d/%m") if pd.notna(emp.get("createdAt")) else ""
                })

            emp_outro = df_emp[(df_emp["status"] == "em aberto") & (df_emp["devedor"] == outro)]
            for _, emp in emp_outro.iterrows():
                todas_pendencias.append({
                    "quem": outro,
                    "descricao": f"Emp: {emp.get('motivo', '-')}",
                    "valor": emp["valor"],
                    "data": emp["createdAt"].strftime("%d/%m") if pd.notna(emp.get("createdAt")) else ""
                })

        if todas_pendencias:
            with st.expander(f"📝 Itens pendentes ({len(todas_pendencias)})", expanded=False):
                for pend in todas_pendencias:
                    cor_tag = "#e91e63" if pend["quem"] == "Voce" else "#03a9f4"
                    st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 6px 8px; border-radius: 4px; margin-bottom: 4px; border-left: 2px solid {cor_tag}; overflow: hidden;">
                        <div style="font-size: 12px; color: white; word-break: break-word;">{pend["descricao"]}</div>
                        <div style="font-size: 11px; color: #aaa;">{fmt(pend["valor"])} | {pend["data"]}</div>
                    </div>''', unsafe_allow_html=True)
        else:
            st.caption("Nenhum item pendente")

        # Historico de acertos
        if not df_logs.empty and "tipo" in df_logs.columns:
            acertos = df_logs[df_logs["tipo"] == "acerto"]
            if not acertos.empty:
                with st.expander("📜 Historico de acertos", expanded=False):
                    acertos = acertos.sort_values("data", ascending=False)
                    for _, acerto in acertos.head(10).iterrows():
                        data_str = acerto["data"].strftime("%d/%m/%Y") if pd.notna(acerto.get("data")) else ""
                        st.caption(f"• {acerto.get('de', '?')} pagou {fmt(acerto['valor'])} pra {acerto.get('para', '?')} | {data_str}")

        # ========== EMPRESTIMOS A TERCEIROS ==========
        st.markdown("---")
        st.markdown('<p class="section-title">🤝 Emprestimos a Terceiros</p>', unsafe_allow_html=True)

        # Busca emprestimos a terceiros do usuario atual (da nova collection)
        df_terceiros = pd.DataFrame(carregar_emprestimos_terceiros(colls, user))

        if not df_terceiros.empty:
            # Calcula total
            total_terceiros = df_terceiros["valor"].sum()
            st.markdown(f'<div style="background: rgba(156,39,176,0.2); padding: 8px; border-radius: 6px; text-align: center; margin-bottom: 10px;"><span style="font-size: 12px; color: #ce93d8;">Total a receber</span><br><span style="font-size: 18px; color: white; font-weight: 600;">{fmt(total_terceiros)}</span></div>', unsafe_allow_html=True)

            for i, (_, emp) in enumerate(df_terceiros.iterrows()):
                # Formata datas
                data_emp = emp["data_emprestimo"].strftime("%d/%m") if pd.notna(emp.get("data_emprestimo")) else ""
                data_dev = emp["data_devolucao"].strftime("%d/%m") if pd.notna(emp.get("data_devolucao")) else ""

                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 6px; margin-bottom: 4px; border-left: 2px solid #9c27b0; overflow: hidden;">
                        <div style="font-size: 14px; color: #ce93d8; font-weight: 600;">{emp["devedor"]}</div>
                        <div style="font-size: 12px; color: #aaa; word-break: break-word;">{emp.get("descricao", "-")}</div>
                        <div style="font-size: 14px; color: white;">{fmt(emp["valor"])} <span style="font-size: 10px; color: #888;">| {data_emp} - {data_dev}</span></div>
                    </div>''', unsafe_allow_html=True)
                with col2:
                    if st.button("✅", key=f"quitar_terceiro_{i}", help="Recebido"):
                        colls["emprestimos_terceiros"].update_one(
                            {"_id": emp["_id"]},
                            {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                        )
                        limpar_cache_dados()
                        st.rerun()
        else:
            st.caption("Nenhum emprestimo a terceiros")

        # ========== MINHAS DIVIDAS A TERCEIROS ==========
        st.markdown("---")
        st.markdown('<p class="section-title">💸 Minhas Dividas</p>', unsafe_allow_html=True)

        df_dividas = pd.DataFrame(carregar_dividas_terceiros(colls, user))

        if not df_dividas.empty:
            # Separa dividas normais e emprestimos pessoais
            df_dividas_pessoas = df_dividas[df_dividas.get("emprestimo_conta", pd.Series([False] * len(df_dividas))).fillna(False) == False]
            df_emp_pessoal = df_dividas[df_dividas.get("emprestimo_conta", pd.Series([False] * len(df_dividas))).fillna(False) == True]

            total_dividas = df_dividas["valor"].sum()
            st.markdown(f'<div style="background: rgba(244,67,54,0.2); padding: 8px; border-radius: 6px; text-align: center; margin-bottom: 10px;"><span style="font-size: 12px; color: #ef9a9a;">Total que devo</span><br><span style="font-size: 18px; color: white; font-weight: 600;">{fmt(total_dividas)}</span></div>', unsafe_allow_html=True)

            # Primeiro mostra dividas a terceiros (pessoas)
            if not df_dividas_pessoas.empty:
                st.caption("👥 Terceiros")
                for i, (_, div) in enumerate(df_dividas_pessoas.iterrows()):
                    data_emp = div["data_emprestimo"].strftime("%d/%m") if pd.notna(div.get("data_emprestimo")) else ""
                    data_pag = div["data_pagamento"].strftime("%d/%m") if pd.notna(div.get("data_pagamento")) else ""

                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 6px; margin-bottom: 4px; border-left: 2px solid #f44336; overflow: hidden;">
                            <div style="font-size: 14px; color: #ef9a9a; font-weight: 600;">{div["credor"]}</div>
                            <div style="font-size: 12px; color: #aaa; word-break: break-word;">{div.get("descricao", "-")}</div>
                            <div style="font-size: 14px; color: white;">{fmt(div["valor"])} <span style="font-size: 10px; color: #888;">| {data_emp} - {data_pag}</span></div>
                        </div>''', unsafe_allow_html=True)
                    with col2:
                        if st.button("✅", key=f"quitar_divida_{i}", help="Paguei"):
                            colls["dividas_terceiros"].update_one(
                                {"_id": div["_id"]},
                                {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                            )
                            limpar_cache_dados()
                            st.rerun()

            # Depois mostra emprestimos pessoais (contas)
            if not df_emp_pessoal.empty:
                st.markdown("")
                st.markdown("")
                st.caption("🏦 Emprestimos Pessoais")
                for i, (_, div) in enumerate(df_emp_pessoal.iterrows()):
                    data_emp = div["data_emprestimo"].strftime("%d/%m") if pd.notna(div.get("data_emprestimo")) else ""
                    data_pag = div["data_pagamento"].strftime("%d/%m") if pd.notna(div.get("data_pagamento")) else ""

                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 6px; margin-bottom: 4px; border-left: 2px solid #8d6e63; overflow: hidden;">
                            <div style="font-size: 14px; color: #bcaaa4; font-weight: 600;">{div["credor"]}</div>
                            <div style="font-size: 12px; color: #aaa; word-break: break-word;">{div.get("descricao", "-")}</div>
                            <div style="font-size: 14px; color: white;">{fmt(div["valor"])} <span style="font-size: 10px; color: #888;">| {data_emp} - {data_pag}</span></div>
                        </div>''', unsafe_allow_html=True)
                    with col2:
                        if st.button("✅", key=f"quitar_emp_pessoal_{i}", help="Devolvi"):
                            # Marca como quitado
                            colls["dividas_terceiros"].update_one(
                                {"_id": div["_id"]},
                                {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                            )
                            # Registra como despesa (dinheiro saiu da conta corrente pra poupanca)
                            colls["despesas"].insert_one({
                                "label": "🏦 Poupanca",
                                "buyer": user,
                                "item": f"Devolucao - {div['credor']}",
                                "description": div.get("descricao", ""),
                                "quantity": 1,
                                "total_value": div["valor"],
                                "payment_method": "Debito",
                                "installment": 0,
                                "createdAt": datetime.now(),
                                "pagamento_compartilhado": "👤 Pra mim",
                                "tem_pendencia": False,
                                "devedor": None,
                                "valor_pendente": None,
                                "status_pendencia": None,
                                "origem": "emprestimo_pessoal"
                            })
                            limpar_cache_dados()
                            st.rerun()
        else:
            st.caption("Nenhuma divida")

        # ========== CONTAS FIXAS (NAO CREDITO) ==========
        st.markdown("---")
        st.markdown('<p class="section-title">📋 Contas Fixas do Mes - Pgto Manual</p>', unsafe_allow_html=True)

        df_contas_fixas = pd.DataFrame(carregar_contas_fixas(colls))
        hoje = date.today()
        mes_ano_atual = f"{hoje.year}-{hoje.month:02d}"

        if not df_contas_fixas.empty:
            # Filtra contas fixas do usuario que NAO sao de cartao de credito
            contas_nao_credito = []
            for _, conta in df_contas_fixas.iterrows():
                is_credito = conta.get("cartao_credito", False)
                if not is_credito:
                    if conta["responsavel"] == user:
                        contas_nao_credito.append({
                            "_id": conta["_id"],
                            "nome": conta["nome"],
                            "valor": conta["valor"],
                            "dia_vencimento": conta["dia_vencimento"],
                            "categoria": conta.get("categoria", ""),
                            "meu_valor": conta["valor"]
                        })
                    elif conta["responsavel"] == "Dividido":
                        contas_nao_credito.append({
                            "_id": conta["_id"],
                            "nome": conta["nome"],
                            "valor": conta["valor"],
                            "dia_vencimento": conta["dia_vencimento"],
                            "categoria": conta.get("categoria", ""),
                            "meu_valor": conta["valor"] / 2
                        })

            if contas_nao_credito:
                # Busca quais contas ja foram pagas este mes
                df_pagamentos = pd.DataFrame(carregar_pagamentos_contas_fixas(colls, user, mes_ano_atual))
                contas_pagas_ids = set(df_pagamentos["conta_fixa_id"].astype(str).tolist()) if not df_pagamentos.empty and "conta_fixa_id" in df_pagamentos.columns else set()

                total_contas_fixas = sum(c["meu_valor"] for c in contas_nao_credito)
                total_pagas = sum(c["meu_valor"] for c in contas_nao_credito if str(c["_id"]) in contas_pagas_ids)
                total_pendentes = total_contas_fixas - total_pagas

                st.markdown(f'''
                <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                    <div style="flex: 1; background: rgba(76,175,80,0.2); padding: 6px; border-radius: 6px; text-align: center;">
                        <span style="font-size: 11px; color: #81c784;">Pagas</span><br>
                        <span style="font-size: 14px; color: white; font-weight: 600;">{fmt(total_pagas)}</span>
                    </div>
                    <div style="flex: 1; background: rgba(255,152,0,0.2); padding: 6px; border-radius: 6px; text-align: center;">
                        <span style="font-size: 11px; color: #ffcc80;">Pendentes</span><br>
                        <span style="font-size: 14px; color: white; font-weight: 600;">{fmt(total_pendentes)}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

                for i, conta in enumerate(contas_nao_credito):
                    ja_paga = str(conta["_id"]) in contas_pagas_ids
                    cor_borda = "#4caf50" if ja_paga else "#ff9800"
                    icone_status = "✅" if ja_paga else "⏳"

                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 6px; margin-bottom: 4px; border-left: 2px solid {cor_borda}; overflow: hidden;">
                            <div style="font-size: 14px; color: white; font-weight: 600;">{icone_status} {conta["nome"]}</div>
                            <div style="font-size: 12px; color: #aaa;">{conta["categoria"]}</div>
                            <div style="font-size: 14px; color: white;">{fmt(conta["meu_valor"])} <span style="font-size: 10px; color: #888;">| Vence dia {int(conta["dia_vencimento"])}</span></div>
                        </div>''', unsafe_allow_html=True)
                    with col2:
                        if not ja_paga:
                            if st.button("✅", key=f"pagar_conta_fixa_{i}", help="Marcar como paga"):
                                # Registra pagamento da conta fixa
                                colls["quitacoes"].insert_one({
                                    "tipo": "conta_fixa",
                                    "conta_fixa_id": conta["_id"],
                                    "pagador": user,
                                    "valor": conta["meu_valor"],
                                    "nome_conta": conta["nome"],
                                    "mes_ano": mes_ano_atual,
                                    "data": datetime.now()
                                })
                                # Registra como despesa
                                colls["despesas"].insert_one({
                                    "label": conta["categoria"] if conta["categoria"] in ["📄 Contas", "💊 Saude", "📦 Outros"] else "📄 Contas",
                                    "buyer": user,
                                    "item": conta["nome"],
                                    "description": "Conta fixa mensal",
                                    "quantity": 1,
                                    "total_value": conta["meu_valor"],
                                    "payment_method": "Debito",
                                    "installment": 0,
                                    "createdAt": datetime.now(),
                                    "pagamento_compartilhado": "👤 Pra mim",
                                    "tem_pendencia": False,
                                    "devedor": None,
                                    "valor_pendente": None,
                                    "status_pendencia": None,
                                    "origem": "conta_fixa"
                                })
                                limpar_cache_dados()
                                st.rerun()
                        else:
                            st.markdown('<span style="color: #4caf50; font-size: 14px;">Paga</span>', unsafe_allow_html=True)
            else:
                st.caption("Nenhuma conta fixa (fora do cartao)")
        else:
            st.caption("Nenhuma conta fixa cadastrada")

    # ========== METAS ==========
    elif menu == "🎯 Metas":
        st.markdown('<p class="page-title">🎯 Minhas Metas</p>', unsafe_allow_html=True)

        st.markdown("---")

        with st.expander("➕ Criar Nova Meta", expanded=False):
            with st.form("form_meta", clear_on_submit=True):
                categoria_meta = st.selectbox("🏷️ Categoria", ["🍔 Comida", "🛒 Mercado", "⛽ Combustivel", "🚗 Automoveis", "🍺 Bebidas", "👗 Vestuario", "💊 Saude", "🎮 Lazer", "📄 Contas", "👨‍👩‍👧 Boa pra familia", "📦 Outros", "💰 Total Geral"])
                valor_meta = st.number_input("💵 Limite mensal", min_value=1.00, value=500.00, format="%.2f")

                if st.form_submit_button("✅ Criar Meta", use_container_width=True):
                    colls["metas"].insert_one({"categoria": categoria_meta, "pessoa": user, "limite": valor_meta, "ativo": True, "createdAt": datetime.now()})
                    limpar_cache_dados()
                    st.success("✅ Meta criada!")
                    st.rerun()

        df_metas = pd.DataFrame(carregar_metas(colls, user))
        df_desp = pd.DataFrame(carregar_despesas(colls))

        if not df_metas.empty and not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])

            # Periodo baseado no fechamento da fatura
            data_inicio, data_fim = get_periodo_fatura(colls, user)

            df_mes = df_desp[
                (df_desp["buyer"] == user) &
                (df_desp["createdAt"].dt.date >= data_inicio) &
                (df_desp["createdAt"].dt.date <= data_fim)
            ]

            st.markdown(f'<p style="font-size: 10px; text-align: center; color: #888; margin-bottom: 8px;">Fatura: {data_inicio.strftime("%d/%m")} a {data_fim.strftime("%d/%m")}</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-title">📊 Meu Progresso</p>', unsafe_allow_html=True)

            for _, meta in df_metas.iterrows():
                cat, limite = meta["categoria"], meta["limite"]

                gasto = df_mes["total_value"].sum() if "Total" in cat else (df_mes[df_mes["label"] == cat]["total_value"].sum() if not df_mes.empty else 0)

                pct = min((gasto / limite) * 100, 100) if limite > 0 else 0
                restante = max(limite - gasto, 0)

                st.caption(f"**{cat}**")
                st.progress(pct / 100)
                st.caption(f"💸 {fmt(gasto)} | 🎯 {fmt(limite)} | 💰 {fmt(restante)}")

                if pct >= 100:
                    st.warning("⚠️ Meta ultrapassada!")
                elif pct >= 80:
                    st.info("⚡ Proximo do limite!")
                st.markdown("---")
        else:
            st.info("📝 Crie metas para acompanhar!")

    # ========== AMBAS (visao compartilhada) ==========
    elif menu == "👯 Ambas":
        st.markdown('<p class="page-title">👯 Gastos Conjuntos</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(carregar_despesas(colls))

        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])

            # Determina periodo baseado no fechamento da fatura
            data_inicio, data_fim = get_periodo_fatura(colls, user)

            # Mostra periodo
            st.markdown(f'<p style="font-size: 10px; text-align: center; color: #888; margin-bottom: 8px;">Periodo: {data_inicio.strftime("%d/%m")} a {data_fim.strftime("%d/%m")}</p>', unsafe_allow_html=True)

            # Filtra gastos divididos no periodo
            df_dividido = df_desp[df_desp["pagamento_compartilhado"].str.contains("Dividido", na=False)]
            df_dividido_periodo = df_dividido[
                (df_dividido["createdAt"].dt.date >= data_inicio) &
                (df_dividido["createdAt"].dt.date <= data_fim)
            ]

            if not df_dividido_periodo.empty:
                # Total gasto junto
                total_dividido = df_dividido_periodo["total_value"].sum()
                gasto_su = df_dividido_periodo[df_dividido_periodo["buyer"] == "Susanna"]["total_value"].sum()
                gasto_pi = df_dividido_periodo[df_dividido_periodo["buyer"] == "Pietrah"]["total_value"].sum()

                # Card principal - total dividido
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%); padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
                    <span style="font-size: 12px; color: #ce93d8;">👯 Total Gasto Junto</span>
                    <h2 style="margin: 4px 0; font-size: 22px; color: white; font-weight: 600;">{fmt(total_dividido)}</h2>
                    <span style="font-size: 11px; color: #ce93d8;">Cada uma: {fmt(total_dividido/2)}</span>
                </div>
                ''', unsafe_allow_html=True)

                # Cards de quem pagou o que
                st.markdown(f'''
                <div style="display: flex; flex-direction: row; gap: 6px; width: 100%; margin-bottom: 12px;">
                    <div style="flex: 1; background: linear-gradient(135deg, #c2185b 0%, #e91e63 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #f48fb1; text-align: center;">
                        <span style="font-size: 10px; opacity: 0.9;">⚡ Susanna pagou</span><br>
                        <span style="font-size: 14px; font-weight: 600;">{fmt(gasto_su)}</span>
                    </div>
                    <div style="flex: 1; background: linear-gradient(135deg, #0277bd 0%, #03a9f4 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #4fc3f7; text-align: center;">
                        <span style="font-size: 10px; opacity: 0.9;">👩 Pietrah pagou</span><br>
                        <span style="font-size: 14px; font-weight: 600;">{fmt(gasto_pi)}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

                st.markdown("---")

                # Grafico por categoria
                st.markdown('<p style="font-size: 12px; text-align: center; margin: 4px 0 8px 0; font-weight: 500;">📊 Por Categoria</p>', unsafe_allow_html=True)

                cat_dividido = df_dividido_periodo.groupby("label")["total_value"].sum().sort_values(ascending=False)
                max_cat = cat_dividido.max() if not cat_dividido.empty else 1

                cores_cat = ['#9c27b0', '#7b1fa2', '#6a1b9a', '#4a148c', '#ea80fc', '#e040fb', '#d500f9', '#aa00ff']
                for i, (cat, val) in enumerate(cat_dividido.items()):
                    pct = (val / max_cat) * 100
                    pct_total = (val / total_dividido) * 100
                    cor = cores_cat[i % len(cores_cat)]
                    st.markdown(f'''
                    <div style="margin-bottom: 6px;">
                        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #ccc; margin-bottom: 2px;">
                            <span>{cat}</span>
                            <span>{fmt(val)} ({pct_total:.0f}%)</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); border-radius: 4px; height: 8px; overflow: hidden;">
                            <div style="background: {cor}; width: {pct}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown("---")

                # Detalhamento dos gastos
                st.markdown('<p style="font-size: 12px; text-align: center; margin: 4px 0 8px 0; font-weight: 500;">📋 Detalhamento</p>', unsafe_allow_html=True)

                df_ordenado = df_dividido_periodo.sort_values("createdAt", ascending=False)
                for _, gasto in df_ordenado.iterrows():
                    data_str = gasto["createdAt"].strftime("%d/%m")
                    item_desc = gasto.get("item", "") or gasto.get("description", "") or "-"
                    cor_borda = "#e91e63" if gasto["buyer"] == "Susanna" else "#03a9f4"
                    icone = "⚡" if gasto["buyer"] == "Susanna" else "👩"

                    st.markdown(f'''
                    <div style="background: rgba(255,255,255,0.05); padding: 6px 8px; border-radius: 6px; margin-bottom: 4px; border-left: 2px solid {cor_borda};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 10px; color: #aaa;">{gasto["label"]}</span><br>
                                <span style="font-size: 11px; color: white;">{item_desc}</span>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 12px; color: white; font-weight: 600;">{fmt(gasto["total_value"])}</span><br>
                                <span style="font-size: 9px; color: #888;">{icone} {data_str}</span>
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.info("📝 Nenhum gasto dividido neste periodo.")
        else:
            st.info("📝 Sem gastos ainda.")

    # ========== RELATORIO ==========
    elif menu == "📊 Relatorio":
        st.markdown('<p class="page-title">📊 Meu Relatorio</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(carregar_despesas(colls))
        df_contas_fixas = pd.DataFrame(carregar_contas_fixas(colls))

        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            df_desp["dia_semana"] = df_desp["createdAt"].dt.dayofweek
            df_desp["dia"] = df_desp["createdAt"].dt.day

            # Periodo baseado no fechamento da fatura
            data_inicio, data_fim = get_periodo_fatura(colls, user)

            # Filtra pelo periodo da fatura
            df_user = df_desp[
                (df_desp["buyer"] == user) &
                (df_desp["createdAt"].dt.date >= data_inicio) &
                (df_desp["createdAt"].dt.date <= data_fim)
            ]

            # Filtra gastos reais (sem Cofrinho, Renda Variavel e contas fixas pagas - evita duplicacao)
            df_user_gastos = df_user[~df_user["label"].str.contains("Cofrinho|Renda Variavel", na=False)]
            if "origem" in df_user_gastos.columns:
                df_user_gastos = df_user_gastos[df_user_gastos["origem"].fillna("") != "conta_fixa"]

            # Calcula totais de contas fixas do usuario
            user_fixas = 0
            if not df_contas_fixas.empty:
                user_fixas = df_contas_fixas[df_contas_fixas["responsavel"] == user]["valor"].sum()
                divididas = df_contas_fixas[df_contas_fixas["responsavel"] == "Dividido"]["valor"].sum()
                user_fixas += divididas / 2

            # Totais
            total_var = df_user_gastos["total_value"].sum() if not df_user_gastos.empty else 0

            # Soma emprestimos a terceiros (do periodo atual)
            df_emprestimos_terceiros_rel = pd.DataFrame(carregar_emprestimos_terceiros_periodo(colls, user, data_inicio, data_fim))
            total_emprestei = df_emprestimos_terceiros_rel["valor"].sum() if not df_emprestimos_terceiros_rel.empty else 0

            total_geral = total_var + user_fixas + total_emprestei

            # ========== RESUMO DA FATURA ==========
            st.markdown(f'<p style="font-size: 10px; text-align: center; color: #888; margin-bottom: 8px;">Fatura: {data_inicio.strftime("%d/%m")} a {data_fim.strftime("%d/%m")}</p>', unsafe_allow_html=True)
            st.markdown(f'''
            <div style="background: linear-gradient(135deg, {'#c2185b' if user == 'Susanna' else '#0277bd'} 0%, {'#e91e63' if user == 'Susanna' else '#03a9f4'} 100%); padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
                <span style="font-size: 11px; color: rgba(255,255,255,0.8);">Total do mês</span>
                <h2 style="margin: 4px 0; font-size: 24px; color: white; font-weight: 600;">{fmt(total_geral)}</h2>
                <span style="font-size: 10px; color: rgba(255,255,255,0.7);">Variaveis: {fmt(total_var)} | Fixas: {fmt(user_fixas)}</span>
            </div>
            ''', unsafe_allow_html=True)

            # ========== METRICAS DE HABITOS ==========
            if not df_user_gastos.empty:
                # Calculos
                dias_com_gasto = df_user_gastos["createdAt"].dt.date.nunique()
                num_compras = len(df_user_gastos)
                media_por_compra = total_var / num_compras if num_compras > 0 else 0

                # Dias no periodo da fatura
                dias_no_periodo = (data_fim - data_inicio).days + 1
                media_diaria = total_var / dias_no_periodo if dias_no_periodo > 0 else 0

                # Dia da semana que mais gasta
                dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
                gastos_por_dia = df_user_gastos.groupby("dia_semana")["total_value"].sum()
                dia_mais_gasto = dias_semana[gastos_por_dia.idxmax()] if not gastos_por_dia.empty else "-"
                valor_dia_mais = gastos_por_dia.max() if not gastos_por_dia.empty else 0

                st.markdown("---")
                st.markdown('<p style="font-size: 12px; text-align: center; margin: 4px 0 8px 0; font-weight: 500;">📈 Seus Habitos</p>', unsafe_allow_html=True)

                # Cards de metricas
                st.markdown(f'''
                <div style="display: flex; flex-direction: row; gap: 6px; width: 100%; margin-bottom: 8px;">
                    <div style="flex: 1; background: rgba(255,255,255,0.05); padding: 6px; border-radius: 6px; text-align: center;">
                        <span style="font-size: 10px; color: #aaa;">Media/dia</span><br>
                        <span style="font-size: 14px; color: white; font-weight: 600;">{fmt(media_diaria)}</span>
                    </div>
                    <div style="flex: 1; background: rgba(255,255,255,0.05); padding: 6px; border-radius: 6px; text-align: center;">
                        <span style="font-size: 10px; color: #aaa;">Media/compra</span><br>
                        <span style="font-size: 14px; color: white; font-weight: 600;">{fmt(media_por_compra)}</span>
                    </div>
                    <div style="flex: 1; background: rgba(255,255,255,0.05); padding: 6px; border-radius: 6px; text-align: center;">
                        <span style="font-size: 10px; color: #aaa;">Compras</span><br>
                        <span style="font-size: 14px; color: white; font-weight: 600;">{num_compras}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

                st.markdown(f'''
                <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; text-align: center; margin-bottom: 8px;">
                    <span style="font-size: 10px; color: #aaa;">Dia que mais gasta</span><br>
                    <span style="font-size: 14px; color: white; font-weight: 600;">{dia_mais_gasto}</span>
                    <span style="font-size: 11px; color: #888;"> ({fmt(valor_dia_mais)})</span>
                </div>
                ''', unsafe_allow_html=True)

                # Grafico por dia da semana
                st.markdown('<p style="font-size: 11px; text-align: center; margin: 8px 0 4px 0; color: #888;">Gastos por dia da semana</p>', unsafe_allow_html=True)
                max_dia = gastos_por_dia.max() if not gastos_por_dia.empty else 1
                for i, dia in enumerate(dias_semana):
                    val = gastos_por_dia.get(i, 0)
                    pct = (val / max_dia * 100) if max_dia > 0 else 0
                    cor = '#e91e63' if user == 'Susanna' else '#03a9f4'
                    st.markdown(f'''
                    <div style="display: flex; align-items: center; margin-bottom: 3px;">
                        <span style="font-size: 10px; color: #888; width: 30px;">{dia}</span>
                        <div style="flex: 1; background: rgba(255,255,255,0.1); border-radius: 3px; height: 6px; overflow: hidden; margin: 0 6px;">
                            <div style="background: {cor}; width: {pct}%; height: 100%;"></div>
                        </div>
                        <span style="font-size: 9px; color: #aaa; width: 55px; text-align: right;">{fmt(val)}</span>
                    </div>
                    ''', unsafe_allow_html=True)

            # ========== CONTROLE DE CARTAO ==========
            st.markdown("---")
            st.markdown('<p style="font-size: 12px; text-align: center; margin: 4px 0 8px 0; font-weight: 500;">💳 Controle de Cartao</p>', unsafe_allow_html=True)

            # Gastos no credito do mes
            credito_mes = df_user[df_user["payment_method"] == "Credito"]["total_value"].sum()

            # Parcelas futuras (de meses anteriores)
            df_user_todos = df_desp[df_desp["buyer"] == user]
            df_parcelados = df_user_todos[(df_user_todos["payment_method"] == "Credito") & (df_user_todos["installment"] > 1)]

            parcelas_a_vencer = 0
            if not df_parcelados.empty:
                hoje = date.today()
                for _, compra in df_parcelados.iterrows():
                    parcelas_total = compra["installment"]
                    valor_parcela = compra["total_value"] / parcelas_total
                    data_compra = compra["createdAt"].date()

                    # Quantas parcelas ja passaram
                    meses_passados = (hoje.year - data_compra.year) * 12 + (hoje.month - data_compra.month)
                    parcelas_restantes = max(0, parcelas_total - meses_passados - 1)
                    parcelas_a_vencer += valor_parcela * parcelas_restantes

            # Previsao da fatura (credito do periodo + parcelas de compras anteriores)
            parcelas_este_mes = 0
            parcelas_prox_mes = 0
            hoje = date.today()
            if not df_parcelados.empty:
                # Calcula proximo mes baseado no periodo da fatura
                if data_fim.month == 12:
                    prox_mes = date(data_fim.year + 1, 1, 15)
                else:
                    prox_mes = date(data_fim.year, data_fim.month + 1, 15)

                for _, compra in df_parcelados.iterrows():
                    parcelas_total = compra["installment"]
                    valor_parcela = compra["total_value"] / parcelas_total
                    data_compra = compra["createdAt"].date()

                    # Verifica se alguma parcela cai no periodo atual
                    for p in range(int(parcelas_total)):
                        mes_parcela = data_compra.month + p
                        ano_parcela = data_compra.year + (mes_parcela - 1) // 12
                        mes_parcela = ((mes_parcela - 1) % 12) + 1
                        try:
                            data_parcela = date(ano_parcela, mes_parcela, 15)
                        except:
                            continue
                        if data_inicio <= data_parcela <= data_fim:
                            parcelas_este_mes += valor_parcela
                        elif data_fim < data_parcela <= prox_mes:
                            parcelas_prox_mes += valor_parcela

            # Compras a vista no credito
            credito_avista = 0
            if not df_user.empty:
                credito_avista = df_user[(df_user["payment_method"] == "Credito") & ((df_user["installment"] == 0) | (df_user["installment"] == 1))]["total_value"].sum()

            # Contas fixas no cartao de credito
            contas_fixas_credito = 0
            if not df_contas_fixas.empty:
                for _, conta in df_contas_fixas.iterrows():
                    if conta.get("cartao_credito", False):
                        if conta["responsavel"] == user:
                            contas_fixas_credito += conta["valor"]
                        elif conta["responsavel"] == "Dividido":
                            contas_fixas_credito += conta["valor"] / 2

            fatura_estimada = credito_avista + parcelas_este_mes + contas_fixas_credito
            fatura_prox_mes = parcelas_prox_mes + contas_fixas_credito

            # Compromisso = parcelas restantes + contas fixas de credito (compromisso mensal recorrente)
            compromisso_total = parcelas_a_vencer + contas_fixas_credito

            st.markdown(f'''
            <div style="display: flex; flex-direction: row; gap: 6px; width: 100%; margin-bottom: 8px;">
                <div style="flex: 1; background: rgba(156,39,176,0.2); padding: 6px; border-radius: 6px; text-align: center;">
                    <span style="font-size: 10px; color: #ce93d8;">Fatura estimada</span><br>
                    <span style="font-size: 16px; color: white; font-weight: 600;">{fmt(fatura_estimada)}</span>
                </div>
                <div style="flex: 1; background: rgba(0,150,136,0.2); padding: 6px; border-radius: 6px; text-align: center;">
                    <span style="font-size: 10px; color: #80cbc4;">Prox. mes</span><br>
                    <span style="font-size: 16px; color: white; font-weight: 600;">{fmt(fatura_prox_mes)}</span>
                </div>
                <div style="flex: 1; background: rgba(255,152,0,0.2); padding: 6px; border-radius: 6px; text-align: center;">
                    <span style="font-size: 10px; color: #ffcc80;">Compromisso</span><br>
                    <span style="font-size: 16px; color: white; font-weight: 600;">{fmt(compromisso_total)}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            # Detalhes das parcelas
            if not df_parcelados.empty:
                compras_ativas = []
                for _, compra in df_parcelados.iterrows():
                    parcelas_total = compra["installment"]
                    data_compra = compra["createdAt"].date()
                    meses_passados = (date.today().year - data_compra.year) * 12 + (date.today().month - data_compra.month)
                    parcela_atual = min(meses_passados + 1, parcelas_total)

                    if parcela_atual <= parcelas_total:
                        compras_ativas.append({
                            "item": compra.get("item", "") or compra.get("label", ""),
                            "valor_parcela": compra["total_value"] / parcelas_total,
                            "parcela_atual": parcela_atual,
                            "parcelas_total": parcelas_total
                        })

                if compras_ativas:
                    with st.expander(f"📋 Parcelas ativas ({len(compras_ativas)})", expanded=False):
                        for p in compras_ativas:
                            st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 6px 8px; border-radius: 4px; margin-bottom: 4px;">
                                <span style="font-size: 12px; color: white;">{p["item"]}</span>
                                <span style="font-size: 11px; color: #aaa; float: right;">{fmt(p["valor_parcela"])} ({p["parcela_atual"]}/{p["parcelas_total"]})</span>
                            </div>''', unsafe_allow_html=True)

            # ========== COMPRAS QUENTES ==========
            st.markdown("---")
            st.markdown('<p style="font-size: 12px; text-align: center; margin: 4px 0 8px 0; font-weight: 500;">🔥 Compras Quentes</p>', unsafe_allow_html=True)

            if not df_user_gastos.empty:
                # Top 3 maiores gastos do mes
                top_compras = df_user_gastos.nlargest(3, "total_value")

                medalhas = ["🥇", "🥈", "🥉"]
                for i, (_, compra) in enumerate(top_compras.iterrows()):
                    item = compra.get("item", "-")
                    categoria = compra.get("label", "-")
                    valor = compra["total_value"]
                    data_compra = compra["createdAt"].strftime("%d/%m")

                    st.markdown(f'''
                    <div style="background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #f44336;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 14px;">{medalhas[i]}</span>
                                <span style="font-size: 12px; color: white; font-weight: 500;"> {item}</span><br>
                                <span style="font-size: 10px; color: #888;">{categoria} | {data_compra}</span>
                            </div>
                            <div style="font-size: 14px; font-weight: 600; color: #f44336;">{fmt(valor)}</div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.caption("Sem compras no periodo")

            st.markdown("---")

            # ========== CONTAS FIXAS ==========
            if not df_contas_fixas.empty:
                contas_user = df_contas_fixas[
                    (df_contas_fixas["responsavel"] == user) |
                    (df_contas_fixas["responsavel"] == "Dividido")
                ]

                if not contas_user.empty:
                    with st.expander("📋 Minhas Contas Fixas", expanded=False):
                        for _, conta in contas_user.iterrows():
                            valor_meu = conta['valor'] / 2 if conta["responsavel"] == "Dividido" else conta['valor']
                            tipo = "🔷" if conta["responsavel"] == "Dividido" else "🔸"
                            st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 6px 8px; border-radius: 4px; margin-bottom: 4px; overflow: hidden;">
                                <div style="font-size: 12px; color: white;">{tipo} {conta['nome']}</div>
                                <div style="font-size: 11px; color: #aaa;">{fmt(valor_meu)} | Dia {int(conta['dia_vencimento'])}</div>
                            </div>''', unsafe_allow_html=True)
            

            # ========== MEUS GASTOS (PERIODO DA FATURA) ==========
            data_inicio, data_fim = get_periodo_fatura(colls, user)

            df_meus_gastos = df_desp[
                (df_desp["buyer"] == user) &
                (df_desp["createdAt"].dt.date >= data_inicio) &
                (df_desp["createdAt"].dt.date <= data_fim)
            ]
            df_meus_gastos = df_meus_gastos[~df_meus_gastos["label"].str.contains("Cofrinho|Renda Variavel", na=False)]
            # Exclui contas fixas (pagas ou nao) - elas ja aparecem no expander de contas fixas
            if "origem" in df_meus_gastos.columns:
                df_meus_gastos = df_meus_gastos[df_meus_gastos["origem"].fillna("") != "conta_fixa"]

            with st.expander(f"💸 Meus Gastos ", expanded=False):
                if not df_meus_gastos.empty:
                    df_meus_gastos = df_meus_gastos.sort_values("createdAt", ascending=False)
                    for _, gasto in df_meus_gastos.iterrows():
                        data_str = gasto["createdAt"].strftime("%d/%m")
                        item = gasto.get("item", "-")
                        categoria = gasto.get("label", "-")
                        valor = gasto["total_value"]
                        pagamento = gasto.get("payment_method", "-")
                        num_parcelas = gasto.get("installment", 0)

                        # Se for parcelamento (installment > 1), mostra "Parcelamento" e qual parcela atual
                        if pagamento == "Credito" and num_parcelas > 1:
                            pagamento = "Parcelamento"
                            data_compra = gasto["createdAt"].date()
                            meses_passados = (data_fim.year - data_compra.year) * 12 + (data_fim.month - data_compra.month)
                            parcela_atual = min(meses_passados + 1, int(num_parcelas))
                            data_str = f"{parcela_atual}/{int(num_parcelas)}"
                            valor = valor / num_parcelas  # Valor da parcela

                        st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 6px 8px; border-radius: 4px; margin-bottom: 4px; border-left: 2px solid {'#e91e63' if user == 'Susanna' else '#03a9f4'}; overflow: hidden;">
                            <div style="font-size: 12px; color: white; word-break: break-word;">{item}</div>
                            <div style="font-size: 11px; color: #aaa;">{categoria} | {pagamento} | {data_str}</div>
                            <div style="font-size: 13px; color: white; font-weight: 600;">{fmt(valor)}</div>
                        </div>''', unsafe_allow_html=True)
                else:
                    st.caption("Nenhum gasto no periodo")
        else:
            st.info("📝 Nenhum gasto registrado.")

    # ========== COMBUSTIVEL ==========
    elif menu == "⛽":
        st.markdown('<p class="page-title">⛽ Abastecimentos</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(carregar_despesas(colls))

        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])

            # Filtra apenas combustivel
            df_combustivel = df_desp[(df_desp["label"] == "⛽ Combustivel") | (df_desp["label"].str.contains("Combustivel", na=False))]

            if not df_combustivel.empty:
                # Cards de ultimo abastecimento
                st.markdown('<p class="section-title" style="font-size: 14px;">🏆 Ultimo Abastecimento</p>', unsafe_allow_html=True)

                # Ultimo abastecimento moto
                df_moto = df_combustivel[df_combustivel["item"].str.lower().str.contains("moto", na=False)]
                if not df_moto.empty:
                    ultimo_moto = df_moto.sort_values("createdAt", ascending=False).iloc[0]
                    moto_user = ultimo_moto["buyer"]
                    moto_data = ultimo_moto["createdAt"].strftime("%d/%m")
                    moto_valor = ultimo_moto["total_value"]
                else:
                    moto_user = "-"
                    moto_data = "-"
                    moto_valor = 0

                # Ultimo abastecimento carro
                df_carro = df_combustivel[df_combustivel["item"].str.lower().str.contains("carro", na=False)]
                if not df_carro.empty:
                    ultimo_carro = df_carro.sort_values("createdAt", ascending=False).iloc[0]
                    carro_user = ultimo_carro["buyer"]
                    carro_data = ultimo_carro["createdAt"].strftime("%d/%m")
                    carro_valor = ultimo_carro["total_value"]
                else:
                    carro_user = "-"
                    carro_data = "-"
                    carro_valor = 0

                # Cores por usuario
                cor_moto = "linear-gradient(135deg, #c2185b 0%, #e91e63 100%)" if moto_user == "Susanna" else "linear-gradient(135deg, #0277bd 0%, #03a9f4 100%)"
                borda_moto = "#f48fb1" if moto_user == "Susanna" else "#4fc3f7"
                cor_carro = "linear-gradient(135deg, #c2185b 0%, #e91e63 100%)" if carro_user == "Susanna" else "linear-gradient(135deg, #0277bd 0%, #03a9f4 100%)"
                borda_carro = "#f48fb1" if carro_user == "Susanna" else "#4fc3f7"

                st.markdown(f'''
                <div style="display: flex; flex-direction: row; gap: 6px; width: 100%;">
                    <div style="flex: 1; background: {cor_moto}; padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid {borda_moto};">
                        <span style="font-size: 14px; opacity: 0.9;">🏍️ Moto</span><br>
                        <span style="font-size: 11px;">{moto_user} | {moto_data}</span><br>
                        <span style="font-size: 12px; font-weight: 600;">{fmt(moto_valor)}</span>
                    </div>
                    <div style="flex: 1; background: {cor_carro}; padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid {borda_carro};">
                        <span style="font-size: 14px; opacity: 0.9;">🚗 Carro</span><br>
                        <span style="font-size: 11px;">{carro_user} | {carro_data}</span><br>
                        <span style="font-size: 12px; font-weight: 600;">{fmt(carro_valor)}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

                st.markdown("---")

                # Historico completo
                st.markdown('<p class="section-title" style="font-size: 14px;">📜 Historico</p>', unsafe_allow_html=True)

                df_combustivel_sorted = df_combustivel.sort_values("createdAt", ascending=False)

                for _, abast in df_combustivel_sorted.iterrows():
                    abast_user = abast["buyer"]
                    abast_data = abast["createdAt"].strftime("%d/%m/%Y")
                    abast_valor = abast["total_value"]
                    abast_tipo = abast.get("item", "Veiculo")
                    abast_pag = abast.get("payment_method", "-")

                    cor_abast = "#e91e63" if abast_user == "Susanna" else "#03a9f4"
                    emoji_veiculo = "🏍️" if "moto" in str(abast_tipo).lower() else "🚗"

                    st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid {cor_abast};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 14px; color: white;">{emoji_veiculo} {abast_tipo}</span><br>
                                <span style="font-size: 11px; color: #aaa;">{abast_user} | {abast_data} | {abast_pag}</span>
                            </div>
                            <div style="font-size: 14px; font-weight: 600; color: white;">{fmt(abast_valor)}</div>
                        </div>
                    </div>''', unsafe_allow_html=True)
            else:
                st.info("⛽ Nenhum abastecimento registrado ainda.")
        else:
            st.info("⛽ Nenhum abastecimento registrado ainda.")

    # ========== EVOLUCAO ==========
    elif menu == "📈 Evolucao":
        st.markdown('<p class="page-title">📈 Minha Evolucao</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(carregar_despesas(colls))
        df_contas_fixas = pd.DataFrame(carregar_contas_fixas(colls))

        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            df_desp["mes"] = df_desp["createdAt"].dt.to_period("M").astype(str)

            # Filtrar apenas meus gastos (sem cofrinho e renda variavel)
            df_user = df_desp[df_desp["buyer"] == user]
            df_user_gastos = df_user[~df_user["label"].str.contains("Cofrinho|Renda Variavel", na=False)]
            if "origem" in df_user_gastos.columns:
                df_user_gastos = df_user_gastos[df_user_gastos["origem"].fillna("") != "conta_fixa"]

            if not df_user.empty:
                # ========== COMPARATIVO COM MES ANTERIOR ==========
                st.markdown('<p class="section-title">📈 vs Mes Anterior</p>', unsafe_allow_html=True)

                # Periodo atual
                data_inicio, data_fim = get_periodo_fatura(colls, user)

                # Calcula periodo do mes anterior
                if data_inicio.month == 1:
                    mes_ant_inicio = date(data_inicio.year - 1, 12, data_inicio.day)
                    mes_ant_fim = date(data_fim.year - 1, 12, data_fim.day)
                else:
                    try:
                        mes_ant_inicio = date(data_inicio.year, data_inicio.month - 1, data_inicio.day)
                    except:
                        mes_ant_inicio = date(data_inicio.year, data_inicio.month - 1, 28)
                    try:
                        mes_ant_fim = date(data_fim.year, data_fim.month - 1, data_fim.day)
                    except:
                        mes_ant_fim = date(data_fim.year, data_fim.month - 1, 28)

                # Gastos do mes atual
                df_mes_atual = df_user_gastos[
                    (df_user_gastos["createdAt"].dt.date >= data_inicio) &
                    (df_user_gastos["createdAt"].dt.date <= data_fim)
                ]
                total_mes_atual = df_mes_atual["total_value"].sum() if not df_mes_atual.empty else 0

                # Gastos do mes anterior
                df_mes_anterior = df_user_gastos[
                    (df_user_gastos["createdAt"].dt.date >= mes_ant_inicio) &
                    (df_user_gastos["createdAt"].dt.date <= mes_ant_fim)
                ]
                total_mes_anterior = df_mes_anterior["total_value"].sum() if not df_mes_anterior.empty else 0

                # Calcula diferenca total
                diferenca = total_mes_atual - total_mes_anterior
                if total_mes_anterior > 0:
                    pct_diferenca = ((total_mes_atual - total_mes_anterior) / total_mes_anterior) * 100
                else:
                    pct_diferenca = 100 if total_mes_atual > 0 else 0

                # Define cor e emoji
                if diferenca > 0:
                    cor_comp = "#f44336"
                    emoji_comp = "📈"
                    texto_comp = f"+{fmt(abs(diferenca))} ({pct_diferenca:+.0f}%)"
                elif diferenca < 0:
                    cor_comp = "#4caf50"
                    emoji_comp = "📉"
                    texto_comp = f"-{fmt(abs(diferenca))} ({pct_diferenca:.0f}%)"
                else:
                    cor_comp = "#888"
                    emoji_comp = "➡️"
                    texto_comp = "Igual"

                # Card resumo
                st.markdown(f'''
                <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px; text-align: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; color: #888;">Total</span><br>
                    <span style="font-size: 12px; color: #aaa;">{fmt(total_mes_anterior)}</span>
                    <span style="font-size: 14px; color: white;"> → </span>
                    <span style="font-size: 12px; color: #aaa;">{fmt(total_mes_atual)}</span>
                    <span style="font-size: 14px; color: {cor_comp}; font-weight: 600; margin-left: 8px;">{emoji_comp} {texto_comp}</span>
                </div>
                ''', unsafe_allow_html=True)

                # Comparativo por categoria
                cat_atual = df_mes_atual.groupby("label")["total_value"].sum() if not df_mes_atual.empty else pd.Series(dtype=float)
                cat_anterior = df_mes_anterior.groupby("label")["total_value"].sum() if not df_mes_anterior.empty else pd.Series(dtype=float)

                todas_cats = set(cat_atual.index.tolist() + cat_anterior.index.tolist())

                comparativos = []
                for cat in todas_cats:
                    val_atual = cat_atual.get(cat, 0)
                    val_anterior = cat_anterior.get(cat, 0)
                    diff = val_atual - val_anterior
                    if val_anterior > 0:
                        pct = ((val_atual - val_anterior) / val_anterior) * 100
                    else:
                        pct = 100 if val_atual > 0 else 0
                    comparativos.append({"cat": cat, "atual": val_atual, "anterior": val_anterior, "diff": diff, "pct": pct})

                comparativos = sorted(comparativos, key=lambda x: abs(x["diff"]), reverse=True)

                for comp in comparativos[:5]:
                    if comp["diff"] > 0:
                        cor_cat = "#f44336"
                        seta = "↑"
                    elif comp["diff"] < 0:
                        cor_cat = "#4caf50"
                        seta = "↓"
                    else:
                        cor_cat = "#888"
                        seta = "→"

                    st.markdown(f'''
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <span style="font-size: 13px; color: #ccc;">{comp["cat"]}</span>
                        <span style="font-size: 12px;">
                            <span style="color: #888;">{fmt(comp["anterior"])}</span>
                            <span style="color: {cor_cat};"> {seta} </span>
                            <span style="color: white;">{fmt(comp["atual"])}</span>
                            <span style="color: {cor_cat}; font-weight: 600; margin-left: 4px;">({comp["pct"]:+.0f}%)</span>
                        </span>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown("---")

                # ========== ESTATISTICAS GERAIS ==========
                st.markdown('<p class="section-title">📊 Estatisticas Gerais</p>', unsafe_allow_html=True)

                # Calcula estatisticas
                total_gasto_historico = df_user_gastos["total_value"].sum()
                num_compras_total = len(df_user_gastos)
                media_por_compra = total_gasto_historico / num_compras_total if num_compras_total > 0 else 0

                # Media mensal
                meses_distintos = df_user_gastos["mes"].nunique()
                media_mensal = total_gasto_historico / meses_distintos if meses_distintos > 0 else 0

                # Maior gasto de todos os tempos
                maior_gasto = df_user_gastos.loc[df_user_gastos["total_value"].idxmax()] if not df_user_gastos.empty else None

                # Categoria mais gastadora
                cat_mais_gasta = df_user_gastos.groupby("label")["total_value"].sum().idxmax() if not df_user_gastos.empty else "-"
                valor_cat_mais = df_user_gastos.groupby("label")["total_value"].sum().max() if not df_user_gastos.empty else 0

                st.markdown(f'''
                <div style="display: flex; flex-direction: row; gap: 6px; width: 100%; margin-bottom: 8px;">
                    <div style="flex: 1; background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; text-align: center;">
                        <span style="font-size: 10px; color: #888;">Total historico</span><br>
                        <span style="font-size: 13px; color: white; font-weight: 600;">{fmt(total_gasto_historico)}</span>
                    </div>
                    <div style="flex: 1; background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; text-align: center;">
                        <span style="font-size: 10px; color: #888;">Media mensal</span><br>
                        <span style="font-size: 13px; color: white; font-weight: 600;">{fmt(media_mensal)}</span>
                    </div>
                </div>
                <div style="display: flex; flex-direction: row; gap: 6px; width: 100%; margin-bottom: 8px;">
                    <div style="flex: 1; background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; text-align: center;">
                        <span style="font-size: 10px; color: #888;">Qtd compras</span><br>
                        <span style="font-size: 13px; color: white; font-weight: 600;">{num_compras_total}</span>
                    </div>
                    <div style="flex: 1; background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; text-align: center;">
                        <span style="font-size: 10px; color: #888;">Media/compra</span><br>
                        <span style="font-size: 13px; color: white; font-weight: 600;">{fmt(media_por_compra)}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

                # Maior gasto e categoria campeã
                if maior_gasto is not None:
                    st.markdown(f'''
                    <div style="background: rgba(244, 67, 54, 0.1); padding: 8px 10px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #f44336;">
                        <span style="font-size: 11px; color: #f44336;">🔥 Maior gasto de todos os tempos</span><br>
                        <span style="font-size: 13px; color: white; font-weight: 500;">{maior_gasto.get("item", "-")}</span>
                        <span style="font-size: 13px; color: #f44336; font-weight: 600; float: right;">{fmt(maior_gasto["total_value"])}</span>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown(f'''
                <div style="background: rgba(156, 39, 176, 0.1); padding: 8px 10px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #9c27b0;">
                    <span style="font-size: 11px; color: #9c27b0;">🏆 Categoria campea</span><br>
                    <span style="font-size: 13px; color: white; font-weight: 500;">{cat_mais_gasta}</span>
                    <span style="font-size: 13px; color: #9c27b0; font-weight: 600; float: right;">{fmt(valor_cat_mais)}</span>
                </div>
                ''', unsafe_allow_html=True)

                st.markdown("---")

                # ========== GRAFICO EVOLUCAO MENSAL ==========
                st.markdown('<p class="section-title">💰 Evolucao Mensal</p>', unsafe_allow_html=True)
                evolucao = df_user_gastos.groupby("mes")["total_value"].sum().reset_index()

                cor_linha = '#e91e63' if user == "Susanna" else '#03a9f4'

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=evolucao["mes"], y=evolucao["total_value"],
                                        mode='lines+markers', name='Total',
                                        line=dict(color=cor_linha, width=2),
                                        marker=dict(size=5, color=cor_linha)))
                fig.update_layout(height=120, margin=dict(t=0, b=0, l=0, r=0),
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                 font=dict(color='white', size=8))
                fig.update_xaxes(gridcolor='#333', tickfont=dict(size=7))
                fig.update_yaxes(gridcolor='#333', showticklabels=False)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")

                # ========== RANKING DE MESES ==========
                st.markdown('<p class="section-title">🏅 Ranking de Meses</p>', unsafe_allow_html=True)

                meses_ranking = df_user_gastos.groupby("mes")["total_value"].sum().sort_values(ascending=False).head(5)

                medalhas_mes = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
                for i, (mes, valor) in enumerate(meses_ranking.items()):
                    st.markdown(f'''
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <span style="font-size: 13px; color: #ccc;">{medalhas_mes[i]} {mes}</span>
                        <span style="font-size: 13px; color: white; font-weight: 600;">{fmt(valor)}</span>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown("---")

                # Top 5 categorias historico
                st.markdown('<p class="section-title">🏷️ Top 5 Categorias (historico)</p>', unsafe_allow_html=True)
                top_cats = df_user_gastos.groupby("label")["total_value"].sum().nlargest(5).index.tolist()
                df_top = df_user_gastos[df_user_gastos["label"].isin(top_cats)]
                evolucao_cat = df_top.groupby(["mes", "label"])["total_value"].sum().reset_index()

                fig3 = px.area(evolucao_cat, x="mes", y="total_value", color="label")
                fig3.update_layout(height=120, margin=dict(t=0, b=0, l=0, r=0),
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  font=dict(color='white', size=8), legend=dict(orientation="h", y=1.2, font=dict(size=6)), showlegend=True)
                fig3.update_xaxes(gridcolor='#333', tickfont=dict(size=7))
                fig3.update_yaxes(gridcolor='#333', showticklabels=False)
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("📝 Voce ainda nao tem gastos registrados.")
        else:
            st.info("📝 Nenhum gasto registrado.")

    # ========== CONFIG ==========
    elif menu == "⚙️ Config":
        st.markdown('<p class="page-title">⚙️ Configuracoes</p>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p class="section-title">📅 Fechamento da Fatura</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 11px; color: #aaa; text-align: center;">Define o dia de fechamento da fatura do cartao para cada mes</p>', unsafe_allow_html=True)

        hoje = date.today()

        # Mostra os proximos 3 meses para configurar
        meses_config = []
        for i in range(3):
            if hoje.month + i > 12:
                meses_config.append((hoje.year + 1, (hoje.month + i - 1) % 12 + 1))
            else:
                meses_config.append((hoje.year, hoje.month + i))

        nomes_meses = ["", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        # Carrega configuracoes atuais do usuario
        fechamentos = carregar_fechamento_fatura(colls, user)
        fechamentos_dict = {f.get("mes_ano"): f.get("dia_fechamento", 7) for f in fechamentos}

        with st.form("form_fechamento", clear_on_submit=False):
            valores_form = {}
            for ano, mes in meses_config:
                mes_ano = f"{ano}-{mes:02d}"
                dia_atual = fechamentos_dict.get(mes_ano, 7)
                valores_form[mes_ano] = st.number_input(
                    f"📆 {nomes_meses[mes]}/{ano}",
                    min_value=1,
                    max_value=28,
                    value=dia_atual,
                    key=f"fechamento_{mes_ano}"
                )

            if st.form_submit_button("💾 Salvar", use_container_width=True):
                for mes_ano, dia in valores_form.items():
                    # Atualiza ou insere para o usuario atual
                    colls["config"].update_one(
                        {"tipo": "fechamento_fatura", "mes_ano": mes_ano, "user": user},
                        {"$set": {"dia_fechamento": dia}},
                        upsert=True
                    )
                limpar_cache_dados()
                st.success("✅ Fechamentos salvos!")
                st.rerun()

        # Mostra periodo atual
        st.markdown("---")
        st.markdown('<p class="section-title">📊 Periodo Atual</p>', unsafe_allow_html=True)

        data_inicio, data_fim = get_periodo_fatura(colls, user)
        st.markdown(f'''
        <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px; text-align: center;">
            <span style="font-size: 12px; color: #aaa;">Fatura atual</span><br>
            <span style="font-size: 16px; color: white; font-weight: 600;">{data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}</span>
        </div>
        ''', unsafe_allow_html=True)


if __name__ == "__main__":
    # Selecao de usuario
    if not get_user():
        show_user_selector()
        st.stop()

    # Usuario selecionado - mostra o app
    main()
