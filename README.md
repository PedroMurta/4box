# 📊 Painel Estratégico: NineBox & FourBox

Este repositório contém o painel interativo desenvolvido em **Python + Streamlit**, com os gráficos **NineBox** e **FourBox**, voltados à análise estratégica de unidades operacionais com base em métricas de desempenho. A aplicação permite a visualização, comparação e segmentação de dados a partir de diferentes eixos personalizados pelo usuário.

---

## ✨ Visão Geral

### 🔹 4Box

Permite o mapeamento de unidades em 4 quadrantes com base em dois eixos:
- **Eixo X** (Operacional): Ex. produção, custo, caixa
- **Eixo Y** (Estratégico): Ex. orçamento, receita, capacidade produtiva

Cada bolha representa uma unidade. O tamanho pode refletir a **idade da unidade** (ou outro critério).

### 🔹 9Box

Um modelo expandido com **9 quadrantes**, muito utilizado em análises de desempenho x potencial (ou eficiência x estratégia, como neste caso).  
Permite identificar:
- Unidades de **alto desempenho** (quadrante 9)
- Unidades com **baixo desempenho** (quadrante 1)
- Casos intermediários para melhoria ou manutenção estratégica

---

## ⚙️ Funcionalidades

- Filtros por: empresa, período, conselho, unidade e tipologia
- Escolha de **variáveis e pesos personalizados** para cada eixo
- Estilização amigável e responsiva com cores e destaques
- Tamanhos de bolha proporcionais à idade da unidade (quando disponível)
- Destaque visual para unidade selecionada
- Tooltip interativo com métricas detalhadas por unidade
- Integração com dados organizacionais reais

---

## 📦 Tecnologias Utilizadas
- [Apache Iceberg 1.9+](https://iceberg.apache.org/)
- [Pyspark 3-4-4+](https://spark.apache.org/)
- [Python 3.10+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- [NumPy](https://numpy.org/)

---

## 🚀 Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/PedroMurta/4box.git
cd 4box
pip install -r requirements.txt
streamlit run app.py
