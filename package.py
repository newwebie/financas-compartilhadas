import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from bson import ObjectId
import certifi

# Configuração da página
st.set_page_config(
    page_title="💰 Finanças",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS customizado para mobile
st.markdown("""
<style>
    /* Sidebar mobile-friendly */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        min-width: 200px;
        max-width: 250px;
    }
    
    /* Cores Susanna - Rosa/Magenta */
    .susanna-card {
        background: linear-gradient(135deg, #e91e63 0%, #ff6090 100%);
        padding: 12px;
        border-radius: 12px;
        color: white;
        margin: 5px 0;
        border-left: 4px solid #ff80ab;
        font-size: 14px;
    }
    .susanna-card h4 {
        margin: 0 0 5px 0;
        font-size: 14px;
    }
    .susanna-card h2 {
        margin: 0;
        font-size: 20px;
    }
    .susanna-card small {
        font-size: 11px;
    }
    .susanna-header {
        color: #ff80ab !important;
        font-size: 14px;
        margin: 5px 0;
    }
    
    /* Cores Pietrah - Azul/Cyan */
    .pietrah-card {
        background: linear-gradient(135deg, #0288d1 0%, #4fc3f7 100%);
        padding: 12px;
        border-radius: 12px;
        color: white;
        margin: 5px 0;
        border-left: 4px solid #81d4fa;
        font-size: 14px;
    }
    .pietrah-card h4 {
        margin: 0 0 5px 0;
        font-size: 14px;
    }
    .pietrah-card h2 {
        margin: 0;
        font-size: 20px;
    }
    .pietrah-card small {
        font-size: 11px;
    }
    .pietrah-header {
        color: #4fc3f7 !important;
        font-size: 14px;
        margin: 5px 0;
    }
    
    /* Cards gerais */
    .block-container {
        padding: 1rem 0.5rem;
        max-width: 100%;
    }
    
    /* Títulos */
    .page-title {
        font-size: 20px;
        text-align: center;
        margin: 10px 0;
        padding: 0 10px;
    }
    .section-title {
        font-size: 16px;
        text-align: center;
        margin: 8px 0;
    }
    
    div[data-testid="stExpander"] {
        border-radius: 10px;
        border: 1px solid #333;
        font-size: 14px;
    }
    
    /* Box de sucesso - Verde */
    .success-box {
        background: linear-gradient(135deg, #1b5e20 0%, #4caf50 100%);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin: 8px 0;
        border: 2px solid #81c784;
        font-size: 14px;
    }
    .success-box h2 {
        font-size: 18px;
        margin: 0;
    }
    
    /* Box de info - Roxo */
    .info-box {
        background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin: 8px 0;
        border: 2px solid #ba68c8;
        font-size: 14px;
    }
    .info-box h3 {
        font-size: 14px;
        margin: 0 0 5px 0;
    }
    .info-box h2 {
        font-size: 20px;
        margin: 0;
    }
    .info-box p {
        font-size: 12px;
        margin: 5px 0 0 0;
    }
    
    /* Susanna deve pagar */
    .susanna-deve {
        background: linear-gradient(135deg, #880e4f 0%, #ad1457 100%);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin: 8px 0;
        border: 2px solid #f48fb1;
    }
    .susanna-deve h3 {
        font-size: 14px;
        margin: 0 0 5px 0;
    }
    .susanna-deve h2 {
        font-size: 22px;
        margin: 0;
    }
    .susanna-deve p {
        font-size: 12px;
        margin: 5px 0 0 0;
    }
    
    /* Pietrah deve pagar */
    .pietrah-deve {
        background: linear-gradient(135deg, #01579b 0%, #0277bd 100%);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin: 8px 0;
        border: 2px solid #4fc3f7;
    }
    .pietrah-deve h3 {
        font-size: 14px;
        margin: 0 0 5px 0;
    }
    .pietrah-deve h2 {
        font-size: 22px;
        margin: 0;
    }
    .pietrah-deve p {
        font-size: 12px;
        margin: 5px 0 0 0;
    }
    
    /* Mobile adjustments */
    @media (max-width: 768px) {
        .block-container {
            padding: 0.5rem;
        }
    }
    
    /* Radio buttons as menu */
    div[data-testid="stSidebar"] .stRadio > div {
        flex-direction: column;
        gap: 3px;
    }
    div[data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(255,255,255,0.05);
        padding: 10px 12px;
        border-radius: 8px;
        margin: 2px 0;
        font-size: 14px;
    }
    div[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255,255,255,0.15);
    }
</style>
""", unsafe_allow_html=True)


def connect_mongodb():
    """Conecta ao MongoDB"""
    URI = st.secrets["uri"]
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=30000, connectTimeoutMS=30000,
            socketTimeoutMS=30000, maxPoolSize=10, retryWrites=True)
        client.admin.command('ping')
        return client
    except ConnectionFailure as e:
        st.error(f"❌ Falha na conexão: {e}")
        raise
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        raise


def get_collections(client):
    """Retorna as collections do banco"""
    URI = st.secrets["uri"]
    try:
        if "/" in URI.split("@")[-1]:
            db_name = URI.split("/")[-1].split("?")[0]
            if not db_name: db_name = "financas"
        else:
            db_name = "financas"
    except:
        db_name = "financas"
    
    db = client[db_name]
    return {
        "despesas": db["despesas"],
        "emprestimos": db["emprestimos"],
        "metas": db["metas"],
        "quitacoes": db["quitacoes"]
    }


def formatar_brl(valor):
    """Formata valor para BRL"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def get_mes_ano_options(df):
    """Retorna lista de mês/ano disponíveis"""
    if df.empty or "createdAt" not in df.columns:
        return []
    df["mes_ano"] = df["createdAt"].dt.to_period("M")
    return sorted(df["mes_ano"].unique(), reverse=True)


def main():
    client = connect_mongodb()
    if client is None:
        st.stop()
    
    colls = get_collections(client)
    
    # Menu lateral
    with st.sidebar:
        st.markdown("## 💰 Finanças")
        st.markdown("---")
        
        menu = st.radio(
            "Menu",
            [
                "🏠 Início",
                "➕ Novo Gasto",
                "🤝 Acerto de Contas",
                "💸 Empréstimos",
                "🎯 Metas",
                "👯 Gastos Juntas",
                "📊 Relatório",
                "📈 Evolução"
            ],
            label_visibility="collapsed"
        )
    
    # ========== PÁGINA INÍCIO ==========
    if menu == "🏠 Início":
        st.markdown('<p class="page-title">👋 Bem-vindas!</p>', unsafe_allow_html=True)
        
        # Carregar dados
        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        df_emp = pd.DataFrame(list(colls["emprestimos"].find({})))
        
        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            
            # Mês atual
            hoje = date.today()
            mes_atual = df_desp[df_desp["createdAt"].dt.month == hoje.month]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<p class="susanna-header"><strong>Susanna</strong></p>', unsafe_allow_html=True)
                total_su = mes_atual[mes_atual["buyer"] == "Susanna"]["total_value"].sum()
                st.markdown(f'<div class="susanna-card"><h3>Gastos este mês</h3><h2>{formatar_brl(total_su)}</h2></div>', unsafe_allow_html=True)
                
            with col2:
                st.markdown('<p class="pietrah-header"><strong>Pietrah</strong></p>', unsafe_allow_html=True)
                total_pi = mes_atual[mes_atual["buyer"] == "Pietrah"]["total_value"].sum()
                st.markdown(f'<div class="pietrah-card"><h3>Gastos este mês</h3><h2>{formatar_brl(total_pi)}</h2></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Gráficos de categoria por pessoa
            st.markdown('<p class="section-title">📊 Gastos por Categoria</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            # Paleta de cores Susanna (tons de rosa/magenta)
            cores_susanna = ['#e91e63', '#f48fb1', '#f06292', '#ec407a', '#d81b60', '#c2185b', '#ad1457', '#880e4f', '#ff80ab', '#ff4081']
            
            # Paleta de cores Pietrah (tons de azul/cyan)
            cores_pietrah = ['#0288d1', '#4fc3f7', '#29b6f6', '#03a9f4', '#039be5', '#0277bd', '#01579b', '#81d4fa', '#00bcd4', '#26c6da']
            
            with col1:
                st.markdown('<p class="susanna-header"><strong>Susanna</strong></p>', unsafe_allow_html=True)
                su_cat = mes_atual[mes_atual["buyer"] == "Susanna"].groupby("label")["total_value"].sum().reset_index()
                if not su_cat.empty:
                    fig_su = px.pie(su_cat, names="label", values="total_value", hole=0.4,
                                   color_discrete_sequence=cores_susanna)
                    fig_su.update_traces(textposition='outside', textinfo='label+percent',
                                        marker=dict(line=dict(color='#ff80ab', width=2)))
                    fig_su.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=200,
                                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                        font=dict(color='white', size=10))
                    st.plotly_chart(fig_su, use_container_width=True)
                else:
                    st.info("Sem gastos este mês")
            
            with col2:
                st.markdown('<p class="pietrah-header"><strong>Pietrah</strong></p>', unsafe_allow_html=True)
                pi_cat = mes_atual[mes_atual["buyer"] == "Pietrah"].groupby("label")["total_value"].sum().reset_index()
                if not pi_cat.empty:
                    fig_pi = px.pie(pi_cat, names="label", values="total_value", hole=0.4,
                                   color_discrete_sequence=cores_pietrah)
                    fig_pi.update_traces(textposition='outside', textinfo='label+percent',
                                        marker=dict(line=dict(color='#4fc3f7', width=2)))
                    fig_pi.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20), height=300,
                                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                        font=dict(color='white'))
                    st.plotly_chart(fig_pi, use_container_width=True)
                else:
                    st.info("Sem gastos este mês")
            
            st.markdown("---")
            
            # Saldo entre elas
            su_deve = df_desp[(df_desp["devedor"] == "Susanna") & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            pi_deve = df_desp[(df_desp["devedor"] == "Pietrah") & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            
            # Adicionar empréstimos ao saldo
            if not df_emp.empty:
                df_emp["createdAt"] = pd.to_datetime(df_emp["createdAt"])
                emp_su_deve = df_emp[(df_emp["devedor"] == "Susanna") & (df_emp["status"] == "em aberto")]["valor"].sum()
                emp_pi_deve = df_emp[(df_emp["devedor"] == "Pietrah") & (df_emp["status"] == "em aberto")]["valor"].sum()
                su_deve += emp_su_deve
                pi_deve += emp_pi_deve
            
            saldo = pi_deve - su_deve
            
            st.markdown("### 💫 Saldo entre vocês")
            
            if abs(saldo) < 0.01:
                st.markdown('<div class="success-box">✨ Vocês estão quites! ✨</div>', unsafe_allow_html=True)
            elif saldo > 0:
                st.markdown(f'<div class="pietrah-deve">Pietrah deve {formatar_brl(saldo)} para Susanna</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="susanna-deve">Susanna deve {formatar_brl(abs(saldo))} para Pietrah</div>', unsafe_allow_html=True)
        else:
            st.info("📝 Nenhum gasto registrado ainda. Comece em '➕ Novo Gasto'!")
    
    # ========== PÁGINA NOVO GASTO ==========
    elif menu == "➕ Novo Gasto":
        st.markdown('<p class="page-title">➕ Novo Gasto</p>', unsafe_allow_html=True)
        
        # Campos fora do form para atualização dinâmica do total
        compradora = st.selectbox("👤 Quem comprou?", ["Susanna", "Pietrah"], key="sel_compradora")
        
        label = st.selectbox("🏷️ Categoria", [
            "🍔 Comida", "🛒 Mercado", "⛽ Combustível", "🚗 Automóveis", 
            "🍺 Bebidas", "👗 Vestuário", "💊 Saúde", "🎮 Lazer",
            "📄 Contas", "👨‍👩‍👧 Boa pra família", "🐷 Cofrinho", "📦 Outros"
        ], key="sel_categoria")
        
        item = st.text_input("📝 Item", key="txt_item")
        description = st.text_input("💬 Descrição (opcional)", key="txt_desc")
        
        col1, col2 = st.columns(2)
        with col1:
            quantidade = st.number_input("🔢 Quantidade", min_value=1, value=1, key="num_qtd")
        with col2:
            preco = st.number_input("💵 Preço unitário", min_value=0.01, value=1.00, format="%.2f", key="num_preco")
        
        # Total dinâmico
        valor_total = quantidade * preco
        st.info(f"💰 **Total: {formatar_brl(valor_total)}**")
        
        pagamento = st.selectbox("💳 Forma de pagamento", ["VR 🍽️", "Débito 💳", "Crédito 💳", "Pix 📱", "Dinheiro 💵"], key="sel_pgto")
        
        tipo_despesa = st.selectbox("🤝 Tipo de despesa", [
            "👤 Individual (só minha)",
            "👯 Nossa (divide no meio)",
            "✂️ Cada uma pagou metade"
        ], key="sel_tipo")
        
        parcelas = st.number_input("📅 Parcelas (0 = à vista)", min_value=0, value=0, key="num_parcelas")
        
        if st.button("✅ Salvar Gasto", use_container_width=True, key="btn_salvar_gasto"):
            try:
                valor_final = valor_total
                
                if "Cada uma pagou metade" in tipo_despesa:
                    valor_final = round(valor_total / 2, 2)
                
                def gerar_pendencia(buyer, tipo, valor):
                    if "Cada uma pagou metade" in tipo:
                        return {"tem_pendencia": False, "devedor": None, "valor_pendente": None, "status_pendencia": None}
                    if "Nossa" in tipo:
                        devedor = "Pietrah" if buyer == "Susanna" else "Susanna"
                        return {"tem_pendencia": True, "devedor": devedor, "valor_pendente": round(valor / 2, 2), "status_pendencia": "em aberto"}
                    return {"tem_pendencia": False, "devedor": None, "valor_pendente": None, "status_pendencia": None}
                
                pendencia = gerar_pendencia(compradora, tipo_despesa, valor_final)
                
                doc = {
                    "label": label, "buyer": compradora, "item": item, "description": description,
                    "quantity": quantidade, "total_value": valor_final, "payment_method": pagamento.split()[0],
                    "installment": parcelas, "createdAt": datetime.now(),
                    "pagamento_compartilhado": tipo_despesa,
                    **pendencia
                }
                
                result = colls["despesas"].insert_one(doc)
                
                # Se for gasto "Nossa", registrar no acerto de contas
                if "Nossa" in tipo_despesa:
                    devedor = "Pietrah" if compradora == "Susanna" else "Susanna"
                    log_acerto = {
                        "tipo": "despesa_compartilhada",
                        "despesa_id": result.inserted_id,
                        "data": datetime.now(),
                        "credor": compradora,
                        "devedor": devedor,
                        "valor": round(valor_final / 2, 2),
                        "descricao": f"{label} - {item}" if item else label,
                        "observacao": description,
                        "status": "em aberto"
                    }
                    colls["quitacoes"].insert_one(log_acerto)
                
                if "Cada uma pagou metade" in tipo_despesa:
                    outra = "Pietrah" if compradora == "Susanna" else "Susanna"
                    doc2 = doc.copy()
                    doc2.pop("_id", None)
                    doc2["buyer"] = outra
                    doc2["registrado_por"] = compradora
                    colls["despesas"].insert_one(doc2)
                
                st.success("✅ Gasto registrado com sucesso!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erro: {e}")
        
        st.markdown("---")
        
        # Cadastro de Contas Fixas
        with st.expander("📋 Cadastrar Conta Fixa"):
            with st.form("form_conta_fixa", clear_on_submit=True):
                st.markdown("**Registre contas que se repetem todo mês**")
                
                nome_conta = st.text_input("📝 Nome da conta", placeholder="Ex: Aluguel, Internet, Luz...")
                valor_conta = st.number_input("💵 Valor", min_value=0.01, value=100.00, format="%.2f")
                dia_vencimento = st.number_input("📅 Dia do vencimento", min_value=1, max_value=31, value=10)
                responsavel = st.selectbox("👤 Responsável pelo pagamento", ["Susanna", "Pietrah", "Dividido"])
                categoria_conta = st.selectbox("🏷️ Categoria", [
                    "🏠 Aluguel", "💡 Luz", "💧 Água", "📶 Internet", 
                    "📱 Celular", "🎬 Streaming", "🏥 Plano de Saúde", "📦 Outros"
                ])
                obs_conta = st.text_input("💬 Observação (opcional)")
                
                if st.form_submit_button("✅ Cadastrar Conta Fixa", use_container_width=True):
                    conta_fixa = {
                        "nome": nome_conta,
                        "valor": valor_conta,
                        "dia_vencimento": dia_vencimento,
                        "responsavel": responsavel,
                        "categoria": categoria_conta,
                        "observacao": obs_conta,
                        "ativo": True,
                        "createdAt": datetime.now()
                    }
                    
                    # Criar collection contas_fixas se não existir
                    colls["contas_fixas"] = client[colls["despesas"].database.name]["contas_fixas"]
                    colls["contas_fixas"].insert_one(conta_fixa)
                    st.success("✅ Conta fixa cadastrada!")
                    st.rerun()
    
    # ========== PÁGINA ACERTO DE CONTAS ==========
    elif menu == "🤝 Acerto de Contas":
        st.markdown('<p class="page-title">🤝 Acerto de Contas</p>', unsafe_allow_html=True)
        
        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        df_emp = pd.DataFrame(list(colls["emprestimos"].find({})))
        df_logs = pd.DataFrame(list(colls["quitacoes"].find({})))
        
        # Calcular pendências de despesas
        su_deve_desp = 0
        pi_deve_desp = 0
        
        if not df_desp.empty:
            su_deve_desp = df_desp[(df_desp["devedor"] == "Susanna") & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            pi_deve_desp = df_desp[(df_desp["devedor"] == "Pietrah") & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
        
        # Calcular pendências de empréstimos
        su_deve_emp = 0
        pi_deve_emp = 0
        
        if not df_emp.empty:
            su_deve_emp = df_emp[(df_emp["devedor"] == "Susanna") & (df_emp["status"] == "em aberto")]["valor"].sum()
            pi_deve_emp = df_emp[(df_emp["devedor"] == "Pietrah") & (df_emp["status"] == "em aberto")]["valor"].sum()
        
        su_deve_total = su_deve_desp + su_deve_emp
        pi_deve_total = pi_deve_desp + pi_deve_emp
        
        saldo = pi_deve_total - su_deve_total
        
        # Cards de resumo
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'''<div class="susanna-card">
                <h4>Susanna deve</h4>
                <h2>{formatar_brl(su_deve_total)}</h2>
                <small>Despesas: {formatar_brl(su_deve_desp)} | Empréstimos: {formatar_brl(su_deve_emp)}</small>
            </div>''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''<div class="pietrah-card">
                <h4>Pietrah deve</h4>
                <h2>{formatar_brl(pi_deve_total)}</h2>
                <small>Despesas: {formatar_brl(pi_deve_desp)} | Empréstimos: {formatar_brl(pi_deve_emp)}</small>
            </div>''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Saldo final
        if abs(saldo) < 0.01:
            st.markdown('<div class="success-box"><h2>✨ Vocês estão quites! ✨</h2></div>', unsafe_allow_html=True)
        elif saldo > 0:
            st.markdown(f'<div class="pietrah-deve"><h3>Pietrah deve pagar</h3><h2>{formatar_brl(saldo)}</h2><p>para Susanna</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="susanna-deve"><h3>Susanna deve pagar</h3><h2>{formatar_brl(abs(saldo))}</h2><p>para Pietrah</p></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detalhamento das pendências
        st.markdown('<p class="section-title">📋 De onde vem cada valor</p>', unsafe_allow_html=True)
        
        # Pendências de despesas compartilhadas
        if not df_logs.empty and "tipo" in df_logs.columns and "status" in df_logs.columns:
            logs_abertos = df_logs[(df_logs["tipo"] == "despesa_compartilhada") & (df_logs["status"] == "em aberto")]
            if not logs_abertos.empty:
                with st.expander("🛒 Despesas Compartilhadas em Aberto", expanded=True):
                    for _, log in logs_abertos.iterrows():
                        data_str = log["data"].strftime("%d/%m/%Y") if pd.notna(log.get("data")) else ""
                        st.markdown(f"""
                        **{log.get('descricao', 'Sem descrição')}**
                        - 💵 Valor: {formatar_brl(log['valor'])}
                        - 👤 {log['devedor']} deve para {log['credor']}
                        - 📅 {data_str}
                        - 📝 {log.get('observacao', '') or 'Sem observação'}
                        ---
                        """)
        
        # Pendências de empréstimos
        if not df_emp.empty:
            emp_abertos = df_emp[df_emp["status"] == "em aberto"]
            if not emp_abertos.empty:
                with st.expander("💸 Empréstimos em Aberto", expanded=True):
                    for _, emp in emp_abertos.iterrows():
                        data_str = emp["createdAt"].strftime("%d/%m/%Y") if pd.notna(emp.get("createdAt")) else ""
                        st.markdown(f"""
                        **Empréstimo**
                        - 💵 Valor: {formatar_brl(emp['valor'])}
                        - 👤 {emp['devedor']} deve para {emp['credor']}
                        - 📅 {data_str}
                        - 📝 {emp.get('motivo', '') or 'Sem motivo informado'}
                        ---
                        """)
        
        st.markdown("---")
        
        # Botão para quitar tudo
        st.markdown('<p class="section-title">💸 Quitar Pendências</p>', unsafe_allow_html=True)
        
        if abs(saldo) > 0.01:
            with st.form("form_quitar"):
                valor_quitar = st.number_input("Valor a quitar", min_value=0.01, max_value=float(max(su_deve_total, pi_deve_total)), value=float(abs(saldo)))
                obs_quitacao = st.text_input("📝 Observação (opcional)")
                
                if st.form_submit_button("✅ Registrar Quitação", use_container_width=True):
                    quitacao = {
                        "tipo": "quitacao",
                        "data": datetime.now(),
                        "valor": valor_quitar,
                        "de": "Pietrah" if saldo > 0 else "Susanna",
                        "para": "Susanna" if saldo > 0 else "Pietrah",
                        "observacao": obs_quitacao
                    }
                    colls["quitacoes"].insert_one(quitacao)
                    
                    # Quitar pendências de despesas
                    if saldo > 0:
                        colls["despesas"].update_many(
                            {"devedor": "Pietrah", "status_pendencia": "em aberto"},
                            {"$set": {"status_pendencia": "quitado", "data_quitacao": datetime.now()}}
                        )
                        colls["emprestimos"].update_many(
                            {"devedor": "Pietrah", "status": "em aberto"},
                            {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                        )
                        colls["quitacoes"].update_many(
                            {"devedor": "Pietrah", "status": "em aberto", "tipo": "despesa_compartilhada"},
                            {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                        )
                    else:
                        colls["despesas"].update_many(
                            {"devedor": "Susanna", "status_pendencia": "em aberto"},
                            {"$set": {"status_pendencia": "quitado", "data_quitacao": datetime.now()}}
                        )
                        colls["emprestimos"].update_many(
                            {"devedor": "Susanna", "status": "em aberto"},
                            {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                        )
                        colls["quitacoes"].update_many(
                            {"devedor": "Susanna", "status": "em aberto", "tipo": "despesa_compartilhada"},
                            {"$set": {"status": "quitado", "data_quitacao": datetime.now()}}
                        )
                    
                    st.success("✅ Quitação registrada!")
                    st.balloons()
                    st.rerun()
        
        # Histórico de quitações
        if not df_logs.empty and "tipo" in df_logs.columns:
            quitacoes_historico = df_logs[df_logs["tipo"] == "quitacao"]
            if not quitacoes_historico.empty:
                st.markdown('<p class="section-title">📜 Histórico de Quitações</p>', unsafe_allow_html=True)
                quitacoes_historico = quitacoes_historico.sort_values("data", ascending=False)
                
                for _, row in quitacoes_historico.head(10).iterrows():
                    data_str = row["data"].strftime("%d/%m/%Y") if pd.notna(row.get("data")) else ""
                    with st.expander(f"💸 {row.get('de', '?')} → {row.get('para', '?')} | {formatar_brl(row['valor'])} | {data_str}"):
                        if row.get("observacao"):
                            st.write(f"📝 {row['observacao']}")
    
    # ========== PÁGINA EMPRÉSTIMOS ==========
    elif menu == "💸 Empréstimos":
        st.markdown('<p class="page-title">💸 Empréstimos</p>', unsafe_allow_html=True)
        
        # Novo empréstimo
        with st.expander("➕ Registrar Novo Empréstimo", expanded=False):
            with st.form("form_emprestimo", clear_on_submit=True):
                quem_emprestou = st.selectbox("💰 Quem emprestou?", ["Susanna", "Pietrah"])
                
                valor_emp = st.number_input("💵 Valor", min_value=0.01, value=10.00, format="%.2f")
                motivo = st.text_area("📝 Motivo / Observação", placeholder="Ex: Emprestei pra pagar o Uber")
                
                if st.form_submit_button("✅ Registrar Empréstimo", use_container_width=True):
                    devedor = "Pietrah" if quem_emprestou == "Susanna" else "Susanna"
                    
                    emp_doc = {
                        "credor": quem_emprestou,
                        "devedor": devedor,
                        "valor": valor_emp,
                        "motivo": motivo,
                        "status": "em aberto",
                        "createdAt": datetime.now()
                    }
                    colls["emprestimos"].insert_one(emp_doc)
                    st.success("✅ Empréstimo registrado!")
                    st.rerun()
        
        # Listar empréstimos por mês
        df_emp = pd.DataFrame(list(colls["emprestimos"].find({})))
        
        if not df_emp.empty:
            df_emp["_id"] = df_emp["_id"].astype(str)
            df_emp["createdAt"] = pd.to_datetime(df_emp["createdAt"])
            df_emp["mes_ano"] = df_emp["createdAt"].dt.to_period("M")
            
            meses = sorted(df_emp["mes_ano"].unique(), reverse=True)
            
            for mes in meses:
                df_mes = df_emp[df_emp["mes_ano"] == mes]
                total_mes = df_mes["valor"].sum()
                
                with st.expander(f"📅 {mes.strftime('%B %Y')} | Total: {formatar_brl(total_mes)}"):
                    for _, row in df_mes.iterrows():
                        status_emoji = "🔴" if row["status"] == "em aberto" else "✅"
                        st.markdown(f"""
                        {status_emoji} **{row['credor']}** emprestou **{formatar_brl(row['valor'])}** para **{row['devedor']}**
                        
                        📝 _{row.get('motivo', 'Sem descrição')}_
                        
                        🕐 {row['createdAt'].strftime('%d/%m/%Y %H:%M')}
                        
                        ---
                        """)
        else:
            st.info("📝 Nenhum empréstimo registrado ainda.")
    
    # ========== PÁGINA METAS ==========
    elif menu == "🎯 Metas":
        st.markdown('<p class="page-title">🎯 Metas e Orçamento</p>', unsafe_allow_html=True)
        
        # Seletor de usuário
        usuario_metas = st.selectbox("👤 Visualizar metas de:", ["Susanna", "Pietrah", "Ambas"], key="sel_usuario_metas")
        
        st.markdown("---")
        
        # Criar nova meta
        with st.expander("➕ Criar Nova Meta", expanded=False):
            with st.form("form_meta", clear_on_submit=True):
                categoria_meta = st.selectbox("🏷️ Categoria", [
                    "🍔 Comida", "🛒 Mercado", "⛽ Combustível", "🚗 Automóveis", 
                    "🍺 Bebidas", "👗 Vestuário", "💊 Saúde", "🎮 Lazer",
                    "📄 Contas", "👨‍👩‍👧 Boa pra família", "📦 Outros", "💰 Total Geral"
                ])
                
                pessoa_meta = st.selectbox("👤 Para quem?", ["Susanna", "Pietrah", "Ambas"])
                
                valor_meta = st.number_input("💵 Limite mensal", min_value=1.00, value=500.00, format="%.2f")
                
                if st.form_submit_button("✅ Criar Meta", use_container_width=True):
                    meta_doc = {
                        "categoria": categoria_meta,
                        "pessoa": pessoa_meta,
                        "limite": valor_meta,
                        "ativo": True,
                        "createdAt": datetime.now()
                    }
                    colls["metas"].insert_one(meta_doc)
                    st.success("✅ Meta criada!")
                    st.rerun()
        
        # Mostrar metas e progresso
        df_metas = pd.DataFrame(list(colls["metas"].find({"ativo": True})))
        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        
        if not df_metas.empty and not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            hoje = date.today()
            df_mes = df_desp[df_desp["createdAt"].dt.month == hoje.month]
            
            # Filtrar metas pelo usuário selecionado
            if usuario_metas != "Ambas":
                df_metas_filtrado = df_metas[(df_metas["pessoa"] == usuario_metas) | (df_metas["pessoa"] == "Ambas")]
            else:
                df_metas_filtrado = df_metas
            
            if df_metas_filtrado.empty:
                st.info(f"📝 Nenhuma meta cadastrada para {usuario_metas}.")
            else:
                st.markdown(f'<p class="section-title">📊 Progresso - {usuario_metas}</p>', unsafe_allow_html=True)
                
                for _, meta in df_metas_filtrado.iterrows():
                    cat = meta["categoria"]
                    pessoa = meta["pessoa"]
                    limite = meta["limite"]
                    
                    # Filtrar gastos
                    if pessoa == "Ambas":
                        if "Total" in cat:
                            gasto = df_mes["total_value"].sum()
                        else:
                            gasto = df_mes[df_mes["label"] == cat]["total_value"].sum()
                    else:
                        if "Total" in cat:
                            gasto = df_mes[df_mes["buyer"] == pessoa]["total_value"].sum()
                        else:
                            gasto = df_mes[(df_mes["buyer"] == pessoa) & (df_mes["label"] == cat)]["total_value"].sum()
                    
                    pct = min((gasto / limite) * 100, 100) if limite > 0 else 0
                    restante = max(limite - gasto, 0)
                    
                    st.markdown(f"**{cat}** - {pessoa}")
                    st.progress(pct / 100)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.caption(f"💸: {formatar_brl(gasto)}")
                    col2.caption(f"🎯: {formatar_brl(limite)}")
                    col3.caption(f"💰: {formatar_brl(restante)}")
                    
                    if pct >= 100:
                        st.warning("⚠️ Meta ultrapassada!")
                    elif pct >= 80:
                        st.info("⚡ Atenção: próximo do limite!")
                    
                    st.markdown("---")
        else:
            st.info("📝 Crie metas para acompanhar seus gastos!")
    
    # ========== PÁGINA GASTOS JUNTAS ==========
    elif menu == "👯 Gastos Juntas":
        st.markdown('<p class="page-title">👯 Gastos Compartilhados</p>', unsafe_allow_html=True)
        
        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        
        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            
            # Filtrar apenas gastos "Nossa"
            df_nossa = df_desp[df_desp["pagamento_compartilhado"].str.contains("Nossa", na=False)]
            
            if not df_nossa.empty:
                hoje = date.today()
                df_mes = df_nossa[df_nossa["createdAt"].dt.month == hoje.month]
                
                total_compartilhado = df_mes["total_value"].sum()
                
                st.markdown(f'<div class="info-box"><h3>💸 Total Compartilhado este Mês</h3><h2>{formatar_brl(total_compartilhado)}</h2><p>Cada uma: {formatar_brl(total_compartilhado/2)}</p></div>', unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Quem pagou mais
                su_pagou = df_mes[df_mes["buyer"] == "Susanna"]["total_value"].sum()
                pi_pagou = df_mes[df_mes["buyer"] == "Pietrah"]["total_value"].sum()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Susanna pagou")
                    st.metric("", formatar_brl(su_pagou))
                with col2:
                    st.markdown("#### Pietrah pagou")
                    st.metric("", formatar_brl(pi_pagou))
                
                st.markdown("---")
                
                # Gráfico de categorias compartilhadas
                gastos_cat = df_mes.groupby("label")["total_value"].sum().reset_index()
                
                if not gastos_cat.empty:
                    fig = px.pie(gastos_cat, names="label", values="total_value", hole=0.4)
                    fig.update_traces(textposition='outside', textinfo='percent')
                    fig.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10), height=220,
                                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                     font=dict(color='white', size=10), legend=dict(font=dict(size=10)))
                    st.plotly_chart(fig, use_container_width=True)
                
                # Lista de gastos
                with st.expander("📋 Ver todos os gastos compartilhados"):
                    df_show = df_mes[["createdAt", "buyer", "label", "item", "total_value"]].copy()
                    df_show["createdAt"] = df_show["createdAt"].dt.strftime("%d/%m")
                    df_show.columns = ["Data", "Quem pagou", "Categoria", "Item", "Valor"]
                    st.dataframe(df_show, use_container_width=True)
            else:
                st.info("📝 Nenhum gasto compartilhado encontrado.")
        else:
            st.info("📝 Nenhum gasto registrado ainda.")
    
    # ========== PÁGINA RELATÓRIO ==========
    elif menu == "📊 Relatório":
        st.markdown('<p class="page-title">📊 Relatório Mensal</p>', unsafe_allow_html=True)
        
        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        
        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            df_desp["mes_ano"] = df_desp["createdAt"].dt.to_period("M")
            
            meses = sorted(df_desp["mes_ano"].unique(), reverse=True)
            mes_selecionado = st.selectbox("📅 Selecione o mês", meses, format_func=lambda x: x.strftime("%B %Y"))
            
            df_mes = df_desp[df_desp["mes_ano"] == mes_selecionado]
            
            st.markdown("---")
            
            # Resumo geral
            total_mes = df_mes["total_value"].sum()
            st.markdown(f'<div class="info-box"><h3>💰 Total do Mês</h3><h2>{formatar_brl(total_mes)}</h2></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                su_total = df_mes[df_mes["buyer"] == "Susanna"]["total_value"].sum()
                st.markdown(f'''<div class="susanna-card">
                    <h4>Susanna</h4>
                    <h2>{formatar_brl(su_total)}</h2>
                </div>''', unsafe_allow_html=True)
                
                # Top categorias
                su_cat = df_mes[df_mes["buyer"] == "Susanna"].groupby("label")["total_value"].sum().sort_values(ascending=False).head(3)
                st.markdown('<p class="susanna-header"><strong>Top 3 categorias:</strong></p>', unsafe_allow_html=True)
                for cat, val in su_cat.items():
                    st.caption(f"🔸 {cat}: {formatar_brl(val)}")
            
            with col2:
                pi_total = df_mes[df_mes["buyer"] == "Pietrah"]["total_value"].sum()
                st.markdown(f'''<div class="pietrah-card">
                    <h4>Pietrah</h4>
                    <h2>{formatar_brl(pi_total)}</h2>
                </div>''', unsafe_allow_html=True)
                
                pi_cat = df_mes[df_mes["buyer"] == "Pietrah"].groupby("label")["total_value"].sum().sort_values(ascending=False).head(3)
                st.markdown('<p class="pietrah-header"><strong>Top 3 categorias:</strong></p>', unsafe_allow_html=True)
                for cat, val in pi_cat.items():
                    st.caption(f"🔹 {cat}: {formatar_brl(val)}")
            
            st.markdown("---")
            
            # Gráfico comparativo
            comparativo = df_mes.groupby(["buyer", "label"])["total_value"].sum().reset_index()
            
            if not comparativo.empty:
                fig = px.bar(comparativo, x="label", y="total_value", color="buyer",
                            barmode="group",
                            color_discrete_map={"Susanna": "#e91e63", "Pietrah": "#0288d1"})
                fig.update_layout(xaxis_title="", yaxis_title="", legend_title="", height=220,
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                 font=dict(color='white', size=10), margin=dict(t=10, b=10, l=10, r=10))
                fig.update_xaxes(gridcolor='#333', tickfont=dict(size=9))
                fig.update_yaxes(gridcolor='#333')
                st.plotly_chart(fig, use_container_width=True)
            
            # Formas de pagamento
            st.markdown('<p class="section-title">💳 Por Forma de Pagamento</p>', unsafe_allow_html=True)
            pgto = df_mes.groupby("payment_method")["total_value"].sum().reset_index()
            
            fig = px.pie(pgto, names="payment_method", values="total_value", hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent')
            fig.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10), height=200,
                             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                             font=dict(color='white', size=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📝 Nenhum gasto registrado ainda.")
    
    # ========== PÁGINA EVOLUÇÃO ==========
    elif menu == "📈 Evolução":
        st.markdown('<p class="page-title">📈 Evolução dos Gastos</p>', unsafe_allow_html=True)
        
        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        
        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            df_desp["mes"] = df_desp["createdAt"].dt.to_period("M").astype(str)
            
            # Evolução mensal total
            evolucao = df_desp.groupby("mes")["total_value"].sum().reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=evolucao["mes"], y=evolucao["total_value"],
                                    mode='lines+markers', name='Total',
                                    line=dict(color='#9c27b0', width=2),
                                    marker=dict(size=6, color='#ba68c8')))
            fig.update_layout(title="", xaxis_title="", yaxis_title="", height=200,
                             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                             font=dict(color='white', size=10), margin=dict(t=10, b=10, l=10, r=10))
            fig.update_xaxes(gridcolor='#333')
            fig.update_yaxes(gridcolor='#333')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Evolução por pessoa
            st.markdown('<p class="section-title">Por Pessoa</p>', unsafe_allow_html=True)
            evolucao_pessoa = df_desp.groupby(["mes", "buyer"])["total_value"].sum().reset_index()
            
            fig2 = px.line(evolucao_pessoa, x="mes", y="total_value", color="buyer",
                          markers=True,
                          color_discrete_map={"Susanna": "#e91e63", "Pietrah": "#0288d1"})
            fig2.update_layout(xaxis_title="", yaxis_title="", legend_title="", height=200,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(color='white', size=10), margin=dict(t=10, b=10, l=10, r=10))
            fig2.update_xaxes(gridcolor='#333')
            fig2.update_yaxes(gridcolor='#333')
            st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown("---")
            
            # Evolução por categoria (top 5)
            st.markdown('<p class="section-title">Top 5 Categorias</p>', unsafe_allow_html=True)
            top_cats = df_desp.groupby("label")["total_value"].sum().nlargest(5).index.tolist()
            df_top = df_desp[df_desp["label"].isin(top_cats)]
            evolucao_cat = df_top.groupby(["mes", "label"])["total_value"].sum().reset_index()
            
            fig3 = px.area(evolucao_cat, x="mes", y="total_value", color="label")
            fig3.update_layout(xaxis_title="", yaxis_title="", legend_title="", height=200,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(color='white', size=10), margin=dict(t=10, b=10, l=10, r=10))
            fig3.update_xaxes(gridcolor='#333')
            fig3.update_yaxes(gridcolor='#333')
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("📝 Nenhum gasto registrado ainda.")


if __name__ == "__main__":
    main()