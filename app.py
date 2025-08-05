# 1. IMPORTAÇÕES
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
from filtros import sidebar_filtros
from four_box import grafico_fourbox
from graficos import (
    grafico_ninebox, pagina_indicadores, grafico_nota_producao_series,
    grafico_custo_realizado_vs_meta, exibir_cards_orcamentarios
)
from painel_especialidades import exibir_metricas_com_donut
from radar import grafico_radar_notas, exibir_cards_radar


# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    layout="wide",
    page_title="Painel 4Box",
    initial_sidebar_state="expanded",
    page_icon="icone_ss.png"
)

# CSS
with open("estilo.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 3. LEITURA DOS DADOS
@st.cache_data
def carregar_dados():
    #df = pd.read_parquet("indicadores_4box_temporais.parquet")
    df = pd.read_parquet("indicadores_4box_padronizado1.parquet")
    df[df.select_dtypes(exclude="category").columns] = df.select_dtypes(exclude="category").fillna(0)
    return df

df = carregar_dados()

df.rename(columns={
    "curs_prese": "curso_prese",
    "curs_dista": "curso_ead",
    "pct_curs_prese": "pct_curso_prese",
    "pct_curs_dista": "pct_curso_ead"
}, inplace=True)

df["competencia"] = df["competencia"].astype(str)
df["ano"] = df["competencia"].str[:4]
df["mes"] = df["competencia"].str[5:7].astype(int)
df["semestre"] = df["mes"].apply(lambda m: "1" if m <= 6 else "2")
df["trimestre_mes"] = df["mes"].apply(lambda m: "1" if m <= 3 else "2" if m <= 6 else "3" if m <= 9 else "4")   
df["trimestre"] = df["ano"].astype(str) + "-" + df["trimestre_mes"].astype(str) 
df["ano_semestre"] =  df["ano"] + "-" + df["semestre"] 
df['idade_unidade'] = df['idade_unidade'].astype(int)

for col in [
    "nota_producao", "nota_custo", "nota_receita",
    "nota_orcamento", "nota_caixa", "nota_capacidade_produtiva"
]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df.sort_values(by="competencia", inplace=True)

# 4. BARRA DE NAVEGAÇÃO
aba_selecionada = option_menu(
    menu_title=None,
    options=["Painel 4Box", "Painel 9Box", "Atendimentos", "Custo", "Orçamento/Receita", "Tabela", "Radar"],
    icons=["bar-chart", "bar-chart","clock", "graph-up", "box", "table", 'activity'],
    orientation="horizontal",
    default_index=0,
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "#b7bc75", "font-size": "18px"},
        "nav-link": {"font-size": "12px", "font-weight": "500", "color": "#3f4f6b", "margin": "0 10px"},
        "nav-link-selected": {"background-color": "#3f4f6b", "color": "white"},
    }
)

# 5. FILTROS
with st.sidebar:
    df_filtro, empresa_sel, competencia_sel, agrupamento_opcao, conselho_sel, unidade_sel, tipologia_sel, \
    variaveis_x, pesos_x, variaveis_y, pesos_y, filtro_col, df_empresa, nome_map = sidebar_filtros(df)

# Corrigido: define a coluna correta para o período
coluna_periodo = {
    "Mês": "competencia",
    "Semestre": "ano_semestre",
    "Ano": "ano",
    "Trimestre": "trimestre"
}[agrupamento_opcao]

# 6. ABA PRINCIPAL - 4Box
if aba_selecionada == "Painel 4Box":
    fig = grafico_fourbox(
    df_filtro,
    empresa_sel,
    competencia_sel,
    unidade_sel,
    coluna_periodo,
    variaveis_x,
    pesos_x,
    variaveis_y,
    pesos_y,
    nome_map,
    filtro_col
)

    with st.expander("ℹ️ Ver interpretação estratégica dos quadrantes"):
        st.markdown("""
        ### 📊 Interpretação dos Quadrantes
        > **Eixo X**: esforço, recurso, insumo ou execução operacional.  
        > **Eixo Y**: retorno, entrega, desempenho ou resultado estratégico.

        #### ⭐ Tamanho das Bolhas
        > Idade da unidade. Quanto maior a bolha, maior a data de inauguração, quanto menor a bolha, mais recente a unidade foi inaugurada.

        #### 💡 Cor das Bolhas
        > Indica a Tipologia de cada Unidade.
        
        """)

    st.plotly_chart(fig, use_container_width=True)

# 7. ABA 9Box
elif aba_selecionada == "Painel 9Box":
    fig = grafico_ninebox(
        df_filtro,  # usa df_filtro também aqui
        empresa_sel,
        competencia_sel,
        unidade_sel,
        coluna_periodo,
        variaveis_x,
        pesos_x,
        variaveis_y,
        pesos_y,
        {
            "nota_orcamento": "Orçamento",
            "nota_caixa": "Caixa",
            "nota_capacidade_produtiva": "Capacidade Produtiva",
            "nota_receita": "Receita",
            "nota_custo": "Custo",
            "nota_producao": "Produção",
            "nota_nps": 'NPS'
        }
    )

    with st.expander("ℹ️ Ver interpretação estratégica dos quadrantes 9Box"):
        st.markdown("""
        ### 🧭 Interpretação do Gráfico 9Box
        - **Eixo X (Operação)**: uso de recursos, insumos, estrutura.
        - **Eixo Y (Estratégia)**: entrega, resultado, desempenho.
        - O gráfico classifica unidades em 9 zonas de desempenho e eficiência combinadas.

        <small>*Ajuste as variáveis e pesos dos eixos na lateral esquerda.*</small>
        """, unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True)

# 8. ABA ATENDIMENTOS
elif aba_selecionada == "Atendimentos":
    st.subheader("🧾 Produção")
    with st.expander("ℹ️ Interpretação dos gráficos"):
        st.markdown("""
        ###  Gráfico de linhas         
        > Reflete a nota histórica de produção da UO por competência.

        ####  Gráfico de Donuts
        > Especialidade -> Executado -> meta. 
        ...         
        """)
    st.plotly_chart(grafico_nota_producao_series(df, empresa_sel, unidade_sel), use_container_width=True)
    st.markdown(f"<h4 style='text-align: center;'><b><br>{unidade_sel} ({competencia_sel})</br></h4>", unsafe_allow_html=True)
    exibir_metricas_com_donut(df, unidade_sel, coluna_periodo, competencia_sel)

    

    
# 9. ABA CUSTO
elif aba_selecionada == "Custo":
    st.subheader("💸 Custo Realizado vs Meta por Competência")
    with st.expander("ℹ️ Descrição"):
        st.markdown("""
        ### 📊 Interpretação dos Quadrantes
        > **Meta do Custo**: Valor definido para execução do custo de cada atendimento da UO no período selecionado. 
        
        > **Realizado**: Valor Real executado.
        
        > **Coluna Azul**: Valor da meta.
        
        > **Coluna Vermelha**: Quando o valor executado é superior a meta.
        
        > **Coluna Verde**: Quando o valor executado é melhor que a meta.
        """)
    st.plotly_chart(grafico_custo_realizado_vs_meta(df, empresa_sel, unidade_sel, competencia_sel), use_container_width=True)
    
    

    

# 10. ABA ORÇAMENTO
elif aba_selecionada == "Orçamento/Receita":
    st.subheader("📦 Indicadores Orçamentários")
    with st.expander("ℹ️ Ver Descrição das Variáveis"):
        st.markdown("""
        ### 📊 Descrição:
        > **Execução das Receitas**: Valor da Receita Realizada sobre a Receita Prevista da UO no período selecionado.  
        > **Execução Orçamentária**: Despesa Liquidade sobre a Despesa Prevista da UO no período selecionado.
        
        """)

    
    st.markdown(f"<h4 style='text-align: center;'><b><br>{unidade_sel} ({competencia_sel})</br></h4>", unsafe_allow_html=True)
    exibir_cards_orcamentarios(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo)

    
# 11. ABA TABELA
elif aba_selecionada == "Tabela":
    pagina_indicadores(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo)
    
# 12. ABA RADAR
elif aba_selecionada == "Radar":
    st.subheader("📡 Radar de Notas por Indicador")
    st.markdown(f"<h4 style='text-align: center;'><b>{unidade_sel} ({competencia_sel})</b></h4><br>", unsafe_allow_html=True)

    col_grafico, col_cards = st.columns([2, 1])

    with col_grafico:
        fig_radar = grafico_radar_notas(df, empresa_sel, unidade_sel, competencia_sel, agrupamento_opcao)
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown(f"<br><br>", unsafe_allow_html=True)
    with col_cards:
        exibir_cards_radar(df, empresa_sel, unidade_sel, competencia_sel, agrupamento_opcao)
