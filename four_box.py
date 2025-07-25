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

def grafico_fourbox(
    df, empresa_sel, competencia_sel, unidade_sel, coluna_periodo,
    colunas_x, pesos_x, colunas_y, pesos_y, nome_map
):
    # Filtro principal
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

   # ✅ Tamanho proporcional à idade_unidade, se disponível
    #if "idade_unidade" in df_filtro.columns:
    #    df_filtro["idade_unidade"] = pd.to_numeric(df_filtro["idade_unidade"], errors="coerce")
    #    idade = df_filtro["idade_unidade"].fillna(1)

        # Normaliza a idade entre 10 e 50 para melhorar contraste visual
    #    idade_norm = (idade - idade.min()) / (idade.max() - idade.min())
    #    tamanhos = 10 + idade_norm * 40  # mapeia para [10, 50]
    #else:
    #    tamanhos = np.repeat(15, len(df_filtro))

    # Gráfico de dispersão
    fig = px.scatter(
        df_filtro,
        x="eixo_x",
        y="eixo_y",
        color="tipologia",
        size='idade_unidade',
        size_max=47,  # controla o tamanho máximo da bolha
        hover_name="unidade",
        hover_data={var: ':.2f' for var in colunas_x + colunas_y},
        labels={"eixo_x": "Eixo X", "eixo_y": "Eixo Y"},
        color_discrete_map=cores_tipologia,
        title=f"Gráfico 4Box – {empresa_sel} ({competencia_sel})"
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

    # Linhas centrais
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

    # Anotação de referência
    fig.add_annotation(
        x=2, y=2,
        text="Melhor Resultado",
        showarrow=True,
        arrowhead=2, ax=40, ay=-40,
        font=dict(color="blue")
    )

    # Layout final
    fig.update_layout(
        height=800,
        paper_bgcolor='ghostwhite',
        plot_bgcolor='ghostwhite',
        xaxis=dict(range=[0, 2], tickvals=[], showticklabels=False),
        yaxis=dict(range=[0, 2], tickvals=[], showticklabels=False),
        legend_title="Tipologia",
        showlegend=True
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
