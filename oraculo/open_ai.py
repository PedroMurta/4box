# ========================================
# 1. Imports e Setup
# ========================================
import os
import pandas as pd
import httpx

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter


# Cliente httpx ignorando certificados SSL (para ambientes com self-signed cert)
http_client = httpx.Client(verify=False)

os.environ["OPENAI_API_KEY"] = "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"
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


# Cliente httpx ignorando certificados SSL (para ambientes com self-signed cert)
http_client = httpx.Client(verify=False)


# ========================================
# 2. Carregar DataFrame
# ========================================
df = pd.read_parquet("matriz_anual.parquet")
print("✅ DataFrame carregado com", df.shape[0], "linhas")

# ========================================
# 2. Carregar Metadados
# ========================================
with open("metadados.md", "r", encoding="utf-8") as f:
    metadados_texto = f.read()

print("✅ Metadados carregados")

df['ano'] = df['ano'].astype('uint')

# ========================================
# 3. Quebrar Metadados em Chunks
# ========================================
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

metadados_chunks = text_splitter.split_text(metadados_texto)
print(f"✅ Metadados divididos em {len(metadados_chunks)} chunks")

# ========================================
# 4. Criar ChromaDB com embeddings da OpenAI
# ========================================
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY,
    http_client=http_client  # <- ignorar SSL
)

vectorstore = Chroma.from_texts(
    texts=metadados_chunks,
    embedding=embedding_model,
    persist_directory="./chroma_metadados_openai"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
print("✅ ChromaDB inicializado com OpenAI Embeddings")

# ========================================
# 5. Configurar LLM da OpenAI
# ========================================

# Configurar OpenAI LLM
print("🤖 Carregando modelo OpenAI...")
llm = ChatOpenAI(
    model="gpt-3.5-turbo-0125",   # pode trocar para "gpt-4.1-mini", "gpt-4o-mini" etc.
    temperature=0,
    api_key=OPENAI_API_KEY,
    http_client=httpx.Client(verify=False)
)
print("✅ OpenAI LLM configurado!")

from langchain.agents import initialize_agent, Tool

def executar_pandas(query: str):
    """
    Executa código Python/Pandas no DataFrame `df`.
    A query deve ser uma expressão válida em Pandas, ex:
    df[df["execucao_orcamentaria"] > 0 & (df["ano"] == 2024)]
    """
    try:
        return str(eval(query))
    except Exception as e:
        return f"Erro: {e}"

tools = [
    Tool(
        name="Executor de DataFrame",
        func=executar_pandas,
        description=(
            "Use para consultar o DataFrame df. "
            "A consulta deve ser em sintaxe Pandas, não SQL. "
            "Exemplo: df[df['execucao_orcamentaria'] > 0 & (df['ano'] == 2024)]"
        )
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True
)


# ========================================
# 7. Teste inicial
# ========================================
pergunta = "Quais unidades da empresa SEST tiveram uma boa operação (eixo_x > 0.5) e uma boa estratégia (eixo_y > 0.5) em 2024 \n Quais foram as notas padronizadas desses indicadores que contribuiram para essa boa operação?"
resposta = agent.run(pergunta)
print(resposta)


# ========================================
# 6. RetrievalQA com metadados
# ========================================
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff"
)

