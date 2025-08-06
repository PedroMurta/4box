import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import numpy as np

# ===== CONSTANTES GLOBAIS =====
CORES_QUADRANTES_NINEBOX = {
    "1": "#ec7063", "2": "#f1948a", "3": "#f5b7b1",
    "4": "#f7dc6f", "5": "#fcf3cf", "6": "#f9e79f",
    "7": "#82e0aa", "8": "#a9dfbf", "9": "#abebc6"
}

CORES_TIPOLOGIA = {
    "A": "#0c64a3", "B": "#7E220D", "C": "#8fac1b",
    "CN": "#109410", "D": "#7627d6", "DN": "#574b63"
}

CORES_PADROES = {
    "meta": "#81a4cd",
    "realizado_bom": "#588157",
    "realizado_ruim": "#b04c52",
    "receita": "#588157",
    "despesa": "#81a4cd"
}

LAYOUT_CONFIG = {
    "paper_bgcolor": 'ghostwhite',
    "plot_bgcolor": 'ghostwhite',
    "margin": dict(t=50, b=50, l=50, r=50)
}

# ===== FUNÇÕES UTILITÁRIAS =====
def filtrar_dados_base(df, empresa_sel, unidade_sel=None):
    """Filtragem básica otimizada"""
    mask = df["empresa"] == empresa_sel
    if unidade_sel and unidade_sel != "Todas":
        mask &= df["unidade"] == unidade_sel
    return df[mask].copy()

def converter_colunas_numericas(df, colunas):
    """Converte múltiplas colunas para numéricas de forma otimizada"""
    for col in colunas:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r"[^\d,.-]", "", regex=True).str.replace(",", "."),
                errors="coerce"
            ).fillna(0)
    return df

def criar_card_html(titulo, valor, cor="#3f4f6b"):
    """Cria HTML para cards padronizado"""
    return f"""
    <div style="border: 2px solid #ccc; border-radius: 12px; padding: 10px; margin: 5px;
                background-color: {cor}; text-align: center; color: white;">
        <div style="font-size: 16px; font-weight: bold;">{titulo}</div>
        <div style="font-size: 20px; margin-top: 5px;">{valor}</div>
    </div>
    """

# ===== GRÁFICO NINEBOX OTIMIZADO =====
@st.cache_data
def calcular_dados_ninebox(df, empresa_sel, competencia_sel, coluna_periodo, colunas_x, pesos_x, colunas_y, pesos_y):
    """Cálculos do NineBox com cache"""
    df_filtro = df[
        (df["empresa"] == empresa_sel) & 
        (df[coluna_periodo] == competencia_sel)
    ].copy()
    
    if df_filtro.empty:
        return None
    
    # Cálculo vetorizado dos eixos
    df_filtro["eixo_x"] = sum(df_filtro[var].fillna(0) * peso for var, peso in zip(colunas_x, pesos_x))
    df_filtro["eixo_y"] = sum(df_filtro[var].fillna(0) * peso for var, peso in zip(colunas_y, pesos_y))
    
    # Tamanho das bolhas otimizado
    if "idade_unidade" in df_filtro.columns:
        idade = pd.to_numeric(df_filtro["idade_unidade"], errors="coerce").fillna(1)
        df_filtro["tamanho"] = np.interp(idade, (idade.min(), idade.max()), (10, 50))
    else:
        df_filtro["tamanho"] = 15
    
    return df_filtro

def grafico_ninebox(df, empresa_sel, competencia_sel, unidade_sel, coluna_periodo, 
                   colunas_x, pesos_x, colunas_y, pesos_y, nome_map):
    """Gráfico NineBox otimizado"""
    
    df_dados = calcular_dados_ninebox(df, empresa_sel, competencia_sel, coluna_periodo, 
                                     colunas_x, pesos_x, colunas_y, pesos_y)
    
    if df_dados is None:
        st.warning("Sem dados para os filtros selecionados.")
        return px.scatter()
    
    df_dados["destaque"] = df_dados["unidade"] == unidade_sel if unidade_sel != "Todas" else False
    
    # Criação do gráfico
    fig = px.scatter(
        df_dados,
        x="eixo_x", y="eixo_y",
        color="tipologia",
        size="tamanho",
        size_max=45,
        hover_name="unidade",
        hover_data={var: ':.2f' for var in set(colunas_x + colunas_y)} | {"eixo_x": ':.2f', "eixo_y": ':.2f'},
        labels={"eixo_x": "Operação", "eixo_y": "Estratégia"},
        color_discrete_map=CORES_TIPOLOGIA,
        title=f"Gráfico 9Box – {empresa_sel} ({competencia_sel})"
    )
    
    # Adicionar quadrantes de forma otimizada
    adicionar_quadrantes_ninebox(fig)
    adicionar_bordas_ninebox(fig)
    adicionar_labels_ninebox(fig)
    
    # Layout final
    fig.update_layout(
        height=900,
        **LAYOUT_CONFIG,
        xaxis=dict(range=[0, 15], tickvals=[], showticklabels=False),
        yaxis=dict(range=[0, 15], tickvals=[], showticklabels=False),
        legend_title="Tipologia",
        showlegend=True
    )
    
    # Anotação dos eixos
    texto_eixos = criar_texto_eixos(colunas_x, pesos_x, colunas_y, pesos_y, nome_map)
    fig.add_annotation(
        text=texto_eixos,
        xref="paper", yref="paper", x=0, y=-0.2,
        showarrow=False, align="left",
        font=dict(size=12, color="black")
    )
    
    return fig

def adicionar_quadrantes_ninebox(fig):
    """Adiciona quadrantes do NineBox"""
    for row, (y0, y1) in enumerate([(10, 15), (5, 10), (0, 5)]):
        for col, (x0, x1) in enumerate([(0, 5), (5, 10), (10, 15)]):
            numero = str((2 - row) + col * 3 + 1)
            fig.add_shape(
                type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                fillcolor=CORES_QUADRANTES_NINEBOX.get(numero, "#ccc"), 
                opacity=0.25, line=dict(width=0), layer="below"
            )
            fig.add_annotation(
                x=(x0 + x1) / 2, y=(y0 + y1) / 2,
                text=f"<b>{numero}</b>", showarrow=False,
                font=dict(size=16), xanchor="center", yanchor="middle"
            )

def adicionar_bordas_ninebox(fig):
    """Adiciona linhas de grade do NineBox"""
    for pos in [0, 5, 10, 15]:
        # Linhas verticais
        fig.add_shape(type="line", x0=pos, x1=pos, y0=0, y1=15, 
                     line=dict(color="black", width=1))
        # Linhas horizontais  
        fig.add_shape(type="line", x0=0, x1=15, y0=pos, y1=pos, 
                     line=dict(color="black", width=1))

def adicionar_labels_ninebox(fig):
    """Adiciona labels dos eixos do NineBox"""
    labels_y = [("Alta Estratégia", 13), ("Média Estratégia", 8), ("Baixa Estratégia", 3)]
    labels_x = [("Baixa Eficiência", 3), ("Média Eficiência", 8), ("Alta Eficiência", 13)]
    
    for texto, pos in labels_y:
        fig.add_annotation(text=texto, x=-0.3, y=pos, showarrow=False, 
                          font=dict(size=12), xanchor="right")
    
    for texto, pos in labels_x:
        fig.add_annotation(text=texto, x=pos, y=-0.3, showarrow=False, 
                          font=dict(size=12), yanchor="top")

def criar_texto_eixos(colunas_x, pesos_x, colunas_y, pesos_y, nome_map):
    """Cria texto explicativo dos eixos"""
    texto_x = ", ".join([f"{nome_map.get(v, v)} (peso {p})" for v, p in zip(colunas_x, pesos_x)])
    texto_y = ", ".join([f"{nome_map.get(v, v)} (peso {p})" for v, p in zip(colunas_y, pesos_y)])
    return f"<b>Eixo X:</b> {texto_x}<br><b>Eixo Y:</b> {texto_y}"

# ===== GRÁFICOS DE SÉRIE TEMPORAL =====
def grafico_nota_producao_series(df, empresa_sel, unidade_sel):
    """Gráfico de série temporal da nota de produção otimizado"""
    df_filtrado = filtrar_dados_base(df, empresa_sel, unidade_sel)
    
    fig = px.line(
        df_filtrado,
        x="competencia",
        y="nota_producao",
        color="unidade" if unidade_sel == "Todas" else None,
        title="Série Histórica - Nota Produção",
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Competência",
        yaxis_title="Nota de Produção",
        height=500,
        **LAYOUT_CONFIG
    )
    
    return fig

# ===== GRÁFICOS DE CUSTO =====
@st.cache_data
def processar_dados_custo(df, empresa_sel, unidade_sel):
    """Processa dados de custo com cache"""
    df_filtrado = filtrar_dados_base(df, empresa_sel, unidade_sel)
    
    # Garante todas as competências
    todas_competencias = pd.DataFrame(sorted(df["competencia"].unique()), columns=["competencia"])
    
    # Agrupamento otimizado
    df_custo = df_filtrado.groupby("competencia", as_index=False)[
        ["soma_custo_realizado", "soma_meta"]
    ].sum()
    
    # Merge otimizado
    df_resultado = todas_competencias.merge(df_custo, on="competencia", how="left").fillna(0)
    df_resultado["cor_realizado"] = np.where(
        df_resultado["soma_custo_realizado"] > df_resultado["soma_meta"],
        CORES_PADROES["realizado_ruim"], 
        CORES_PADROES["realizado_bom"]
    )
    
    return df_resultado

def grafico_custo_realizado_vs_meta(df, empresa_sel, unidade_sel, competencia_sel):
    """Gráfico de custo vs meta otimizado"""
    df_custo = processar_dados_custo(df, empresa_sel, unidade_sel)
    
    fig = go.Figure()
    
    # Barras Realizado
    fig.add_trace(go.Bar(
        x=df_custo["competencia"],
        y=df_custo["soma_custo_realizado"],
        name="Realizado",
        marker_color=df_custo["cor_realizado"],
        text=df_custo["soma_custo_realizado"].apply(lambda x: f"{x:,.2f}"),
        textposition="inside",
        textangle=0,
        insidetextanchor="middle"
    ))
    
    # Barras Meta
    fig.add_trace(go.Bar(
        x=df_custo["competencia"],
        y=df_custo["soma_meta"],
        name="Meta",
        marker_color=CORES_PADROES["meta"],
        text=df_custo["soma_meta"].apply(lambda x: f"{x:,.2f}"),
        textposition="inside",
        textangle=0,
        insidetextanchor="middle"
    ))
    
    # Layout otimizado
    titulo = f"{empresa_sel}"
    if unidade_sel != "Todas":
        titulo += f" – {unidade_sel}<br><br>"
    
    
    fig.update_layout(
        title=titulo,
        xaxis_title="Competência",
        yaxis_title="Valor (R$)",
        barmode="group",
        height=550,
        xaxis_tickangle=-45,
        **LAYOUT_CONFIG
    )
    
    return fig

# ===== GRÁFICOS DE RECEITA/DESPESA =====
def criar_grafico_barras_comparativo(valores, labels, titulo_y, cores=None):
    """Cria gráfico de barras comparativo genérico"""
    if cores is None:
        cores = [CORES_PADROES["realizado_bom"] if valores[0] <= valores[1] 
                else CORES_PADROES["realizado_ruim"], CORES_PADROES["meta"]]
    
    fig = go.Figure()
    
    for i, (valor, label, cor) in enumerate(zip(valores, labels, cores)):
        fig.add_trace(go.Bar(
            x=[titulo_y],
            y=[valor],
            name=label,
            marker_color=cor,
            text=f"R$ {valor:,.0f}",
            textposition="auto"
        ))
    
    fig.update_layout(
        yaxis_title="Valor (R$)",
        barmode="group",
        height=400,
        showlegend=True,
        **LAYOUT_CONFIG
    )
    
    return fig

def grafico_receita_realizada_vs_prevista(receita_prevista, receita_realizada):
    """Gráfico de receita otimizado"""
    return criar_grafico_barras_comparativo(
        [receita_realizada, receita_prevista],
        ["Realizado", "Previsto"],
        "Receita"
    )

def grafico_despesa_realizada_vs_prevista(despesa_prevista, despesa_liquidada):
    """Gráfico de despesa otimizado"""
    return criar_grafico_barras_comparativo(
        [despesa_liquidada, despesa_prevista],
        ["Realizado", "Previsto"],
        "Despesa"
    )

# ===== CARDS ORÇAMENTÁRIOS =====
def exibir_cards_orcamentarios(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo):
    """Cards orçamentários otimizados"""
    df_filtrado = filtrar_dados_base(df, empresa_sel, unidade_sel)
    df_filtrado = df_filtrado[df_filtrado[coluna_periodo] == competencia_sel]
    
    colunas_valores = [
        "receita_prevista", "receita_realizada",
        "despesa_prevista", "despesa_liquidada",
        "proposta", "execucao_orcamentaria"
    ]
    
    df_filtrado = converter_colunas_numericas(df_filtrado, colunas_valores)
    
    # Cálculos agregados
    metricas = {
        "receita_prevista": df_filtrado["receita_prevista"].sum(),
        "receita_realizada": df_filtrado["receita_realizada"].sum(),
        "despesa_prevista": df_filtrado["despesa_prevista"].sum(),
        "despesa_liquidada": df_filtrado["despesa_liquidada"].sum(),
        "proposta": df_filtrado["proposta"].sum(),
        "execucao_orcamentaria": df_filtrado["execucao_orcamentaria"].mean()
    }
    
    perc_exec_receita = (
        metricas["receita_realizada"] / metricas["receita_prevista"] * 100 
        if metricas["receita_prevista"] > 0 else 0
    )
    
    # Exibição dos cards
    col1, col2, col3, col4 = st.columns(4)
    cards_linha1 = [
        ("📥 Receita Prevista", f"R$ {metricas['receita_prevista']:,.0f}"),
        ("📤 Receita Realizada", f"R$ {metricas['receita_realizada']:,.0f}"),
        ("📊 Proposta Orçamentária", f"R$ {metricas['proposta']:,.0f}"),
        ("📈 Execução das Receitas", f"{perc_exec_receita:.2f}%")
    ]
    
    for col, (titulo, valor) in zip([col1, col2, col3, col4], cards_linha1):
        with col:
            st.markdown(criar_card_html(titulo, valor), unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    col5, col6, col7 = st.columns(3)
    cards_linha2 = [
        ("💸 Despesa Prevista", f"R$ {metricas['despesa_prevista']:,.0f}"),
        ("💰 Despesa Liquidada", f"R$ {metricas['despesa_liquidada']:,.0f}"),
        ("📊 Execução Orçamentária", f"{metricas['execucao_orcamentaria']:.2f}%")
    ]
    st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    for col, (titulo, valor) in zip([col5, col6, col7], cards_linha2):
        with col:
            st.markdown(criar_card_html(titulo, valor), unsafe_allow_html=True)
    
    # Gráficos comparativos
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Execução da Receita")
        fig_receita = grafico_receita_realizada_vs_prevista(
            metricas["receita_prevista"], metricas["receita_realizada"]
        )
        st.plotly_chart(fig_receita, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Execução da Despesa")
        fig_despesa = grafico_despesa_realizada_vs_prevista(
            metricas["despesa_prevista"], metricas["despesa_liquidada"]
        )
        st.plotly_chart(fig_despesa, use_container_width=True)

# ===== FLUXO DE CAIXA =====
@st.cache_data
def processar_dados_fluxo_caixa(df, empresa_sel, unidade_sel):
    """Processa dados de fluxo de caixa com cache"""
    df_filtrado = filtrar_dados_base(df, empresa_sel, unidade_sel)
    
    # Garante todas as competências
    todas_competencias = pd.DataFrame(sorted(df["competencia"].unique()), columns=["competencia"])
    
    # Agrupamento
    df_fluxo = df_filtrado.groupby("competencia", as_index=False)[
        ["receitas", "despesas"]
    ].sum()
    
    # Merge e cores
    df_resultado = todas_competencias.merge(df_fluxo, on="competencia", how="left").fillna(0)
    df_resultado["cor_receita"] = CORES_PADROES["receita"]
    df_resultado["cor_despesa"] = CORES_PADROES["despesa"]
    
    return df_resultado

def grafico_fluxo_caixa(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo):
    """Gráfico de fluxo de caixa otimizado"""
    df_fluxo = processar_dados_fluxo_caixa(df, empresa_sel, unidade_sel)
    
    fig = go.Figure()
    
    # Receitas
    fig.add_trace(go.Bar(
        x=df_fluxo["competencia"],
        y=df_fluxo["receitas"],
        name="Receita",
        marker_color=df_fluxo["cor_receita"],
        text=df_fluxo["receitas"].apply(lambda x: f"{x:,.2f}"),
        textposition="inside",
        textangle=0,
        insidetextanchor="middle"
    ))
    
    # Despesas
    fig.add_trace(go.Bar(
        x=df_fluxo["competencia"],
        y=df_fluxo["despesas"],
        name="Despesa",
        marker_color=df_fluxo["cor_despesa"],
        text=df_fluxo["despesas"].apply(lambda x: f"{x:,.2f}"),
        textposition="outside"
    ))
    
    # Layout
    titulo = f"{empresa_sel}"
    if unidade_sel != "Todas":
        titulo += f" – {unidade_sel}<br><br>"
    
    
    fig.update_layout(
        title=titulo,
        xaxis_title="Competência",
        yaxis_title="Valor (R$)",
        barmode="group",
        height=550,
        width=900,
        xaxis_tickangle=-45,
        xaxis=dict(
            tickmode='array',
            tickvals=list(df_fluxo["competencia"]),
            ticktext=list(df_fluxo["competencia"].astype(str))
        ),
        **LAYOUT_CONFIG
    )
    
    return fig

def exibir_cards_fluxo_caixa(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo):
    """Cards de fluxo de caixa otimizados"""
    df_filtrado = filtrar_dados_base(df, empresa_sel, unidade_sel)
    df_filtrado = df_filtrado[df_filtrado[coluna_periodo] == competencia_sel]
    
    colunas_valores = ["receitas", "despesas"]
    df_filtrado = converter_colunas_numericas(df_filtrado, colunas_valores)
    
    receita = df_filtrado["receitas"].sum()
    despesa = df_filtrado["despesas"].sum()
    saldo = (receita / despesa) * 100 if despesa > 0 else 0
    
    # Determinar coluna de nota baseada no período
    sufixos_nota = {
        "competencia": "mensal",
        "trimestre": "trimestral", 
        "ano_semestre": "semestral",
        "ano": "anual"
    }
    sufixo_nota = sufixos_nota.get(coluna_periodo, "mensal")
    coluna_nota = f"nota_caixa_{sufixo_nota}"
    
    nota = (
        pd.to_numeric(df_filtrado[coluna_nota], errors="coerce").mean()
        if coluna_nota in df_filtrado.columns else None
    )
    
    cor_nota = "#2ecc71" if nota is not None and nota >= 1.5 else "rgba(0,0,0,0.7)"
    st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    # Exibição dos cards
    col1, col2, col3 = st.columns(3)
    cards = [
        ("📘 Receita no Período", f"R$ {receita:,.0f}"),
        ("📙 Despesa no Período", f"R$ {despesa:,.0f}"),
        ("📈 Executado", f"{saldo:.2f}%" if saldo is not None else "-")
    ]
    
    cores = ["#3f4f6b", "#3f4f6b", cor_nota]
    st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    for col, (titulo, valor), cor in zip([col1, col2, col3], cards, cores):
        with col:
            st.markdown(criar_card_html(titulo, valor, cor), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)