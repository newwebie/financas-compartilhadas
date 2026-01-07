import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import certifi

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
    .block-container {
        padding: 0.5rem 0.75rem !important;
        max-width: 100% !important;
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
    return {"despesas": db["despesas"], "emprestimos": db["emprestimos"], "metas": db["metas"], "quitacoes": db["quitacoes"], "contas_fixas": db["contas_fixas"], "emprestimos_terceiros": db["emprestimos_terceiros"], "dividas_terceiros": db["dividas_terceiros"]}


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
    """Carrega emprestimos a terceiros do usuario."""
    return list(_colls["emprestimos_terceiros"].find({"credor": user, "status": "em aberto"}))


@st.cache_data(ttl=300)
def carregar_dividas_terceiros(_colls, user):
    """Carrega dividas a terceiros do usuario."""
    return list(_colls["dividas_terceiros"].find({"devedor": user, "status": "em aberto"}))


@st.cache_data(ttl=300)
def carregar_pagamentos_contas_fixas(_colls, user, mes_ano):
    """Carrega pagamentos de contas fixas do usuario no mes."""
    return list(_colls["quitacoes"].find({"tipo": "conta_fixa", "pagador": user, "mes_ano": mes_ano}))


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

        menu_opcoes = ["🏠 Inicio", "➕ Novo", "🤝 Acerto", "🎯 Metas", "👯 Ambas", "📊 Relatorio", "📈 Evolucao"]

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
            hoje = date.today()
            mes_atual = df[(df["createdAt"].dt.month == hoje.month) & (df["createdAt"].dt.year == hoje.year)]
            meus_registros = mes_atual[mes_atual["buyer"] == user]

            # === DASHBOARD - 3 CARDS ===
            st.markdown('<p class="section-title"></p>', unsafe_allow_html=True)

            # Card 1: Gastos (tudo menos Cofrinho e Renda Variavel)
            gastos_reais = meus_registros[~meus_registros["label"].str.contains("Cofrinho|Renda Variavel", na=False)]["total_value"].sum()

            # Card 2: Cofrinho
            cofrinho = meus_registros[meus_registros["label"].str.contains("Cofrinho", na=False)]["total_value"].sum()

            # Card 3: Renda Variavel
            renda_variavel = meus_registros[meus_registros["label"].str.contains("Renda Variavel", na=False)]["total_value"].sum()

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
            st.markdown("")

            # === GRAFICO POR CATEGORIA (incluindo Cofrinho e Contas Fixas) ===
            st.markdown('<p class="section-title">📊 Gastos por Categoria</p>', unsafe_allow_html=True)

            # Exclui apenas Renda Variavel do grafico (Cofrinho aparece)
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

            # Minhas pendencias
            user_deve = df[(df["devedor"] == user) & (df["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            outro_deve = df[(df["devedor"] == outro) & (df["status_pendencia"] == "em aberto")]["valor_pendente"].sum()

            if not df_emp.empty:
                df_emp["createdAt"] = pd.to_datetime(df_emp["createdAt"])
                user_deve += df_emp[(df_emp["devedor"] == user) & (df_emp["status"] == "em aberto")]["valor"].sum()
                outro_deve += df_emp[(df_emp["devedor"] == outro) & (df_emp["status"] == "em aberto")]["valor"].sum()

            saldo = outro_deve - user_deve

            # Busca dividas a terceiros
            df_dividas_terceiros = pd.DataFrame(carregar_dividas_terceiros(colls, user))
            total_dividas = df_dividas_terceiros["valor"].sum() if not df_dividas_terceiros.empty else 0

            # Saldo
            if abs(saldo) < 0.01 and total_dividas == 0:
                st.markdown('<div class="ok-box"><h3 style="font-size: 12px;">✨ Quites!</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="section-title" style="font-size: 14px;">💫 Situacao</p>', unsafe_allow_html=True)

                # Card unico se só tem um tipo de divida, ou dois cards lado a lado
                if saldo > 0 and total_dividas == 0:
                    # Só a outra me deve
                    st.markdown(f'<div class="ok-box"><h3 style="font-size: 12px;">🤑 {outro} te deve {fmt(saldo)}</h3></div>', unsafe_allow_html=True)
                elif saldo > 0 and total_dividas > 0:
                    # Outra me deve + eu devo a terceiros
                    st.markdown(f'''
                    <div style="display: flex; flex-direction: row; gap: 6px; width: 100%;">
                        <div style="flex: 1; background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #81c784;">
                            <span style="font-size: 14px; opacity: 0.9;">🤑 {outro} te deve</span><br>
                            <span style="font-size: 12px; font-weight: 600;">{fmt(saldo)}</span>
                        </div>
                        <div style="flex: 1; background: linear-gradient(135deg, #c62828 0%, #f44336 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #ef9a9a;">
                            <span style="font-size: 14px; opacity: 0.9;">💸 Devo (terceiros)</span><br>
                            <span style="font-size: 12px; font-weight: 600;">{fmt(total_dividas)}</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                elif saldo <= 0 and total_dividas > 0:
                    # Eu devo pra outra + eu devo a terceiros
                    cor_divida_outra = "linear-gradient(135deg, #c2185b 0%, #e91e63 100%)" if user == "Susanna" else "linear-gradient(135deg, #0277bd 0%, #03a9f4 100%)"
                    borda_divida = "#f48fb1" if user == "Susanna" else "#4fc3f7"
                    st.markdown(f'''
                    <div style="display: flex; flex-direction: row; gap: 6px; width: 100%;">
                        <div style="flex: 1; background: {cor_divida_outra}; padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid {borda_divida};">
                            <span style="font-size: 14px; opacity: 0.9;">Devo pra {outro}</span><br>
                            <span style="font-size: 12px; font-weight: 600;">{fmt(abs(saldo))}</span>
                        </div>
                        <div style="flex: 1; background: linear-gradient(135deg, #c62828 0%, #f44336 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #ef9a9a;">
                            <span style="font-size: 14px; opacity: 0.9;">💸 Devo (terceiros)</span><br>
                            <span style="font-size: 12px; font-weight: 600;">{fmt(total_dividas)}</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                elif saldo <= 0 and total_dividas == 0:
                    # Só eu devo pra outra
                    st.markdown(f'<div class="{cor_card}"><h4 style="font-size: 14px;">Voce deve pra {outro}</h4><h2 style="font-size: 12px;">{fmt(abs(saldo))}</h2></div>', unsafe_allow_html=True)
                elif abs(saldo) < 0.01 and total_dividas > 0:
                    # Só devo a terceiros
                    st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #c62828 0%, #f44336 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #ef9a9a;">
                        <span style="font-size: 14px; opacity: 0.9;">💸 Devo (terceiros)</span><br>
                        <span style="font-size: 12px; font-weight: 600;">{fmt(total_dividas)}</span>
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            st.info("📝 Sem registros ainda. Va em '➕ Novo'!")

    # ========== NOVO ==========
    elif menu == "➕ Novo":
        st.markdown('<p class="page-title">➕ Novo Registro</p>', unsafe_allow_html=True)

        # Inicializa estado do formulario selecionado
        if "form_selecionado" not in st.session_state:
            st.session_state.form_selecionado = None

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

                divida_submitted = st.form_submit_button("✅ Registrar", use_container_width=True)

            if divida_submitted and pessoa_credor:
                colls["dividas_terceiros"].insert_one({
                    "devedor": user,
                    "credor": pessoa_credor,
                    "valor": valor_divida,
                    "descricao": desc_divida,
                    "data_emprestimo": datetime.now(),
                    "data_pagamento": datetime.combine(data_pagamento, datetime.min.time()),
                    "status": "em aberto"
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
                    st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 6px 8px; border-radius: 4px; margin-bottom: 4px; border-left: 2px solid {cor_tag};">
                        <span style="font-size: 12px; color: white;">{pend["descricao"]}</span>
                        <span style="font-size: 11px; color: #aaa; float: right;">{fmt(pend["valor"])} | {pend["data"]}</span>
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

                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 6px; margin-bottom: 4px; border-left: 2px solid #9c27b0;">
                        <span style="font-size: 14px; color: #ce93d8; font-weight: 600;">{emp["devedor"]}</span><br>
                        <span style="font-size: 12px; color: #aaa;">{emp.get("descricao", "-")}</span><br>
                        <span style="font-size: 14px; color: white;">{fmt(emp["valor"])}</span>
                        <span style="font-size: 11px; color: #888;"> | Emp: {data_emp} | Dev: {data_dev}</span>
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
            total_dividas = df_dividas["valor"].sum()
            st.markdown(f'<div style="background: rgba(244,67,54,0.2); padding: 8px; border-radius: 6px; text-align: center; margin-bottom: 10px;"><span style="font-size: 12px; color: #ef9a9a;">Total que devo</span><br><span style="font-size: 18px; color: white; font-weight: 600;">{fmt(total_dividas)}</span></div>', unsafe_allow_html=True)

            for i, (_, div) in enumerate(df_dividas.iterrows()):
                data_emp = div["data_emprestimo"].strftime("%d/%m") if pd.notna(div.get("data_emprestimo")) else ""
                data_pag = div["data_pagamento"].strftime("%d/%m") if pd.notna(div.get("data_pagamento")) else ""

                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 6px; margin-bottom: 4px; border-left: 2px solid #f44336;">
                        <span style="font-size: 14px; color: #ef9a9a; font-weight: 600;">{div["credor"]}</span><br>
                        <span style="font-size: 12px; color: #aaa;">{div.get("descricao", "-")}</span><br>
                        <span style="font-size: 14px; color: white;">{fmt(div["valor"])}</span>
                        <span style="font-size: 11px; color: #888;"> | Emp: {data_emp} | Pag: {data_pag}</span>
                    </div>''', unsafe_allow_html=True)
                with col2:
                    if st.button("✅", key=f"quitar_divida_{i}", help="Paguei"):
                        colls["dividas_terceiros"].update_one(
                            {"_id": div["_id"]},
                            {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                        )
                        limpar_cache_dados()
                        st.rerun()
        else:
            st.caption("Nenhuma divida a terceiros")

        # ========== CONTAS FIXAS (NAO CREDITO) ==========
        st.markdown("---")
        st.markdown('<p class="section-title">📋 Contas Fixas do Mes</p>', unsafe_allow_html=True)

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

                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 6px; margin-bottom: 4px; border-left: 2px solid {cor_borda};">
                            <span style="font-size: 14px; color: white; font-weight: 600;">{icone_status} {conta["nome"]}</span><br>
                            <span style="font-size: 12px; color: #aaa;">{conta["categoria"]}</span>
                            <span style="font-size: 14px; color: white; float: right;">{fmt(conta["meu_valor"])}</span><br>
                            <span style="font-size: 11px; color: #888;">Vence dia {int(conta["dia_vencimento"])}</span>
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
            hoje = date.today()
            df_mes = df_desp[(df_desp["createdAt"].dt.month == hoje.month) & (df_desp["buyer"] == user)]

            st.markdown('<p class="section-title">📊 Meu Progresso</p>', unsafe_allow_html=True)

            for _, meta in df_metas.iterrows():
                cat, limite = meta["categoria"], meta["limite"]

                gasto = df_mes["total_value"].sum() if "Total" in cat else df_mes[df_mes["label"] == cat]["total_value"].sum()

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
            hoje = date.today()

            # Calcula o 5o dia util do mes atual
            def get_5o_dia_util(ano, mes):
                from calendar import monthrange
                dias_uteis = 0
                for dia in range(1, monthrange(ano, mes)[1] + 1):
                    d = date(ano, mes, dia)
                    if d.weekday() < 5:  # Segunda a Sexta
                        dias_uteis += 1
                        if dias_uteis == 5:
                            return d
                return date(ano, mes, 1)

            # Determina periodo de corte (5o dia util)
            quinto_dia_util_atual = get_5o_dia_util(hoje.year, hoje.month)

            if hoje >= quinto_dia_util_atual:
                # Estamos apos o 5o dia util - periodo atual
                data_inicio = quinto_dia_util_atual
                # Proximo mes
                if hoje.month == 12:
                    prox_mes = date(hoje.year + 1, 1, 1)
                else:
                    prox_mes = date(hoje.year, hoje.month + 1, 1)
                data_fim = get_5o_dia_util(prox_mes.year, prox_mes.month) - timedelta(days=1)
            else:
                # Estamos antes do 5o dia util - periodo anterior
                if hoje.month == 1:
                    mes_anterior = date(hoje.year - 1, 12, 1)
                else:
                    mes_anterior = date(hoje.year, hoje.month - 1, 1)
                data_inicio = get_5o_dia_util(mes_anterior.year, mes_anterior.month)
                data_fim = quinto_dia_util_atual - timedelta(days=1)

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
            df_desp["mes_ano"] = df_desp["createdAt"].dt.to_period("M")
            df_desp["dia_semana"] = df_desp["createdAt"].dt.dayofweek
            df_desp["dia"] = df_desp["createdAt"].dt.day

            # Filtros
            meses = sorted(df_desp["mes_ano"].unique(), reverse=True)
            mes_selecionado = st.selectbox("📅 Mes", meses, format_func=lambda x: x.strftime("%B %Y"))

            df_mes = df_desp[df_desp["mes_ano"] == mes_selecionado]
            df_user = df_mes[df_mes["buyer"] == user]

            # Filtra gastos reais (sem Cofrinho e Renda Variavel)
            df_user_gastos = df_user[~df_user["label"].str.contains("Cofrinho|Renda Variavel", na=False)]

            # Calcula totais de contas fixas do usuario
            user_fixas = 0
            if not df_contas_fixas.empty:
                user_fixas = df_contas_fixas[df_contas_fixas["responsavel"] == user]["valor"].sum()
                divididas = df_contas_fixas[df_contas_fixas["responsavel"] == "Dividido"]["valor"].sum()
                user_fixas += divididas / 2

            # Totais
            total_var = df_user_gastos["total_value"].sum()
            total_geral = total_var + user_fixas

            # ========== RESUMO DO MES ==========
            st.markdown(f'''
            <div style="background: linear-gradient(135deg, {'#c2185b' if user == 'Susanna' else '#0277bd'} 0%, {'#e91e63' if user == 'Susanna' else '#03a9f4'} 100%); padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
                <span style="font-size: 11px; color: rgba(255,255,255,0.8);">Total do Mes</span>
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

                # Dias no mes
                from calendar import monthrange
                mes_py = mes_selecionado.to_timestamp()
                dias_no_mes = monthrange(mes_py.year, mes_py.month)[1]
                media_diaria = total_var / dias_no_mes

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

            # ========== COMPARATIVO COM MES ANTERIOR ==========
            if len(meses) > 1:
                idx_atual = list(meses).index(mes_selecionado)
                if idx_atual < len(meses) - 1:
                    mes_anterior = meses[idx_atual + 1]
                    df_mes_ant = df_desp[(df_desp["mes_ano"] == mes_anterior) & (df_desp["buyer"] == user)]
                    df_mes_ant_gastos = df_mes_ant[~df_mes_ant["label"].str.contains("Cofrinho|Renda Variavel", na=False)]
                    total_ant = df_mes_ant_gastos["total_value"].sum()

                    if total_ant > 0:
                        diff = total_var - total_ant
                        diff_pct = (diff / total_ant) * 100

                        cor_diff = "#4caf50" if diff < 0 else "#f44336"
                        seta = "↓" if diff < 0 else "↑"
                        texto = "menos" if diff < 0 else "mais"

                        st.markdown("---")
                        st.markdown(f'''
                        <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; text-align: center;">
                            <span style="font-size: 10px; color: #aaa;">vs mes anterior</span><br>
                            <span style="font-size: 16px; color: {cor_diff}; font-weight: 600;">{seta} {abs(diff_pct):.0f}% {texto}</span><br>
                            <span style="font-size: 10px; color: #888;">{fmt(abs(diff))} de diferenca</span>
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

            # Previsao da fatura (credito do mes + parcelas de compras anteriores)
            parcelas_este_mes = 0
            parcelas_prox_mes = 0
            if not df_parcelados.empty:
                mes_atual = mes_selecionado.to_timestamp()
                # Calcula proximo mes
                if mes_atual.month == 12:
                    prox_mes = date(mes_atual.year + 1, 1, 1)
                else:
                    prox_mes = date(mes_atual.year, mes_atual.month + 1, 1)

                for _, compra in df_parcelados.iterrows():
                    parcelas_total = compra["installment"]
                    valor_parcela = compra["total_value"] / parcelas_total
                    data_compra = compra["createdAt"]

                    # Verifica se essa parcela cai neste mes
                    meses_desde = (mes_atual.year - data_compra.year) * 12 + (mes_atual.month - data_compra.month)
                    if 0 <= meses_desde < parcelas_total:
                        parcelas_este_mes += valor_parcela

                    # Verifica se cai no proximo mes
                    meses_desde_prox = (prox_mes.year - data_compra.year) * 12 + (prox_mes.month - data_compra.month)
                    if 0 <= meses_desde_prox < parcelas_total:
                        parcelas_prox_mes += valor_parcela

            # Compras a vista no credito
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
                    <span style="font-size: 16px; color: white; font-weight: 600;">{fmt(parcelas_a_vencer)}</span>
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

            # ========== POR CATEGORIA ==========
            st.markdown("---")
            st.markdown('<p style="font-size: 12px; text-align: center; margin: 4px 0 8px 0; font-weight: 500;">🏷️ Por Categoria</p>', unsafe_allow_html=True)

            # Adiciona contas fixas de credito ao grafico
            cat_data = df_user_gastos.groupby("label")["total_value"].sum() if not df_user_gastos.empty else pd.Series(dtype=float)

            # Soma contas fixas de credito por categoria
            if not df_contas_fixas.empty:
                for _, conta in df_contas_fixas.iterrows():
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

                            if cat_label in cat_data.index:
                                cat_data[cat_label] += valor_meu
                            else:
                                cat_data[cat_label] = valor_meu

            cat_data = cat_data.sort_values(ascending=False)
            total_com_fixas = cat_data.sum() if not cat_data.empty else 0

            if not cat_data.empty:
                max_cat = cat_data.max()

                cores_distintas = ['#e91e63', '#2196f3', '#4caf50', '#ff9800', '#9c27b0', '#00bcd4', '#ffeb3b', '#f44336']
                for i, (cat, val) in enumerate(cat_data.items()):
                    pct = (val / max_cat) * 100
                    pct_total = (val / total_com_fixas * 100) if total_com_fixas > 0 else 0
                    cor = cores_distintas[i % len(cores_distintas)]
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

            # ========== CONTAS FIXAS ==========
            if not df_contas_fixas.empty:
                contas_user = df_contas_fixas[
                    (df_contas_fixas["responsavel"] == user) |
                    (df_contas_fixas["responsavel"] == "Dividido")
                ]

                if not contas_user.empty:
                    st.markdown("---")
                    with st.expander("📋 Minhas Contas Fixas", expanded=False):
                        for _, conta in contas_user.iterrows():
                            valor_meu = conta['valor'] / 2 if conta["responsavel"] == "Dividido" else conta['valor']
                            tipo = "🔷" if conta["responsavel"] == "Dividido" else "🔸"
                            st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 6px 8px; border-radius: 4px; margin-bottom: 4px;">
                                <span style="font-size: 12px; color: white;">{tipo} {conta['nome']}</span>
                                <span style="font-size: 11px; color: #aaa; float: right;">{fmt(valor_meu)} | Dia {int(conta['dia_vencimento'])}</span>
                            </div>''', unsafe_allow_html=True)
        else:
            st.info("📝 Nenhum gasto registrado.")

    # ========== EVOLUCAO ==========
    elif menu == "📈 Evolucao":
        st.markdown('<p class="page-title">📈 Minha Evolucao</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(carregar_despesas(colls))

        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            df_desp["mes"] = df_desp["createdAt"].dt.to_period("M").astype(str)

            # Filtrar apenas meus gastos
            df_user = df_desp[df_desp["buyer"] == user]

            if not df_user.empty:
                # Meu total por mes
                st.markdown('<p class="section-title">💰 Meu total por mes</p>', unsafe_allow_html=True)
                evolucao = df_user.groupby("mes")["total_value"].sum().reset_index()

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

                # Top 5 categorias
                st.markdown('<p class="section-title">🏷️ Minhas top 5 categorias</p>', unsafe_allow_html=True)
                top_cats = df_user.groupby("label")["total_value"].sum().nlargest(5).index.tolist()
                df_top = df_user[df_user["label"].isin(top_cats)]
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


if __name__ == "__main__":
    # Selecao de usuario
    if not get_user():
        show_user_selector()
        st.stop()

    # Usuario selecionado - mostra o app
    main()
