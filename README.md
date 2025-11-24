# 🤖 Agente Autônomo de Análise Exploratória de Dados

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://seu-app.streamlit.app)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://python.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

> **Sistema inteligente com agentes autônomos capaz de analisar qualquer arquivo CSV, responder perguntas em linguagem natural e gerar visualizações automáticas com memória persistente.**

---

## 🎯 Visão Geral

Este projeto implementa um **Agente Autônomo de Análise Exploratória de Dados (EDA)** utilizando **LangChain**, **LLMs** (OpenAI GPT-4, Google Gemini, Ollama) e **Streamlit**. O sistema possui **memória conversacional persistente** e **18 ferramentas especializadas** para análise de dados.

### 🚀 Funcionalidades Principais

- ✅ **Análise Automatizada** - 18 ferramentas de análise (histograma, correlação, outliers, clustering, etc.)
- ✅ **Memória Persistente** - Sistema vetorial com ChromaDB para manter contexto das conversas
- ✅ **Multi-LLM Support** - OpenAI, Google Gemini e Ollama
- ✅ **Interface Web Moderna** - Streamlit responsiva e intuitiva
- ✅ **Visualizações Automáticas** - Geração e salvamento automático de gráficos
- ✅ **Conclusões Inteligentes** - Resumos automáticos baseados em análises anteriores
- ✅ **Segurança Multi-Usuário** - ThreadLocal para isolamento de dados
- ✅ **Containerização** - Docker e Docker Compose prontos para produção

---

## 🏗️ Arquitetura do Sistema

```
agentes_engenheiro_dados/
├── src/
│   ├── app.py              # Interface Streamlit
│   ├── agent.py            # Agente LangChain com memória
│   ├── tools.py            # Ferramentas básicas de EDA
│   ├── tools_refactored.py # Ferramentas avançadas
│   ├── utils.py            # Utilitários reutilizáveis
│   ├── memory_store.py     # Sistema de memória vetorial
│   └── langsmith_setup.py  # Configuração de tracing
├── data/                   # Armazenamento de datasets
├── plots/                  # Gráficos gerados
├── chroma_store/          # Banco de dados vetorial
├── dockerfile             # Configuração Docker
├── docker-compose.yml     # Orquestração de serviços
├── pyproject.toml         # Gerenciamento com UV
└── requirements.txt       # Dependências do projeto
```

---

## 🚀 Quick Start

### 🌐 Demo Online

👉 **[Acessar Aplicação](https://i2a2-agentes-autonomos-datascience.streamlit.app/)** _(disponível após deploy)_

### 💻 Execução Local com UV

#### Pré-requisitos

- Python 3.13+
- [UV](https://github.com/astral-sh/uv) - Gerenciador de pacotes Python
- API Key (Google Gemini recomendado)

#### 1️⃣ Instalação com UV

```bash
# Instalar UV (se ainda não tiver)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clonar repositório
git clone https://github.com/givgramacho/I2A2_agentes_autonomos_DataScience.git
cd I2A2_agentes_autonomos_DataScience

# Criar ambiente virtual e instalar dependências
uv venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

uv pip install -r requirements.txt
```

#### 2️⃣ Configurar Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas chaves
# LLM_PROVIDER=gemini
# GOOGLE_API_KEY=sua_chave_aqui
```

#### 3️⃣ Executar Aplicação

```bash
streamlit run src/app.py
```

Acesse seu link: http://localhost:8501 
ou 
[**Aplicação após deploy no Streamlit em :** https://i2a2-agentes-autonomos-datascience.streamlit.app/](https://i2a2-agentes-autonomos-datascience.streamlit.app/)

### 🐳 Execução com Docker

#### Opção 1: Docker Compose (Recomendado)

```bash
# Iniciar com Docker Compose
docker-compose up -d

# Parar
docker-compose down

# Verificar logs
docker-compose logs -f
```

#### Opção 2: Docker Build Manual

```bash
# Construir imagem
docker build -t i2a2-agente-datascience .

# Executar container
docker run -p 8501:8501 --name i2a2-app i2a2-agente-datascience

# Parar container
docker stop i2a2-app
```

#### Acesso
- **URL Local:** http://localhost:8501
- **Health Check:** Container com monitoramento automático
- **Logs:** `docker-compose logs -f` para acompanhamento em tempo real

---

## 📊 Ferramentas de Análise

### 📈 Análise Básica

- **Schema** - Estrutura e tipos de dados
- **Dataset Info** - Informações completas do dataset
- **Missing Values** - Análise de valores ausentes
- **Describe** - Estatísticas descritivas

### 📊 Visualizações

- **Histogram** - Distribuição de variáveis
- **Boxplot** - Análise de outliers e distribuição
- **Scatter** - Relação entre variáveis
- **Correlation** - Matriz de correlação

### 🔍 Análise Avançada

- **Outliers Detection** - Identificação de valores extremos
- **Clustering** - K-means para segmentação
- **Time Trend** - Análise de séries temporais
- **Frequency** - Valores mais frequentes
- **Crosstab** - Tabelas cruzadas

### 📐 Estatística

- **Central Tendency** - Média, mediana, moda
- **Variability** - Variância, desvio padrão
- **Range** - Valores mínimos e máximos
- **Class Balance** - Balanceamento de classes
- **Conclusion** - Geração automática de conclusões

---

## 🔧 Configuração Avançada

### Provedores LLM Suportados

#### 🤖 OpenAI

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
```

#### 🔥 Google Gemini (Recomendado)

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash-exp
GOOGLE_API_KEY=...
```

#### 🦙 Ollama (Local)

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
```

### Memória e Persistência

- **ChromaDB** - Armazenamento vetorial para memória
- **ConversationBufferMemory** - Histórico de conversas
- **ThreadSafe** - Isolamento multi-usuário

---

## 🐳 Docker e Deploy

### Dockerfile Otimizado

```dockerfile
FROM python:3.13.1-slim
WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Expor porta
EXPOSE 8501

CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app:/app/src
```

---

## 📈 Melhorias Implementadas

### ✅ Críticas

- **Segurança Multi-Usuário** - ThreadLocal para isolamento de dados
- **Módulo Utils** - Redução de 60% de código duplicado
- **Validação Robusta** - Verificação automática de colunas
- **Limpeza Automática** - Gerenciamento de gráficos antigos

### 🚀 Performance

- **Cache Inteligente** - Otimização de consultas
- **Async Operations** - Processamento não-bloqueante
- **Memory Management** - Controle de uso de memória

### 🛡️ Segurança

- **Input Validation** - Sanitização automática
- **Error Handling** - Captura robusta de erros
- **Environment Variables** - Segredos protegidos

---

## 🧪 Testes e Qualidade

### Estrutura de Testes

```bash
# Executar testes
pytest tests/

# Cobertura de código
pytest --cov=src tests/

# Linting
ruff check src/
black src/
```

### Métricas de Qualidade

- **Cobertura de Código:** 70%+ (alvo)
- **Complexidade:** Média (6-8 por função)
- **Documentation:** 100% de funções documentadas

---

## 📚 Documentação

- **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** - Guia completo de deploy
- **[DOCUMENTO_PROJETO.md](DOCUMENTO_PROJETO.md)** - Especificação técnica
- **[MELHORIAS_IMPLEMENTADAS.md](MELHORIAS_IMPLEMENTADAS.md)** - Histórico de melhorias

---

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o repositório
2. **Branch** para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -m 'Add nova funcionalidade'`)
4. **Push** para o branch (`git push origin feature/nova-funcionalidade`)
5. **Pull Request** descrevendo as mudanças

### Padrões de Código

- **Black** para formatação
- **Ruff** para linting
- **Type Hints** obrigatórios
- **Docstrings** seguindo padrão Google

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **LangChain** - Framework de agentes
- **Streamlit** - Interface web
- **Google Gemini** - LLM poderoso
- **ChromaDB** - Armazenamento vetorial

---

## 📞 Contato

**Givanildo Gramacho**GitHub: [@givgramacho](https://github.com/givgramacho)

- LinkedIn: [Givanildo Gramacho](https://linkedin.com/in/givanildo-gramacho)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=givgramacho/I2A2_agentes_autonomos_DataScience&type=Date)](https://star-history.com/#givgramacho/I2A2_agentes_autonomos_DataScience&Date)

---


<div align="center">
  <strong>Desenvolvido com ❤️ Givanildo Gramacho - I2A2 Curso de agentes inteligentes 2025</strong>
</div>
