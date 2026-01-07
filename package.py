import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from bson import ObjectId
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
    return {"despesas": db["despesas"], "emprestimos": db["emprestimos"], "metas": db["metas"], "quitacoes": db["quitacoes"], "contas_fixas": db["contas_fixas"]}


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

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⚡Susanna", use_container_width=True, type="primary"):
            st.session_state.usuario_atual = "Susanna"
            st.rerun()

    with col2:
        if st.button("👩 Pietrah", use_container_width=True, type="secondary"):
            st.session_state.usuario_atual = "Pietrah"
            st.rerun()


def show_user_badge():
    """Mostra badge do usuario na sidebar com opcao de trocar."""
    user = get_user()
    cor = "#e91e63" if user == "Susanna" else "#03a9f4"

    st.markdown(f"""
    <div style="text-align: center; padding: 10px; background: {cor}20; border-radius: 8px; margin-bottom: 10px;">
        <span style="font-size: 20px;">👩</span>
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
        menu = st.radio("", ["🏠 Inicio", "➕ Novo", "🤝 Acerto", "💸 Emprestimo", "🎯 Metas", "👯 Ambas", "📊 Relatorio", "📈 Evolucao"], label_visibility="collapsed")

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
                <div style="flex: 1; background: {cor_gastos}; padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid {borda_gastos};">
                    <h4 style="margin: 0; font-size: 8px; opacity: 0.9;">💸 Gastos</h4>
                    <h2 style="margin: 0; font-size: 11px; font-weight: 600;">{fmt(gastos_reais)}</h2>
                </div>
                <div style="flex: 1; background: linear-gradient(135deg, #388e3c 0%, #66bb6a 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #81c784;">
                    <h4 style="margin: 0; font-size: 8px; opacity: 0.9;">🐷 Cofrinho</h4>
                    <h2 style="margin: 0; font-size: 11px; font-weight: 600;">{fmt(cofrinho)}</h2>
                </div>
                <div style="flex: 1; background: linear-gradient(135deg, #f57c00 0%, #ffb74d 100%); padding: 4px 6px; border-radius: 6px; color: white; border-left: 2px solid #ffcc80;">
                    <h4 style="margin: 0; font-size: 8px; opacity: 0.9;">💵 Renda Extra</h4>
                    <h2 style="margin: 0; font-size: 11px; font-weight: 600;">{fmt(renda_variavel)}</h2>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            st.markdown("---")

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
                            <span style="font-size: 9px; color: white;">{row["label"]}</span>
                            <span style="font-size: 9px; color: #aaa;">{fmt(row["total_value"])} ({pct_total:.1f}%)</span>
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

            # Saldo
            if abs(saldo) < 0.01:
                st.markdown('<div class="ok-box"><h3>✨ Quites!</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="section-title">💫 Situacao</p>', unsafe_allow_html=True)
                if saldo > 0:
                    # Outro deve pra mim
                    st.markdown(f'<div class="ok-box"><h3>🤑 {outro} te deve {fmt(saldo)}</h3></div>', unsafe_allow_html=True)
                else:
                    # Eu devo pro outro
                    st.markdown(f'<div class="{cor_card}"><h4>Voce deve pra {outro}</h4><h2>{fmt(abs(saldo))}</h2></div>', unsafe_allow_html=True)
        else:
            st.info("📝 Sem registros ainda. Va em '➕ Novo'!")

    # ========== NOVO ==========
    elif menu == "➕ Novo":
        st.markdown('<p class="page-title">➕ Novo Registro</p>', unsafe_allow_html=True)

        with st.form("form_novo_gasto", clear_on_submit=True):

            label = st.selectbox("🏷️ Categoria", ["🍔 Comida", "⛽ Combustivel", "🚗 Automoveis", "🍺 Bebidas", "👗 Vestuario", "💊 Saude", "🎮 Lazer", "📄 Contas", "👨‍👩‍👧 Boa pra familia", "🐷 Cofrinho", "💵 Renda Variavel", "📦 Outros"])
            item = st.text_input("📝 Item")
            description = st.text_input("💬 Descricao")

            c1, c2 = st.columns(2)
            with c1:
                quantidade = st.number_input("🔢 Qtd", min_value=1, value=1)
            with c2:
                preco = st.number_input("💵 Preco", min_value=0.01, value=1.00, format="%.2f")

            pagamento = st.selectbox("💳 Pagamento", ["VR", "Debito", "Credito", "Pix", "Dinheiro"])
            tipo_despesa = st.selectbox("🤝 Tipo", ["👤 Individual", "👯 Nossa (divide)", "✂️ Metade cada"])
            parcelas = st.number_input("📅 Parcelas (0=a vista)", min_value=0, value=0)

            submitted = st.form_submit_button("✅ Salvar Gasto", use_container_width=True)

        if submitted:
            try:
                valor_total = quantidade * preco
                valor_final = valor_total
                if "Metade" in tipo_despesa:
                    valor_final = round(valor_total / 2, 2)

                pend = {"tem_pendencia": False, "devedor": None, "valor_pendente": None, "status_pendencia": None}
                if "Nossa" in tipo_despesa:
                    devedor = outro
                    pend = {"tem_pendencia": True, "devedor": devedor, "valor_pendente": round(valor_final / 2, 2), "status_pendencia": "em aberto"}

                doc = {
                    "label": label, "buyer": user, "item": item, "description": description,
                    "quantity": quantidade, "total_value": valor_final, "payment_method": pagamento,
                    "installment": parcelas, "createdAt": datetime.now(), "pagamento_compartilhado": tipo_despesa, **pend
                }

                result = colls["despesas"].insert_one(doc)

                if "Nossa" in tipo_despesa:
                    colls["quitacoes"].insert_one({
                        "tipo": "despesa_compartilhada", "despesa_id": result.inserted_id, "data": datetime.now(),
                        "credor": user, "devedor": pend["devedor"], "valor": pend["valor_pendente"],
                        "descricao": f"{label} - {item}" if item else label, "observacao": description, "status": "em aberto"
                    })

                if "Metade" in tipo_despesa:
                    doc2 = doc.copy()
                    doc2.pop("_id", None)
                    doc2["buyer"] = outro
                    doc2["registrado_por"] = user
                    colls["despesas"].insert_one(doc2)

                st.success(f"✅ Gasto de {fmt(valor_final)} salvo!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erro: {e}")

        st.markdown("---")

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

        user_deve_desp, outro_deve_desp = 0, 0
        if not df_desp.empty:
            user_deve_desp = df_desp[(df_desp["devedor"] == user) & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            outro_deve_desp = df_desp[(df_desp["devedor"] == outro) & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()

        user_deve_emp, outro_deve_emp = 0, 0
        if not df_emp.empty:
            user_deve_emp = df_emp[(df_emp["devedor"] == user) & (df_emp["status"] == "em aberto")]["valor"].sum()
            outro_deve_emp = df_emp[(df_emp["devedor"] == outro) & (df_emp["status"] == "em aberto")]["valor"].sum()

        user_deve_total = user_deve_desp + user_deve_emp
        outro_deve_total = outro_deve_desp + outro_deve_emp
        saldo = outro_deve_total - user_deve_total

        # Minha situacao
        st.markdown('<p class="section-title">📋 Minha situacao</p>', unsafe_allow_html=True)

        if user_deve_total > 0:
            st.markdown(f'<div class="{cor_card}"><h4>Voce deve</h4><h2>{fmt(user_deve_total)}</h2><small>Desp: {fmt(user_deve_desp)} | Emp: {fmt(user_deve_emp)}</small></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ok-box"><h3>✨ Voce nao deve nada!</h3></div>', unsafe_allow_html=True)

        st.markdown("---")

        # O que o outro deve pra mim
        st.markdown(f'<p class="section-title">💰 {outro} te deve</p>', unsafe_allow_html=True)
        if outro_deve_total > 0:
            st.markdown(f'<div class="{cor_outro}"><h4>{outro} deve</h4><h2>{fmt(outro_deve_total)}</h2><small>Desp: {fmt(outro_deve_desp)} | Emp: {fmt(outro_deve_emp)}</small></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ok-box"><h3>✨ {outro} nao te deve nada!</h3></div>', unsafe_allow_html=True)

        st.markdown("---")

        # Resultado final
        st.markdown('<p class="section-title">💫 Resultado</p>', unsafe_allow_html=True)
        if abs(saldo) < 0.01:
            st.markdown('<div class="ok-box"><h3>✨ Voces estao quites!</h3></div>', unsafe_allow_html=True)
        elif saldo > 0:
            st.markdown(f'<div class="ok-box"><h3>🤑 {outro} te paga {fmt(saldo)}</h3></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="{cor_card}"><h4>Voce paga pra {outro}</h4><h2>{fmt(abs(saldo))}</h2></div>', unsafe_allow_html=True)

        # Detalhes das pendencias
        st.markdown("---")
        st.markdown('<p class="section-title">🔍 Detalhamento</p>', unsafe_allow_html=True)

        if not df_logs.empty and "tipo" in df_logs.columns and "status" in df_logs.columns:
            logs_abertos = df_logs[(df_logs["tipo"] == "despesa_compartilhada") & (df_logs["status"] == "em aberto")]
            meus_logs = logs_abertos[logs_abertos["devedor"] == user]
            if not meus_logs.empty:
                with st.expander(f"🛒 Minhas pendencias ({len(meus_logs)})", expanded=False):
                    for _, log in meus_logs.iterrows():
                        data_str = log["data"].strftime("%d/%m") if pd.notna(log.get("data")) else ""
                        st.caption(f"• {log.get('descricao', '-')} | {fmt(log['valor'])} | {data_str}")

        if not df_emp.empty:
            emp_abertos = df_emp[(df_emp["status"] == "em aberto") & (df_emp["devedor"] == user)]
            if not emp_abertos.empty:
                with st.expander(f"💸 Emprestimos que devo ({len(emp_abertos)})", expanded=False):
                    for _, emp in emp_abertos.iterrows():
                        data_str = emp["createdAt"].strftime("%d/%m") if pd.notna(emp.get("createdAt")) else ""
                        st.caption(f"• {emp['credor']} me emprestou {fmt(emp['valor'])} | {data_str}")

        # Quitar
        if abs(saldo) > 0.01:
            st.markdown("---")  
            st.markdown('<p class="section-title">✅ Quitar</p>', unsafe_allow_html=True)

            with st.form("form_quitar"):
                valor_quitar = st.number_input("Valor", min_value=0.01, max_value=float(max(user_deve_total, outro_deve_total, 0.01)), value=float(abs(saldo)))
                obs_quitacao = st.text_input("Obs")

                if st.form_submit_button("✅ Quitar", use_container_width=True):
                    quitacao = {
                        "tipo": "quitacao", "data": datetime.now(), "valor": valor_quitar,
                        "de": outro if saldo > 0 else user,
                        "para": user if saldo > 0 else outro, "observacao": obs_quitacao
                    }
                    colls["quitacoes"].insert_one(quitacao)

                    quem_paga = outro if saldo > 0 else user
                    colls["despesas"].update_many({"devedor": quem_paga, "status_pendencia": "em aberto"}, {"$set": {"status_pendencia": "quitado", "data_quitacao": datetime.now()}})
                    colls["emprestimos"].update_many({"devedor": quem_paga, "status": "em aberto"}, {"$set": {"status": "quitado", "data_quitacao": datetime.now()}})
                    colls["quitacoes"].update_many({"devedor": quem_paga, "status": "em aberto", "tipo": "despesa_compartilhada"}, {"$set": {"status": "quitado", "data_quitacao": datetime.now()}})

                    st.success("✅ Quitado!")
                    st.balloons()
                    st.rerun()

        # Historico
        if not df_logs.empty and "tipo" in df_logs.columns:
            quitacoes_historico = df_logs[df_logs["tipo"] == "quitacao"]
            if not quitacoes_historico.empty:
                st.markdown("---")
                with st.expander("📜 Historico de quitacoes"):
                    quitacoes_historico["data"] = pd.to_datetime(quitacoes_historico["data"])
                    quitacoes_historico = quitacoes_historico.sort_values("data", ascending=False)
                    for _, row in quitacoes_historico.head(10).iterrows():
                        data_str = row["data"].strftime("%d/%m/%Y") if pd.notna(row.get("data")) else ""
                        st.caption(f"• {row.get('de', '?')} -> {row.get('para', '?')} | {fmt(row['valor'])} | {data_str}")

    # ========== EMPRESTIMOS ==========
    elif menu == "💸 Emprestimo":
        st.markdown('<p class="page-title">💸 Emprestimos</p>', unsafe_allow_html=True)

        with st.expander("➕ Novo Emprestimo", expanded=False):
            with st.form("form_emprestimo", clear_on_submit=True):
                st.markdown(f"**💰 Ajudando uma pobre**")
                valor_emp = st.number_input("💵 Valor", min_value=0.01, value=10.00, format="%.2f")
                motivo = st.text_area("📝 Motivo / Observacao", placeholder="Ex: Emprestei pra pagar o Uber")

                if st.form_submit_button("✅ Registrar", use_container_width=True):
                    colls["emprestimos"].insert_one({
                        "credor": user, "devedor": outro, "valor": valor_emp,
                        "motivo": motivo, "status": "em aberto", "createdAt": datetime.now()
                    })
                    st.success("✅ Emprestimo registrado!")
                    st.rerun()

        df_emp = pd.DataFrame(list(colls["emprestimos"].find({})))

        if not df_emp.empty:
            # Filtrar apenas emprestimos relacionados ao usuario
            df_emp = df_emp[(df_emp["credor"] == user) | (df_emp["devedor"] == user)]

            if not df_emp.empty:
                df_emp["_id"] = df_emp["_id"].astype(str)
                df_emp["createdAt"] = pd.to_datetime(df_emp["createdAt"])
                df_emp["mes_ano"] = df_emp["createdAt"].dt.to_period("M")

                meses = sorted(df_emp["mes_ano"].unique(), reverse=True)

                for mes in meses:
                    df_mes = df_emp[df_emp["mes_ano"] == mes]
                    total_mes = df_mes["valor"].sum()

                    with st.expander(f"📅 {mes.strftime('%B %Y')} | {fmt(total_mes)}"):
                        for _, row in df_mes.iterrows():
                            status_emoji = "🔴" if row["status"] == "em aberto" else "✅"
                            relacao = "emprestei" if row["credor"] == user else "devo"
                            st.markdown(f"{status_emoji} **{relacao.upper()}**: {fmt(row['valor'])}")
                            st.caption(f"📝 {row.get('motivo', 'Sem descricao')} | 🕐 {row['createdAt'].strftime('%d/%m/%Y %H:%M')}")
                            st.markdown("---")
            else:
                st.info("📝 Nenhum emprestimo seu registrado.")
        else:
            st.info("📝 Nenhum emprestimo registrado.")

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
        st.markdown('<p class="page-title">👯 Visao Geral (Ambas)</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(list(colls["despesas"].find({})))

        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            hoje = date.today()
            mes_atual = df_desp[df_desp["createdAt"].dt.month == hoje.month]

            # Gastos do mes
            st.markdown('<p class="section-title">💸 Gastos este mes</p>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                total_su = mes_atual[mes_atual["buyer"] == "Susanna"]["total_value"].sum()
                st.markdown(f'<div class="su-card"><h4>Susanna</h4><h2>{fmt(total_su)}</h2></div>', unsafe_allow_html=True)
            with c2:
                total_pi = mes_atual[mes_atual["buyer"] == "Pietrah"]["total_value"].sum()
                st.markdown(f'<div class="pi-card"><h4>Pietrah</h4><h2>{fmt(total_pi)}</h2></div>', unsafe_allow_html=True)

            # Graficos por categoria
            st.markdown('<p class="section-title">📊 Por Categoria</p>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            cores_su = ['#e91e63', '#f48fb1', '#f06292', '#ec407a', '#d81b60', '#c2185b', '#ad1457', '#880e4f', '#ff80ab', '#ff4081']
            cores_pi = ['#03a9f4', '#4fc3f7', '#29b6f6', '#0288d1', '#039be5', '#0277bd', '#01579b', '#81d4fa', '#00bcd4', '#26c6da']

            with c1:
                su_cat = mes_atual[mes_atual["buyer"] == "Susanna"].groupby("label")["total_value"].sum().reset_index()
                if not su_cat.empty:
                    fig_su = px.pie(su_cat, names="label", values="total_value", hole=0.5, color_discrete_sequence=cores_su)
                    fig_su.update_traces(textposition='inside', textinfo='percent', marker=dict(line=dict(color='#ff80ab', width=1)))
                    fig_su.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=120,
                                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white', size=8))
                    st.plotly_chart(fig_su, use_container_width=True)
                else:
                    st.caption("Sem gastos")

            with c2:
                pi_cat = mes_atual[mes_atual["buyer"] == "Pietrah"].groupby("label")["total_value"].sum().reset_index()
                if not pi_cat.empty:
                    fig_pi = px.pie(pi_cat, names="label", values="total_value", hole=0.5, color_discrete_sequence=cores_pi)
                    fig_pi.update_traces(textposition='inside', textinfo='percent', marker=dict(line=dict(color='#4fc3f7', width=1)))
                    fig_pi.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=120,
                                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white', size=8))
                    st.plotly_chart(fig_pi, use_container_width=True)
                else:
                    st.caption("Sem gastos")

            st.markdown("---")

            # Pendencias
            df_emp = pd.DataFrame(list(colls["emprestimos"].find({})))
            su_deve = df_desp[(df_desp["devedor"] == "Susanna") & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            pi_deve = df_desp[(df_desp["devedor"] == "Pietrah") & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()

            if not df_emp.empty:
                df_emp["createdAt"] = pd.to_datetime(df_emp["createdAt"])
                su_deve += df_emp[(df_emp["devedor"] == "Susanna") & (df_emp["status"] == "em aberto")]["valor"].sum()
                pi_deve += df_emp[(df_emp["devedor"] == "Pietrah") & (df_emp["status"] == "em aberto")]["valor"].sum()

            saldo = pi_deve - su_deve

            # Saldo
            if abs(saldo) < 0.01:
                st.markdown('<div class="ok-box"><h3>✨ Quites!</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="section-title">💫 Pendencias</p>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<div class="su-card"><h4>Susanna deve</h4><h2>{fmt(su_deve)}</h2></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="pi-card"><h4>Pietrah deve</h4><h2>{fmt(pi_deve)}</h2></div>', unsafe_allow_html=True)

                # Resultado final
                if saldo > 0:
                    st.markdown(f'<div class="pi-deve"><p>Pietrah paga {fmt(saldo)} p/ Susanna</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="su-deve"><p>Susanna paga {fmt(abs(saldo))} p/ Pietrah</p></div>', unsafe_allow_html=True)

            # Gastos compartilhados
            st.markdown("---")
            st.markdown('<p class="section-title">👯 Gastos Compartilhados</p>', unsafe_allow_html=True)

            df_nossa = df_desp[df_desp["pagamento_compartilhado"].str.contains("Nossa", na=False)]
            if not df_nossa.empty:
                df_nossa_mes = df_nossa[df_nossa["createdAt"].dt.month == hoje.month]
                total_compartilhado = df_nossa_mes["total_value"].sum()

                st.markdown(f'<div class="info-box"><h2>{fmt(total_compartilhado)}</h2><p>Total compartilhado | Cada: {fmt(total_compartilhado/2)}</p></div>', unsafe_allow_html=True)
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
