import plotly.express as px
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def grafico_radar_notas(df, empresa_sel, unidade_sel, competencia_sel, agrupamento_opcao):
    """Gráfico radar com valores padronizados - Versão Final"""
    
    # Mapeamento de filtros e sufixos
    mapeamento_filtro = {
        "Mês": "competencia",
        "Trimestre": "trimestre",
        "Semestre": "ano_semestre", 
        "Ano": "ano"
    }
    
    mapeamento_sufixo = {
        "Mês": "_mensal",
        "Trimestre": "_trimestral",
        "Semestre": "_semestral",
        "Ano": "_anual"
    }
    
    filtro_col = mapeamento_filtro[agrupamento_opcao]
    sufixo = mapeamento_sufixo[agrupamento_opcao]
    
    # Filtrar dados
    df_filtrado = df[
        (df["empresa"] == empresa_sel) &
        (df[filtro_col] == competencia_sel)
    ]
    
    if unidade_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["unidade"] == unidade_sel]
    
    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font_size=16
        )
        return fig
    
    # Obter valores padronizados
    valores_padronizados = obter_valores_padronizados(df_filtrado, sufixo)
    indicadores = ["Custo", "Produção", "NPS", "Caixa", "Orçamento", "Receita"]
    
    # Criar gráfico radar
    fig = go.Figure()
    
    # Trace valores padronizados
    fig.add_trace(go.Scatterpolar(
        r=valores_padronizados,
        theta=indicadores,
        fill='toself',
        name='Indicadores Padronizados',
        line=dict(color='rgba(31, 119, 180, 0.8)', width=3),
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    # Layout otimizado
    fig.update_layout(
        polar=dict(
            gridshape="linear",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(size=12),
                tickformat=".2f"
            ),
            angularaxis=dict(
                tickfont=dict(size=13),
                rotation=90,
                direction='clockwise'
            )
        ),
        height=700,
        margin=dict(l=60, r=60, t=80, b=60),
        title=dict(
            text=f"Radar de Indicadores - {agrupamento_opcao}",
            x=0.5,
            font=dict(size=16, color='#2c3e50')
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def obter_valores_originais(df_filtrado):
    """
    Obtém valores originais (não padronizados) de forma segura
    
    Args:
        df_filtrado: DataFrame já filtrado
        sufixo: Sufixo do período (_mensal, _trimestral, etc.)
    
    Returns:
        list: Lista com valores originais na ordem [custo, produção, nps, caixa, orçamento, receita]
    """
    # Definir colunas originais na ordem correta
    colunas_ordem = [
        f"nota_custo",
        f"nota_producao",
        f"nota_nps",
        f"nota_caixa",
        f"nota_orcamento",
        f"nota_receita"
    ]
    
    # Verificar quais colunas existem
    colunas_existentes = [col for col in colunas_ordem if col in df_filtrado.columns]
    
    
    # Obter valores (média se múltiplas linhas)
    if len(df_filtrado) == 1:
        row = df_filtrado.iloc[0]
    else:
        row = df_filtrado[colunas_existentes].mean()
    
    # Extrair valores na ordem correta, convertendo para percentuais onde necessário
    valores = []
    for i, col in enumerate(colunas_ordem):
        if col in df_filtrado.columns:
            valor = row.get(col, 0)
            # Garantir que não é NaN
            if pd.isna(valor):
                valor = 0
            
            # Converter valores para formato de exibição apropriado
            if i == 2:  # NPS (índice 2)
                # NPS já deve estar em escala apropriada (normalmente 0-1 ou 0-100)
                # Vamos assumir que está em 0-1 e converter para escala -100 a +100
                if valor <= 1:
                    valor = valor * 200 - 100  # Converte 0-1 para -100 a +100
                valores.append(float(valor))
            else:  # Outros indicadores (custo, produção, caixa, orçamento, receita)
                # Se valor está entre 0-1, converter para percentual
                if valor <= 1:
                    valor = valor * 100
                valores.append(float(valor))
        else:
            valores.append(0.0)
    
    return valores

def obter_valores_padronizados(df_filtrado, sufixo):
    """
    Obtém valores padronizados de forma segura
    
    Args:
        df_filtrado: DataFrame já filtrado
        sufixo: Sufixo do período (_mensal, _trimestral, etc.)
    
    Returns:
        list: Lista com valores padronizados na ordem [custo, produção, nps, caixa, orçamento, receita]
    """
    # Definir colunas padronizadas na ordem correta
    colunas_ordem = [
        f"nota_custo{sufixo}_padronizada",
        f"nota_producao{sufixo}_padronizada",
        f"nota_nps{sufixo}_padronizada",
        f"nota_caixa{sufixo}_padronizada",
        f"nota_orcamento{sufixo}_padronizada",
        f"nota_receita{sufixo}_padronizada"
    ]
    
    # Verificar quais colunas existem
    colunas_existentes = [col for col in colunas_ordem if col in df_filtrado.columns]
    
    if not colunas_existentes:
        print(f"⚠️ Nenhuma coluna padronizada encontrada para sufixo {sufixo}")
        return [0, 0, 0, 0, 0, 0]
    
    # Obter valores (média se múltiplas linhas)
    if len(df_filtrado) == 1:
        row = df_filtrado.iloc[0]
    else:
        row = df_filtrado[colunas_existentes].mean()
    
    # Extrair valores na ordem correta, usando 0 para colunas não encontradas
    valores = []
    for col in colunas_ordem:
        if col in df_filtrado.columns:
            valor = row.get(col, 0)
            # Garantir que não é NaN
            if pd.isna(valor):
                valor = 0
            valores.append(float(valor))
        else:
            valores.append(0.0)
    
    return valores


def calcular_valores_periodo(df_filtrado):
    """Calcula valores agregados por período usando as colunas do DataFrame"""
    
    # Somar valores para o período (agregado)
    soma_custo_realizado = df_filtrado["soma_custo_realizado"].sum()
    soma_meta = df_filtrado["soma_meta"].sum()
    
    despesa_liquidada = df_filtrado["despesa_liquidada"].sum()
    despesa_prevista = df_filtrado["despesa_prevista"].sum()
    
    receitas = df_filtrado["receitas"].sum()
    despesas = df_filtrado["despesas"].sum()
    
    receita_prevista = df_filtrado["receita_prevista"].sum()
    receita_realizada = df_filtrado["receita_realizada"].sum()
    
    # Produção (média ponderada ou soma)
    nota_producao = df_filtrado["nota_producao"].mean() * 100
    
    # Calcular indicadores
    custo = (soma_custo_realizado / soma_meta * 100) if soma_meta > 0 else 0
    orcamento = (despesa_liquidada / despesa_prevista * 100) if despesa_prevista > 0 else 0
    caixa = (receitas / despesas * 100) if despesas > 0 else 0
    producao = nota_producao
    receita = (receita_realizada / receita_prevista * 100) if receita_prevista > 0 else 0
    
    return {
        "custo": custo,
        "orcamento": orcamento, 
        "caixa": caixa,
        "producao": producao,
        "receita": receita
    }

def exibir_cards_radar(df, empresa_sel, unidade_sel, competencia_sel, agrupamento_opcao):
    """Cards com valores padronizados (Coluna 1) e calculados por período (Coluna 2)"""
    
    # Mapeamento
    coluna_periodo = {
        "Mês": "competencia",
        "Trimestre": "trimestre",
        "Semestre": "ano_semestre",
        "Ano": "ano"
    }[agrupamento_opcao]
    
    sufixo = {
        "Mês": "_mensal",
        "Trimestre": "_trimestral", 
        "Semestre": "_semestral",
        "Ano": "_anual"
    }[agrupamento_opcao]
    
    # Filtrar dados
    df_filtrado = df[df["empresa"] == empresa_sel]
    
    if unidade_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["unidade"] == unidade_sel]
    
    df_filtrado = df_filtrado[df_filtrado[coluna_periodo] == competencia_sel]
    
    if df_filtrado.empty:
        st.warning("Sem dados disponíveis para os filtros selecionados.")
        return
    
    # Calcular valores agregados por período (Coluna 2)
    valores_agregados = calcular_valores_periodo(df_filtrado)
    
    # Pegar valores padronizados (Coluna 1)
    if len(df_filtrado) == 1:
        row = df_filtrado.iloc[0]
    else:
        # Para múltiplas linhas, fazer média dos valores padronizados
        colunas_padronizadas = [
            f"nota_custo{sufixo}_padronizada",
            f"nota_producao{sufixo}_padronizada",
            f"nota_caixa{sufixo}_padronizada", 
            f"nota_orcamento{sufixo}_padronizada",
            f"nota_receita{sufixo}_padronizada"
        ]
        colunas_existentes = [col for col in colunas_padronizadas if col in df_filtrado.columns]
        if colunas_existentes:
            row = df_filtrado[colunas_existentes].mean()
        else:
            row = df_filtrado.iloc[0]  # fallback
    
    # Configuração dos indicadores
    indicadores_config = [
        ("custo", "💸 Custo", "custo"),
        ("producao", "🏭 Produção", "producao"),
        ("caixa", "💰 Caixa", "caixa"),
        ("orcamento", "📊 Orçamento", "orcamento"),
        ("receita", "📈 Receita", "receita")
    ]
    
    # Título
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style='
            background-color: #3f4f6b;
            color: white;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 20px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.4);
        '>
            📊 Indicadores por Período ({agrupamento_opcao})
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Exibir cards
    for nome_base, nome_display, chave_agregado in indicadores_config:
        
        # Coluna 1: Valor padronizado
        col_padronizada = f"nota_{nome_base}{sufixo}_padronizada"
        valor_padronizado = row.get(col_padronizada, 0)
        if pd.isna(valor_padronizado):
            valor_padronizado = 0
        
        # Coluna 2: Valor calculado agregado
        valor_agregado = valores_agregados.get(chave_agregado, 0)
        
        # Cards lado a lado
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
                <div style="
                    background-color: #3f4f6b;
                    color: white;
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    margin-bottom: 10px;
                    box-shadow: 2px 2px 6px rgba(0,0,0,0.4);
                    font-weight: bold;
                ">
                    <div style="font-size: 16px; margin-bottom: 8px;">
                        {nome_display} - Padronizado
                    </div>
                    <div style="font-size: 24px; font-weight: bold;">
                        {valor_padronizado:.2f}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div style="
                    background-color: rgba(0,0,0,0.4);
                    color: white;
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    margin-bottom: 10px;
                    box-shadow: 2px 2px 6px rgba(0,0,0,0.4);
                    font-weight: bold;
                ">
                    <div style="font-size: 16px; margin-bottom: 8px;">
                        {nome_display} - Executado
                    </div>
                    <div style="font-size: 24px; font-weight: bold;">
                        {valor_agregado:.2f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Função para debug/verificação
def debug_colunas_disponiveis(df):
    """Mostra colunas disponíveis para debug"""
    colunas_relevantes = [
        col for col in df.columns 
        if any(palavra in col.lower() for palavra in [
            'soma_custo_realizado', 'soma_meta', 'despesa_liquidada', 
            'despesa_prevista', 'receitas', 'despesas', 'receita_prevista', 
            'receita_realizada', 'nota_producao', 'padronizada'
        ])
    ]
    print("🔍 Colunas relevantes encontradas:")
    for col in sorted(colunas_relevantes):
        print(f"   - {col}")
    return colunas_relevantes





'''
# 14. ABA METODOLOGIA
elif aba_selecionada == "Metodologia":
    st.markdown(f"<br><br>", unsafe_allow_html=True)

    st.markdown("""
### 📐 Metodologia de Padronização dos Indicadores

A padronização tem como objetivo **tornar os indicadores comparáveis** entre unidades, períodos e contextos distintos, permitindo análises mais consistentes e justas.

---

### 🔢 Fórmulas de Cálculo das Notas

| Indicador                | Fórmula Utilizada                                              | Interpretação                                                                 |
|--------------------------|----------------------------------------------------------------|--------------------------------------------------------------------------------|
| **Produção**             | `1 + ((Produção - Meta) / 100)`                                 | Avalia o desempenho da produção em relação à meta de 100%                      |
| **Receita**              | `1 + ((Receita - Meta) / 100)`                              | Mede o percentual de alcance da receita em relação à previsão                 |
| **Custo**                | `1 + ((Meta - Execução do Custo) / 100)`                       | Penaliza execuções acima da meta (quanto menor o custo, melhor a nota)        |
| **Orçamento**            | `1 - (abs(Meta - Execução Orçamentária) / 100)`                 | Nota máxima quando há aderência total à meta orçamentária                     |
| **Caixa**                | `1 + ((Caixa - Meta) / 100)`                          | Avalia o saldo financeiro em relação à meta esperada                          |
| **Capacidade Produtiva** | `Capacidade Produtiva / 100`                                   | Mede o nível de uso da capacidade produtiva da unidade                        |
| **NPS**                  | `Nota NPS` (sem transformação)                                 | Já é uma nota padronizada de satisfação do cliente                            |

---

### ⏲️ Periodicidade das Notas

As notas são calculadas para os seguintes períodos:

- **Mensal** (por competência)
- **Trimestral** (T1 a T4)
- **Semestral** (S1 e S2)
- **Anual** (valor agregado do ano)

Cada período considera os dados por **empresa(SEST ou SENAT)**, **unidade operacional** e **tempo**.

---

### ⚙️ Regras Complementares

- **Notas ausentes** são preenchidas com `0`, evitando distorções na análise.
- Para competências **anteriores a maio de 2024**, aplica-se uma **nota NPS padrão igual a 1**, devido à ausência de dados.

---

### ✂️ Tratamento de Valores Extremos (Clipping)

Antes da normalização das notas para a escala de **0 a 1**, é realizada uma técnica chamada **clipping**, que remove os valores extremos (_*outliers*_).

Esses valores muito altos ou baixos podem distorcer os resultados e gerar interpretações erradas sobre o desempenho das unidades. O clipping atua como um "corte nas pontas", focando nos valores mais representativos do conjunto.

#### Limites aplicados por indicador:

| Indicador         | Limite Inferior | Limite Superior |
|-------------------|------------------|------------------|
| **Orçamento**     | 5%               | Sem limite       |
| **Receita**       | 5%               | 85%              |
| **Custo**         | 20%              | 95%              |
| **Produção**      | 5%               | 85%              |
| **Caixa**         | 5%               | 90%              |

> Após esse tratamento, os valores restantes são normalizados para a escala de **0 a 1**, onde:
>
> - **0** representa o pior desempenho (dentro do intervalo considerado);
> - **1** representa o melhor desempenho (dentro do intervalo considerado).

As notas de **NPS** e **Capacidade Produtiva** não passam por essa normalização, mantendo seus valores originais.

---

Essa metodologia permite uma avaliação mais justa e comparável entre diferentes unidades, períodos e contextos operacionais.
""")


'''