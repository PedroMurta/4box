import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ===== CONSTANTES =====
ESPECIALIDADES = [
    "Odontologia", "Fisioterapia", "Psicologia", "Nutrição", 
    "Palestra SEST", "ELC", "Curso Presencial", "Curso EAD", "Palestra SENAT"
]

# Mapeamento para compatibilidade com colunas do DataFrame
MAPA_COLUNAS = {
    "Odontologia": "odonto",
    "Fisioterapia": "fisio", 
    "Psicologia": "psico",
    "Nutrição": "nutri",
    "Palestra SEST": "pale_sest",
    "ELC": "elc",
    "Curso Presencial": "curso_prese",
    "Curso EAD": "curso_ead",
    "Palestra SENAT": "pale_senat"
}

CORES_PERFORMANCE = {
    "bom": "#588157",
    "ruim": "#b04c52", 
    "donut_bom": "#588157",
    "donut_ruim": "#b04c52",
    "neutro": "#1e1e1e"
}

CONFIGURACAO_DONUT = {
    "margin": dict(t=10, b=10, l=10, r=10),
    "width": 250,
    "height": 250,
    "paper_bgcolor": "#c9dddb",
    "plot_bgcolor": "#a5b8bd"
}

# ===== FUNÇÕES UTILITÁRIAS =====
@st.cache_data
def processar_dados_temporais_especialidades(df):
    """Processa dados temporais com cache"""
    df = df.copy()
    df["ano"] = df["competencia"].str[:4]
    df["mes"] = df["competencia"].str[5:7].astype(int)
    df["semestre"] = (df["mes"] > 6).astype(int) + 1
    df["trimestre_mes"] = ((df["mes"] - 1) // 3 + 1).astype(str)
    df["trimestre"] = df["ano"] + "-" + df["trimestre_mes"]
    df["ano_semestre"] = df["ano"] + "-" + df["semestre"].astype(str)
    return df

def calcular_metricas_especialidade(linha, especialidade_nome):
    """Calcula métricas para uma especialidade específica"""
    especialidade_col = MAPA_COLUNAS[especialidade_nome]
    
    valor_real = int(linha.get(especialidade_col, 0))
    valor_meta = int(linha.get(f"meta_{especialidade_col}", 0))
    delta = valor_real - valor_meta
    
    simbolo = "↑" if delta >= 0 else "↓"
    cor = CORES_PERFORMANCE["bom"] if delta >= 0 else CORES_PERFORMANCE["ruim"]
    texto_delta = f"<span style='color:{cor}; font-size:16px;'>{simbolo} {abs(delta):,}".replace(",", ".") + "</span>"
    
    valor_pct = linha.get(f"pct_{especialidade_col}")
    try:
        valor_pct = float(valor_pct) if valor_pct is not None else None
    except (ValueError, TypeError):
        valor_pct = None
    
    return {
        'valor_real': valor_real,
        'valor_meta': valor_meta,
        'delta': delta,
        'texto_delta': texto_delta,
        'valor_pct': valor_pct,
        'cor_borda': cor
    }

def criar_donut_chart(valor_pct):
    """Cria gráfico donut otimizado"""
    if valor_pct is None:
        return None
    
    valor_plotado = min(valor_pct, 100)
    cor_donut = CORES_PERFORMANCE["donut_bom"] if valor_pct >= 100 else CORES_PERFORMANCE["donut_ruim"]
    
    fig = go.Figure(go.Pie(
        values=[valor_plotado, 100 - valor_plotado],
        hole=0.65,
        marker=dict(
            colors=[cor_donut, CORES_PERFORMANCE["neutro"]],
            line=dict(color="black", width=2)
        ),
        textinfo='none',
        showlegend=False
    ))
    
    fig.update_layout(
        **CONFIGURACAO_DONUT,
        annotations=[dict(
            text=f"{valor_pct:.0f}%",
            x=0.5, y=0.5,
            font_size=24,
            showarrow=False,
            font_color=cor_donut
        )]
    )
    
    return fig

def agregar_dados_periodo(df_unidade):
    """Agrega dados quando há múltiplas linhas para o mesmo período"""
    if len(df_unidade) <= 1:
        return df_unidade.iloc[0] if len(df_unidade) == 1 else {}
    
    # Especialidades por empresa
    ESPECIALIDADES_SEST = ["odonto", "fisio", "psico", "nutri", "pale_sest", "elc"]
    ESPECIALIDADES_SENAT = ["curso_prese", "curso_ead", "pale_senat"]
    
    agregados = {}
    
    # Processar especialidades SEST
    df_sest = df_unidade[df_unidade['empresa'] == 'SEST'] if 'empresa' in df_unidade.columns else df_unidade
    for esp_col in ESPECIALIDADES_SEST:
        if not df_sest.empty:
            valor_total = df_sest[esp_col].sum()
            meta_total = df_sest[f"meta_{esp_col}"].sum()
        else:
            valor_total = meta_total = 0
        
        agregados[esp_col] = valor_total
        agregados[f"meta_{esp_col}"] = meta_total
        agregados[f"pct_{esp_col}"] = (100 * valor_total / meta_total if meta_total > 0 else 0)
    
    # Processar especialidades SENAT
    df_senat = df_unidade[df_unidade['empresa'] == 'SENAT'] if 'empresa' in df_unidade.columns else df_unidade
    for esp_col in ESPECIALIDADES_SENAT:
        if not df_senat.empty:
            valor_total = df_senat[esp_col].sum()
            meta_total = df_senat[f"meta_{esp_col}"].sum()
        else:
            valor_total = meta_total = 0
        
        agregados[esp_col] = valor_total
        agregados[f"meta_{esp_col}"] = meta_total
        agregados[f"pct_{esp_col}"] = (100 * valor_total / meta_total if meta_total > 0 else 0)
    
    return agregados

def criar_card_especialidade(especialidade_nome, metricas, indice):
    """Cria card HTML para uma especialidade"""
    return f"""
    <div style="border: 3px solid {metricas['cor_borda']}; border-radius: 12px; padding: 10px; 
                text-align: center; background-color: rgb(63, 79, 107); color: #C9D6DF;">
        <div style="font-weight: bold; font-size: 22px;">{especialidade_nome.upper()}</div>
        <div style="font-size: 19px; margin: 5px 0;">
            <i>Realizado: <b>{metricas['valor_real']:,}</b></i> <br> 
            Meta: {metricas['valor_meta']:,}
        </div>
        <div style="margin-bottom: 10px;">{metricas['texto_delta']}</div>
    """

# ===== FUNÇÃO PRINCIPAL =====
def exibir_metricas_com_donut(df, unidade_sel, coluna_periodo, valor_periodo):
    """
    Exibe métricas das especialidades com gráficos donut de forma otimizada
    
    Args:
        df: DataFrame com os dados
        unidade_sel: Unidade selecionada
        coluna_periodo: Coluna que representa o período (competencia, trimestre, etc.)
        valor_periodo: Valor do período selecionado
    """
    
    # Processamento temporal com cache
    df = processar_dados_temporais_especialidades(df)
    
    # Filtro principal otimizado
    mask = (df["unidade"] == unidade_sel) & (df[coluna_periodo] == valor_periodo)
    df_unidade = df[mask].copy()
    
    if df_unidade.empty:
        st.warning("Unidade não encontrada para o período selecionado.")
        return
    
    # Agregação de dados se necessário
    linha = agregar_dados_periodo(df_unidade)
    
    # Criação das colunas para layout responsivo
    colunas = st.columns(3)
    
    # Processamento otimizado de cada especialidade
    for i, especialidade_nome in enumerate(ESPECIALIDADES):
        # Cálculo das métricas
        metricas = calcular_metricas_especialidade(linha, especialidade_nome)
        
        # Criação do gráfico donut
        fig = criar_donut_chart(metricas['valor_pct'])
        
        # Renderização do card e gráfico
        with colunas[i % 3]:
            # Card com informações
            card_html = criar_card_especialidade(especialidade_nome, metricas, i)
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Gráfico donut se disponível
            if fig:
                st.plotly_chart(
                    fig, 
                    use_container_width=True, 
                    config={"displayModeBar": False}, 
                    key=f"donut_{MAPA_COLUNAS[especialidade_nome]}_{valor_periodo}"
                )
            
            # Fechamento da div do card
            st.markdown("</div>", unsafe_allow_html=True)

# ===== FUNÇÕES AUXILIARES PARA ANÁLISE =====
@st.cache_data
def calcular_resumo_performance(df, unidade_sel, coluna_periodo, valor_periodo):
    """Calcula resumo de performance para análise"""
    df = processar_dados_temporais_especialidades(df)
    
    mask = (df["unidade"] == unidade_sel) & (df[coluna_periodo] == valor_periodo)
    df_unidade = df[mask].copy()
    
    if df_unidade.empty:
        return None
    
    linha = agregar_dados_periodo(df_unidade)
    
    resumo = {
        'especialidades_acima_meta': 0,
        'especialidades_abaixo_meta': 0,
        'performance_media': 0,
        'melhor_performance': ('', 0),
        'pior_performance': ('', 100)
    }
    
    performances = []
    
    for esp_nome in ESPECIALIDADES:
        esp_col = MAPA_COLUNAS[esp_nome]
        valor_pct = linha.get(f"pct_{esp_col}", 0)
        try:
            valor_pct = float(valor_pct) if valor_pct is not None else 0
        except (ValueError, TypeError):
            valor_pct = 0
        
        performances.append(valor_pct)
        
        if valor_pct >= 100:
            resumo['especialidades_acima_meta'] += 1
        else:
            resumo['especialidades_abaixo_meta'] += 1
        
        # Melhor performance
        if valor_pct > resumo['melhor_performance'][1]:
            resumo['melhor_performance'] = (esp_nome, valor_pct)
        
        # Pior performance
        if valor_pct < resumo['pior_performance'][1]:
            resumo['pior_performance'] = (esp_nome, valor_pct)
    
    resumo['performance_media'] = sum(performances) / len(performances) if performances else 0
    
    return resumo

def exibir_resumo_performance(df, unidade_sel, coluna_periodo, valor_periodo):
    """Exibe resumo da performance das especialidades"""
    resumo = calcular_resumo_performance(df, unidade_sel, coluna_periodo, valor_periodo)
    
    if not resumo:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Especialidades Acima da Meta",
            resumo['especialidades_acima_meta'],
            delta=f"{resumo['especialidades_acima_meta']}/{len(ESPECIALIDADES)}"
        )
    
    with col2:
        st.metric(
            "Performance Média",
            f"{resumo['performance_media']:.1f}%",
            delta="Meta: 100%"
        )
    
    with col3:
        st.metric(
            "Melhor Performance",
            resumo['melhor_performance'][0].upper(),
            delta=f"{resumo['melhor_performance'][1]:.1f}%"
        )
    
    with col4:
        st.metric(
            "Pior Performance", 
            resumo['pior_performance'][0].upper(),
            delta=f"{resumo['pior_performance'][1]:.1f}%"
        )

# ===== FUNÇÃO PARA COMPARAÇÃO TEMPORAL =====
def comparar_performance_temporal(df, unidade_sel, coluna_periodo):
    """Compara performance entre diferentes períodos"""
    df = processar_dados_temporais_especialidades(df)
    
    periodos_disponiveis = sorted(df[df["unidade"] == unidade_sel][coluna_periodo].unique())
    
    if len(periodos_disponiveis) < 2:
        st.info("Necessário pelo menos 2 períodos para comparação temporal.")
        return
    
    dados_comparacao = []
    
    for periodo in periodos_disponiveis[-6:]:  # Últimos 6 períodos
        mask = (df["unidade"] == unidade_sel) & (df[coluna_periodo] == periodo)
        df_periodo = df[mask].copy()
        
        if not df_periodo.empty:
            linha = agregar_dados_periodo(df_periodo)
            
            performance_total = []
            for esp_nome in ESPECIALIDADES:
                esp_col = MAPA_COLUNAS[esp_nome]
                valor_pct = linha.get(f"pct_{esp_col}", 0)
                try:
                    valor_pct = float(valor_pct) if valor_pct is not None else 0
                except (ValueError, TypeError):
                    valor_pct = 0
                performance_total.append(valor_pct)
            
            dados_comparacao.append({
                'periodo': periodo,
                'performance_media': sum(performance_total) / len(performance_total) if performance_total else 0
            })
    
    if dados_comparacao:
        import plotly.express as px
        df_comparacao = pd.DataFrame(dados_comparacao)
        
        fig = px.line(
            df_comparacao,
            x='periodo',
            y='performance_media',
            title=f'Evolução da Performance Média - {unidade_sel}',
            markers=True
        )
        
        fig.add_hline(y=100, line_dash="dash", line_color="red", 
                     annotation_text="Meta (100%)")
        
        fig.update_layout(
            xaxis_title="Período",
            yaxis_title="Performance Média (%)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)