import streamlit as st
import plotly.graph_objects as go


def exibir_metricas_com_donut(df, unidade_sel, coluna_periodo, valor_periodo):
    # Garante que colunas de tempo estejam disponíveis
    df["ano"] = df["competencia"].str[:4]
    df["mes"] = df["competencia"].str[5:7].astype(int)
    df["semestre"] = df["mes"].apply(lambda m: "1" if m <= 6 else "2")
    df["ano_semestre"] = df["semestre"] + "-" + df["ano"]

    # Filtro principal baseado em período
    df_unidade = df[
        (df["unidade"] == unidade_sel) &
        (df[coluna_periodo] == valor_periodo)
    ].copy()

    if df_unidade.empty:
        st.warning("Unidade não encontrada para o período selecionado.")
        return

    # Agregação se houver mais de uma linha (ex: ano ou semestre)
    if len(df_unidade) > 1:
        agregados = {}
        especialidades = [
            "odonto", "fisio", "psico", "nutri", 
            "pale_sest", "elc", "curso_prese", "curso_ead", "pale_senat"
        ]
        for esp in especialidades:
            agregados[esp] = df_unidade[esp].sum()
            agregados[f"meta_{esp}"] = df_unidade[f"meta_{esp}"].sum()
            agregados[f"pct_{esp}"] = (
                100 * agregados[esp] / agregados[f"meta_{esp}"]
                if agregados[f"meta_{esp}"] > 0 else 0
            )
        linha = agregados
    else:
        linha = df_unidade.iloc[0]

    colunas = st.columns(3)
    for i, esp in enumerate([
        "odonto", "fisio", "psico", "nutri", 
        "pale_sest", "elc", "curso_prese", "curso_ead", "pale_senat"
    ]):
        valor_real = int(linha.get(esp, 0))
        valor_meta = int(linha.get(f"meta_{esp}", 0))
        delta = valor_real - valor_meta

        simbolo = "↑" if delta >= 0 else "↓"
        cor = "#588157" if delta >= 0 else "#b04c52"
        texto_delta = f"<span style='color:{cor}; font-size:16px;'>{simbolo} {abs(delta):,}".replace(",", ".") + "</span>"

        valor_pct = linha.get(f"pct_{esp}", None)
        try:
            valor_pct = float(valor_pct) if valor_pct is not None else None
        except (ValueError, TypeError):
            valor_pct = None

        fig = None
        if valor_pct is not None:
            valor_plotado = min(valor_pct, 100)
            cor_donut = "#588157" if valor_pct >= 100 else "#b04c52"
            fig = go.Figure(go.Pie(
                values=[valor_plotado, 100 - valor_plotado],
                hole=0.65,
                marker=dict(
                    colors=[cor_donut, "#1e1e1e"],
                    line=dict(color="black", width=2)
                ),
                textinfo='none',
                showlegend=False
            ))
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                width=250,
                height=250,
                annotations=[dict(
                    text=f"{valor_pct:.0f}%",
                    x=0.5, y=0.5,
                    font_size=24,
                    showarrow=False,
                    font_color=cor_donut
                )],
                paper_bgcolor="#c9dddb",
                plot_bgcolor="#a5b8bd"
            )

        with colunas[i % 3]:
            st.markdown(
                f"""
                <div style="border: 3px solid {cor}; border-radius: 12px; padding: 10px; text-align: center; background-color: rgb(63, 79, 107); color: #C9D6DF;">
                    <div style="font-weight: bold; font-size: 16px;">{esp.upper()}</div>
                    <div style="font-size: 22px; margin: 5px 0;"><i>Realizado: <b>{valor_real:,}</b></i> <br> Meta: {valor_meta:,}</div>
                    <div style="margin-bottom: 10px;">{texto_delta}</div>
                """,
                unsafe_allow_html=True
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"donut_{esp}")
            st.markdown("</div>", unsafe_allow_html=True)
