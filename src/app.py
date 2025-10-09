# src/app.py
import os
import streamlit as st
from agent import build_agent, ask_agent, load_csv
from glob import glob
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

st.set_page_config(page_title="Agente EDA CSV", layout="wide", page_icon="📊")
st.title("📊 Agente Genérico de EDA em CSV")

# Inicializar session_state para persistir o agente e LLM
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'llm' not in st.session_state:
    st.session_state.llm = None
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
    
# Configuração no sidebar
st.sidebar.header("⚙️ Configurações do Agente")
provider = st.sidebar.selectbox(
    "🌐 Provedor LLM",
    ["OpenAI", "Google Gemini", "Ollama (local)"]
)

api_key_input = st.sidebar.text_input("🔑 API Key", type="password")

# Modelos por provedor
if provider == "OpenAI":
    model_input = st.sidebar.selectbox(
        "🤖 Modelo OpenAI",
        ["gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["LLM_MODEL"] = model_input

elif provider == "Google Gemini":
    model_input = st.sidebar.selectbox(
        "🤖 Modelo Gemini",
        ["gemini-2.5-flash", "gemini-2.5-flash-preview-09-2025", "gemini-flash-latest"]
    )
    if api_key_input:
        os.environ["GOOGLE_API_KEY"] = api_key_input
    os.environ["LLM_PROVIDER"] = "gemini"
    os.environ["LLM_MODEL"] = model_input

elif provider == "Ollama (local)":
    model_input = st.sidebar.text_input("Modelo Ollama", value="llama3.1:8b")
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["LLM_MODEL"] = model_input



# Upload do CSV
uploaded = st.file_uploader("📂 Envie um arquivo CSV", type=["csv"])

if uploaded:
    csv_path = os.path.join("data", uploaded.name)
    os.makedirs("data", exist_ok=True)
    
    # Só recarrega se for um arquivo diferente
    if st.session_state.current_file != uploaded.name:
        with open(csv_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.success(f"Arquivo CSV salvo em: `{csv_path}`")
        load_csv(csv_path)
        # build_agent() agora retorna (agent, llm)
        agent, llm = build_agent()
        st.session_state.agent = agent
        st.session_state.llm = llm
        st.session_state.current_file = uploaded.name
    
    agent = st.session_state.agent
    llm = st.session_state.llm
else:
    st.info("Envie um arquivo CSV para começar.")
    agent = None
    llm = None

# Caixa de pergunta
query = st.text_input("💬 Pergunta para o agente", 
    placeholder="Exemplo: Crie um histograma da coluna Amount com 50 bins")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔎 Perguntar"):
        if not agent:
            st.warning("Envie um CSV antes de perguntar.")
        else:
            with st.spinner("Agente analisando..."):
                ans = ask_agent(agent, query, csv_path=csv_path, llm=llm)
            st.subheader("📥 Resposta do agente")
            st.write(ans)

            # Mostrar último gráfico
            plots = sorted(glob("plots/*.png"), reverse=True)
            if plots:
                st.image(plots[0], caption=os.path.basename(plots[0]))

with col2:
    if st.button("📝 Gerar Conclusão Final"):
        if not agent:
            st.warning("Envie um CSV antes de gerar conclusões.")
        else:
            with st.spinner("Gerando conclusão a partir das análises..."):
                ans = ask_agent(agent, "Quais conclusões você obteve?", csv_path=csv_path, llm=llm)
            st.subheader("📊 Conclusão Final")
            st.write(ans)

            # Se houver gráficos, mostrar todos
            plots = sorted(glob("plots/*.png"), reverse=True)[:3]
            if plots:
                st.image(plots, caption=[os.path.basename(p) for p in plots])