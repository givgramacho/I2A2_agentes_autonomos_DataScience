# src/agent.py
import os
import logging
import pandas as pd
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import Tool
from langchain_core.prompts import MessagesPlaceholder

# Importar tools base e set_dataframe de tools.py
from tools import (
    schema_tool, dataset_info_tool, missing_tool, describe_tool, histogram_tool,
    set_dataframe
)

# Importar tools adicionais de tools_refactored.py
from tools_refactored import (
    boxplot_tool, scatter_tool, correlation_tool, outliers_tool,
    clustering_tool, time_trend_tool, frequency_tool, crosstab_tool,
    central_tendency_tool, variability_tool, range_tool,
    class_balance_tool, conclusion_tool
)

from memory_store import init_memory
from langsmith_setup import get_langsmith_client
from utils import logger


# Empacotar tools com descrições bem claras
TOOLS = [
    Tool(name="schema", func=lambda q: schema_tool(""), description="Retorna schema (colunas e tipos)."),
    Tool(name="dataset_info", func=lambda q: dataset_info_tool(""), description="Retorna informações COMPLETAS do dataset: shape, tipos, memória, missing values, estatísticas, duplicatas e amostra dos dados."),
    Tool(name="missing", func=lambda q: missing_tool(""), description="Retorna colunas com valores ausentes."),
    Tool(name="describe", func=lambda q: describe_tool(q), description="Estatísticas descritivas."),
    Tool(name="histogram", func=lambda q: histogram_tool(q), description="Cria histograma. Params: column=Nome ou apenas Nome"),
    Tool(name="boxplot", func=lambda q: boxplot_tool(q), description="Cria boxplot. Params: column=Nome ou columns=Col1|Col2"),
    Tool(name="scatter", func=lambda q: scatter_tool(q), description="Scatter plot. Params: x=Col1, y=Col2"),
    Tool(name="correlation", func=lambda q: correlation_tool(""), description="Calcula matriz de correlação entre variáveis numéricas."),
    Tool(name="outliers", func=lambda q: outliers_tool(q), description="Detecta outliers. Params: column=Nome, method=iqr ou zscore"),
    Tool(name="clustering", func=lambda q: clustering_tool(q), description="K-means clustering. Params: n_clusters=3, columns=Col1|Col2"),
    Tool(name="time_trend", func=lambda q: time_trend_tool(q), description="Análise temporal. Params: column=Time, target=Amount"),
    Tool(name="frequency", func=lambda q: frequency_tool(q), description="Valores mais frequentes. Params: column=Nome, top=10"),
    Tool(name="crosstab", func=lambda q: crosstab_tool(q), description="Tabela cruzada. Params: col1=Class, col2=Amount"),
    Tool(name="central_tendency", func=lambda q: central_tendency_tool(q), description="Média, mediana, moda. Params: column=Nome"),
    Tool(name="variability", func=lambda q: variability_tool(q), description="Variância, desvio padrão, CV. Params: column=Nome"),
    Tool(name="range", func=lambda q: range_tool(q), description="Min e max de uma coluna. Params: column=Nome"),
    Tool(name="class_balance", func=lambda q: class_balance_tool(""), description="Balanceamento de classes (coluna 'Class')."),
    Tool(name="conclusion", func=lambda q: conclusion_tool(""), description="Gera conclusão baseada na memória."),
]


def load_csv(path: str):
    """Carrega CSV e define como DataFrame global."""
    try:
        df = pd.read_csv(path)
        set_dataframe(df)
        logger.info(f"CSV loaded successfully: {path}")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV {path}: {e}")
        raise


def build_agent():
    """Constrói o agente com memória e LLM, suportando OpenAI, Gemini e Ollama.
    
    Returns:
        tuple: (agent, llm) - Retorna o agente e a instância do LLM
    """
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    logger.info(f"Building agent with provider={provider}, model={model}")

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API Key da OpenAI não definida.")
        llm = ChatOpenAI(model=model, temperature=0, openai_api_key=api_key)

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API Key do Google Gemini não definida.")
        llm = ChatGoogleGenerativeAI(model=model, temperature=0, api_key=api_key)

    elif provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        llm = ChatOllama(model=model, temperature=0)

    else:
        raise ValueError(f"Provedor {provider} não suportado.")

    # Memória persistente
    mems = init_memory()
    memory = mems.get("buffer")

    # Prompt customizado para FORÇAR uso de tools e evitar loops
    prefix = """Você é um Engenheiro de Dados especializado em Análise Exploratória (EDA).

REGRAS CRÍTICAS:
1. Você DEVE SEMPRE usar as ferramentas (tools) disponíveis para responder perguntas sobre dados.
2. NUNCA responda diretamente sem usar uma tool primeiro.
3. SEMPRE siga EXATAMENTE este formato:

Thought: [Seu raciocínio sobre o que fazer]
Action: [Nome EXATO da ferramenta]
Action Input: [Parâmetros da ferramenta]
Observation: [Resultado da ferramenta - será preenchido automaticamente]
... (repita Thought/Action/Action Input/Observation se necessário)
Thought: Agora sei a resposta final
Final Answer: [Resposta final formatada para o usuário]

4. Se você não souber qual tool usar, use "dataset_info" para ver as colunas disponíveis.
5. Para perguntas sobre conversas anteriores, use a memória do chat_history.

Você tem acesso às seguintes ferramentas:"""

    suffix = """SEMPRE comece com Thought, depois Action, depois Action Input.

Chat History: {chat_history}

Question: {input}
Thought: {agent_scratchpad}"""

    agent = initialize_agent(
        tools=TOOLS,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        max_iterations=8,
        handle_parsing_errors=True,
        max_execution_time=120,
        early_stopping_method="generate",
        agent_kwargs={
            "prefix": prefix,
            "suffix": suffix,
        }
    )
    
    logger.info("Agent built successfully with memory")
    # Retornar agente e LLM como tupla
    return agent, llm


def ask_agent(agent, question: str, csv_path: str = None, llm=None):
    """Executa uma pergunta ao agente.
    
    Args:
        agent: O agente executor
        question: Pergunta em linguagem natural
        csv_path: Caminho opcional para CSV
        llm: Instância do LLM (necessário para conclusões detalhadas)
    """
    try:
        if csv_path:
            load_csv(csv_path)
        
        logger.info(f"Processing question: {question[:100]}...")
        
        # Executar pergunta com memória
        response = agent.run(question)

        # Se a pergunta for de conclusão, melhora o resumo com análise detalhada
        if "conclusão" in question.lower():
            history = agent.memory.load_memory_variables({})
            context = str(history.get("chat_history", ""))
            
            # Usa LLM passado como parâmetro ou tenta acessar do agente
            if llm is None:
                try:
                    llm = agent.agent.llm_chain.llm
                except:
                    # Fallback: retorna resposta simples se não conseguir acessar LLM
                    logger.warning("Could not access LLM for enhanced conclusion")
                    return response
            
            conclusion_prompt = f"""Você é um Engenheiro de Machine Learning e Analista de Dados experiente.

Baseado nas análises realizadas no dataset, gere um relatório técnico completo incluindo:

## 📊 Histórico de Análises:
{context}

## 📋 Resposta do Agente:
{response}

## 🎯 Sua Tarefa:
Gere uma conclusão técnica profissional com:
1. **Resumo Executivo** das principais descobertas
2. **Insights Técnicos** sobre padrões identificados
3. **Recomendações** para próximos passos de análise
4. **Observações Estatísticas** relevantes

Formate em Markdown."""

            try:
                enhanced_response = llm.predict(conclusion_prompt)
                return enhanced_response
            except Exception as e:
                logger.error(f"Error generating enhanced conclusion: {e}")
                return response

        return response

    except Exception as e:
        logger.error(f"Error in ask_agent: {e}")
        return f"Erro ao processar pergunta: {str(e)}"
