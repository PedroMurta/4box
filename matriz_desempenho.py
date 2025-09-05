import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from filtros import aplicar_sufixos_colunas

# Constantes globais (melhor performance)
CORES_TIPOLOGIA = {
    "A": "#0c64a3", "B": "#C55C44", "C": "#8fac1b",
    "CN": "#751094", "D": "#7627d6", "DN": "#574b63"
}

CORES_QUADRANTES = {
    "Alto X, Alto Y": "#13eb66",
    "Alto X, Baixo Y": "#ead377", 
    "Baixo X, Alto Y": "#a7cf30",
    "Baixo X, Baixo Y": "#e64937"
}

QUADRANTES_CONFIG = [
    (0.5, 1.0, 0.5, 1.0, "Alto X, Alto Y"),
    (0.5, 1.0, 0.0, 0.5, "Alto X, Baixo Y"),
    (0.0, 0.5, 0.5, 1.0, "Baixo X, Alto Y"),
    (0.0, 0.5, 0.0, 0.5, "Baixo X, Baixo Y"),
]

BORDAS_CONFIG = [
    {"type": "line", "x0": 0, "x1": 0, "y0": 0, "y1": 1, "line": {"color": "black", "width": 2}},
    {"type": "line", "x0": 1, "x1": 1, "y0": 0, "y1": 1, "line": {"color": "black", "width": 2}},
    {"type": "line", "x0": 0, "x1": 1, "y0": 0, "y1": 0, "line": {"color": "black", "width": 2}},
    {"type": "line", "x0": 0, "x1": 1, "y0": 1, "y1": 1, "line": {"color": "black", "width": 2}},
    {"type": "line", "x0": 0.5, "x1": 0.5, "y0": 0, "y1": 1, "line": {"color": "black", "width": 1}},
    {"type": "line", "x0": 0, "x1": 1, "y0": 0.5, "y1": 0.5, "line": {"color": "black", "width": 1}},
]

def colorir_nota_otimizado(valor):
    """Versão otimizada da função de coloração"""
    if pd.isna(valor):
        return f"<span style='color:#999999'>N/A</span>"
    
    cor_map = {
        (lambda x: x < 0.3): "#e64937",
        (lambda x: x < 0.5): "#e06666", 
        (lambda x: x < 0.75): "#d6d304", 
        (lambda x: x < 0.9): "#2cd147",
        (lambda x: x < 1): "#1071d2",
        (lambda x: True): "#0066cc"  # default
    }
    
    for condicao, cor in cor_map.items():
        if condicao(valor):
            return f"<span style='color:{cor}'>{valor:.2f}</span>"

def calcular_eixos_vetorizado(df, colunas_x, pesos_x, colunas_y, pesos_y):
    """Cálculo vetorizado dos eixos para melhor performance"""
    # Eixo X
    soma_ponderada_x = pd.Series(0, index=df.index, dtype=float)
    for col, peso in zip(colunas_x, pesos_x):
        if col in df.columns:
            soma_ponderada_x += df[col].fillna(0) * peso
    df["eixo_x"] = soma_ponderada_x / sum(pesos_x)
    
    # Eixo Y
    soma_ponderada_y = pd.Series(0, index=df.index, dtype=float)
    for col, peso in zip(colunas_y, pesos_y):
        if col in df.columns:
            soma_ponderada_y += df[col].fillna(0) * peso
    df["eixo_y"] = soma_ponderada_y / sum(pesos_y)
    
    return df

def preparar_dados_hover(df, colunas_x, colunas_y, nome_map):
    """Prepara dados de hover de forma otimizada"""
    custom_cols = ["hover_x", "hover_y", "idade_unidade"]
    
    # Hover para eixos principais
    df["hover_x"] = df["eixo_x"].fillna(0).apply(colorir_nota_otimizado)
    df["hover_y"] = df["eixo_y"].fillna(0).apply(colorir_nota_otimizado)
    
    # Hover para indicadores individuais
    for col in colunas_x + colunas_y:
        if col in df.columns:
            nova_col = f"hover_{col}"
            df[nova_col] = df[col].fillna(0).apply(colorir_nota_otimizado)
            custom_cols.append(nova_col)
    
    return df, custom_cols

def criar_template_hover(colunas_x, colunas_y, nome_map, font_size=18):
    """Cria template de hover com tamanho de fonte ajustável"""
    base_template = (
        f"<span style='font-size:{font_size}px'>"
        "<b>%{hovertext}</b><br><br>"
        "Índice Operação: %{customdata[0]}<br>"
        "Índice Estratégia: %{customdata[1]}<br><br>"
        "Idade da Unidade: %{customdata[2]} ano(s)<br><br>"
    )
    
    indicadores_template = ""
    for i, col in enumerate(colunas_x + colunas_y, start=3):
        if col in nome_map:
            nome = nome_map[col]
            indicadores_template += f"{nome}: %{{customdata[{i}]}}<br>"
    
    return base_template + indicadores_template + "</span><extra></extra>"

def adicionar_quadrantes(fig):
    """Adiciona quadrantes de forma otimizada"""
    for x0, x1, y0, y1, nome in QUADRANTES_CONFIG:
        # Adiciona retângulo
        fig.add_shape(
            type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
            fillcolor=CORES_QUADRANTES[nome], opacity=0.2,
            line=dict(width=0), layer="below"
        )
        
        # Adiciona anotação
        fig.add_annotation(
            x=(x0 + x1) / 2, y=(y0 + y1) / 2,
            text=f"<b>{nome}</b>", showarrow=False,
            font=dict(size=19, color="black"),
            xanchor="center", yanchor="middle"
        )

def adicionar_bordas(fig):
    """Adiciona bordas e linhas centrais"""
    for config in BORDAS_CONFIG:
        fig.add_shape(**config)

def filtrar_dados_principal(df, empresa_sel, competencia_sel, coluna_periodo):
    """Filtra dados principais de forma otimizada"""
    mask_empresa = df["empresa"] == empresa_sel
    
    if isinstance(competencia_sel, (list, tuple)):
        mask_periodo = df[coluna_periodo].isin(competencia_sel)
    else:
        mask_periodo = df[coluna_periodo] == competencia_sel
    
    return df[mask_empresa & mask_periodo].copy()

def grafico_fourbox(
    df, empresa_sel, competencia_sel, unidade_sel, coluna_periodo,
    colunas_x_base, pesos_x, colunas_y_base, pesos_y, nome_map, filtro_col
):
    """Função principal otimizada para criar o gráfico 4Box"""

    # Aplica sufixos corretos
    colunas_x = aplicar_sufixos_colunas(colunas_x_base, filtro_col)
    colunas_y = aplicar_sufixos_colunas(colunas_y_base, filtro_col)

    # Filtro principal otimizado
    df_filtro = filtrar_dados_principal(df, empresa_sel, competencia_sel, coluna_periodo)

    if df_filtro.empty:
        return px.scatter(title="Sem dados disponíveis")

    # Preparações iniciais
    df_filtro = calcular_eixos_vetorizado(df_filtro, colunas_x, pesos_x, colunas_y, pesos_y)
    df_filtro["destaque"] = df_filtro["unidade"] == unidade_sel if unidade_sel != "Todas" else False
    df_filtro["idade_unidade"] = pd.to_numeric(df_filtro.get("idade_unidade", 10), errors="coerce").fillna(10)

    # Prepara dados de hover
    df_filtro, custom_cols = preparar_dados_hover(df_filtro, colunas_x, colunas_y, nome_map)

    # Nomes legíveis para rodapé
    # Nomes legíveis para rodapé (geração automática)
    BASE_LABELS = {
        'nota_orcamento': 'Orçamento',
        'nota_caixa': 'Equilíbrio Financeiro',
        'nota_nps': 'NPS',
        'nota_receita_operacional': 'Receita Operacional',
        'nota_custo': 'Custo',
        'nota_producao': 'Produção',
    }

    nomes_legiveis = {}
    for base, label in BASE_LABELS.items():
        for suf in ("", "_anual", "_trimestral", "_semestral", "_mensal"):
            nomes_legiveis[f"{base}{suf}"] = label
            if suf:  # também cobre *_padronizada
                nomes_legiveis[f"{base}{suf}_padronizada"] = label

    # Rodapé
    texto_eixo_x = ", ".join(nomes_legiveis.get(v, v) for v, p in zip(colunas_x, pesos_x))
    texto_eixo_y = ", ".join(nomes_legiveis.get(v, v) for v, p in zip(colunas_y, pesos_y))


    # Gráfico
    fig = px.scatter(
        df_filtro,
        x="eixo_x", y="eixo_y",
        color="tipologia",
        size="idade_unidade",
        size_max=30,
        hover_name="unidade",
        custom_data=custom_cols,
        labels={"eixo_x": f"Operação - ({texto_eixo_x})", "eixo_y": f"Estratégia - ({texto_eixo_y})"},
        color_discrete_map=CORES_TIPOLOGIA,
        category_orders={"tipologia": sorted(df_filtro["tipologia"].dropna().unique())},
        title=f"Matriz Desempenho – {empresa_sel} ({coluna_periodo}: {competencia_sel})"
    )

    # Template de hover
    hover_template = criar_template_hover(colunas_x, colunas_y, nome_map)
    fig.update_traces(
        hovertemplate=hover_template,
        marker=dict(
            line=dict(width=2, color='rgba(11, 63, 66, 0.3)'),
            opacity=0.8
        )
    )

    # Adiciona quadrantes e bordas
    adicionar_quadrantes(fig)
    adicionar_bordas(fig)

    # Layout
    fig.update_layout(
        height=900, width=900,
        paper_bgcolor='#F3F3F3', plot_bgcolor='#F3F3F3',
        xaxis=dict(
            range=[0, 1],
            tickvals=[],
            showticklabels=False,
            title_font=dict(size=16)
        ),
        yaxis=dict(
            range=[0, 1],
            tickvals=[],
            showticklabels=False,
            title_font=dict(size=16)
        ),
        legend=dict(
            title="Tipologia",
            title_font=dict(size=14),
            font=dict(size=14),
            x=-0.02,
            y=1.0,
            xanchor='right',
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True,
        margin=dict(t=70, b=70, l=70, r=70)
    )

    # Rodapé explicativo
    fig.add_annotation(
        text=f"<b>Eixo X:</b> {texto_eixo_x}<br><b>Eixo Y:</b> {texto_eixo_y}",
        xref="paper", yref="paper", x=0, y=-0.25,
        showarrow=False, align="left",
        font=dict(size=18, color="gray")
    )

    return fig
