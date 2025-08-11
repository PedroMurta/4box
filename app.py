# 1. IMPORTAÇÕES
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu

from filtros import sidebar_filtros
from four_box import grafico_fourbox
from graficos import (
    grafico_nota_producao_series, grafico_custo_realizado_vs_meta, 
    exibir_cards_orcamentarios, grafico_fluxo_caixa, exibir_cards_fluxo_caixa
)
from painel_especialidades import exibir_metricas_com_donut
from radar import grafico_radar_notas, exibir_cards_radar

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    layout="wide",
    page_title="Painel 4Box",
    #initial_sidebar_state="expanded",
    page_icon="icone_ss.png"
)

# CSS
with open("estilo.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 3. CACHE E PROCESSAMENTO DE DADOS
@st.cache_data
def carregar_e_processar_dados():
    """Carrega e processa todos os dados de uma só vez"""
    df = pd.read_parquet("indicadores.parquet")
    
    # Renomeações
    df.rename(columns={
        "curs_prese": "curso_prese",
        "curs_dista": "curso_ead",
        "pct_curs_prese": "pct_curso_prese",
        "pct_curs_dista": "pct_curso_ead"
    }, inplace=True)
    
    # Processamento temporal
    df["competencia"] = df["competencia"].astype(str)
    df["ano"] = df["competencia"].str[:4]
    df["mes"] = df["competencia"].str[5:7].astype(int)
    
    # Aplicação vetorizada para semestre e trimestre
    df["semestre"] = (df["mes"] > 6).astype(int) + 1
    df["trimestre_mes"] = ((df["mes"] - 1) // 3 + 1).astype(str)
    df["trimestre"] = df["ano"] + "-" + df["trimestre_mes"]
    df["ano_semestre"] = df["ano"] + "-" + df["semestre"].astype(str)
    
    # Conversões numéricas em batch
    colunas_numericas = [
        "nota_producao", "nota_custo", "nota_receita",
        "nota_orcamento", "nota_caixa", "nota_capacidade_produtiva", "idade_unidade"
    ]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Preenchimento de NaN apenas para colunas não categóricas
    df[df.select_dtypes(exclude="category").columns] = df.select_dtypes(exclude="category").fillna(0)
    
    df.sort_values(by="competencia", inplace=True)
    return df

# Mapeamento de colunas por período (constante)
COLUNA_PERIODO_MAP = {
    "Mês": "competencia",
    "Semestre": "ano_semestre", 
    "Ano": "ano",
    "Trimestre": "trimestre"
}

# Configuração de abas (constante)
#ABAS_CONFIG = {
#    "options": ["Painel 4Box", "Radar", "Atendimentos", "Orçamento/Receita", "Custo", "Caixa"],
#    "icons": ["bar-chart", "activity", "clock", "box", "graph-up", "credit-card"],
#    "styles": {
#        "container": {"padding": "0!important", "background-color": "#fafafa"},
#        "icon": {"color": "#b7bc75", "font-size": "18px"},
#        "nav-link": {"font-size": "12px", "font-weight": "500", "color": "#3f4f6b", "margin": "0 10px"},
#        "nav-link-selected": {"background-color": "#3f4f6b", "color": "white"},
#    }
#}

# Configuração de abas (constante)
ABAS_CONFIG = {
    "options": ["Painel 4Box", "Radar"],
    "icons": ["bar-chart", "activity"],
    "styles": {
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "#b7bc75", "font-size": "18px"},
        "nav-link": {"font-size": "12px", "font-weight": "500", "color": "#3f4f6b", "margin": "0 10px"},
        "nav-link-selected": {"background-color": "#3f4f6b", "color": "white"},
    }
}

def main():
    # Carregamento único dos dados
    df = carregar_e_processar_dados()
    
    # 4. NAVEGAÇÃO
    aba_selecionada = option_menu(
        menu_title=None,
        orientation="horizontal",
        default_index=0,
        **ABAS_CONFIG
    )
    
    # 5. FILTROS (processamento único)
    filtros = sidebar_filtros(df)
    (df_filtro, empresa_sel, competencia_sel, agrupamento_opcao, 
     conselho_sel, unidade_sel, tipologia_sel, variaveis_x, pesos_x, 
     variaveis_y, pesos_y, filtro_col, df_empresa, nome_map) = filtros
    
    coluna_periodo = COLUNA_PERIODO_MAP[agrupamento_opcao]
    
    # 6. RENDERIZAÇÃO DAS ABAS
    if aba_selecionada == "Painel 4Box":
        renderizar_aba_4box(df_filtro, empresa_sel, competencia_sel, unidade_sel, 
                           coluna_periodo, variaveis_x, pesos_x, variaveis_y, 
                           pesos_y, nome_map, filtro_col)
    
    #elif aba_selecionada == "Atendimentos":
    #    renderizar_aba_atendimentos(df, empresa_sel, unidade_sel, competencia_sel, 
    #                               coluna_periodo)
    
    #elif aba_selecionada == "Custo":
    #    renderizar_aba_custo(df, empresa_sel, unidade_sel, competencia_sel)
    
    #elif aba_selecionada == "Orçamento/Receita":
    #    renderizar_aba_orcamento(df, empresa_sel, unidade_sel, competencia_sel, 
    #                           coluna_periodo)
    
    elif aba_selecionada == "Radar":
        renderizar_aba_radar(df, empresa_sel, unidade_sel, competencia_sel, 
                            agrupamento_opcao)
    
    #elif aba_selecionada == "Caixa":
    #    renderizar_aba_caixa(df, empresa_sel, unidade_sel, competencia_sel, 
    #                        coluna_periodo)

# Funções de renderização (separadas para melhor organização)
def renderizar_aba_4box(df_filtro, empresa_sel, competencia_sel, unidade_sel, 
                       coluna_periodo, variaveis_x, pesos_x, variaveis_y, 
                       pesos_y, nome_map, filtro_col):
    fig = grafico_fourbox(
        df_filtro, empresa_sel, competencia_sel, unidade_sel,
        coluna_periodo, variaveis_x, pesos_x, variaveis_y, pesos_y,
        nome_map, filtro_col
    )
    
    with st.expander("ℹ️ Ver interpretação estratégica dos quadrantes"):
        st.markdown("""
        ### 📊 Interpretação dos Quadrantes
        > **Eixo X**: esforço, recurso, insumo ou execução operacional.  
        > **Eixo Y**: retorno, entrega, desempenho ou resultado estratégico.

        #### ⭐ Tamanho das Bolhas
        > Idade da unidade. Quanto maior a bolha, maior a data de inauguração.

        #### 💡 Cor das Bolhas
        > Indica a Tipologia de cada Unidade.
        """)
    
    st.plotly_chart(fig, use_container_width=True)

def renderizar_aba_atendimentos(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo):
    st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    st.subheader("🧾 Produção")
    st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    with st.expander("ℹ️ Interpretação dos gráficos"):
        st.markdown("""
        ### Gráfico de linhas         
        > Reflete a nota histórica de produção da UO por competência.
        #### Gráfico de Donuts
        > Especialidade -> Executado -> meta.
        """)
    
    st.plotly_chart(grafico_nota_producao_series(df, empresa_sel, unidade_sel), 
                   use_container_width=True)
    st.markdown(f"<h4 style='text-align: center;'><b><br>{unidade_sel} ({competencia_sel})</br></h4>", 
               unsafe_allow_html=True)
    exibir_metricas_com_donut(df, unidade_sel, coluna_periodo, competencia_sel)

def renderizar_aba_custo(df, empresa_sel, unidade_sel, competencia_sel):
    st.subheader("💸 Custo Realizado vs Meta por Competência")
    with st.expander("ℹ️ Descrição"):
        st.markdown("""
        ### 📊 Interpretação
        > **Meta do Custo**: Valor definido para execução do custo.
        > **Realizado**: Valor Real executado.
        > **Coluna Azul**: Valor da meta.
        > **Coluna Vermelha**: Valor executado superior à meta.
        > **Coluna Verde**: Valor executado melhor que a meta.
        """)
    
    st.plotly_chart(grafico_custo_realizado_vs_meta(df, empresa_sel, unidade_sel, competencia_sel), 
                   use_container_width=True)

def renderizar_aba_orcamento(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo):
    st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    st.subheader("📦 Indicadores Orçamentários")
    st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    with st.expander("ℹ️ Ver Descrição das Variáveis"):
        st.markdown("""
        ### 📊 Descrição:
        > **Execução das Receitas**: Receita Realizada sobre a Prevista.
        > **Execução Orçamentária**: Despesa Liquidada sobre a Prevista.
        """)
    
    st.markdown(f"<h4 style='text-align: center;'><b><br>{unidade_sel} ({competencia_sel})</br></h4>", 
               unsafe_allow_html=True)
    exibir_cards_orcamentarios(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo)

def renderizar_aba_radar(df, empresa_sel, unidade_sel, competencia_sel, agrupamento_opcao):
    st.subheader("📡 Radar de Indicadores")
    st.markdown(f"<h4 style='text-align: center;'><b>{unidade_sel} ({competencia_sel})</b></h4><br>", 
               unsafe_allow_html=True)
    
    col_grafico, col_cards = st.columns([2, 1])
    
    with col_grafico:
        fig_radar = grafico_radar_notas(df, empresa_sel, unidade_sel, competencia_sel, agrupamento_opcao)
        st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    with col_cards:
        exibir_cards_radar(df, empresa_sel, unidade_sel, competencia_sel, agrupamento_opcao)

def renderizar_aba_caixa(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo):
    st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    st.markdown("## 💰 Fluxo de Caixa <br>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'><b>{unidade_sel} ({competencia_sel})</b></h4><br>", 
               unsafe_allow_html=True)
    exibir_cards_fluxo_caixa(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo)
    st.plotly_chart(grafico_fluxo_caixa(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo), 
                   use_container_width=True)

if __name__ == "__main__":
    main()