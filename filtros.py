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
    idx = PESO_DEFAULT.get(label, 1) - 1
    return st.selectbox(
        label,
        options=PESO_OPTIONS,
        index=idx,
        format_func=lambda x: x[0],
        key=key
    )[1]

def criar_dropdowns_peso_em_linha(colunas_selecionadas, prefixo_key, titulo):
    """
    Cria dropdowns de peso organizados em linha
    
    Args:
        colunas_selecionadas: Lista de colunas base selecionadas
        prefixo_key: Prefixo para as keys dos selectbox
        titulo: Título da seção
    
    Returns:
        Lista de pesos selecionados
    """
    st.markdown(f"**{titulo}**")
    
    if not colunas_selecionadas:
        st.warning("Selecione pelo menos uma variável")
        return []
    
    num_colunas = len(colunas_selecionadas)
    pesos = []
    
    # Criar colunas dinamicamente baseado no número de variáveis
    if num_colunas == 1:
        cols = [st.container()]
    elif num_colunas == 2:
        cols = st.columns(2)
    elif num_colunas == 3:
        cols = st.columns(3)
    else:  # 4 ou mais
        cols = st.columns(4)
    
    # Distribuir os dropdowns pelas colunas
    for i, col_base in enumerate(colunas_selecionadas):
        label = BASE_LABELS[col_base]
        
        # Usar a coluna correspondente (circular se houver mais variáveis que colunas)
        col_index = i % len(cols)
        
        with cols[col_index]:
            peso = seletor_peso_otimizado(
                label, 
                key=f"{prefixo_key}_{i}"
            )
            pesos.append(peso)
    
    return pesos

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
    """Função principal de filtros otimizada - VERSÃO COM DROPDOWNS EM LINHA"""
    df = processar_dados_temporais(df)
    nome_map = criar_nome_map()
    
    with st.sidebar:
        st.image('sestsenat_0.png', width=280)
        
        
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
        
        # 🔧 CONFIGURAÇÃO DE EIXOS MODIFICADA - DROPDOWNS EM LINHA
        with st.popover("🔧 Indicadores e Pesos"):
            colunas_base = list(BASE_LABELS.keys())
            
            # Seleção das variáveis do Eixo X
            st.markdown("#### Pesos Eixo X (Operação)")
            colunas_x_base = st.multiselect(
                "Variáveis do Eixo X",
                options=colunas_base,
                default=["nota_orcamento", "nota_caixa", "nota_nps"],
                format_func=lambda x: BASE_LABELS[x],
                max_selections=4,
                key="multiselect_x"
            )
            
            # 🎯 DROPDOWNS DE PESO EM LINHA - EIXO X
            pesos_x = criar_dropdowns_peso_em_linha(
                colunas_x_base, 
                "peso_x", 
                "🎯 Pesos:"
            )
            
            # Separador visual
            st.markdown("---")
            
            # Seleção das variáveis do Eixo Y
            st.markdown("#### Pesos Eixo Y (Estratégia)")
            colunas_y_base = st.multiselect(
                "Variáveis do Eixo Y", 
                options=colunas_base,
                default=["nota_receita", "nota_custo", "nota_producao"],
                format_func=lambda x: BASE_LABELS[x],
                max_selections=4,
                key="multiselect_y"
            )
            
            # 🎯 DROPDOWNS DE PESO EM LINHA - EIXO Y
            pesos_y = criar_dropdowns_peso_em_linha(
                colunas_y_base, 
                "peso_y", 
                "🎯 Pesos:"
            )
    
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

# ============================================================================
# 🎨 FUNÇÃO ADICIONAL: CSS PARA DROPDOWNS MAIS COMPACTOS (OPCIONAL)
# ============================================================================
def aplicar_estilo_dropdowns_compactos():
    """
    Aplica CSS para deixar os dropdowns de peso mais compactos
    """
    st.markdown("""
    <style>
    /* Dropdowns de peso mais compactos */
    div[data-testid="column"] .stSelectbox {
        margin-bottom: 8px;
    }
    
    div[data-testid="column"] .stSelectbox > label {
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 4px;
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    div[data-testid="column"] .stSelectbox > div {
        margin-bottom: 0;
    }
    
    /* Popover mais largo para acomodar dropdowns em linha */
    .stPopover > div {
        min-width: 400px !important;
    }
    
    /* Título dos pesos com destaque */
    .stMarkdown strong {
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)