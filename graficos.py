import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import numpy as np

# Cores dos quadrantes
cores_quadrantes = {
    "Resultado com Risco": "#f5b7b1",
    "Potenciais de Excelência": "#f9e79f",
    "Unidades Referência": "#abebc6",
    "Unidade em Risco Gerencial": "#f1948a",
    "Zona de Ajuste": "#fcf3cf",
    "Base Produtiva Consistente": "#a9dfbf",
    "Crítico Total": "#ec7063",
    "Baixo Desempenho Geral": "#f7dc6f",
    "Potência Operacional Sem Direção Estratégica": "#82e0aa"
}

# ==============================
# ========= NineBox ============
# ==============================
def grafico_ninebox(
    df,
    empresa_sel,
    competencia_sel,
    unidade_sel,
    coluna_periodo,
    colunas_x,
    pesos_x,
    colunas_y,
    pesos_y,
    nome_map
):
    df_filtro = df[
        (df["empresa"] == empresa_sel) &
        (df[coluna_periodo] == competencia_sel)
    ].copy()

    if df_filtro.empty:
        st.warning("Sem dados para os filtros selecionados.")
        return px.scatter()

    # Cálculo dos eixos com pesos
    df_filtro["eixo_x"] = sum(df_filtro[var] * peso for var, peso in zip(colunas_x, pesos_x))
    df_filtro["eixo_y"] = sum(df_filtro[var] * peso for var, peso in zip(colunas_y, pesos_y))
    df_filtro["destaque"] = df_filtro["unidade"] == unidade_sel if unidade_sel != "Todas" else False

    # Tamanho da bolha com base na idade
    if "idade_unidade" in df_filtro.columns:
        idade = pd.to_numeric(df_filtro["idade_unidade"], errors="coerce").fillna(1)
        tamanhos = np.interp(idade, (idade.min(), idade.max()), (10, 50))
    else:
        tamanhos = np.repeat(15, len(df_filtro))

    # Paleta de cores
    cores_tipologia = {
        "A": "#0c64a3", "B": "#7E220D", "C": "#8fac1b",
        "CN": "#109410", "D": "#7627d6", "DN": "#574b63"
    }

    cores_quadrantes = {
        "1": "#ec7063", "2": "#f1948a", "3": "#f5b7b1",
        "4": "#f7dc6f", "5": "#fcf3cf", "6": "#f9e79f",
        "7": "#82e0aa", "8": "#a9dfbf", "9": "#abebc6"
    }

    fig = px.scatter(
        df_filtro,
        x="eixo_x",
        y="eixo_y",
        color="tipologia",
        size=tamanhos,
        size_max=45,
        hover_name="unidade",
        hover_data={var: ':.2f' for var in set(colunas_x + colunas_y)} | {"eixo_x": ':.2f', "eixo_y": ':.2f'},
        labels={"eixo_x": "Operação", "eixo_y": "Estratégia"},
        color_discrete_map=cores_tipologia,
        title=f"Gráfico 9Box – {empresa_sel} ({competencia_sel})"
    )

    # Desenhar quadrantes
    for row, (y0, y1) in enumerate([(10, 15), (5, 10), (0, 5)]):       # linha 1 = topo
        for col, (x0, x1) in enumerate([(0, 5), (5, 10), (10, 15)]):   # col 1 = esquerda
            numero = str((2 - row) + col * 3 + 1)  # Nova fórmula correta
            fig.add_shape(
                type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                fillcolor=cores_quadrantes.get(numero, "#ccc"), opacity=0.25,
                line=dict(width=0), layer="below"
            )
            fig.add_annotation(
                x=(x0 + x1) / 2, y=(y0 + y1) / 2,
                text=f"<b>{numero}</b>", showarrow=False,
                font=dict(size=16), xanchor="center", yanchor="middle"
            )


    # Linhas de grade
    for x in [0, 5, 10, 15]:
        fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=15, line=dict(color="black", width=1))
    for y in [0, 5, 10, 15]:
        fig.add_shape(type="line", x0=0, x1=15, y0=y, y1=y, line=dict(color="black", width=1))

    # Legendas dos eixos
    fig.add_annotation(text="Alta Estratégia", x=-0.3, y=13, showarrow=False, font=dict(size=12), xanchor="right")
    fig.add_annotation(text="Média Estratégia", x=-0.3, y=8, showarrow=False, font=dict(size=12), xanchor="right")
    fig.add_annotation(text="Baixa Estratégia", x=-0.3, y=3, showarrow=False, font=dict(size=12), xanchor="right")

    fig.add_annotation(text="Baixa Eficiência", x=3, y=-0.3, showarrow=False, font=dict(size=12), yanchor="top")
    fig.add_annotation(text="Média Eficiência", x=8, y=-0.3, showarrow=False, font=dict(size=12), yanchor="top")
    fig.add_annotation(text="Alta Eficiência", x=13, y=-0.3, showarrow=False, font=dict(size=12), yanchor="top")

    # Layout
    fig.update_layout(
        height=900,
        paper_bgcolor='ghostwhite',
        plot_bgcolor='ghostwhite',
        xaxis=dict(range=[0, 15], tickvals=[], showticklabels=False),
        yaxis=dict(range=[0, 15], tickvals=[], showticklabels=False),
        legend_title="Tipologia",
        showlegend=True
    )

    # Anotação explicativa dos eixos
    fig.add_annotation(
        text=(f"<b>Eixo X:</b> " + ", ".join([f"{nome_map[v]} (peso {p})" for v, p in zip(colunas_x, pesos_x)]) +
              "<br><b>Eixo Y:</b> " + ", ".join([f"{nome_map[v]} (peso {p})" for v, p in zip(colunas_y, pesos_y)])),
        xref="paper", yref="paper",
        x=0, y=-0.2,
        showarrow=False,
        align="left",
        font=dict(size=12, color="black"),
    )

    return fig
# ==============================
# ========= DataFrame ==========
# ==============================

def pagina_indicadores(df_empresa, empresa_sel, unidade_sel, competencia_sel, coluna_periodo):
    st.subheader("📊 Indicadores em Desenvolvimento")
    st.write("Visualize os indicadores detalhados por unidade, empresa e período.")

    df_empresa = df_empresa[df_empresa["empresa"] == empresa_sel].copy()

    todas_colunas = df_empresa.columns.tolist()
    colunas_nota_comp = [
        col for col in todas_colunas
        if col.startswith("nota_") and not col.endswith("_trimestral") and not col.endswith("_semestral") and not col.endswith("_anual")
    ]
    colunas_nota_trim = [col for col in todas_colunas if col.endswith("_trimestral")]
    colunas_nota_sem = [col for col in todas_colunas if col.endswith("_semestral")]

    colunas_agregadas = colunas_nota_comp + colunas_nota_trim + colunas_nota_sem

    # === ✅ Notas agregadas no período selecionado (dinâmica)
    df_periodo = df_empresa[df_empresa[coluna_periodo] == competencia_sel].copy()
    df_periodo_agg = df_periodo.groupby(["empresa", "unidade", coluna_periodo], as_index=False)[colunas_agregadas].mean()

    df_periodo_view = df_periodo_agg.query("empresa == @empresa_sel")
    if unidade_sel != "Todas":
        df_periodo_view = df_periodo_view.query("unidade == @unidade_sel")

    st.markdown("#### ✅ Notas agregadas no período selecionado")
    st.dataframe(df_periodo_view)

    # === 📅 Notas por competência (estática)
    df_comp = df_empresa.copy()
    if unidade_sel != "Todas":
        df_comp = df_comp[df_comp["unidade"] == unidade_sel]

    st.markdown("#### 📅 Notas por competência")
    st.dataframe(df_comp[["empresa", "unidade", "competencia", "ano"] + colunas_nota_comp])

    # === 🗓️ Notas por trimestre (estática)
    df_trim = df_empresa.copy()
    if unidade_sel != "Todas":
        df_trim = df_trim[df_trim["unidade"] == unidade_sel]
    df_trim[colunas_nota_trim] = df_trim[colunas_nota_trim].apply(pd.to_numeric, errors='coerce')

    df_trim_agg = (
        df_trim.groupby(["empresa", "unidade", "ano_trimestre"], as_index=False)[colunas_nota_trim]
        .mean()
        .rename(columns={"ano_trimestre": "trimestre"})
    )

    df_trim_view = df_trim_agg.query("empresa == @empresa_sel")
    if unidade_sel != "Todas":
        df_trim_view = df_trim_view.query("unidade == @unidade_sel")

    st.markdown("#### 🗓️ Notas por trimestre")
    st.dataframe(df_trim_view[["trimestre", "empresa", "unidade"] + colunas_nota_trim])

    # === 📆 Notas por semestre (estática)
    df_sem = df_empresa.copy()
    if unidade_sel != "Todas":
        df_sem = df_sem[df_sem["unidade"] == unidade_sel]
    df_sem[colunas_nota_sem] = df_sem[colunas_nota_sem].apply(pd.to_numeric, errors='coerce')

    df_sem_agg = (
        df_sem.groupby(["empresa", "unidade", "ano_semestre"], as_index=False)[colunas_nota_sem]
        .mean()
        .rename(columns={"ano_semestre": "semestre"})
    )

    df_sem_view = df_sem_agg.query("empresa == @empresa_sel")
    if unidade_sel != "Todas":
        df_sem_view = df_sem_view.query("unidade == @unidade_sel")

    st.markdown("#### 📆 Notas por semestre")
    st.dataframe(df_sem_view[[ "semestre", "empresa", "unidade"] + colunas_nota_sem])




#==============================
#========== Produção ==========
#==============================
def grafico_nota_producao_series(df, empresa_sel, unidade_sel):
    df_filtrado = df[df["empresa"] == empresa_sel].copy()
    
    if unidade_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["unidade"] == unidade_sel]

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
        height=500
    )

    return fig


# ==============================
# ========= Custo/Meta =========
# ==============================
def grafico_custo_realizado_vs_meta(df, empresa_sel, unidade_sel, competencia_sel):
    df_filtrado = df[df["empresa"] == empresa_sel].copy()

    if unidade_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["unidade"] == unidade_sel]

    # Garante todas as competências
    todas_competencias = pd.DataFrame(sorted(df["competencia"].unique()), columns=["competencia"])

    # Agrupa os dados
    df_custo = df_filtrado.groupby("competencia", as_index=False)[
        ["soma_custo_realizado", "soma_meta"]
    ].sum()

    # Garante que todas as competências estejam presentes
    df_custo = todas_competencias.merge(df_custo, on="competencia", how="left").fillna(0)

    # Adiciona colunas auxiliares
    df_custo["cor_realizado"] = df_custo.apply(
        lambda row: "#b04c52" if row["soma_custo_realizado"] > row["soma_meta"] else "#588157", axis=1
    )

    fig = go.Figure()

    # Barras "Realizado" (com destaque se ultrapassar)
    fig.add_trace(go.Bar(
        x=df_custo["competencia"],
        y=df_custo["soma_custo_realizado"],
        name="Realizado",
        marker_color=df_custo["cor_realizado"],
        text=df_custo["soma_custo_realizado"].round(2).astype(str),
        textposition="inside"
    ))

    # Barras "Meta"
    fig.add_trace(go.Bar(
        x=df_custo["competencia"],
        y=df_custo["soma_meta"],
        name="Meta",
        marker_color="#81a4cd",
        text=df_custo["soma_meta"].round(2).astype(str),
        textposition="inside"
    ))

    # Layout
    fig.update_layout(
    title=f"{empresa_sel}" +
          (f" – {unidade_sel}" if unidade_sel != "Todas" else "") +
          f"<br><br>Competência: {competencia_sel}",
    xaxis_title="Competência",
    yaxis_title="Valor (R$)",
    barmode="group",
    height=550,
    legend_title="",
    xaxis_tickangle=-45
)


    return fig


# ==============================
# ========= Custo/Meta =========
# ==============================
def card_personalizado(titulo, valor, cor_fundo="#f5f5f5", cor_borda="#CCCCCC"):
    st.markdown(
        f"""
        <div style='border: 2px solid {cor_borda}; border-radius: 10px; padding: 15px;
                    background-color: {cor_fundo}; text-align: center; margin: 5px;'>
            <div style='font-size: 16px; font-weight: bold;'>{titulo}</div>
            <div style='font-size: 22px; margin-top: 5px;'>{valor}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def grafico_pizza_receita(receita_prevista, receita_realizada):
    if receita_prevista == 0:
        return go.Figure()

    perc_exec = receita_realizada / receita_prevista * 100

    if perc_exec <= 100:
        labels = ["Executado", "A executar"]
        values = [perc_exec, 100 - perc_exec]
        colors = ["#d67327", "#3f4f6b"]
    else:
        labels = ["Executado (100%)", f"Excedente ({perc_exec - 100:.0f}%)"]
        values = [100, perc_exec - 100]
        colors = ["#d67327", "#bc4b51"]  # laranja + vermelho p/ excesso

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textinfo='label+percent',
        insidetextorientation='radial'
    )])

    fig.update_layout(
        #title_text="Execução da Receita Prevista",  # ou "Execução da Despesa Prevista"
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=40, b=80, l=0, r=0),
        height=420
    )

    return fig

def grafico_pizza_despesa(despesa_prevista, despesa_liquidada):
    if despesa_prevista == 0:
        return go.Figure()

    perc_exec = despesa_liquidada / despesa_prevista * 100

    if perc_exec <= 100:
        labels = ["Liquidado", "A liquidar"]
        values = [perc_exec, 100 - perc_exec]
        colors = ["#118ab2", "#3f4f6b"]
    else:
        labels = ["Liquidado (100%)", f"Excedente ({perc_exec - 100:.0f}%)"]
        values = [100, perc_exec - 100]
        colors = ["#118ab2", "#ef476f"]  # azul + vermelho p/ excesso

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textinfo='label+percent',
        insidetextorientation='radial'
    )])

    fig.update_layout(
        #title_text="Execução da Despesa Prevista",  # ou "Execução da Despesa Prevista"
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=40, b=80, l=0, r=0),
        height=420
    )

    return fig

# ==============================
# ========= Orçamento ==========
# ==============================
def exibir_cards_orcamentarios(df, empresa_sel, unidade_sel, competencia_sel, coluna_periodo):
    df_filtrado = df[df["empresa"] == empresa_sel].copy()

    if unidade_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["unidade"] == unidade_sel]

    # Filtro por período (ano, semestre ou competência)
    df_filtrado = df_filtrado[df_filtrado[coluna_periodo] == competencia_sel]

    # Conversão segura das colunas
    colunas_valores = [
        "receita_prevista", "receita_realizada",
        "despesa_prevista", "despesa_liquidada",
        "proposta", "execucao_orcamentaria"
    ]

    for col in colunas_valores:
        df_filtrado[col] = pd.to_numeric(
            df_filtrado[col].astype(str)
            .str.replace(r"[^\d,.-]", "", regex=True)
            .str.replace(",", "."),
            errors="coerce"
        ).fillna(0)

    # Agregações
    receita_prevista = df_filtrado["receita_prevista"].sum()
    receita_realizada = df_filtrado["receita_realizada"].sum()
    despesa_prevista = df_filtrado["despesa_prevista"].sum()
    despesa_liquidada = df_filtrado["despesa_liquidada"].sum()
    proposta = df_filtrado["proposta"].sum()
    execucao_orcamentaria = df_filtrado["execucao_orcamentaria"].mean()

    perc_exec_receita = (receita_realizada / receita_prevista * 100) if receita_prevista > 0 else 0

    # Estilo dos cards
    def card_html(titulo, valor, cor="#3f4f6b"):
        return f"""
        <div style="border: 2px solid #ccc; border-radius: 12px; padding: 10px; margin: 5px;
                    background-color: {cor}; text-align: center; color: white;">
            <div style="font-size: 16px; font-weight: bold;">{titulo}</div>
            <div style="font-size: 20px; margin-top: 5px;">{valor}</div>
        </div>
        """

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(card_html("📥 Receita Prevista", f"R$ {receita_prevista:,.0f}"), unsafe_allow_html=True)
    with col2:
        st.markdown(card_html("📤 Receita Realizada", f"R$ {receita_realizada:,.0f}"), unsafe_allow_html=True)
    with col3:
        st.markdown(card_html("📊 Proposta Orçamentária", f"R$ {proposta:,.0f}"), unsafe_allow_html=True)        
    with col4:
        st.markdown(card_html("📈 Execução das Receitas", f"{perc_exec_receita:.2f}%"), unsafe_allow_html=True)

    col5, col6, col7 = st.columns(3)
    with col5:
        st.markdown(card_html("💸 Despesa Prevista", f"R$ {despesa_prevista:,.0f}"), unsafe_allow_html=True)
    with col6:
        st.markdown(card_html("💰 Despesa Liquidada", f"R$ {despesa_liquidada:,.0f}"), unsafe_allow_html=True)
    with col7:
        st.markdown(card_html("📊 Execução Orçamentária", f"{execucao_orcamentaria:,.2f}%"), unsafe_allow_html=True)

   
        # Gráficos de pizza lado a lado com estilo aprimorado
        # Donuts com fundo personalizado estilo especialidades
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        percentual = receita_realizada / receita_prevista * 100 if receita_prevista else 0
        cor_borda = "#000000" if percentual < 100 else "#2a9d8f"
        cor_fundo = "#dcefee"  # azul claro suave

        st.markdown(f"""
        <div style='
            background-color: {cor_fundo};
            padding: 10px 15px;
            border: 3px solid {cor_borda};
            border-radius: 12px;
            text-align: center;
        '>
            <h5 style='margin-bottom: 0;'>Execução Receita</h5>
            
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(grafico_pizza_receita(receita_prevista, receita_realizada), use_container_width=True)

    with col2:
        percentual = despesa_liquidada / despesa_prevista * 100 if despesa_prevista else 0
        cor_borda = "#010000" if percentual < 100 else "#2a9d8f"
        cor_fundo = "#dcefee"

        st.markdown(f"""
        <div style='
            background-color: {cor_fundo};
            padding: 10px 15px;
            border: 3px solid {cor_borda};
            border-radius: 12px;
            text-align: center;
        '>
            <h5 style='margin-bottom: 0;'>Execução Orçamentária</h5>
           
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(grafico_pizza_despesa(despesa_prevista, despesa_liquidada), use_container_width=True)




