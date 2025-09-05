import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import numpy as np

CORES_PADROES = {
    "meta": "#81a4cd",
    "realizado_bom": "#588157",
    "realizado_ruim": "#b04c52",
    "receita": "#588157",
    "despesa": "#81a4cd"
}

LAYOUT_CONFIG = {
    "paper_bgcolor": '#F3F3F3',
    "plot_bgcolor": '#F3F3F3',
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

def criar_card_html(titulo, valor, cor="rgba(0, 48, 124, 0.7)"):
    """Cria HTML para cards padronizado"""
    return f"""
    <div style="border: 2px solid #ccc; border-radius: 12px; padding: 10px; margin: 5px;
                background-color: {cor}; text-align: center; color: white;">
        <div style="font-size: 16px; font-weight: bold;">{titulo}</div>
        <div style="font-size: 20px; margin-top: 5px;">{valor}</div>
    </div>
    """


# ===== GRÁFICOS DE SÉRIE TEMPORAL =====
@st.cache_data
def grafico_nota_producao_series(df, empresa_sel, unidade_sel):
    """Série temporal mostrando o valor da coluna 'nota_producao' visível em todos os markers."""
    df_filtrado = filtrar_dados_base(df, empresa_sel, unidade_sel).copy()

    # garantir formato e ordenação
    df_filtrado["competencia"] = df_filtrado["competencia"].astype(str)
    df_filtrado = df_filtrado.sort_values("competencia")
    df_filtrado["nota_producao"] = pd.to_numeric(df_filtrado["nota_producao"], errors="coerce")

    # coluna de texto formatada (vazia quando NaN)
    df_filtrado["text_label"] = df_filtrado["nota_producao"].apply(lambda v: f"{v:.2f}" if pd.notna(v) else "")

    if unidade_sel == "Todas":
        fig = px.line(
            df_filtrado,
            x="competencia",
            y="nota_producao",
            color="unidade",
            markers=True,
            text="text_label",
            title="Série Histórica - Nota Produção"
        )
        fig.update_traces(
            mode="lines+markers+text",
            textposition="top center",
            textfont=dict(size=9, color="#111"),
            texttemplate="%{text}"
        )
    else:
        fig = px.line(
            df_filtrado,
            x="competencia",
            y="nota_producao",
            markers=True,
            text="text_label",
            title="Série Histórica - Nota Produção"
        )
        fig.update_traces(
            mode="lines+markers+text",
            textposition="top center",
            textfont=dict(size=10, color="#111"),
            texttemplate="%{text}"
        )

    fig.update_layout(
        xaxis_title="Competência",
        yaxis_title="Nota de Produção",
        height=500,
        **(LAYOUT_CONFIG if 'LAYOUT_CONFIG' in globals() else {})
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
        height=650,
        width=900,
        xaxis_tickangle=-45,
        xaxis=dict(
            tickmode='array',
            tickvals=list(df_custo["competencia"]),
            ticktext=list(df_custo["competencia"].astype(str))
        ),
        legend=dict(        
        x=.97,         # mais à esquerda
        y=1.13,
        xanchor='left', # ancoragem à direita
        bgcolor='rgba(0,0,0,0)',  # fundo transparente (opcional)
        ),
        showlegend=True,
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
        legend=dict(        
        x=.91,         # mais à esquerda
        y=1.2,
        xanchor='left', # ancoragem à direita
        bgcolor='rgba(0,0,0,0)',  # fundo transparente (opcional)
        ),
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
    
    perc_exec_orcamento = (
        metricas["despesa_liquidada"] / metricas["despesa_prevista"] * 100 
        if metricas["despesa_prevista"] > 0 else 0
    )
    
    # Exibição dos cards
    col1, col2, col3, col4 = st.columns(4)
    cards_linha1 = [
        ("📥 Receita Prevista", f"R$ {metricas['receita_prevista']:,.0f}"),
        ("📤 Receita Realizada", f"R$ {metricas['receita_realizada']:,.0f}"),
        ("📊 Proposta Orçamentária", f"R$ {metricas['proposta']:,.0f}"),
        ("📈 Execução das Receitas Operacionais", f"{perc_exec_receita:.2f}%")
    ]
    
    for col, (titulo, valor) in zip([col1, col2, col3, col4], cards_linha1):
        with col:
            st.markdown(criar_card_html(titulo, valor), unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    col5, col6, col7 = st.columns(3)
    cards_linha2 = [
        ("💸 Despesa Prevista", f"R$ {metricas['despesa_prevista']:,.0f}"),
        ("💰 Despesa Liquidada", f"R$ {metricas['despesa_liquidada']:,.0f}"),
        ("📊 Execução Orçamentária" , f"{perc_exec_orcamento:.2f}%")
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
        height=650,
        width=900,
        xaxis_tickangle=-45,
        xaxis=dict(
            tickmode='array',
            tickvals=list(df_fluxo["competencia"]),
            ticktext=list(df_fluxo["competencia"].astype(str))
        ),
        legend=dict(        
        x=.97,         # mais à esquerda
        y=1.13,
        xanchor='left', # ancoragem à direita
        bgcolor='rgba(0,0,0,0)',  # fundo transparente (opcional)
        ),
        showlegend=True,
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
    
    cor_nota = "#588157" if nota is not None and nota >= 1 else "#8b8fa0"
    #st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    # Exibição dos cards
    col1, col2, col3 = st.columns(3)
    cards = [
        ("📘 Receita no Período", f"R$ {receita:,.0f}"),
        ("📙 Despesa no Período", f"R$ {despesa:,.0f}"),
        ("📈 Executado", f"{saldo:.2f}%" if saldo is not None else "-")
    ]
    

    cores = ["rgba(0, 48, 124, 0.7)", "rgba(0, 48, 124, 0.7)", cor_nota]
    #st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    for col, (titulo, valor), cor in zip([col1, col2, col3], cards, cores):
        with col:
            st.markdown(criar_card_html(titulo, valor, cor), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
