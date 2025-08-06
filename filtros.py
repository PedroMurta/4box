import streamlit as st
import pandas as pd

# Constantes globais
PESO_OPTIONS = [(str(i), i) for i in range(1, 6)]
PESO_DEFAULT = {"Orçamento": 1, "Caixa": 1, "Capacidade Produtiva": 1, "Receita": 1, "Custo": 1, "Produção": 1, "NPS": 1}

SUFIXO_MAP = {
    "competencia": "_mensal_padronizada",
    "ano_semestre": "_semestral_padronizada", 
    "trimestre": "_trimestral_padronizada",
    "ano": "_anual_padronizada"
}

BASE_LABELS = {
    "nota_orcamento": "Orçamento",
    "nota_caixa": "Caixa", 
    "nota_capacidade_produtiva": "Capacidade Produtiva",
    "nota_receita": "Receita",
    "nota_custo": "Custo",
    "nota_producao": "Produção",
    "nota_nps": "NPS"
}

FILTRO_COL_MAP = {
    "Mês": "competencia",
    "Semestre": "ano_semestre",
    "Ano": "ano", 
    "Trimestre": "trimestre"
}

VALORES_PADRAO = {
    "competencia": "2024-01",
    "ano_semestre": "2024-1", 
    "ano": "2024",
    "trimestre": "2024-1"
}

def criar_nome_map():
    """Cria mapeamento de nomes de colunas uma única vez"""
    nome_map = {}
    sufixos = ["", "_mensal", "_trimestral", "_semestral", "_anual"]
    
    for base, label in BASE_LABELS.items():
        for sufixo in sufixos:
            nome_map[f"{base}{sufixo}"] = label
            if sufixo:
                nome_map[f"{base}{sufixo}_padronizada"] = label
    
    return nome_map

@st.cache_data
def processar_dados_temporais(df):
    """Processa dados temporais de forma otimizada"""
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
    """Seletor de peso otimizado"""
    idx = PESO_DEFAULT[label] - 1
    return st.selectbox(
        label,
        options=PESO_OPTIONS,
        index=idx,
        format_func=lambda x: x[0],
        key=key
    )[1]

def aplicar_filtros_avancados(df_empresa, conselho_sel, tipologia_sel, unidade_sel):
    """Aplica filtros avançados de forma eficiente"""
    mask = pd.Series(True, index=df_empresa.index)
    
    if conselho_sel != "Todos":
        mask &= (df_empresa["conselho"] == conselho_sel)
    if tipologia_sel != "Todas": 
        mask &= (df_empresa["tipologia"] == tipologia_sel)
    if unidade_sel != "Todas":
        mask &= (df_empresa["unidade"] == unidade_sel)
        
    return df_empresa[mask].copy()

def sidebar_filtros(df):
    """Função principal de filtros otimizada"""
    df = processar_dados_temporais(df)
    nome_map = criar_nome_map()
    
    with st.sidebar:
        st.markdown("### Filtros")
        
        # Filtros básicos
        col1, col2 = st.columns(2)
        with col1:
            empresa_sel = st.radio("Empresa", ["SEST", "SENAT"], index=0)
        with col2:
            agrupamento_opcao = st.radio("Agrupar por", 
                                       ["Mês", "Trimestre", "Semestre", "Ano"], 
                                       index=3)
        
        filtro_col = FILTRO_COL_MAP[agrupamento_opcao]
        df_empresa = df[df["empresa"] == empresa_sel].copy()
        
        # Seleção de período
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
            conselho_sel = st.selectbox(
                "Conselho:",
                ["Todos"] + sorted(df_empresa["conselho"].dropna().unique())
            )
            
            unidade_sel = st.selectbox(
                "Unidade:",
                ["Todas"] + sorted(df_empresa["unidade"].dropna().unique())
            )
            
            tipologia_sel = st.selectbox(
                "Tipologia:",
                ["Todas"] + sorted(df_empresa["tipologia"].dropna().unique())
            )
        
        # Configuração de eixos
        with st.popover("🔧 Ajustar Pesos dos Eixos"):
            colunas_base = list(BASE_LABELS.keys())
            
            st.markdown("##### Pesos Eixo X (Operação)")
            colunas_x_base = st.multiselect(
                "Variáveis do Eixo X",
                options=colunas_base,
                default=["nota_orcamento", "nota_caixa", "nota_nps"],
                format_func=lambda x: BASE_LABELS[x],
                max_selections=4
            )
            
            pesos_x = []
            for i, col in enumerate(colunas_x_base):
                peso = seletor_peso_otimizado(BASE_LABELS[col], key=f"peso_x_{i}")
                pesos_x.append(peso)
            
            st.markdown("##### Pesos Eixo Y (Estratégia)")
            colunas_y_base = st.multiselect(
                "Variáveis do Eixo Y", 
                options=colunas_base,
                default=["nota_receita", "nota_custo", "nota_producao"],
                format_func=lambda x: BASE_LABELS[x],
                max_selections=4
            )
            
            pesos_y = []
            for i, col in enumerate(colunas_y_base):
                peso = seletor_peso_otimizado(BASE_LABELS[col], key=f"peso_y_{i}")
                pesos_y.append(peso)
    
    # Aplicar sufixos e preparar dados finais
    sufixo = SUFIXO_MAP.get(filtro_col, "")
    colunas_x = [col + sufixo for col in colunas_x_base]
    colunas_y = [col + sufixo for col in colunas_y_base]
    
    # Conversões numéricas batch
    colunas_numericas = colunas_x + colunas_y + ["idade_unidade"]
    colunas_existentes = [col for col in colunas_numericas if col in df_empresa.columns]
    
    if colunas_existentes:
        df_empresa[colunas_existentes] = df_empresa[colunas_existentes].apply(
            pd.to_numeric, errors="coerce"
        )
    
    # Filtro principal
    df_filtrado = df_empresa[df_empresa[filtro_col] == str(competencia_sel)].copy()
    df_filtrado = aplicar_filtros_avancados(df_filtrado, conselho_sel, tipologia_sel, unidade_sel)
    
    return (
        df_filtrado, empresa_sel, str(competencia_sel), agrupamento_opcao,
        conselho_sel, unidade_sel, tipologia_sel, colunas_x, pesos_x,
        colunas_y, pesos_y, filtro_col, df_empresa, nome_map
    )

def aplicar_sufixos_colunas(colunas, filtro_col):
    """Aplica sufixos às colunas de forma otimizada"""
    sufixo = SUFIXO_MAP.get(filtro_col, "")
    
    if not sufixo:
        return colunas
    
    colunas_processadas = []
    sufixos_para_remover = ["_mensal", "_trimestral", "_semestral", "_anual", "_padronizada"]
    
    for col in colunas:
        if col.endswith(sufixo):
            colunas_processadas.append(col)
        else:
            # Remove sufixos existentes
            col_base = col
            for suf in sufixos_para_remover:
                col_base = col_base.replace(suf, "")
            colunas_processadas.append(col_base + sufixo)
    
    return colunas_processadas