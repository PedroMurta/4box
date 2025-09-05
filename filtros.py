import streamlit as st
import pandas as pd

# ==============================
# Constantes globais
# ==============================
PESO_OPTIONS = [(str(i), i) for i in range(1, 6)]
PESO_DEFAULT = {"Orçamento": 1, "Equilíbrio Financeiro": 1, "Capacidade Produtiva": 1, "Receita Operacional": 1, "Custo": 1, "Produção": 1, "NPS": 1}

SUFIXO_MAP = {
    "competencia": "_mensal_padronizada",
    "ano_semestre": "_semestral_padronizada",
    "trimestre": "_trimestral_padronizada",
    "ano": "_anual_padronizada",
}

BASE_LABELS = {
    "nota_orcamento": "Orçamento",
    "nota_caixa": "Equilíbrio Financeiro",
    "nota_nps": "NPS",
    "nota_receita_operacional": "Receita Operacional",
    "nota_custo": "Custo",
    "nota_producao": "Produção",    
    "nota_capacidade_produtiva": "Capacidade Produtiva",
}

FILTRO_COL_MAP = {"Mês": "competencia", "Semestre": "ano_semestre", "Ano": "ano", "Trimestre": "trimestre"}

VALORES_PADRAO = {"competencia": "2024-01", "ano_semestre": "2024-1", "ano": "2024", "trimestre": "2024-1"}

CONSELHO_PADRAO = "CRES"

# ==============================
# Utilitários
# ==============================
def criar_nome_map():
    nome_map = {}
    sufixos = ["", "_mensal", "_trimestral", "_semestral", "_anual"]
    for base, label in BASE_LABELS.items():
        for suf in sufixos:
            nome_map[f"{base}{suf}"] = label
            if suf:
                nome_map[f"{base}{suf}_padronizada"] = label
    return nome_map

@st.cache_data
def processar_dados_temporais(df):
    df = df.copy()
    df["competencia"] = df["competencia"].astype(str)
    df["ano"] = df["competencia"].str[:4]
    df["mes"] = df["competencia"].str[5:7].astype(int)
    df["semestre"] = (df["mes"] > 6).astype(int) + 1
    df["trimestre_mes"] = ((df["mes"] - 1) // 3 + 1).astype(str)
    df["trimestre"] = df["ano"] + "-" + df["trimestre_mes"]
    df["ano_semestre"] = df["ano"] + "-" + df["semestre"].astype(str)
    return df

def seletor_peso_otimizado(label, key=None):
    idx_default = max(PESO_DEFAULT.get(label, 1) - 1, 0)
    return st.selectbox(label, options=PESO_OPTIONS, index=idx_default,
                        format_func=lambda x: x[0], key=key)[1]

def aplicar_filtros_avancados(df_empresa, conselho_sel, tipologia_sel, unidade_sel):
    mask = pd.Series(True, index=df_empresa.index)
    if conselho_sel != "Todos":
        mask &= (df_empresa["conselho"] == conselho_sel)
    if tipologia_sel != "Todas":
        mask &= (df_empresa["tipologia"] == tipologia_sel)
    if unidade_sel != "Todas":
        mask &= (df_empresa["unidade"] == unidade_sel)
    return df_empresa[mask].copy()

# ==============================
# CSS — Popover responsivo
# ==============================
def css_popover_responsivo():
    st.markdown("""
    <style>
      /* quebra/empilhamento das colunas DENTRO do popover */
      [role="dialog"] [data-testid="stHorizontalBlock"]{
        flex-wrap: wrap !important; gap: .5rem !important;
      }
      @media (max-width: 768px){
        [role="dialog"] [data-testid="column"]{
          flex: 1 0 100% !important; width: 100% !important;
        }
        .stPopover > div{ min-width: 320px !important; } /* evita corte */
      }
      /* selects mais compactos dentro do popover */
      [role="dialog"] .stSelectbox{ margin-bottom:8px; }
      [role="dialog"] .stSelectbox > label{ font-size:13px; font-weight:600; margin-bottom:4px; }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# Dropdowns de peso em linha (responsivo)
# ==============================
def criar_dropdowns_peso_em_linha(colunas_selecionadas, prefixo_key, titulo, cols_por_linha=3):
    st.markdown(f"**{titulo}**")
    if not colunas_selecionadas:
        st.warning("Selecione pelo menos uma variável")
        return []

    pesos = {}
    for i in range(0, len(colunas_selecionadas), cols_por_linha):
        bloco = colunas_selecionadas[i:i+cols_por_linha]
        cols = st.columns(len(bloco), gap="small")
        for c, col_base in zip(cols, bloco):
            with c:
                label_visivel = BASE_LABELS.get(col_base, col_base)
                pesos[col_base] = seletor_peso_otimizado(label_visivel, key=f"{prefixo_key}_{col_base}")

    return [pesos[c] for c in colunas_selecionadas]

# ==============================
# Sidebar (com popover responsivo)
# ==============================
def sidebar_filtros(df):
    """Sidebar com popovers responsivos e dropdowns em linha."""
    df = processar_dados_temporais(df)
    nome_map = criar_nome_map()
    css_popover_responsivo()  # ativa responsividade do popover

    with st.sidebar:
        st.image('sestsenat_0.png', width=280)

        col1, col2 = st.columns(2)
        with col1:
            empresa_sel = st.radio("Empresa", ["SEST", "SENAT"], index=0)
        with col2:
            agrupamento_opcao = st.radio("Agrupar por", ["Mês", "Trimestre", "Semestre", "Ano"], index=3)

        filtro_col = FILTRO_COL_MAP[agrupamento_opcao]
        df_empresa = df[df["empresa"] == empresa_sel].copy()

        # Período
        opcoes = sorted(df_empresa[filtro_col].dropna().unique())
        valor_padrao = VALORES_PADRAO.get(filtro_col, opcoes[-1] if opcoes else None)
        with st.popover("📅 Período"):
            try:
                idx = opcoes.index(valor_padrao) if valor_padrao in opcoes else len(opcoes) - 1
            except (ValueError, IndexError):
                idx = 0
            competencia_sel = st.selectbox("Período:", opcoes, index=idx)

        # Filtros avançados
        with st.popover("🎛️ Filtros Avançados"):
            # Aplicar CRES como padrão para Conselho
            conselhos_disponiveis = ["Todos"] + sorted(df_empresa["conselho"].dropna().unique())
            # Verificar se CRES existe na lista, senão usar "Todos"
            if CONSELHO_PADRAO in conselhos_disponiveis:
                idx_conselho = conselhos_disponiveis.index(CONSELHO_PADRAO)
            else:
                idx_conselho = 0  # "Todos" como fallback
            
            conselho_sel = st.selectbox("Conselho:", conselhos_disponiveis, index=idx_conselho)
            unidade_sel = st.selectbox("Unidade:", ["Todas"] + sorted(df_empresa["unidade"].dropna().unique()))
            tipologia_sel = st.selectbox("Tipologia:", ["Todas"] + sorted(df_empresa["tipologia"].dropna().unique()))

        # Indicadores + Pesos (popover responsivo)
        # Popover principal com 2 popovers internos (X e Y)
        with st.popover("🔧 Indicadores e Pesos"):
            colunas_base = list(BASE_LABELS.keys())
            c1, c2 = st.columns(2, gap="small")

            # ---------------- EIXO X (Operação) ----------------
            with c1:
                with st.popover("Eixo X"):
                    st.markdown("#### Eixo X (Operação)")
                    colunas_x_base = st.multiselect(
                        "Indicadores do Eixo X",
                        options=colunas_base,
                        default=["nota_producao", "nota_custo", "nota_receita_operacional"],
                        format_func=lambda x: BASE_LABELS[x],
                        max_selections=3,
                        key="multiselect_x",
                    )
                    pesos_x = criar_dropdowns_peso_em_linha(
                        colunas_x_base, "peso_x", "🎯 Pesos:"
                    )

            # ---------------- EIXO Y (Estratégia) --------------
            with c2:
                with st.popover("Eixo Y"):
                    st.markdown("#### Eixo Y (Estratégia)")
                    colunas_y_base = st.multiselect(
                        "Indicadores do Eixo Y",
                        options=colunas_base,
                        default=["nota_orcamento", "nota_caixa"],
                        format_func=lambda x: BASE_LABELS[x],
                        max_selections=3,
                        key="multiselect_y",
                    )
                    pesos_y = criar_dropdowns_peso_em_linha(
                        colunas_y_base, "peso_y", "🎯 Pesos:"
                )


    # Aplicar sufixos e preparar dados
    sufixo = SUFIXO_MAP.get(filtro_col, "")
    colunas_x = [col + sufixo for col in colunas_x_base]
    colunas_y = [col + sufixo for col in colunas_y_base]

    # Conversões numéricas batch
    colunas_numericas = colunas_x + colunas_y + ["idade_unidade"]
    colunas_existentes = [col for col in colunas_numericas if col in df_empresa.columns]
    if colunas_existentes:
        df_empresa[colunas_existentes] = df_empresa[colunas_existentes].apply(pd.to_numeric, errors="coerce")

    # Filtro principal
    df_filtrado = df_empresa[df_empresa[filtro_col] == str(competencia_sel)].copy()
    df_filtrado = aplicar_filtros_avancados(df_filtrado, conselho_sel, tipologia_sel, unidade_sel)

    return (
        df_filtrado, empresa_sel, str(competencia_sel), agrupamento_opcao,
        conselho_sel, unidade_sel, tipologia_sel, colunas_x, pesos_x,
        colunas_y, pesos_y, filtro_col, df_empresa, nome_map
    )

# ==============================
# Sufixos util
# ==============================
def aplicar_sufixos_colunas(colunas, filtro_col):
    sufixo = SUFIXO_MAP.get(filtro_col, "")
    if not sufixo:
        return colunas
    colunas_processadas = []
    sufixos_para_remover = ["_mensal", "_trimestral", "_semestral", "_anual", "_padronizada"]
    for col in colunas:
        if col.endswith(sufixo):
            colunas_processadas.append(col)
        else:
            col_base = col
            for suf in sufixos_para_remover:
                col_base = col_base.replace(suf, "")
            colunas_processadas.append(col_base + sufixo)
    return colunas_processadas
