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


def connect_mongodb():
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
        menu = st.radio("", ["🏠 Inicio", "➕ Novo", "🤝 Acerto", "🎯 Metas", "👯 Ambas", "📊 Relatorio", "📈 Evolucao"], label_visibility="collapsed")

    # ========== INICIO ==========
    if menu == "🏠 Inicio":
        st.markdown(f'<p class="page-title">💰 Ola, {user}!</p>', unsafe_allow_html=True)

        df = pd.DataFrame(list(colls["despesas"].find({})))
        df_emp = pd.DataFrame(list(colls["emprestimos"].find({})))

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
                <div style="flex: 1; background: {cor_gastos}; padding: 3px 6px; border-radius: 6px; color: white; border-left: 2px solid {borda_gastos};">
                    <h4 style="margin: 0; font-size: 14px; opacity: 0.9; line-height: 1.2;">💸 Gastos</h4>
                    <h2 style="margin: 0; font-size: 12px; font-weight: 600; line-height: 1.2;">{fmt(gastos_reais)}</h2>
                </div>
                <div style="flex: 1; background: linear-gradient(135deg, #388e3c 0%, #66bb6a 100%); padding: 3px 6px; border-radius: 6px; color: white; border-left: 2px solid #81c784;">
                    <h4 style="margin: 0; font-size: 14px; opacity: 0.9; line-height: 1.2;">🐷 Cofrinho</h4>
                    <h2 style="margin: 0; font-size: 12px; font-weight: 600; line-height: 1.2;">{fmt(cofrinho)}</h2>
                </div>
                <div style="flex: 1; background: linear-gradient(135deg, #f57c00 0%, #ffb74d 100%); padding: 3px 6px; border-radius: 6px; color: white; border-left: 2px solid #ffcc80;">
                    <h4 style="margin: 0; font-size: 14px; opacity: 0.9; line-height: 1.2;">💵 Extra</h4>
                    <h2 style="margin: 0; font-size: 12px; font-weight: 600; line-height: 1.2;">{fmt(renda_variavel)}</h2>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            st.markdown("")
            st.markdown("")
            st.markdown("")

            # === GRAFICO POR CATEGORIA (incluindo Cofrinho) ===
            st.markdown('<p class="section-title">📊 Gastos por Categoria</p>', unsafe_allow_html=True)

            # Exclui apenas Renda Variavel do grafico (Cofrinho aparece)
            gastos_para_grafico = meus_registros[~meus_registros["label"].str.contains("Renda Variavel", na=False)]
            user_cat = gastos_para_grafico.groupby("label")["total_value"].sum().reset_index()
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
            df_dividas_terceiros = pd.DataFrame(list(colls["dividas_terceiros"].find({"devedor": user, "status": "em aberto"})))
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
                        <div style="flex: 1; background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%); padding: 3px 6px; border-radius: 6px; color: white; border-left: 2px solid #81c784;">
                            <h4 style="margin: 0; font-size: 14px; opacity: 0.9; line-height: 1.2;">🤑 {outro} te deve</h4>
                            <h2 style="margin: 0; font-size: 12px; font-weight: 600; line-height: 1.2;">{fmt(saldo)}</h2>
                        </div>
                        <div style="flex: 1; background: linear-gradient(135deg, #c62828 0%, #f44336 100%); padding: 3px 6px; border-radius: 6px; color: white; border-left: 2px solid #ef9a9a;">
                            <h4 style="margin: 0; font-size: 14px; opacity: 0.9; line-height: 1.2;">💸 Devo (terceiros)</h4>
                            <h2 style="margin: 0; font-size: 12px; font-weight: 600; line-height: 1.2;">{fmt(total_dividas)}</h2>
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
                            <h4 style="margin: 0; font-size: 14px; opacity: 0.9;">Devo pra {outro}</h4>
                            <h2 style="margin: 0; font-size: 12px; font-weight: 600;">{fmt(abs(saldo))}</h2>
                        </div>
                        <div style="flex: 1; background: linear-gradient(135deg, #c62828 0%, #f44336 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #ef9a9a;">
                            <h4 style="margin: 0; font-size: 14px; opacity: 0.9;">💸 Devo (terceiros)</h4>
                            <h2 style="margin: 0; font-size: 12px; font-weight: 600;">{fmt(total_dividas)}</h2>
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
                        <h4 style="margin: 0; font-size: 14px; opacity: 0.9;">💸 Devo (terceiros)</h4>
                        <h2 style="margin: 0; font-size: 12px; font-weight: 600;">{fmt(total_dividas)}</h2>
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            st.info("📝 Sem registros ainda. Va em '➕ Novo'!")

    # ========== NOVO ==========
    elif menu == "➕ Novo":
        st.markdown('<p class="page-title">➕ Novo Registro</p>', unsafe_allow_html=True)

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

                # Inicializa pendencia como vazia
                pend = {"tem_pendencia": False, "devedor": None, "valor_pendente": None, "status_pendencia": None}

                # "Pra mim" - so adiciona nos meus gastos, sem pendencia
                # "Dividido" - adiciona nos meus gastos + outra me deve metade
                # "Pra outra" - adiciona nos meus gastos + outra me deve tudo

                if "Dividido" in tipo_despesa:
                    # Eu paguei tudo, mas a outra me deve metade
                    pend = {"tem_pendencia": True, "devedor": outro, "valor_pendente": round(valor_total / 2, 2), "status_pendencia": "em aberto"}
                elif "Pra outra" in tipo_despesa:
                    # Eu comprei pra outra pessoa, ela me deve o valor total
                    pend = {"tem_pendencia": True, "devedor": outro, "valor_pendente": valor_total, "status_pendencia": "em aberto"}

                doc = {
                    "label": label, "buyer": user, "item": item, "description": description,
                    "quantity": quantidade, "total_value": valor_total, "payment_method": pagamento,
                    "installment": parcelas, "createdAt": datetime.now(), "pagamento_compartilhado": tipo_despesa, **pend
                }

                result = colls["despesas"].insert_one(doc)

                # Registra na collection de quitacoes se houver pendencia
                if pend["tem_pendencia"]:
                    colls["quitacoes"].insert_one({
                        "tipo": "despesa_compartilhada", "despesa_id": result.inserted_id, "data": datetime.now(),
                        "credor": user, "devedor": pend["devedor"], "valor": pend["valor_pendente"],
                        "descricao": f"{label} - {item}" if item else label, "observacao": description, "status": "em aberto"
                    })

                st.success(f"✅ Gasto de {fmt(valor_total)} salvo!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erro: {e}")

        st.markdown("---")

        with st.expander("🤝 Emprestimo a Terceiros"):
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
                st.success(f"✅ Emprestimo de {fmt(valor_terceiro)} pra {pessoa_terceiro} registrado!")

        with st.expander("💸 Devo pra Alguem"):
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
                st.success(f"✅ Divida de {fmt(valor_divida)} com {pessoa_credor} registrada!")

        with st.expander("📋 Cadastrar Conta Fixa"):
            with st.form("form_conta_fixa", clear_on_submit=True):
                nome_conta = st.text_input("📝 Nome da conta", placeholder="Ex: Aluguel, Internet...")
                valor_conta = st.number_input("💵 Valor", min_value=0.01, value=100.00, format="%.2f")
                dia_vencimento = st.number_input("📅 Dia vencimento", min_value=1, max_value=31, value=10)
                responsavel = st.selectbox("👤 Responsavel", [user, outro, "Dividido"])
                categoria_conta = st.selectbox("🏷️ Categoria", ["Casa 🏠 ", "📶 Internet", "📱 Celular", "🎬 Streaming", "➕ Saude", "📦 Outros"])
                obs_conta = st.text_input("💬 Observacao")

                cf_submitted = st.form_submit_button("✅ Cadastrar", use_container_width=True)

            if cf_submitted:
                conta_fixa = {
                    "nome": nome_conta, "valor": valor_conta, "dia_vencimento": dia_vencimento,
                    "responsavel": responsavel, "categoria": categoria_conta, "observacao": obs_conta,
                    "ativo": True, "createdAt": datetime.now()
                }
                colls["contas_fixas"].insert_one(conta_fixa)
                st.success("✅ Conta fixa cadastrada!")

    # ========== ACERTO DE CONTAS ==========
    elif menu == "🤝 Acerto":
        st.markdown('<p class="page-title">🤝 Acerto de Contas</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        df_emp = pd.DataFrame(list(colls["emprestimos"].find({})))
        df_logs = pd.DataFrame(list(colls["quitacoes"].find({})))

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

                st.success(f"✅ Acertado! {quem_paga} pagou {fmt(abs(saldo_liquido))} pra {quem_recebe}")
                st.balloons()
                st.rerun()

        st.markdown("---")

        # Detalhamento (para referencia)
        st.markdown('<p class="section-title">📋 Detalhamento</p>', unsafe_allow_html=True)

        # Mostra resumo
        st.markdown(f'''
        <div style="display: flex; gap: 8px; margin-bottom: 10px;">
            <div style="flex: 1; background: rgba(233,30,99,0.2); padding: 6px; border-radius: 6px; text-align: center;">
                <span style="font-size: 8px; color: #f48fb1;">Voce deve</span><br>
                <span style="font-size: 11px; color: white; font-weight: 600;">{fmt(user_deve_bruto)}</span>
            </div>
            <div style="flex: 1; background: rgba(3,169,244,0.2); padding: 6px; border-radius: 6px; text-align: center;">
                <span style="font-size: 8px; color: #4fc3f7;">{outro} deve</span><br>
                <span style="font-size: 11px; color: white; font-weight: 600;">{fmt(outro_deve_bruto)}</span>
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
                    st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 4px 8px; border-radius: 4px; margin-bottom: 4px; border-left: 2px solid {cor_tag};">
                        <span style="font-size: 9px; color: white;">{pend["descricao"]}</span>
                        <span style="font-size: 8px; color: #aaa; float: right;">{fmt(pend["valor"])} | {pend["data"]}</span>
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
        df_terceiros = pd.DataFrame(list(colls["emprestimos_terceiros"].find({"credor": user, "status": "em aberto"})))

        if not df_terceiros.empty:
            # Calcula total
            total_terceiros = df_terceiros["valor"].sum()
            st.markdown(f'<div style="background: rgba(156,39,176,0.2); padding: 6px; border-radius: 6px; text-align: center; margin-bottom: 10px;"><span style="font-size: 8px; color: #ce93d8;">Total a receber</span><br><span style="font-size: 12px; color: white; font-weight: 600;">{fmt(total_terceiros)}</span></div>', unsafe_allow_html=True)

            for i, (_, emp) in enumerate(df_terceiros.iterrows()):
                # Formata datas
                data_emp = emp["data_emprestimo"].strftime("%d/%m") if pd.notna(emp.get("data_emprestimo")) else ""
                data_dev = emp["data_devolucao"].strftime("%d/%m") if pd.notna(emp.get("data_devolucao")) else ""

                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 6px 8px; border-radius: 6px; margin-bottom: 4px; border-left: 2px solid #9c27b0;">
                        <span style="font-size: 10px; color: #ce93d8; font-weight: 600;">{emp["devedor"]}</span><br>
                        <span style="font-size: 8px; color: #aaa;">{emp.get("descricao", "-")}</span><br>
                        <span style="font-size: 9px; color: white;">{fmt(emp["valor"])}</span>
                        <span style="font-size: 8px; color: #888;"> | Emp: {data_emp} | Dev: {data_dev}</span>
                    </div>''', unsafe_allow_html=True)
                with col2:
                    if st.button("✅", key=f"quitar_terceiro_{i}", help="Recebido"):
                        colls["emprestimos_terceiros"].update_one(
                            {"_id": emp["_id"]},
                            {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                        )
                        st.rerun()
        else:
            st.caption("Nenhum emprestimo a terceiros")

        # ========== MINHAS DIVIDAS A TERCEIROS ==========
        st.markdown("---")
        st.markdown('<p class="section-title">💸 Minhas Dividas</p>', unsafe_allow_html=True)

        df_dividas = pd.DataFrame(list(colls["dividas_terceiros"].find({"devedor": user, "status": "em aberto"})))

        if not df_dividas.empty:
            total_dividas = df_dividas["valor"].sum()
            st.markdown(f'<div style="background: rgba(244,67,54,0.2); padding: 6px; border-radius: 6px; text-align: center; margin-bottom: 10px;"><span style="font-size: 8px; color: #ef9a9a;">Total que devo</span><br><span style="font-size: 12px; color: white; font-weight: 600;">{fmt(total_dividas)}</span></div>', unsafe_allow_html=True)

            for i, (_, div) in enumerate(df_dividas.iterrows()):
                data_emp = div["data_emprestimo"].strftime("%d/%m") if pd.notna(div.get("data_emprestimo")) else ""
                data_pag = div["data_pagamento"].strftime("%d/%m") if pd.notna(div.get("data_pagamento")) else ""

                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f'''<div style="background: rgba(255,255,255,0.05); padding: 6px 8px; border-radius: 6px; margin-bottom: 4px; border-left: 2px solid #f44336;">
                        <span style="font-size: 10px; color: #ef9a9a; font-weight: 600;">{div["credor"]}</span><br>
                        <span style="font-size: 8px; color: #aaa;">{div.get("descricao", "-")}</span><br>
                        <span style="font-size: 9px; color: white;">{fmt(div["valor"])}</span>
                        <span style="font-size: 8px; color: #888;"> | Emp: {data_emp} | Pag: {data_pag}</span>
                    </div>''', unsafe_allow_html=True)
                with col2:
                    if st.button("✅", key=f"quitar_divida_{i}", help="Paguei"):
                        colls["dividas_terceiros"].update_one(
                            {"_id": div["_id"]},
                            {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                        )
                        st.rerun()
        else:
            st.caption("Nenhuma divida a terceiros")

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
                    st.success("✅ Meta criada!")
                    st.rerun()

        df_metas = pd.DataFrame(list(colls["metas"].find({"ativo": True, "pessoa": user})))
        df_desp = pd.DataFrame(list(colls["despesas"].find({})))

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
        st.markdown('<p class="page-title">👯 Visao Geral</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(list(colls["despesas"].find({})))

        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            hoje = date.today()
            mes_atual = df_desp[(df_desp["createdAt"].dt.month == hoje.month) & (df_desp["createdAt"].dt.year == hoje.year)]

            # Calcula totais
            total_su = mes_atual[mes_atual["buyer"] == "Susanna"]["total_value"].sum()
            total_pi = mes_atual[mes_atual["buyer"] == "Pietrah"]["total_value"].sum()
            total_ambas = total_su + total_pi

            # === CARDS DE GASTOS DO MES ===
            st.markdown(f'''
            <div style="display: flex; flex-direction: row; gap: 8px; width: 100%; margin-bottom: 12px;">
                <div style="flex: 1; background: linear-gradient(135deg, #c2185b 0%, #e91e63 100%); padding: 8px 10px; border-radius: 8px; color: white; border-left: 3px solid #f48fb1;">
                    <h4 style="margin: 0; font-size: 12px; opacity: 0.9;">⚡ Susanna</h4>
                    <h2 style="margin: 0; font-size: 16px; font-weight: 600;">{fmt(total_su)}</h2>
                </div>
                <div style="flex: 1; background: linear-gradient(135deg, #0277bd 0%, #03a9f4 100%); padding: 8px 10px; border-radius: 8px; color: white; border-left: 3px solid #4fc3f7;">
                    <h4 style="margin: 0; font-size: 12px; opacity: 0.9;">👩 Pietrah</h4>
                    <h2 style="margin: 0; font-size: 16px; font-weight: 600;">{fmt(total_pi)}</h2>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            # Barra comparativa visual
            if total_ambas > 0:
                pct_su = (total_su / total_ambas) * 100
                pct_pi = (total_pi / total_ambas) * 100
                st.markdown(f'''
                <div style="background: rgba(255,255,255,0.1); border-radius: 6px; height: 12px; overflow: hidden; margin-bottom: 8px;">
                    <div style="display: flex; height: 100%;">
                        <div style="background: #e91e63; width: {pct_su}%; height: 100%;"></div>
                        <div style="background: #03a9f4; width: {pct_pi}%; height: 100%;"></div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 10px; color: #888; margin-bottom: 10px;">
                    <span style="color: #f48fb1;">{pct_su:.0f}%</span>
                    <span style="color: #4fc3f7;">{pct_pi:.0f}%</span>
                </div>
                ''', unsafe_allow_html=True)

            st.markdown("---")

            # === SITUACAO / PENDENCIAS ===
            df_emp = pd.DataFrame(list(colls["emprestimos"].find({})))
            su_deve = df_desp[(df_desp["devedor"] == "Susanna") & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            pi_deve = df_desp[(df_desp["devedor"] == "Pietrah") & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()

            if not df_emp.empty:
                df_emp["createdAt"] = pd.to_datetime(df_emp["createdAt"])
                su_deve += df_emp[(df_emp["devedor"] == "Susanna") & (df_emp["status"] == "em aberto")]["valor"].sum()
                pi_deve += df_emp[(df_emp["devedor"] == "Pietrah") & (df_emp["status"] == "em aberto")]["valor"].sum()

            saldo = pi_deve - su_deve

            if abs(saldo) < 0.01:
                st.markdown('<div style="background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%); padding: 12px; border-radius: 8px; text-align: center;"><h3 style="margin: 0; font-size: 16px; color: white;">✨ Quites!</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="font-size: 12px; text-align: center; margin: 4px 0 8px 0; font-weight: 500;">💫 Situacao</p>', unsafe_allow_html=True)

                # Cards de pendencias lado a lado
                st.markdown(f'''
                <div style="display: flex; flex-direction: row; gap: 8px; width: 100%; margin-bottom: 10px;">
                    <div style="flex: 1; background: rgba(233,30,99,0.15); padding: 8px; border-radius: 8px; text-align: center; border: 1px solid rgba(233,30,99,0.3);">
                        <span style="font-size: 10px; color: #f48fb1;">Susanna deve</span>
                        <h3 style="margin: 2px 0 0 0; font-size: 14px; color: white;">{fmt(su_deve)}</h3>
                    </div>
                    <div style="flex: 1; background: rgba(3,169,244,0.15); padding: 8px; border-radius: 8px; text-align: center; border: 1px solid rgba(3,169,244,0.3);">
                        <span style="font-size: 10px; color: #4fc3f7;">Pietrah deve</span>
                        <h3 style="margin: 2px 0 0 0; font-size: 14px; color: white;">{fmt(pi_deve)}</h3>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

                # Resultado final - quem paga
                if saldo > 0:
                    st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #01579b 0%, #0277bd 100%); padding: 10px; border-radius: 8px; text-align: center;">
                        <span style="font-size: 10px; color: #81d4fa;">Resultado</span>
                        <h3 style="margin: 2px 0 0 0; font-size: 14px; color: white;">👩 Pietrah paga {fmt(saldo)} p/ Susanna ⚡</h3>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #880e4f 0%, #c2185b 100%); padding: 10px; border-radius: 8px; text-align: center;">
                        <span style="font-size: 10px; color: #f48fb1;">Resultado</span>
                        <h3 style="margin: 2px 0 0 0; font-size: 14px; color: white;">⚡ Susanna paga {fmt(abs(saldo))} p/ Pietrah 👩</h3>
                    </div>
                    ''', unsafe_allow_html=True)

            st.markdown("---")

            # === TOP CATEGORIAS DE CADA UMA ===
            st.markdown('<p style="font-size: 12px; text-align: center; margin: 4px 0 8px 0; font-weight: 500;">🏆 Top Categorias</p>', unsafe_allow_html=True)

            su_cat = mes_atual[mes_atual["buyer"] == "Susanna"].groupby("label")["total_value"].sum().sort_values(ascending=False).head(3)
            pi_cat = mes_atual[mes_atual["buyer"] == "Pietrah"].groupby("label")["total_value"].sum().sort_values(ascending=False).head(3)

            # Susanna top 3
            if not su_cat.empty:
                st.markdown('<span style="font-size: 10px; color: #f48fb1; font-weight: 500;">⚡ Susanna</span>', unsafe_allow_html=True)
                for cat, val in su_cat.items():
                    pct = (val / total_su * 100) if total_su > 0 else 0
                    st.markdown(f'''
                    <div style="margin-bottom: 4px;">
                        <div style="display: flex; justify-content: space-between; font-size: 9px; color: #ccc;">
                            <span>{cat}</span><span>{fmt(val)}</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); border-radius: 3px; height: 6px; overflow: hidden;">
                            <div style="background: #e91e63; width: {pct}%; height: 100%;"></div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

            st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

            # Pietrah top 3
            if not pi_cat.empty:
                st.markdown('<span style="font-size: 10px; color: #4fc3f7; font-weight: 500;">👩 Pietrah</span>', unsafe_allow_html=True)
                for cat, val in pi_cat.items():
                    pct = (val / total_pi * 100) if total_pi > 0 else 0
                    st.markdown(f'''
                    <div style="margin-bottom: 4px;">
                        <div style="display: flex; justify-content: space-between; font-size: 9px; color: #ccc;">
                            <span>{cat}</span><span>{fmt(val)}</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); border-radius: 3px; height: 6px; overflow: hidden;">
                            <div style="background: #03a9f4; width: {pct}%; height: 100%;"></div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

            # === GASTOS DIVIDIDOS ===
            df_dividido = df_desp[df_desp["pagamento_compartilhado"].str.contains("Dividido", na=False)]
            if not df_dividido.empty:
                df_dividido_mes = df_dividido[(df_dividido["createdAt"].dt.month == hoje.month) & (df_dividido["createdAt"].dt.year == hoje.year)]
                if not df_dividido_mes.empty:
                    total_dividido = df_dividido_mes["total_value"].sum()
                    st.markdown("---")
                    st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%); padding: 10px; border-radius: 8px; text-align: center;">
                        <span style="font-size: 10px; color: #ce93d8;">👯 Gastos Divididos</span>
                        <h3 style="margin: 2px 0 0 0; font-size: 16px; color: white;">{fmt(total_dividido)}</h3>
                        <span style="font-size: 9px; color: #ce93d8;">Cada uma: {fmt(total_dividido/2)}</span>
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            st.info("📝 Sem gastos ainda.")

    # ========== RELATORIO ==========
    elif menu == "📊 Relatorio":
        st.markdown('<p class="page-title">📊 Meu Relatorio</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        df_contas_fixas = pd.DataFrame(list(colls["contas_fixas"].find({"ativo": True})))

        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            df_desp["mes_ano"] = df_desp["createdAt"].dt.to_period("M")

            # Filtros
            meses = sorted(df_desp["mes_ano"].unique(), reverse=True)
            mes_selecionado = st.selectbox("📅 Mes", meses, format_func=lambda x: x.strftime("%B %Y"))

            df_mes = df_desp[df_desp["mes_ano"] == mes_selecionado]
            df_user = df_mes[df_mes["buyer"] == user]

            # Calcula totais de contas fixas do usuario
            user_fixas = 0
            if not df_contas_fixas.empty:
                user_fixas = df_contas_fixas[df_contas_fixas["responsavel"] == user]["valor"].sum()
                divididas = df_contas_fixas[df_contas_fixas["responsavel"] == "Dividido"]["valor"].sum()
                user_fixas += divididas / 2

            # Totais
            total_var = df_user["total_value"].sum()
            total_geral = total_var + user_fixas

            st.markdown(f'<div class="{cor_card}"><h4>Total Geral</h4><h2>{fmt(total_geral)}</h2><small>variaveis + fixas</small></div>', unsafe_allow_html=True)

            st.markdown("---")

            # Breakdown
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'<div class="{cor_card}"><h4>Gastos Variaveis</h4><h2>{fmt(total_var)}</h2></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="{cor_card}"><h4>Contas Fixas</h4><h2>{fmt(user_fixas)}</h2></div>', unsafe_allow_html=True)

            st.markdown("---")

            # Top 3 categorias
            if not df_user.empty:
                st.markdown('<p class="section-title">🏆 Top 3 Categorias</p>', unsafe_allow_html=True)
                top_cat = df_user.groupby("label")["total_value"].sum().sort_values(ascending=False).head(3)
                for i, (cat, val) in enumerate(top_cat.items(), 1):
                    st.caption(f"{i}. {cat}: {fmt(val)}")

            # Grafico por categoria
            if not df_user.empty:
                cat_data = df_user.groupby("label")["total_value"].sum().reset_index()
                if not cat_data.empty:
                    st.markdown('<p class="section-title">📊 Gastos por Categoria</p>', unsafe_allow_html=True)
                    fig = px.pie(cat_data, names="label", values="total_value", hole=0.4, color_discrete_sequence=cores_user)
                    fig.update_traces(textposition='inside', textinfo='percent')
                    fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=130,
                                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                     font=dict(color='white', size=8), legend=dict(font=dict(size=7), orientation="h", y=-0.1))
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Por forma de pagamento
            st.markdown('<p class="section-title">💳 Por Forma de Pagamento</p>', unsafe_allow_html=True)
            pgto = df_user.groupby("payment_method")["total_value"].sum().reset_index()

            if not pgto.empty:
                fig = px.pie(pgto, names="payment_method", values="total_value", hole=0.4)
                fig.update_traces(textposition='inside', textinfo='percent')
                fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=120,
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                 font=dict(color='white', size=8), legend=dict(font=dict(size=7), orientation="h", y=-0.1))
                st.plotly_chart(fig, use_container_width=True)

            # Contas fixas detalhadas
            if not df_contas_fixas.empty:
                contas_user = df_contas_fixas[
                    (df_contas_fixas["responsavel"] == user) |
                    (df_contas_fixas["responsavel"] == "Dividido")
                ]

                if not contas_user.empty:
                    st.markdown("---")
                    with st.expander("📋 Minhas Contas Fixas", expanded=False):
                        for _, conta in contas_user.iterrows():
                            if conta["responsavel"] == "Dividido":
                                valor_display = f"{fmt(conta['valor'])} ({fmt(conta['valor']/2)} cada)"
                                st.caption(f"🔷 **{conta['nome']}** | {conta['categoria']} | {valor_display} | Vence dia {int(conta['dia_vencimento'])}")
                            else:
                                st.caption(f"🔸 **{conta['nome']}** | {conta['categoria']} | {fmt(conta['valor'])} | Vence dia {int(conta['dia_vencimento'])}")
        else:
            st.info("📝 Nenhum gasto registrado.")

    # ========== EVOLUCAO ==========
    elif menu == "📈 Evolucao":
        st.markdown('<p class="page-title">📈 Minha Evolucao</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(list(colls["despesas"].find({})))

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
