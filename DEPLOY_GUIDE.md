# 🚀 Guia Completo de Deploy - Streamlit Cloud

## 📋 Pré-requisitos

- [ ] Conta no GitHub
- [ ] Repositório criado no GitHub
- [ ] Código commitado
- [ ] API Key do Google Gemini

---

## 📦 Passo 1: Preparar Repositório GitHub

### 1.1 Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Nome do repositório: `agentes_engenheiro_dados`
3. Descrição: `Agente autônomo de análise exploratória de dados com LangChain`
4. Público ou Privado: **Público**
5. **NÃO** adicione README, .gitignore ou LICENSE (já temos)
6. Clique em **"Create repository"**

### 1.2 Conectar Repositório Local

```bash
# No terminal, dentro da pasta do projeto
git init
git add .
git commit -m "Initial commit - Agente EDA com memória"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/agentes_engenheiro_dados.git
git push -u origin main
```

**Substitua `SEU-USUARIO` pelo seu nome de usuário do GitHub!**

### 1.3 Verificar no GitHub

Acesse: `https://github.com/SEU-USUARIO/agentes_engenheiro_dados`

Verifique que os arquivos estão lá:
- ✅ `src/app.py`
- ✅ `src/agent.py`
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `.gitignore`
- ❌ `.env` (NÃO deve aparecer - protegido)

---

## 🌐 Passo 2: Deploy no Streamlit Cloud

### 2.1 Acessar Streamlit Cloud

1. Acesse: https://share.streamlit.io
2. Clique em **"Sign in"**
3. Escolha **"Continue with GitHub"**
4. Autorize o Streamlit a acessar sua conta GitHub

### 2.2 Criar Novo App

1. Clique no botão **"New app"** (canto superior direito)

2. Preencha os campos:

   - **Repository:** `SEU-USUARIO/agentes_engenheiro_dados`
   - **Branch:** `main`
   - **Main file path:** `src/app.py`
   - **App URL (optional):** `agente-eda` (ou deixe auto-gerar)

3. **IMPORTANTE:** Clique em **"Advanced settings..."**

### 2.3 Configurar Secrets (API Keys)

Em **"Advanced settings"**, clique na aba **"Secrets"**

Cole o seguinte (substituindo `SUA_CHAVE_AQUI`):

```toml
# Secrets para o agente EDA

LLM_PROVIDER = "gemini"
LLM_MODEL = "gemini-2.0-flash-exp"

# API Key do Google Gemini
GOOGLE_API_KEY = "SUA_CHAVE_GOOGLE_AQUI"

# LangSmith (opcional - deixe false se não usar)
LANGSMITH_TRACING = "false"
LANGSMITH_API_KEY = ""

# Se usar OpenAI, descomente e adicione:
# OPENAI_API_KEY = "SUA_CHAVE_OPENAI_AQUI"
```

**⚠️ NUNCA commite secrets no GitHub! Use apenas o Streamlit Secrets.**

### 2.4 Deploy

1. Clique em **"Deploy!"**
2. Aguarde 2-3 minutos (você verá logs de instalação)
3. Quando aparecer **"Your app is live!"**, está pronto!

---

## ✅ Passo 3: Testar o App

### 3.1 Acessar Aplicação

Sua URL será algo como:

```
https://agente-eda-seu-usuario.streamlit.app
```

Ou

```
https://share.streamlit.io/seu-usuario/agentes_engenheiro_dados/main/src/app.py
```

### 3.2 Testar Funcionalidades

1. **Upload CSV:**
   - Clique em "📁 Upload CSV"
   - Faça upload de `creditcard.csv` ou qualquer CSV

2. **Fazer Perguntas:**
   ```
   - "Mostre o schema do dataset"
   - "Crie um histograma da coluna Amount"
   - "Qual foi minha primeira pergunta?" (teste de memória)
   ```

3. **Gerar Conclusão:**
   - Clique em "📝 Gerar Conclusão Final"

---

## 🔧 Passo 4: Atualizar o README

### 4.1 Atualizar Links no README.md

Edite o arquivo `README.md` e substitua:

```markdown
# ANTES:
👉 **[Acessar Agente EDA Online](https://seu-app.streamlit.app)**

# DEPOIS:
👉 **[Acessar Agente EDA Online](https://agente-eda-seu-usuario.streamlit.app)**
```

### 4.2 Commit e Push

```bash
git add README.md
git commit -m "Update: Link da aplicação online"
git push
```

---

## 🐛 Solução de Problemas

### Problema 1: "ModuleNotFoundError"

**Causa:** Dependência faltando em `requirements.txt`

**Solução:**
```bash
# Local: instale a dependência
pip install nome-da-dependencia

# Adicione ao requirements.txt
pip freeze > requirements.txt

# Commit
git add requirements.txt
git commit -m "Fix: Add missing dependency"
git push
```

O Streamlit Cloud fará redeploy automaticamente.

---

### Problema 2: "Invalid API Key"

**Causa:** API Key não configurada ou inválida

**Solução:**

1. No Streamlit Cloud, vá em **Settings** → **Secrets**
2. Verifique se `GOOGLE_API_KEY` está correto
3. Teste a chave localmente primeiro:
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_API_KEY')[:10])"
   ```
4. Clique em **"Save"** e espere redeploy

---

### Problema 3: App Muito Lento

**Causa:** Cold start ou processamento pesado

**Soluções:**

1. **Otimizar imports:**
   ```python
   # Em vez de importar tudo no topo
   # Importe apenas quando necessário
   
   @st.cache_resource
   def load_model():
       from langchain_google_genai import ChatGoogleGenerativeAI
       return ChatGoogleGenerativeAI(...)
   ```

2. **Usar cache:**
   ```python
   @st.cache_data
   def load_csv(path):
       return pd.read_csv(path)
   ```

3. **Reduzir max_iterations:**
   ```python
   # Em agent.py
   max_iterations=5  # em vez de 10
   ```

---

### Problema 4: ".env aparece no GitHub"

**Causa:** .gitignore não funcionou

**Solução URGENTE:**

```bash
# 1. Remover .env do tracking
git rm --cached .env

# 2. Verificar .gitignore
echo ".env" >> .gitignore

# 3. Commit
git add .gitignore
git commit -m "Fix: Remove .env from tracking"
git push

# 4. REVOKE a API Key no Google Cloud Console
# 5. Gere uma nova chave
# 6. Atualize no Streamlit Secrets
```

---

## 📊 Monitoramento

### Ver Logs em Tempo Real

1. No Streamlit Cloud, clique no seu app
2. No menu hamburger (☰), clique em **"Manage app"**
3. Aba **"Logs"** mostra erros e prints

### Métricas do App

- **Uptime:** 99%+ esperado
- **Response time:** 2-5 segundos
- **Visitors:** Até 1 milhão/mês (plano free)

---

## 🔄 Atualizar App (Redeploy)

### Automático (Recomendado)

```bash
# Faça suas mudanças
git add .
git commit -m "Feature: Nova ferramenta de análise"
git push
```

O Streamlit Cloud detecta automaticamente e faz redeploy!

### Manual

1. No Streamlit Cloud, clique no app
2. Menu hamburger (☰) → **"Reboot app"**

---

## 📝 Checklist Final

Antes de entregar o relatório, verifique:

- [ ] App está online e acessível
- [ ] README.md tem o link correto
- [ ] Secrets configurados no Streamlit Cloud
- [ ] `.env` NÃO está no GitHub
- [ ] Todas as 18 ferramentas funcionam
- [ ] Memória está funcionando
- [ ] Gráficos são gerados corretamente
- [ ] Conclusão automática funciona
- [ ] URL do app adicionada no relatório LaTeX

---

## 🎯 URLs Finais

Depois do deploy, atualize estas URLs:

### 1. No README.md
```markdown
**Link da Aplicação:** https://agente-eda-seu-usuario.streamlit.app
```

### 2. No relatório LaTeX (relatorio.tex)
```latex
\url{https://agente-eda-seu-usuario.streamlit.app}
```

### 3. No relatório PDF
Compile o LaTeX e gere o PDF com as URLs corretas.

---

## 🎉 Pronto!

Agora você tem:

✅ Código no GitHub  
✅ App online no Streamlit Cloud  
✅ README completo  
✅ Relatório LaTeX pronto  
✅ Secrets protegidos  

**Link do seu app:**
```
https://agente-eda-seu-usuario.streamlit.app
```

**Compartilhe este link no relatório e com o professor!** 🚀

---

## 📞 Suporte

**Streamlit Community:**
- https://discuss.streamlit.io/

**LangChain Discord:**
- https://discord.gg/langchain

**GitHub Issues:**
- https://github.com/SEU-USUARIO/agentes_engenheiro_dados/issues

---

**Desenvolvido com ❤️ por [Seu Nome]**
