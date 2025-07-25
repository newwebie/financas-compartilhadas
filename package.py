import streamlit as st
from pymongo import MongoClient
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import certifi


def main():

    # Lendo os secrets
    URI = st.secrets["uri"]

    # Inicializa o cliente MongoDB com TLS
    client = MongoClient(
        URI,
        tls=True,
        tlsCAFile=certifi.where(),
        tlsAllowInvalidCertificates=False,
        serverSelectionTimeoutMS=30000
    )

    # Verificar conexão e definir a collection
    despesas_collection = None

    try:
        client.admin.command('ping')  # Testa a conexão
        # Nome do banco e da coleção podem vir separados ou ser extraídos da URI, se preferir
        db_name = "cluster0.xrpyf.mongodb.net"
        coll_name = "despesas"
        
        db = client[db_name]
        despesas_collection = db[coll_name]

    except Exception as e:
        st.error(f"Erro de conexão com o MongoDB: {e}")
        st.stop()

    st.title("📊 Painel Financeiro")
    tabs = st.tabs([ "Novo gasto", "Pietrah", "Susanna"])


        #REGISTRAR NOVO GASTO
    with tabs[0]:
        with st.form("form_novo_gasto", clear_on_submit=True):

            # --- Campos principais ---


            compradora  = st.selectbox("User", ["Susanna", "Pietrah"])
            
            label = st.selectbox("Selecione uma categoria", [
                "Automovéis", "Bebidas", "Boa pra família", "Combustível", "Comida", "Contas",
                "Lazer", "Mercado", "Outros", "Vestuario", "Saúde", "Cofrinho"
            ])
            item        = st.text_input("Item:")
            description = st.text_input("Descrição:")
            quantidade  = st.number_input("Quantidade", min_value=1, value=1, step=1)
            preco       = st.number_input("Preço Unitário:", min_value=1.00, max_value=5000.00,
                                        value=1.00, step=0.01, format="%.2f")

            valor_total = preco * quantidade

            pagamento = st.selectbox("Forma de Pagamento", ["VR", "Débito", "Crédito"])
            anexo     = st.text_input("Link de anexo:")

            # --- Divisão de pagamento ---
            st.markdown("### Informações adicionais")
            pagamento_compartilhado = st.selectbox("Tipo de Despesa", [
                "Compra individual",
                "Nossa",
                "Cada uma pagou metade"
            ])

            # --- Parcelamento ---
            total_parcelas = st.number_input("Adicionar Parcelas", min_value=0, step=1)

            # botão do formulário
            submitted = st.form_submit_button("Salvar")

        if submitted:
            try:

                valor_total_original = float(preco * quantidade)

                # Ajusta o valor se cada uma pagou metade
                if pagamento_compartilhado == "Cada uma pagou metade":
                    valor_total = round(valor_total_original / 2, 2)  # valor individual
                else:
                    valor_total = valor_total_original

                # Função para gerar campos de pendência fixos
                def gerar_pendencia(buyer, pagamento_compartilhado):
                    if pagamento_compartilhado == "Cada uma pagou metade":
                        return {
                            "tem_pendencia": False,
                            "devedor": None,
                            "valor_pendente": None,
                            "status_pendencia": None
                        }
                    if pagamento_compartilhado == "Nossa":
                        devedor = "Pietrah" if buyer == "Susanna" else "Susanna"
                        return {
                            "tem_pendencia": True,
                            "devedor": devedor,
                            "valor_pendente": round(valor_total / 2, 2),
                            "status_pendencia": "em aberto"
                        }
                    return {
                        "tem_pendencia": False,
                        "devedor": None,
                        "valor_pendente": None,
                        "status_pendencia": None
                    }

                pendencia_info = gerar_pendencia(compradora, pagamento_compartilhado)

                # Documento principal
                documento = {
                    "label": label,
                    "buyer": compradora,
                    "item": item,
                    "description": description,
                    "quantity": quantidade,
                    "total_value": valor_total,
                    "payment_method": pagamento,
                    "attachment": anexo,
                    "installment": int(total_parcelas),
                    "createdAt": datetime.now(),
                    "pagamento_compartilhado": pagamento_compartilhado,

                    # Campos fixos de pendência para Power BI
                    "tem_pendencia": pendencia_info["tem_pendencia"],
                    "devedor": pendencia_info["devedor"],
                    "valor_pendente": pendencia_info["valor_pendente"],
                    "status_pendencia": pendencia_info["status_pendencia"]
                }

                # Inserir no MongoDB
                despesas_collection.insert_one(documento)

                if pagamento_compartilhado == "Cada uma pagou metade":
                    outra_pessoa = "Pietrah" if compradora == "Susanna" else "Susanna"

                    doc_outra = documento.copy()
                    doc_outra.pop("_id", None)  # Remove o _id para evitar duplicidade
                    doc_outra["buyer"] = outra_pessoa
                    doc_outra["registrado_por"] = compradora  # opcional

                    despesas_collection.insert_one(doc_outra)
                st.success("Gasto registrado com sucesso!")

            except Exception as e:
                st.error(f"Erro ao salvar os dados: {e}")
    
    # Despesas Pietrah
    with tabs[1]:

        # 1. Buscar dados da collection (uma única vez)
        df_all = pd.DataFrame(list(despesas_collection.find({})))

        if df_all.empty:
            st.warning("Nenhuma despesa encontrada.")
            st.stop()

        # Conversões
        df_all["_id"] = df_all["_id"].astype(str)
        if "createdAt" in df_all.columns:
            df_all["createdAt"] = pd.to_datetime(df_all["createdAt"])

        # -------------------------------
        # PREPARAÇÃO DE DATAS
        # -------------------------------
        data_min_df = df_all["createdAt"].min().date()
        data_max_df = df_all["createdAt"].max().date()

        hoje = date.today()
        primeiro_dia_mes = hoje.replace(day=1)
        proximo_mes = (primeiro_dia_mes.replace(day=28) + timedelta(days=4)).replace(day=1)
        ultimo_dia_mes = proximo_mes - timedelta(days=1)

        default_ini = max(primeiro_dia_mes, data_min_df)
        default_fim = min(ultimo_dia_mes, data_max_df)

        # -------------------------------
        # SESSION STATE (PREFIXO p_)
        # -------------------------------
        if "p_filtro_aplicado" not in st.session_state:
            st.session_state["p_filtro_aplicado"] = True
            st.session_state["p_data_inicio"]     = default_ini
            st.session_state["p_data_fim"]        = default_fim
            st.session_state["p_modo_periodo"]    = "mes_atual"  # 'mes_atual' | 'todo_periodo' | 'custom'

        # -------------------------------
        # TÍTULO DO FILTRO
        # -------------------------------
        st.markdown("<h3 style='text-align: center;'>📅 Filtrar por período</h3>", unsafe_allow_html=True)

        # -------------------------------
        # FORM DE DATAS (sem reload até aplicar)
        # -------------------------------
        with st.form("form_filtro_datas_pietrah", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                data_inicio_tmp = st.date_input(
                    "Data inicial",
                    value=st.session_state["p_data_inicio"],
                    min_value=data_min_df,
                    max_value=data_max_df,
                    format="DD/MM/YYYY",
                    key="p_data_inicio_input"
                )
            with col2:
                data_fim_tmp = st.date_input(
                    "Data final",
                    value=st.session_state["p_data_fim"],
                    min_value=data_min_df,
                    max_value=data_max_df,
                    format="DD/MM/YYYY",
                    key="p_data_fim_input"
                )

            aplicar = st.form_submit_button("Aplicar filtro")

        # Aplica quando clicar
        if aplicar:
            if data_inicio_tmp > data_fim_tmp:
                st.error("A data inicial não pode ser maior que a final.")
                st.stop()

            st.session_state["p_data_inicio"]  = data_inicio_tmp
            st.session_state["p_data_fim"]     = data_fim_tmp

            if data_inicio_tmp == default_ini and data_fim_tmp == default_fim:
                st.session_state["p_modo_periodo"] = "mes_atual"
            else:
                st.session_state["p_modo_periodo"] = "custom"

            st.session_state["p_filtro_aplicado"] = True

        # -------------------------------
        # BOTÕES EXTRAS
        # -------------------------------
        colb1, colb2 = st.columns([1,1])
        with colb1:
            if st.button("Mostrar todo o período", key="p_btn_todo_periodo"):
                st.session_state["p_data_inicio"]  = data_min_df
                st.session_state["p_data_fim"]     = data_max_df
                st.session_state["p_modo_periodo"] = "todo_periodo"
                st.session_state["p_filtro_aplicado"] = True

        with colb2:
            if st.button("Voltar ao mês atual", key="p_btn_mes_atual"):
                st.session_state["p_data_inicio"]  = default_ini
                st.session_state["p_data_fim"]     = default_fim
                st.session_state["p_modo_periodo"] = "mes_atual"
                st.session_state["p_filtro_aplicado"] = True

        # -------------------------------
        # APLICA O FILTRO NO DF
        # -------------------------------
        df = df_all.copy()
        if st.session_state["p_filtro_aplicado"]:
            di  = st.session_state["p_data_inicio"]
            dfm = st.session_state["p_data_fim"]

            df = df[(df["createdAt"].dt.date >= di) & (df["createdAt"].dt.date <= dfm)]



        st.markdown("---")

        # -------------------------------
        # MÉTRICAS PRINCIPAIS - PIETRAH
        # -------------------------------
        mask_pietrah = df["buyer"] == "Pietrah"

        total_gasto = df.loc[mask_pietrah, "total_value"].sum()

        em_aberto = df[
            (df["devedor"] == "Pietrah") &
            (df["status_pendencia"] == "em aberto")
        ]["valor_pendente"].sum()

        a_receber = df[
            (df["devedor"] == "Susanna") &
            (df["status_pendencia"] == "em aberto")
        ]["valor_pendente"].sum()


        st.markdown("<h1 style='text-align: center;'>Situação Financeira: Pietrah</h1>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("💳 Total Gasto", f"R$ {total_gasto:,.2f}")
        col2.metric("🔴 A Pagar", f"R$ {em_aberto:,.2f}")
        col3.metric("🟢 A Receber", f"R$ {a_receber:,.2f}")

        st.divider()

        # -------------------------------
        # GRÁFICO DE ROSCA POR CATEGORIA
        # -------------------------------
        gastos_por_categoria = (
            df.loc[mask_pietrah]
            .groupby("label")["total_value"]
            .sum()
            .reset_index()
            .sort_values(by="total_value", ascending=False)
        )

        total_geral = gastos_por_categoria["total_value"].sum()
        if total_geral == 0:
            st.info("Não há gastos no período selecionado.")
        else:
            gastos_por_categoria["percentual"] = gastos_por_categoria["total_value"] / total_geral
            gastos_por_categoria["percent_texto"] = gastos_por_categoria["percentual"].apply(lambda x: f"{x:.0%}")
            gastos_por_categoria["legenda_formatada"] = gastos_por_categoria.apply(
                lambda row: f"{row['label']} — R$ {row['total_value']:,.2f}", axis=1
            )

            fig = px.pie(
                gastos_por_categoria,
                names="label",
                values="total_value",
                hole=0.5
            )

            fig.update_traces(
                textinfo="label+value+percent",  # o que mostrar
                texttemplate="%{label}<br>R$ %{value:,.2f}<br>%{percent}",  # formatação
                textposition="outside",         # ← setinha aparece aqui
                pull=[0.03]*len(gastos_por_categoria),  # opcional: afasta levemente as fatias
                marker=dict(line=dict(color="#000000", width=0.5))  # opcional: borda sutil
            )

            fig.update_layout(
                title= "",
                title_x=0.5,
                showlegend=False,
                margin=dict(t=40, b=80, l=40, r=40),  # aumentei as margens inferior e laterais
            )


            st.plotly_chart(fig, use_container_width=True)

            st.write("Gasto por Categoria")

        st.divider()

        # -------------------------------
        # TABELA DETALHADA COM FILTRO E TOTAL
        # -------------------------------
        st.subheader("🧾 Detalhamento dos gastos de Pietrah")

        categorias_disponiveis = df.loc[mask_pietrah, "label"].dropna().unique().tolist()
        categorias_selecionadas = st.multiselect(
            "Filtrar por categoria",
            options=sorted(categorias_disponiveis),
            key="p_multiselect_categorias"
        )

        df_filtrado = df[
            mask_pietrah &
            (df["label"].isin(categorias_selecionadas))
        ][["createdAt", "label", "item", "description", "total_value"]]

        df_filtrado = df_filtrado.sort_values(by="createdAt", ascending=False)

        total_visivel = df_filtrado["total_value"].sum()

        linha_total = pd.DataFrame([{
            "createdAt": None,
            "label": "TOTAL",
            "item": "",
            "description": "",
            "total_value": total_visivel
        }])

        df_exibicao = pd.concat([df_filtrado, linha_total], ignore_index=True)

        with st.expander("🔽 Clique para ver os itens detalhados"):
            st.dataframe(df_exibicao, use_container_width=True)
        
        a_receber_df = df[
            (df["devedor"] == "Susanna") & 
            (df["status_pendencia"] == "em aberto")
        ]

        total_receber = a_receber_df["valor_pendente"].sum()

        # Se houver valores a receber, exibe o expander
        if not a_receber_df.empty:
            # Renomear colunas
            df_mostrar = a_receber_df.rename(columns={
                "item": "Item",
                "label": "Categoria",
                "description": "Descrição",
                "valor_pendente": "Valor Pendente"
            })[["Item", "Categoria", "Descrição", "Valor Pendente"]]

            # Formatando valores como moeda brasileira
            df_mostrar["Valor Pendente"] = df_mostrar["Valor Pendente"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            with st.expander(f"🟢 Valores a receber: R$ {total_receber:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")):
                st.dataframe(df_mostrar, use_container_width=True)




    # Despesas Susanna
    with tabs[2]:
        

        # 1. Buscar dados da collection
        dados = list(despesas_collection.find({}))
        df = pd.DataFrame(dados)

        if not df.empty:
            # Converter _id e datas
            df['_id'] = df['_id'].astype(str)
            if 'createdAt' in df.columns:
                df['createdAt'] = pd.to_datetime(df['createdAt'])
            


            # PREPARAÇÃO
            # -------------------------------
            data_min_df = df["createdAt"].min().date()
            data_max_df = df["createdAt"].max().date()

            hoje = date.today()
            primeiro_dia_mes = hoje.replace(day=1)
            proximo_mes = (primeiro_dia_mes.replace(day=28) + timedelta(days=4)).replace(day=1)
            ultimo_dia_mes = proximo_mes - timedelta(days=1)

            default_ini = max(primeiro_dia_mes, data_min_df)
            default_fim = min(ultimo_dia_mes, data_max_df)

            # -------------------------------
            # SESSION STATE
            # -------------------------------
            if "filtro_aplicado" not in st.session_state:
                st.session_state["filtro_aplicado"]   = True          # já filtra no mês atual
                st.session_state["data_inicio"]       = default_ini
                st.session_state["data_fim"]          = default_fim
                st.session_state["modo_periodo"]      = "mes_atual"   # 'mes_atual' | 'todo_periodo' | 'custom'

            # -------------------------------
            # TÍTULO CENTRALIZADO
            # -------------------------------
            st.markdown("<h3 style='text-align: center;'>📅 Filtrar por período</h3>", unsafe_allow_html=True)

            # -------------------------------
            # FORM DE DATAS
            # -------------------------------
            with st.form("form_filtro_datas", clear_on_submit=False):
                col1, col2 = st.columns(2)
                with col1:
                    data_inicio_tmp = st.date_input(
                        "Data inicial",
                        value=st.session_state["data_inicio"],
                        min_value=data_min_df,
                        max_value=data_max_df,
                        format="DD/MM/YYYY"
                    )
                with col2:
                    data_fim_tmp = st.date_input(
                        "Data final",
                        value=st.session_state["data_fim"],
                        min_value=data_min_df,
                        max_value=data_max_df,
                        format="DD/MM/YYYY"
                    )

                aplicar = st.form_submit_button("Aplicar filtro")

            # Se clicou em aplicar, define se é custom ou mês atual
            if aplicar:
                if data_inicio_tmp > data_fim_tmp:
                    st.error("A data inicial não pode ser maior que a final.")
                    st.stop()

                st.session_state["data_inicio"]  = data_inicio_tmp
                st.session_state["data_fim"]     = data_fim_tmp

                # Checa se o intervalo escolhido é exatamente o do mês atual
                if data_inicio_tmp == default_ini and data_fim_tmp == default_fim:
                    st.session_state["modo_periodo"] = "mes_atual"
                else:
                    st.session_state["modo_periodo"] = "custom"

                st.session_state["filtro_aplicado"] = True

            # -------------------------------
            # BOTÕES EXTRAS
            # -------------------------------
            colb1, colb2 = st.columns([1,1])
            with colb1:
                if st.button("Mostrar todo o período"):
                    st.session_state["data_inicio"]  = data_min_df
                    st.session_state["data_fim"]     = data_max_df
                    st.session_state["modo_periodo"] = "todo_periodo"
                    st.session_state["filtro_aplicado"] = True

            with colb2:
                if st.button("Voltar ao mês atual"):
                    st.session_state["data_inicio"]  = default_ini
                    st.session_state["data_fim"]     = default_fim
                    st.session_state["modo_periodo"] = "mes_atual"
                    st.session_state["filtro_aplicado"] = True

            # -------------------------------
            # APLICA O FILTRO E MOSTRA MENSAGEM SE PRECISAR
            # -------------------------------
            if st.session_state["filtro_aplicado"]:
                di = st.session_state["data_inicio"]
                dfm = st.session_state["data_fim"]

                df = df[(df["createdAt"].dt.date >= di) & (df["createdAt"].dt.date <= dfm)]



            st.markdown("---")

            st.markdown("<h1 style='text-align: center;'>Situação Financeira: Susanna</h1>", unsafe_allow_html=True)

            # --- Totais principais ---

            # Total gasto por Susanna
            total_gasto = df[df["buyer"] == "Susanna"]["total_value"].sum()

            # Valor que Susanna ainda deve (em aberto, onde ela é a devedora)
            em_aberto = df[
                (df["devedor"] == "Susanna") & (df["status_pendencia"] == "em aberto")
            ]["valor_pendente"].sum()

            # Valor que Susanna tem a receber (em aberto, onde Pietrah é a devedora)
            a_receber = df[
                (df["devedor"] == "Pietrah") & (df["status_pendencia"] == "em aberto")
            ]["valor_pendente"].sum()

            

            # --- Mostrar resumo numérico ---
            col1, col2, col3 = st.columns(3)
            col1.metric("💳 Total Gasto", f"R$ {total_gasto:,.2f}")
            col2.metric("🔴 A Pagar", f"R$ {em_aberto:,.2f}")
            col3.metric("🟢 A Receber", f"R$ {a_receber:,.2f}")

            st.divider()
            
            # Agrupar e preparar dados
            gastos_por_categoria = (
                df[df["buyer"] == "Susanna"]
                .groupby("label")["total_value"]
                .sum()
                .reset_index()
                .sort_values(by="total_value", ascending=False)
            )

            # Calcular percentual manualmente
            total_geral = gastos_por_categoria["total_value"].sum()
            gastos_por_categoria["percentual"] = gastos_por_categoria["total_value"] / total_geral

            # 🟡 Texto no centro do gráfico (percentual apenas, sem casas decimais)
            gastos_por_categoria["percent_texto"] = gastos_por_categoria["percentual"].apply(lambda x: f"{x:.0%}")

            # 🔵 Texto na legenda: categoria + valor formatado
            # --- 1. Percentual e valor formatado ---
            gastos_por_categoria["pct"] = (
                gastos_por_categoria["total_value"] / gastos_por_categoria["total_value"].sum()
            )

            def fmt_brl(v):
                return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            gastos_por_categoria["valor_fmt"] = gastos_por_categoria["total_value"].apply(fmt_brl)

            # Cria a string que vai aparecer NA LEGENDA
            gastos_por_categoria["legenda"] = gastos_por_categoria.apply(
                lambda r: f"{r['label']} — {r['valor_fmt']}",
                axis=1
            )

            # --- 2. Decide onde o texto vai (fora/dentro) se ainda quiser usar adaptação ---
            LIMIAR_FORA = 0.06
            text_positions = ["outside" if p < LIMIAR_FORA else "inside"
                            for p in gastos_por_categoria["pct"]]

            # Agora SEM R$ no gráfico, só label + %
            text_templates = [
                "%{label}<br>%{percent}" if pos == "outside" else "%{percent}"
                for pos in text_positions
            ]

            pull_vals = [0.04 if p < LIMIAR_FORA else 0 for p in gastos_por_categoria["pct"]]

            # --- 3. Monta o gráfico usando a coluna 'legenda' como names (gera a legenda bonitinha) ---
            fig = px.pie(
                gastos_por_categoria,
                names="legenda",              # <- legenda com label + R$
                values="total_value",
                hole=0.5
            )

            fig.update_traces(
                textinfo="none",              # controlaremos via texttemplate
                textposition=text_positions,
                texttemplate=text_templates,  # sem R$ aqui
                insidetextorientation="radial",
                pull=pull_vals,
                marker=dict(line=dict(color="white", width=1))
            )

            fig.update_layout(
                title="Distribuição de gastos por categoria",
                title_x=0.5,
                showlegend=True,              # <- mostra legenda
                legend_title_text="",         # legenda sem título
                legend=dict(
                    orientation="v",
                    yanchor="middle", y=0.5,
                    xanchor="left",  x=1.02,  # joga a legenda pra direita do gráfico
                    font=dict(size=12)
                ),
                uniformtext_minsize=11,
                uniformtext_mode="hide",
                margin=dict(t=60, b=40, l=40, r=180),  # mais espaço à direita p/ legenda
                font=dict(size=13)
            )

            st.plotly_chart(fig, use_container_width=True)

            st.divider()

            # --- Tabela de itens gastos por Susanna com filtro por categoria ---
            st.subheader("🧾 Detalhamento dos gastos de Susanna")

            # Filtro por categoria
            categorias_disponiveis = df[df["buyer"] == "Susanna"]["label"].dropna().unique().tolist()
            categorias_selecionadas = st.multiselect(
                "Filtrar por categoria",
                options=sorted(categorias_disponiveis),
                default=sorted(categorias_disponiveis)
            )

            # Filtrar dados com base na seleção
            df_filtrado = df[
                (df["buyer"] == "Susanna") & 
                (df["label"].isin(categorias_selecionadas))
            ][["createdAt", "label", "item", "description", "total_value"]]

            df_filtrado = df_filtrado.sort_values(by="createdAt", ascending=False)

            # Calcular total visível
            total_visivel = df_filtrado["total_value"].sum()

            # Adicionar linha de total ao final
            linha_total = pd.DataFrame([{
                "createdAt": None,
                "label": "TOTAL",
                "item": "",
                "description": "",
                "total_value": total_visivel
            }])
            df_exibicao = pd.concat([df_filtrado, linha_total], ignore_index=True)

            # Expandir ou recolher
            with st.expander("🔽 Clique para ver os itens detalhados"):
                st.dataframe(df_exibicao, use_container_width=True)

        else:
            st.warning("Nenhuma despesa encontrada.")














if __name__ == "__main__":
    main()
