import streamlit as st
import pandas as pd

def seletor_peso(label, key=None):
    padrao = {
        "Orçamento": 1, "Caixa": 1, "Capacidade Produtiva": 1,
        "Receita": 1, "Custo": 1, "Produção": 1, "NPS": 1
    }
    return st.selectbox(
        label,
        options=[("1", 1), ("2", 2), ("3", 3), ("4", 4), ("5", 5)],
        index=padrao[label] - 1,
        format_func=lambda x: x[0],
        key=key
    )[1]

def sidebar_filtros(df):
    df["competencia"] = df["competencia"].astype(str)
    df["ano"] = df["competencia"].str[:4]
    df["mes"] = df["competencia"].str[5:7].astype(int)
    df["semestre"] = df["mes"].apply(lambda m: "1" if m <= 6 else "2")
    df["ano_semestre"] = df["semestre"] + "-" + df["ano"]

    with st.sidebar:
        st.markdown("### Filtros")

        col1, col2 = st.columns(2)
        with col1:
            empresa_sel = st.radio("Empresa", ["SEST", "SENAT"], index=0)
        with col2:
            agrupamento_opcao = st.radio("Agrupar por", ["Mês", "Semestre", "Ano"], index=1)

        filtro_col = {
            "Mês": "competencia",
            "Semestre": "ano_semestre",
            "Ano": "ano"
        }[agrupamento_opcao]

        df_empresa = df[df["empresa"] == empresa_sel].copy()

        opcoes = sorted(df_empresa[filtro_col].dropna().unique())
        valor_padrao = {
            "competencia": "2024-01",
            "ano_semestre": "1-2024",
            "ano": "2024"
        }.get(filtro_col, opcoes[0])

        with st.popover("📅 Período"):
            idx = opcoes.index(valor_padrao) if valor_padrao in opcoes else len(opcoes) - 1
            competencia_sel = st.selectbox("Período:", opcoes, index=idx)

        with st.popover("🎛️ Filtros Avançados"):
            conselho_sel = st.selectbox(
                "Filtrar por conselho (opcional):",
                ["Todos"] + sorted(df_empresa["conselho"].dropna().unique())
            )

            unidade_sel = st.selectbox(
                "Filtrar por unidade (opcional):",
                ["Todas"] + sorted(df_empresa["unidade"].dropna().unique()),
                index=1
            )

            tipologia_sel = st.selectbox(
                "Filtrar por tipologia (opcional):",
                ["Todas"] + sorted(df_empresa["tipologia"].dropna().unique())
            )

        with st.popover("🔧 Ajustar Pesos dos Eixos"):
            colunas_numericas = [
                "nota_orcamento", "nota_caixa", "nota_capacidade_produtiva",
                "nota_receita", "nota_custo", "nota_producao", "nota_nps"
            ]
            nome_map = {
                "nota_orcamento": "Orçamento",
                "nota_caixa": "Caixa",
                "nota_capacidade_produtiva": "Capacidade Produtiva",
                "nota_receita": "Receita",
                "nota_custo": "Custo",
                "nota_producao": "Produção",
                "nota_nps": 'NPS'
            }

            st.markdown("##### Pesos Eixo X (Operação)")
            colunas_x = st.multiselect(
                "Variáveis do Eixo X",
                options=colunas_numericas,
                default=["nota_custo", "nota_caixa", "nota_producao"],
                format_func=lambda x: nome_map[x],
                max_selections=4
            )
            pesos_x = [seletor_peso(nome_map[col], key=f"peso_x_{col}") for col in colunas_x]

            st.markdown("##### Pesos Eixo Y (Estratégia)")
            colunas_y = st.multiselect(
                "Variáveis do Eixo Y",
                options=colunas_numericas,
                default=["nota_orcamento", "nota_receita", "nota_nps"],
                format_func=lambda x: nome_map[x],
                max_selections=4
            )
            pesos_y = [seletor_peso(nome_map[col], key=f"peso_y_{col}") for col in colunas_y]

    # Conversão de métricas para numérico
    col_metricas = [
        "nota_producao", "nota_custo", "nota_receita",
        "nota_orcamento", "nota_caixa", "nota_capacidade_produtiva", "nota_nps"
    ]
    df_empresa[col_metricas] = df_empresa[col_metricas].apply(pd.to_numeric, errors="coerce")

    # Conversão de idade_unidade
    if "idade_unidade" in df_empresa.columns:
        df_empresa["idade_unidade"] = pd.to_numeric(df_empresa["idade_unidade"], errors="coerce")

    # Filtro principal
    df_filtrado = df_empresa[df_empresa[filtro_col] == str(competencia_sel)].copy()
    if conselho_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["conselho"] == conselho_sel]
    if tipologia_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["tipologia"] == tipologia_sel]

    # Agrupamento
    agrup_cols = ["empresa", "unidade", "conselho", "tipologia", filtro_col]
    df_filtro = (
        df_filtrado
        .groupby(agrup_cols, dropna=False, observed=False)
        .mean(numeric_only=True)
        .reset_index()
    )

    # 🔧 Remove idade_unidade antiga para evitar duplicação e faz o merge corretamente
    if "idade_unidade" in df_filtro.columns:
        df_filtro.drop(columns=["idade_unidade"], inplace=True)

    if "idade_unidade" in df_empresa.columns:
        df_filtro = df_filtro.merge(
            df_empresa[["unidade", "idade_unidade"]].drop_duplicates(subset=["unidade"]),
            on="unidade",
            how="left"
        )

    # Preencher valores faltantes nas colunas numéricas
    df_filtro.select_dtypes(include=['number']).fillna(0, inplace=True)

    return (
        df_filtro,
        empresa_sel,
        str(competencia_sel),
        agrupamento_opcao,
        conselho_sel,
        unidade_sel,
        tipologia_sel,
        colunas_x,
        pesos_x,
        colunas_y,
        pesos_y,
        filtro_col
    )
