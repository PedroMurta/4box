import plotly.express as px
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def grafico_radar_notas(df, empresa_sel, unidade_sel, competencia_sel, agrupamento_opcao):
    filtro_col = {
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

    indicadores_exec = [
        ("pct_execucao_custo", "Custo", 1),
        ("nota_producao", "Producao", 100),
        ("nota_nps", "Nps", 100),
        ("perc_financeiro", "Caixa", 1),
        ("execucao_orcamentaria", "Orcamento", 1),
        ("pct_alcance", "Receita", 1)
    ]

    indicadores_pad = [
        (f"nota_custo{sufixo}_padronizada", "Custo"),
        (f"nota_producao{sufixo}_padronizada", "Producao"),
        (f"nota_nps{sufixo}_padronizada", "Nps"),
        (f"nota_caixa{sufixo}_padronizada", "Caixa"),
        (f"nota_orcamento{sufixo}_padronizada", "Orcamento"),
        (f"nota_receita{sufixo}_padronizada", "Receita")
    ]

    df_filtrado = df[
        (df["empresa"] == empresa_sel) &
        (df[filtro_col] == competencia_sel)
    ]
    if unidade_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["unidade"] == unidade_sel]

    if df_filtrado.empty:
        return go.Figure()

    row = df_filtrado.iloc[0]

    executado = [row.get(col, 0.0) * mult for col, _, mult in indicadores_exec]
    padronizado = [row.get(col, 0.0) for col, _ in indicadores_pad]
    indicadores = [nome for _, nome, _ in indicadores_exec]

    df_radar = pd.DataFrame({
        "Indicador": indicadores,
        "Executado": executado,
        "Padronizado": padronizado
    })

    fig = go.Figure()

    #fig.add_trace(go.Scatterpolar(
    #    r=df_radar["Executado"],
    #    theta=df_radar["Indicador"],
    #    fill='toself',
    #    name='Executado',
    #    line=dict(color='rgba(44, 160, 44, 0.7)', width=2)
    #))
    st.markdown("<div style='margin-top: 30px; <br>'></div>", unsafe_allow_html=True)
    fig.add_trace(go.Scatterpolar(
        r=df_radar["Padronizado"],
        theta=df_radar["Indicador"],
        fill='toself',
        name='Padronizado',
        line=dict(color='rgba(31, 119, 180, 0.8)', width=2)
    ))

    fig.update_layout(
        polar=dict(
            gridshape="linear",
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=12)),
            angularaxis=dict(tickfont=dict(size=13), rotation=90, direction='clockwise')
        ),
        height=700,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig



###########################################################################################
def exibir_cards_radar(df, empresa_sel, unidade_sel, competencia_sel, agrupamento_opcao):
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

    indicadores_exec = [
        ("pct_execucao_custo", "💸 Custo", 1),
        ("nota_producao", "🏭 Produção", 100),
        ("nota_nps", "🌟 NPS", 100),
        ("perc_financeiro", "💰 Caixa", 1),
        ("execucao_orcamentaria", "📊 Orçamento", 1),
        ("pct_alcance", "📈 Receita", 1)
    ]

    indicadores_pad = [
        (f"nota_custo{sufixo}_padronizada", "💸 Custo"),
        (f"nota_producao{sufixo}_padronizada", "🏭 Produção"),
        (f"nota_nps{sufixo}_padronizada", "🌟 NPS"),
        (f"nota_caixa{sufixo}_padronizada", "💰 Caixa"),
        (f"nota_orcamento{sufixo}_padronizada", "📊 Orçamento"),
        (f"nota_receita{sufixo}_padronizada", "📈 Receita")
    ]

    df_filtrado = df[df["empresa"] == empresa_sel]
    if unidade_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["unidade"] == unidade_sel]
    df_filtrado = df_filtrado[df_filtrado[coluna_periodo] == competencia_sel]
    if df_filtrado.empty:
        return

    row = df_filtrado.iloc[0]

    st.markdown(
        f"""
        <div style='
            background-color: #3f4f6b;
            color: white;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            width: 100%;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.4);
            margin-bottom: 10px;
        '>
            📊 Indicadores Normalizados ({agrupamento_opcao})
        </div>
        """,
        unsafe_allow_html=True
    )

    for (col_exec, nome, mult), (col_pad, _) in zip(indicadores_exec, indicadores_pad):
        valor_exec = row.get(col_exec, None)
        valor_pad = row.get(col_pad, None)

        if valor_exec is None or valor_pad is None:
            continue

        valor_exec *= mult

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                    <div style="background-color: rgba(31, 119, 180, 0.8); color: white; border-radius: 10px;
                                padding: 10px; text-align: center; margin-bottom: 10px;">
                        <div style="font-size: 15px;">{nome} - Padronizado</div>
                        <div style="font-size: 22px; font-weight: bold;">{valor_pad:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                    <div style="background-color: rgba(0,0,0,0.4); color: black; border-radius: 10px;
                                padding: 10px; text-align: center; margin-bottom: 10px;">
                        <div style="font-size: 15px;">{nome} - Execução</div>
                        <div style="font-size: 22px; font-weight: bold;">{valor_exec:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)


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