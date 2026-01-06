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
    .stCaption { font-size: 9px !important; }
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
        st.error(f"❌ Conexão falhou: {e}")
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


def main():
    client = connect_mongodb()
    if not client:
        st.stop()
    
    colls = get_collections(client)
    
    with st.sidebar:
        st.markdown("### 💰 Menu")
        menu = st.radio("", ["🏠 Início", "➕ Gasto", "🤝 Acerto", "💸 Empréstimo", "🎯 Metas", "👯 Juntas", "📊 Relatório", "📈 Evolução"], label_visibility="collapsed")
    
    # ========== INÍCIO ==========
    if menu == "🏠 Início":
        st.markdown('<p class="page-title">💰 Resumo do Mês</p>', unsafe_allow_html=True)
        
        df = pd.DataFrame(list(colls["despesas"].find({})))
        df_emp = pd.DataFrame(list(colls["emprestimos"].find({})))
        
        if not df.empty:
            df["createdAt"] = pd.to_datetime(df["createdAt"])
            hoje = date.today()
            mes_atual = df[df["createdAt"].dt.month == hoje.month]
            
            # Gastos do mês
            st.markdown('<p class="section-title">💸 Gastos este mês</p>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                total_su = mes_atual[mes_atual["buyer"] == "Susanna"]["total_value"].sum()
                st.markdown(f'<div class="su-card"><h4>Susanna</h4><h2>{fmt(total_su)}</h2></div>', unsafe_allow_html=True)
            with c2:
                total_pi = mes_atual[mes_atual["buyer"] == "Pietrah"]["total_value"].sum()
                st.markdown(f'<div class="pi-card"><h4>Pietrah</h4><h2>{fmt(total_pi)}</h2></div>', unsafe_allow_html=True)
            
            # Gráficos por categoria
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
            
            # Pendências
            su_deve = df[(df["devedor"] == "Susanna") & (df["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            pi_deve = df[(df["devedor"] == "Pietrah") & (df["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            
            if not df_emp.empty:
                df_emp["createdAt"] = pd.to_datetime(df_emp["createdAt"])
                su_deve += df_emp[(df_emp["devedor"] == "Susanna") & (df_emp["status"] == "em aberto")]["valor"].sum()
                pi_deve += df_emp[(df_emp["devedor"] == "Pietrah") & (df_emp["status"] == "em aberto")]["valor"].sum()
            
            saldo = pi_deve - su_deve
            
            # Saldo
            if abs(saldo) < 0.01:
                st.markdown('<div class="ok-box"><h3>✨ Quites!</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="section-title">💫 Pendências</p>', unsafe_allow_html=True)
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
        else:
            st.info("📝 Sem gastos ainda. Vá em '➕ Gasto'!")
    
    # ========== NOVO GASTO ==========
    elif menu == "➕ Gasto":
        st.markdown('<p class="page-title">➕ Novo Gasto</p>', unsafe_allow_html=True)
        
        with st.form("form_novo_gasto", clear_on_submit=True):
            compradora = st.selectbox("👤 Quem?", ["Susanna", "Pietrah"])
            label = st.selectbox("🏷️ Categoria", ["🍔 Comida", "🛒 Mercado", "⛽ Combustível", "🚗 Automóveis", "🍺 Bebidas", "👗 Vestuário", "💊 Saúde", "🎮 Lazer", "📄 Contas", "👨‍👩‍👧 Boa pra família", "🐷 Cofrinho", "📦 Outros"])
            item = st.text_input("📝 Item")
            description = st.text_input("💬 Descrição")
            
            c1, c2 = st.columns(2)
            with c1:
                quantidade = st.number_input("🔢 Qtd", min_value=1, value=1)
            with c2:
                preco = st.number_input("💵 Preço", min_value=0.01, value=1.00, format="%.2f")
            
            pagamento = st.selectbox("💳 Pagamento", ["VR", "Débito", "Crédito", "Pix", "Dinheiro"])
            tipo_despesa = st.selectbox("🤝 Tipo", ["👤 Individual", "👯 Nossa (divide)", "✂️ Metade cada"])
            parcelas = st.number_input("📅 Parcelas (0=à vista)", min_value=0, value=0)
            
            submitted = st.form_submit_button("✅ Salvar Gasto", use_container_width=True)
        
        if submitted:
            try:
                valor_total = quantidade * preco
                valor_final = valor_total
                if "Metade" in tipo_despesa:
                    valor_final = round(valor_total / 2, 2)
                
                pend = {"tem_pendencia": False, "devedor": None, "valor_pendente": None, "status_pendencia": None}
                if "Nossa" in tipo_despesa:
                    devedor = "Pietrah" if compradora == "Susanna" else "Susanna"
                    pend = {"tem_pendencia": True, "devedor": devedor, "valor_pendente": round(valor_final / 2, 2), "status_pendencia": "em aberto"}
                
                doc = {
                    "label": label, "buyer": compradora, "item": item, "description": description,
                    "quantity": quantidade, "total_value": valor_final, "payment_method": pagamento,
                    "installment": parcelas, "createdAt": datetime.now(), "pagamento_compartilhado": tipo_despesa, **pend
                }
                
                result = colls["despesas"].insert_one(doc)
                
                if "Nossa" in tipo_despesa:
                    colls["quitacoes"].insert_one({
                        "tipo": "despesa_compartilhada", "despesa_id": result.inserted_id, "data": datetime.now(),
                        "credor": compradora, "devedor": pend["devedor"], "valor": pend["valor_pendente"],
                        "descricao": f"{label} - {item}" if item else label, "observacao": description, "status": "em aberto"
                    })
                
                if "Metade" in tipo_despesa:
                    outra = "Pietrah" if compradora == "Susanna" else "Susanna"
                    doc2 = doc.copy()
                    doc2.pop("_id", None)
                    doc2["buyer"] = outra
                    doc2["registrado_por"] = compradora
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
                responsavel = st.selectbox("👤 Responsável", ["Susanna", "Pietrah", "Dividido"])
                categoria_conta = st.selectbox("🏷️ Categoria", ["Casa 🏠 ", "📶 Internet", "📱 Celular", "🎬 Streaming", "➕ Saúde", "📦 Outros"])
                obs_conta = st.text_input("💬 Observação")
                
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
        
        su_deve_desp, pi_deve_desp = 0, 0
        if not df_desp.empty:
            su_deve_desp = df_desp[(df_desp["devedor"] == "Susanna") & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
            pi_deve_desp = df_desp[(df_desp["devedor"] == "Pietrah") & (df_desp["status_pendencia"] == "em aberto")]["valor_pendente"].sum()
        
        su_deve_emp, pi_deve_emp = 0, 0
        if not df_emp.empty:
            su_deve_emp = df_emp[(df_emp["devedor"] == "Susanna") & (df_emp["status"] == "em aberto")]["valor"].sum()
            pi_deve_emp = df_emp[(df_emp["devedor"] == "Pietrah") & (df_emp["status"] == "em aberto")]["valor"].sum()
        
        su_deve_total = su_deve_desp + su_deve_emp
        pi_deve_total = pi_deve_desp + pi_deve_emp
        saldo = pi_deve_total - su_deve_total
        
        # Quanto cada uma deve
        st.markdown('<p class="section-title">📋 Quanto cada uma deve</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="su-card"><h4>Susanna</h4><h2>{fmt(su_deve_total)}</h2></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="pi-card"><h4>Pietrah</h4><h2>{fmt(pi_deve_total)}</h2></div>', unsafe_allow_html=True)
        
        # Detalhamento rápido
        c1, c2 = st.columns(2)
        with c1:
            st.caption(f"Desp: {fmt(su_deve_desp)} · Emp: {fmt(su_deve_emp)}")
        with c2:
            st.caption(f"Desp: {fmt(pi_deve_desp)} · Emp: {fmt(pi_deve_emp)}")
        
        st.markdown("---")
        
        # Resultado
        st.markdown('<p class="section-title">💰 Resultado</p>', unsafe_allow_html=True)
        if abs(saldo) < 0.01:
            st.markdown('<div class="ok-box"><h3>✨ Vocês estão quites!</h3></div>', unsafe_allow_html=True)
        elif saldo > 0:
            st.markdown(f'<div class="pi-deve"><p>Pietrah paga {fmt(saldo)} p/ Susanna</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="su-deve"><p>Susanna paga {fmt(abs(saldo))} p/ Pietrah</p></div>', unsafe_allow_html=True)
        
        # Detalhes das pendências
        st.markdown("---")
        st.markdown('<p class="section-title">🔍 Detalhamento</p>', unsafe_allow_html=True)
        
        if not df_logs.empty and "tipo" in df_logs.columns and "status" in df_logs.columns:
            logs_abertos = df_logs[(df_logs["tipo"] == "despesa_compartilhada") & (df_logs["status"] == "em aberto")]
            if not logs_abertos.empty:
                with st.expander(f"🛒 Despesas ({len(logs_abertos)})", expanded=False):
                    for _, log in logs_abertos.iterrows():
                        data_str = log["data"].strftime("%d/%m") if pd.notna(log.get("data")) else ""
                        st.caption(f"• {log.get('descricao', '-')} · {fmt(log['valor'])} · {data_str}")
        
        if not df_emp.empty:
            emp_abertos = df_emp[df_emp["status"] == "em aberto"]
            if not emp_abertos.empty:
                with st.expander(f"💸 Empréstimos ({len(emp_abertos)})", expanded=False):
                    for _, emp in emp_abertos.iterrows():
                        data_str = emp["createdAt"].strftime("%d/%m") if pd.notna(emp.get("createdAt")) else ""
                        st.caption(f"• {emp['credor']}→{emp['devedor']} · {fmt(emp['valor'])} · {data_str}")
        
        # Quitar
        if abs(saldo) > 0.01:
            st.markdown("---")
            st.markdown('<p class="section-title">✅ Quitar</p>', unsafe_allow_html=True)
            
            with st.form("form_quitar"):
                valor_quitar = st.number_input("Valor", min_value=0.01, max_value=float(max(su_deve_total, pi_deve_total, 0.01)), value=float(abs(saldo)))
                obs_quitacao = st.text_input("Obs")
                
                if st.form_submit_button("✅ Quitar", use_container_width=True):
                    quitacao = {
                        "tipo": "quitacao", "data": datetime.now(), "valor": valor_quitar,
                        "de": "Pietrah" if saldo > 0 else "Susanna",
                        "para": "Susanna" if saldo > 0 else "Pietrah", "observacao": obs_quitacao
                    }
                    colls["quitacoes"].insert_one(quitacao)
                    
                    quem_paga = "Pietrah" if saldo > 0 else "Susanna"
                    colls["despesas"].update_many({"devedor": quem_paga, "status_pendencia": "em aberto"}, {"$set": {"status_pendencia": "quitado", "data_quitacao": datetime.now()}})
                    colls["emprestimos"].update_many({"devedor": quem_paga, "status": "em aberto"}, {"$set": {"status": "quitado", "data_quitacao": datetime.now()}})
                    colls["quitacoes"].update_many({"devedor": quem_paga, "status": "em aberto", "tipo": "despesa_compartilhada"}, {"$set": {"status": "quitado", "data_quitacao": datetime.now()}})
                    
                    st.success("✅ Quitado!")
                    st.balloons()
                    st.rerun()
        
        # Histórico
        if not df_logs.empty and "tipo" in df_logs.columns:
            quitacoes_historico = df_logs[df_logs["tipo"] == "quitacao"]
            if not quitacoes_historico.empty:
                st.markdown("---")
                with st.expander("📜 Histórico de quitações"):
                    quitacoes_historico["data"] = pd.to_datetime(quitacoes_historico["data"])
                    quitacoes_historico = quitacoes_historico.sort_values("data", ascending=False)
                    for _, row in quitacoes_historico.head(10).iterrows():
                        data_str = row["data"].strftime("%d/%m/%Y") if pd.notna(row.get("data")) else ""
                        st.caption(f"• {row.get('de', '?')}→{row.get('para', '?')} · {fmt(row['valor'])} · {data_str}")
    
    # ========== EMPRÉSTIMOS ==========
    elif menu == "💸 Empréstimo":
        st.markdown('<p class="page-title">💸 Empréstimos</p>', unsafe_allow_html=True)
        
        with st.expander("➕ Novo Empréstimo", expanded=False):
            with st.form("form_emprestimo", clear_on_submit=True):
                quem_emprestou = st.selectbox("💰 Quem emprestou?", ["Susanna", "Pietrah"])
                valor_emp = st.number_input("💵 Valor", min_value=0.01, value=10.00, format="%.2f")
                motivo = st.text_area("📝 Motivo / Observação", placeholder="Ex: Emprestei pra pagar o Uber")
                
                if st.form_submit_button("✅ Registrar", use_container_width=True):
                    devedor = "Pietrah" if quem_emprestou == "Susanna" else "Susanna"
                    colls["emprestimos"].insert_one({
                        "credor": quem_emprestou, "devedor": devedor, "valor": valor_emp,
                        "motivo": motivo, "status": "em aberto", "createdAt": datetime.now()
                    })
                    st.success("✅ Empréstimo registrado!")
                    st.rerun()
        
        df_emp = pd.DataFrame(list(colls["emprestimos"].find({})))
        
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
                        st.markdown(f"{status_emoji} **{row['credor']}** → **{row['devedor']}**: {fmt(row['valor'])}")
                        st.caption(f"📝 {row.get('motivo', 'Sem descrição')} · 🕐 {row['createdAt'].strftime('%d/%m/%Y %H:%M')}")
                        st.markdown("---")
        else:
            st.info("📝 Nenhum empréstimo registrado.")
    
    # ========== METAS ==========
    elif menu == "🎯 Metas":
        st.markdown('<p class="page-title">🎯 Metas e Orçamento</p>', unsafe_allow_html=True)
        
        usuario_metas = st.selectbox("👤 Ver metas de:", ["Susanna", "Pietrah", "Ambas"], key="sel_user_metas")
        
        st.markdown("---")
        
        with st.expander("➕ Criar Nova Meta", expanded=False):
            with st.form("form_meta", clear_on_submit=True):
                categoria_meta = st.selectbox("🏷️ Categoria", ["🍔 Comida", "🛒 Mercado", "⛽ Combustível", "🚗 Automóveis", "🍺 Bebidas", "👗 Vestuário", "💊 Saúde", "🎮 Lazer", "📄 Contas", "👨‍👩‍👧 Boa pra família", "📦 Outros", "💰 Total Geral"])
                pessoa_meta = st.selectbox("👤 Para quem?", ["Susanna", "Pietrah", "Ambas"])
                valor_meta = st.number_input("💵 Limite mensal", min_value=1.00, value=500.00, format="%.2f")
                
                if st.form_submit_button("✅ Criar Meta", use_container_width=True):
                    colls["metas"].insert_one({"categoria": categoria_meta, "pessoa": pessoa_meta, "limite": valor_meta, "ativo": True, "createdAt": datetime.now()})
                    st.success("✅ Meta criada!")
                    st.rerun()
        
        df_metas = pd.DataFrame(list(colls["metas"].find({"ativo": True})))
        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        
        if not df_metas.empty and not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            hoje = date.today()
            df_mes = df_desp[df_desp["createdAt"].dt.month == hoje.month]
            
            if usuario_metas != "Ambas":
                df_metas_filtrado = df_metas[(df_metas["pessoa"] == usuario_metas) | (df_metas["pessoa"] == "Ambas")]
            else:
                df_metas_filtrado = df_metas
            
            if df_metas_filtrado.empty:
                st.info(f"📝 Nenhuma meta para {usuario_metas}.")
            else:
                st.markdown(f'<p class="section-title">📊 Progresso - {usuario_metas}</p>', unsafe_allow_html=True)
                
                for _, meta in df_metas_filtrado.iterrows():
                    cat, pessoa, limite = meta["categoria"], meta["pessoa"], meta["limite"]
                    
                    if pessoa == "Ambas":
                        gasto = df_mes["total_value"].sum() if "Total" in cat else df_mes[df_mes["label"] == cat]["total_value"].sum()
                    else:
                        gasto = df_mes[df_mes["buyer"] == pessoa]["total_value"].sum() if "Total" in cat else df_mes[(df_mes["buyer"] == pessoa) & (df_mes["label"] == cat)]["total_value"].sum()
                    
                    pct = min((gasto / limite) * 100, 100) if limite > 0 else 0
                    restante = max(limite - gasto, 0)
                    
                    st.caption(f"**{cat}** • {pessoa}")
                    st.progress(pct / 100)
                    st.caption(f"💸 {fmt(gasto)} · 🎯 {fmt(limite)} · 💰 {fmt(restante)}")
                    
                    if pct >= 100:
                        st.warning("⚠️ Meta ultrapassada!")
                    elif pct >= 80:
                        st.info("⚡ Próximo do limite!")
                    st.markdown("---")
        else:
            st.info("📝 Crie metas para acompanhar!")
    
    # ========== GASTOS JUNTAS ==========
    elif menu == "👯 Juntas":
        st.markdown('<p class="page-title">👯 Gastos Compartilhados</p>', unsafe_allow_html=True)
        
        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        
        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            df_nossa = df_desp[df_desp["pagamento_compartilhado"].str.contains("Nossa", na=False)]
            
            if not df_nossa.empty:
                hoje = date.today()
                df_mes = df_nossa[df_nossa["createdAt"].dt.month == hoje.month]
                
                total_compartilhado = df_mes["total_value"].sum()
                
                # Total
                st.markdown('<p class="section-title">💸 Total este mês</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-box"><h2>{fmt(total_compartilhado)}</h2><p>Cada: {fmt(total_compartilhado/2)}</p></div>', unsafe_allow_html=True)
                
                # Quem pagou
                st.markdown('<p class="section-title">💳 Quem pagou</p>', unsafe_allow_html=True)
                su_pagou = df_mes[df_mes["buyer"] == "Susanna"]["total_value"].sum()
                pi_pagou = df_mes[df_mes["buyer"] == "Pietrah"]["total_value"].sum()
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<div class="su-card"><h4>Susanna</h4><h2>{fmt(su_pagou)}</h2></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="pi-card"><h4>Pietrah</h4><h2>{fmt(pi_pagou)}</h2></div>', unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Gráfico por categoria
                gastos_cat = df_mes.groupby("label")["total_value"].sum().reset_index()
                
                if not gastos_cat.empty:
                    st.markdown('<p class="section-title">📊 Onde mais dividimos</p>', unsafe_allow_html=True)
                    fig = px.pie(gastos_cat, names="label", values="total_value", hole=0.4)
                    fig.update_traces(textposition='inside', textinfo='percent')
                    fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=130,
                                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                     font=dict(color='white', size=8), legend=dict(font=dict(size=7), orientation="h", y=-0.1))
                    st.plotly_chart(fig, use_container_width=True)
                
                # Gráfico de quem pagou por categoria
                gastos_pessoa_cat = df_mes.groupby(["buyer", "label"])["total_value"].sum().reset_index()
                
                if not gastos_pessoa_cat.empty:
                    st.markdown('<p class="section-title">👤 Quem pagou o quê</p>', unsafe_allow_html=True)
                    fig2 = px.bar(gastos_pessoa_cat, x="label", y="total_value", color="buyer", barmode="group",
                                color_discrete_map={"Susanna": "#e91e63", "Pietrah": "#03a9f4"})
                    fig2.update_layout(xaxis_title="", yaxis_title="", legend_title="", height=120,
                                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                     font=dict(color='white', size=7), margin=dict(t=0, b=0, l=0, r=0),
                                     legend=dict(orientation="h", y=1.15, font=dict(size=7)))
                    fig2.update_xaxes(gridcolor='#333', tickfont=dict(size=6), tickangle=45)
                    fig2.update_yaxes(gridcolor='#333', showticklabels=False)
                    st.plotly_chart(fig2, use_container_width=True)
                
                with st.expander("📋 Ver todos"):
                    df_show = df_mes[["createdAt", "buyer", "label", "item", "total_value"]].copy()
                    df_show["createdAt"] = df_show["createdAt"].dt.strftime("%d/%m")
                    df_show.columns = ["Data", "Quem", "Cat", "Item", "Valor"]
                    st.dataframe(df_show, use_container_width=True, height=120)
            else:
                st.info("📝 Nenhum gasto compartilhado.")
        else:
            st.info("📝 Nenhum gasto registrado.")
    
    # ========== RELATÓRIO ==========
    elif menu == "📊 Relatório":
        st.markdown('<p class="page-title">📊 Relatório Mensal</p>', unsafe_allow_html=True)

        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        df_contas_fixas = pd.DataFrame(list(colls["contas_fixas"].find({"ativo": True})))

        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            df_desp["mes_ano"] = df_desp["createdAt"].dt.to_period("M")

            # Filtros
            c1, c2 = st.columns(2)
            with c1:
                meses = sorted(df_desp["mes_ano"].unique(), reverse=True)
                mes_selecionado = st.selectbox("📅 Mês", meses, format_func=lambda x: x.strftime("%B %Y"))
            with c2:
                pessoa_selecionada = st.selectbox("👤 Ver dados de:", ["Susanna", "Pietrah", "Ambas"], index=0)

            df_mes = df_desp[df_desp["mes_ano"] == mes_selecionado]

            # Calcula totais de contas fixas
            su_fixas, pi_fixas = 0, 0
            if not df_contas_fixas.empty:
                su_fixas = df_contas_fixas[df_contas_fixas["responsavel"] == "Susanna"]["valor"].sum()
                pi_fixas = df_contas_fixas[df_contas_fixas["responsavel"] == "Pietrah"]["valor"].sum()
                divididas = df_contas_fixas[df_contas_fixas["responsavel"] == "Dividido"]["valor"].sum()
                su_fixas += divididas / 2
                pi_fixas += divididas / 2

            # ============ AMBAS ============
            if pessoa_selecionada == "Ambas":
                # Total geral
                total_variavel_mes = df_mes["total_value"].sum()
                total_fixas_mes = su_fixas + pi_fixas
                total_geral = total_variavel_mes + total_fixas_mes

                st.markdown(f'<div class="info-box"><h2>{fmt(total_geral)}</h2><p>Total geral do mês</p></div>', unsafe_allow_html=True)

                st.markdown("---")

                # Por pessoa - Gastos Variáveis
                st.markdown('<p class="section-title">💸 Gastos Variáveis</p>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    su_var = df_mes[df_mes["buyer"] == "Susanna"]["total_value"].sum()
                    st.markdown(f'<div class="su-card"><h4>Susanna</h4><h2>{fmt(su_var)}</h2></div>', unsafe_allow_html=True)
                with c2:
                    pi_var = df_mes[df_mes["buyer"] == "Pietrah"]["total_value"].sum()
                    st.markdown(f'<div class="pi-card"><h4>Pietrah</h4><h2>{fmt(pi_var)}</h2></div>', unsafe_allow_html=True)

                # Contas Fixas
                if not df_contas_fixas.empty:
                    st.markdown("---")
                    st.markdown('<p class="section-title">📄 Contas Fixas</p>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f'<div class="su-card"><h4>Susanna</h4><h2>{fmt(su_fixas)}</h2></div>', unsafe_allow_html=True)
                    with c2:
                        st.markdown(f'<div class="pi-card"><h4>Pietrah</h4><h2>{fmt(pi_fixas)}</h2></div>', unsafe_allow_html=True)

                # Total por pessoa
                st.markdown("---")
                st.markdown('<p class="section-title">💰 Total (Variáveis + Fixas)</p>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<div class="su-card"><h4>Susanna</h4><h2>{fmt(su_var + su_fixas)}</h2></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="pi-card"><h4>Pietrah</h4><h2>{fmt(pi_var + pi_fixas)}</h2></div>', unsafe_allow_html=True)

            # ============ INDIVIDUAL ============
            else:
                pessoa = pessoa_selecionada
                df_pessoa = df_mes[df_mes["buyer"] == pessoa]

                # Totais da pessoa
                total_var = df_pessoa["total_value"].sum()
                total_fix = su_fixas if pessoa == "Susanna" else pi_fixas
                total_geral = total_var + total_fix

                cor_card = "su-card" if pessoa == "Susanna" else "pi-card"

                # Total geral
                st.markdown(f'<div class="{cor_card}"><h4>Total Geral</h4><h2>{fmt(total_geral)}</h2><small>variáveis + fixas</small></div>', unsafe_allow_html=True)

                st.markdown("---")

                # Breakdown
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<div class="{cor_card}"><h4>Gastos Variáveis</h4><h2>{fmt(total_var)}</h2></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="{cor_card}"><h4>Contas Fixas</h4><h2>{fmt(total_fix)}</h2></div>', unsafe_allow_html=True)

                st.markdown("---")

                # Top 3 categorias
                if not df_pessoa.empty:
                    st.markdown('<p class="section-title">🏆 Top 3 Categorias</p>', unsafe_allow_html=True)
                    top_cat = df_pessoa.groupby("label")["total_value"].sum().sort_values(ascending=False).head(3)
                    for i, (cat, val) in enumerate(top_cat.items(), 1):
                        st.caption(f"{i}. {cat}: {fmt(val)}")

                # Contas fixas detalhadas
                if not df_contas_fixas.empty:
                    contas_pessoa = df_contas_fixas[
                        (df_contas_fixas["responsavel"] == pessoa) |
                        (df_contas_fixas["responsavel"] == "Dividido")
                    ]

                    if not contas_pessoa.empty:
                        st.markdown("---")
                        with st.expander("📋 Contas Fixas Detalhadas", expanded=False):
                            for _, conta in contas_pessoa.iterrows():
                                emoji = "🔸" if pessoa == "Susanna" else "🔹"
                                if conta["responsavel"] == "Dividido":
                                    emoji = "🔷"
                                    st.caption(f"{emoji} **Dividido**")

                                valor_display = fmt(conta["valor"]) if conta["responsavel"] != "Dividido" else f"{fmt(conta['valor'])} ({fmt(conta['valor']/2)} cada)"
                                st.caption(f"**{conta['nome']}** · {conta['categoria']} · {valor_display} · Vence dia {int(conta['dia_vencimento'])}")
                                if conta.get("observacao"):
                                    st.caption(f"💬 {conta['observacao']}")
                                

            # Gráfico por categoria
            if pessoa_selecionada == "Ambas":
                comparativo = df_mes.groupby(["buyer", "label"])["total_value"].sum().reset_index()
                if not comparativo.empty:
                    st.markdown('<p class="section-title">📊 Comparativo por Categoria</p>', unsafe_allow_html=True)
                    fig = px.bar(comparativo, x="label", y="total_value", color="buyer", barmode="group",
                                color_discrete_map={"Susanna": "#e91e63", "Pietrah": "#03a9f4"})
                    fig.update_layout(xaxis_title="", yaxis_title="", legend_title="", height=140,
                                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                     font=dict(color='white', size=7), margin=dict(t=0, b=0, l=0, r=0),
                                     legend=dict(orientation="h", y=1.15, font=dict(size=7)))
                    fig.update_xaxes(gridcolor='#333', tickfont=dict(size=6), tickangle=45)
                    fig.update_yaxes(gridcolor='#333', showticklabels=False)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                df_pessoa = df_mes[df_mes["buyer"] == pessoa_selecionada]
                if not df_pessoa.empty:
                    cat_data = df_pessoa.groupby("label")["total_value"].sum().reset_index()
                    if not cat_data.empty:
                        st.markdown('<p class="section-title">📊 Gastos por Categoria</p>', unsafe_allow_html=True)
                        cores = ['#e91e63', '#f48fb1', '#f06292', '#ec407a'] if pessoa_selecionada == "Susanna" else ['#03a9f4', '#4fc3f7', '#29b6f6', '#0288d1']
                        fig = px.pie(cat_data, names="label", values="total_value", hole=0.4, color_discrete_sequence=cores)
                        fig.update_traces(textposition='inside', textinfo='percent')
                        fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=130,
                                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                         font=dict(color='white', size=8), legend=dict(font=dict(size=7), orientation="h", y=-0.1))
                        st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Por forma de pagamento
            st.markdown('<p class="section-title">💳 Por Forma de Pagamento</p>', unsafe_allow_html=True)
            if pessoa_selecionada == "Ambas":
                pgto = df_mes.groupby("payment_method")["total_value"].sum().reset_index()
            else:
                pgto = df_mes[df_mes["buyer"] == pessoa_selecionada].groupby("payment_method")["total_value"].sum().reset_index()

            if not pgto.empty:
                fig = px.pie(pgto, names="payment_method", values="total_value", hole=0.4)
                fig.update_traces(textposition='inside', textinfo='percent')
                fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=120,
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                 font=dict(color='white', size=8), legend=dict(font=dict(size=7), orientation="h", y=-0.1))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📝 Nenhum gasto registrado.")
    
    # ========== EVOLUÇÃO ==========
    elif menu == "📈 Evolução":
        st.markdown('<p class="page-title">📈 Evolução</p>', unsafe_allow_html=True)
        
        df_desp = pd.DataFrame(list(colls["despesas"].find({})))
        
        if not df_desp.empty:
            df_desp["createdAt"] = pd.to_datetime(df_desp["createdAt"])
            df_desp["mes"] = df_desp["createdAt"].dt.to_period("M").astype(str)
            
            # Total por mês
            st.markdown('<p class="section-title">💰 Total por mês</p>', unsafe_allow_html=True)
            evolucao = df_desp.groupby("mes")["total_value"].sum().reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=evolucao["mes"], y=evolucao["total_value"],
                                    mode='lines+markers', name='Total',
                                    line=dict(color='#9c27b0', width=2),
                                    marker=dict(size=5, color='#ba68c8')))
            fig.update_layout(height=120, margin=dict(t=0, b=0, l=0, r=0),
                             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                             font=dict(color='white', size=8))
            fig.update_xaxes(gridcolor='#333', tickfont=dict(size=7))
            fig.update_yaxes(gridcolor='#333', showticklabels=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Por pessoa
            st.markdown('<p class="section-title">👤 Por pessoa</p>', unsafe_allow_html=True)
            evolucao_pessoa = df_desp.groupby(["mes", "buyer"])["total_value"].sum().reset_index()
            
            fig2 = px.line(evolucao_pessoa, x="mes", y="total_value", color="buyer",
                          markers=True, color_discrete_map={"Susanna": "#e91e63", "Pietrah": "#03a9f4"})
            fig2.update_layout(height=120, margin=dict(t=0, b=0, l=0, r=0),
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(color='white', size=8), legend=dict(orientation="h", y=1.15, font=dict(size=7)), showlegend=True)
            fig2.update_xaxes(gridcolor='#333', tickfont=dict(size=7))
            fig2.update_yaxes(gridcolor='#333', showticklabels=False)
            st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown("---")
            
            # Top 5 categorias
            st.markdown('<p class="section-title">🏷️ Top 5 categorias</p>', unsafe_allow_html=True)
            top_cats = df_desp.groupby("label")["total_value"].sum().nlargest(5).index.tolist()
            df_top = df_desp[df_desp["label"].isin(top_cats)]
            evolucao_cat = df_top.groupby(["mes", "label"])["total_value"].sum().reset_index()
            
            fig3 = px.area(evolucao_cat, x="mes", y="total_value", color="label")
            fig3.update_layout(height=120, margin=dict(t=0, b=0, l=0, r=0),
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(color='white', size=8), legend=dict(orientation="h", y=1.2, font=dict(size=6)), showlegend=True)
            fig3.update_xaxes(gridcolor='#333', tickfont=dict(size=7))
            fig3.update_yaxes(gridcolor='#333', showticklabels=False)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("📝 Nenhum gasto registrado.")


if __name__ == "__main__":
    main()