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
    df["trimestre_mes"] = df["mes"].apply(lambda m: "1" if m <= 3 else "2" if m <= 6 else "3" if m <= 9 else "4")
    df["trimestre"] = df["ano"].astype(str) + "-" + df["trimestre_mes"].astype(str)
    df["ano_semestre"] = df["ano"] + "-" + df["semestre"]

    with st.sidebar:
        st.markdown("### Filtros")

        col1, col2 = st.columns(2)
        with col1:
            empresa_sel = st.radio("Empresa", ["SEST", "SENAT"], index=0)
        with col2:
            agrupamento_opcao = st.radio("Agrupar por", ["Mês", "Trimestre", "Semestre", "Ano"], index=3)

        filtro_col = {
            "Mês": "competencia",
            "Semestre": "ano_semestre",
            "Ano": "ano",
            "Trimestre": "trimestre"
        }[agrupamento_opcao]

        sufixo_map = {
            "Mês": "_mensal",
            "Trimestre": "_trimestral",
            "Semestre": "_semestral",
            "Ano": "_anual"
        }
        sufixo = sufixo_map[agrupamento_opcao]

        df_empresa = df[df["empresa"] == empresa_sel].copy()

        opcoes = sorted(df_empresa[filtro_col].dropna().unique())
        valor_padrao = {
            "competencia": "2024-01",
            "ano_semestre": "2024-1",
            "ano": "2024",
            "trimestre": "2024-1"
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
                index=0
            )

            tipologia_sel = st.selectbox(
                "Filtrar por tipologia (opcional):",
                ["Todas"] + sorted(df_empresa["tipologia"].dropna().unique())
            )

        with st.popover("🔧 Ajustar Pesos dos Eixos"):
            colunas_base = [
                "nota_orcamento", "nota_caixa", "nota_capacidade_produtiva",
                "nota_receita", "nota_custo", "nota_producao", "nota_nps"
            ]
            
            # Mapeamento com variações por período
            base_labels = {
                "nota_orcamento": "Orçamento",
                "nota_caixa": "Caixa",
                "nota_capacidade_produtiva": "Capacidade Produtiva",
                "nota_receita": "Receita",
                "nota_custo": "Custo",
                "nota_producao": "Produção",
                "nota_nps": "NPS"
            }

            nome_map = {}
            for base, label in base_labels.items():
                for sufixo in ["", "_mensal", "_trimestral", "_semestral", "_anual"]:
                    nome_map[f"{base}{sufixo}"] = label
                    if sufixo != "":
                        nome_map[f"{base}{sufixo}_padronizada"] = label

                        
            

            st.markdown("##### Pesos Eixo X (Operação)")
            colunas_x_base = st.multiselect(
                "Variáveis do Eixo X",
                options=colunas_base,
                default=["nota_orcamento", "nota_caixa", "nota_nps"],
                format_func=lambda x: nome_map[x],
                max_selections=4
            )
            pesos_x = [seletor_peso(nome_map[col], key=f"peso_x_{col}") for col in colunas_x_base]
            colunas_x = [col + sufixo for col in colunas_x_base]

            st.markdown("##### Pesos Eixo Y (Estratégia)")
            colunas_y_base = st.multiselect(
                "Variáveis do Eixo Y",
                options=colunas_base,
                default=["nota_receita", "nota_custo", "nota_producao"],
                format_func=lambda x: nome_map[x],
                max_selections=4
            )
            pesos_y = [seletor_peso(nome_map[col], key=f"peso_y_{col}") for col in colunas_y_base]
            colunas_y = [col + sufixo for col in colunas_y_base]

    # Conversão para numérico
    df_empresa[colunas_x + colunas_y] = df_empresa[colunas_x + colunas_y].apply(pd.to_numeric, errors="coerce")

    # Conversão de idade_unidade
    if "idade_unidade" in df_empresa.columns:
        df_empresa["idade_unidade"] = pd.to_numeric(df_empresa["idade_unidade"], errors="coerce")

    # Filtro principal
    df_filtrado = df_empresa[df_empresa[filtro_col] == str(competencia_sel)].copy()
    if conselho_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["conselho"] == conselho_sel]
    if tipologia_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["tipologia"] == tipologia_sel]
    if unidade_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["unidade"] == unidade_sel]
        

    return (
        df_filtrado,
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
        filtro_col,
        df_empresa,
        nome_map
    )

def aplicar_sufixos_colunas(colunas, filtro_col):
    sufixo_map = {
        "competencia": "_mensal_padronizada",
        "ano_semestre": "_semestral_padronizada",
        "trimestre": "_trimestral_padronizada",
        "ano": "_anual_padronizada"
    }
    sufixo = sufixo_map.get(filtro_col, "")

    colunas_com_sufixo = []
    for col in colunas:
        # Ignora se já termina com o sufixo correto
        if col.endswith(sufixo):
            colunas_com_sufixo.append(col)
        # Remove outros sufixos antes de aplicar o correto
        else:
            col_base = (
                col.replace("_mensal", "")
                   .replace("_trimestral", "")
                   .replace("_semestral", "")
                   .replace("_anual", "")
                   .replace("_padronizada", "")
            )
            colunas_com_sufixo.append(col_base + sufixo)

    return colunas_com_sufixo
