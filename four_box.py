import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Paletas de cores
cores_tipologia = {
    "A": "#0c64a3", "B": "#C55C44", "C": "#8fac1b",
    "CN": "#751094", "D": "#7627d6", "DN": "#574b63"
}

cores_quadrantes = {
    "Alto X, Alto Y": "#13eb66",
    "Alto X, Baixo Y": "#ead377",
    "Baixo X, Alto Y": "#a7cf30",
    "Baixo X, Baixo Y": "#e64937"
}

# Função para aplicar cor no hover
def colorir_nota(valor):
    if valor < 0:
        return f"<span style='color:#e64937'>{valor:.2f}</span>"
    elif valor < 0.7:
        return f"<span style='color:#ff9999'>{valor:.2f}</span>"
    elif valor < 1:
        return f"<span style='color:#a7cf30'>{valor:.2f}</span>"
    elif valor < 1.2:
        return f"<span style='color:#13eb66'>{valor:.2f}</span>"
    else:
        return f"<span style='color:#0066cc'>{valor:.2f}</span>"

def grafico_fourbox(
    df, empresa_sel, competencia_sel, unidade_sel, coluna_periodo,
    colunas_x, pesos_x, colunas_y, pesos_y, nome_map
):
    # Filtro principal
    if isinstance(competencia_sel, (list, tuple)):
        df_filtro = df[
            (df["empresa"] == empresa_sel) &
            (df[coluna_periodo].isin(competencia_sel))
        ].copy()
    else:
        df_filtro = df[
            (df["empresa"] == empresa_sel) &
            (df[coluna_periodo] == competencia_sel)
        ].copy()

    if df_filtro.empty:
        return px.scatter(title="Sem dados disponíveis")

    # Cálculo dos eixos com pesos
    df_filtro["eixo_x"] = sum(df_filtro[var] * peso for var, peso in zip(colunas_x, pesos_x)) / sum(pesos_x)
    df_filtro["eixo_y"] = sum(df_filtro[var] * peso for var, peso in zip(colunas_y, pesos_y)) / sum(pesos_y)
    df_filtro["destaque"] = df_filtro["unidade"] == unidade_sel if unidade_sel != "Todas" else False

    # Tamanho proporcional à idade_unidade
    if "idade_unidade" in df_filtro.columns:
        df_filtro["idade_unidade"] = pd.to_numeric(df_filtro["idade_unidade"], errors="coerce")
        tamanho_ativo = "idade_unidade"
    else:
        df_filtro[tamanho_ativo := "tamanho_padrao"] = 10

    # Aplica formatação e cor para todos os indicadores
    custom_cols = ["hover_x", "hover_y"]
    for col in colunas_x + colunas_y:
        nova_col = f"hover_{col}"
        df_filtro[nova_col] = df_filtro[col].apply(colorir_nota)
        custom_cols.append(nova_col)

    df_filtro["hover_x"] = df_filtro["eixo_x"].apply(colorir_nota)
    df_filtro["hover_y"] = df_filtro["eixo_y"].apply(colorir_nota)


    # 2. Monta o gráfico com essas colunas
    fig = px.scatter(
        df_filtro,
        x="eixo_x",
        y="eixo_y",
        color="tipologia",
        size=tamanho_ativo,
        size_max=47,
        hover_name="unidade",
        custom_data=custom_cols,
        labels={"eixo_x": "Eixo X", "eixo_y": "Eixo Y"},
        color_discrete_map=cores_tipologia,
        title=f"Gráfico 4Box – {empresa_sel} ({coluna_periodo}: {competencia_sel})"
    )

    # 3. Cria template com os nomes das variáveis
    indicadores_template = ""
    for i, col in enumerate(colunas_x + colunas_y, start=2):
        nome = nome_map.get(col, col)
        indicadores_template += f"{nome}: %{{customdata[{i}]}}<br>"

        # 4. Aplica o template final
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                    "Nota Eixo X: %{customdata[0]}<br>" +
                    "Nota Eixo Y: %{customdata[1]}<br>" +
                    indicadores_template +
                    "<extra></extra>"
)
    # Quadrantes
    quadrantes = [
        (1, 2, 1, 2, "Alto X, Alto Y"),
        (1, 2, 0, 1, "Alto X, Baixo Y"),
        (0, 1, 1, 2, "Baixo X, Alto Y"),
        (0, 1, 0, 1, "Baixo X, Baixo Y"),
    ]
    for x0, x1, y0, y1, nome in quadrantes:
        fig.add_shape(
            type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
            fillcolor=cores_quadrantes[nome], opacity=0.2,
            line=dict(width=0), layer="below"
        )
        fig.add_annotation(
            x=(x0 + x1) / 2, y=(y0 + y1) / 2,
            text=f"<b>{nome}</b>", showarrow=False,
            font=dict(size=14, color="black"),
            xanchor="center", yanchor="middle"
        )

    # Bordas e linhas centrais
    fig.add_shape(type="line", x0=0, x1=0, y0=0, y1=2, line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=2, x1=2, y0=0, y1=2, line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=0, x1=2, y0=0, y1=0, line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=0, x1=2, y0=2, y1=2, line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=1, x1=1, y0=0, y1=2, line=dict(color="black", width=1))
    fig.add_shape(type="line", x0=0, x1=2, y0=1, y1=1, line=dict(color="black", width=1))

    # Ponto ideal
    fig.add_trace(go.Scatter(
        x=[1], y=[1],
        mode='markers+text',
        marker=dict(size=27, color="blue", symbol="star"),
        text=["IDEAL"],
        textposition="top center",
        showlegend=False
    ))

    # Layout final
    fig.update_layout(
        height=800,
        paper_bgcolor='ghostwhite',
        plot_bgcolor='ghostwhite',
        xaxis=dict(range=[0, 2], tickvals=[], showticklabels=False),
        yaxis=dict(range=[0, 2], tickvals=[], showticklabels=False),
        legend_title="Tipologia",
        showlegend=True,
        margin=dict(t=100, b=100),
    )

    # Anotação explicativa
    fig.add_annotation(
        text=(f"<b>Eixo X:</b> " + ", ".join([f"{nome_map[v]} (peso {p})" for v, p in zip(colunas_x, pesos_x)]) +
              "<br><b>Eixo Y:</b> " + ", ".join([f"{nome_map[v]} (peso {p})" for v, p in zip(colunas_y, pesos_y)])),
        xref="paper", yref="paper",
        x=0, y=-0.25,
        showarrow=False,
        align="left",
        font=dict(size=12, color="gray"),
    )

    return fig
