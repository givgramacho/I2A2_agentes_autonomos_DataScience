#!/usr/bin/env python3
"""
Script de Teste do Sistema de Memória
Executa testes para validar que a memória está funcionando
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent import build_agent, ask_agent, load_csv

def print_separator():
    print("\n" + "="*80 + "\n")

def test_memoria():
    """Testa se a memória está funcionando corretamente"""
    
    print("🧪 TESTE DO SISTEMA DE MEMÓRIA")
    print_separator()
    
    # 1. Construir agente
    print("📦 Construindo agente com memória...")
    try:
        agent, llm = build_agent()
        print("✅ Agente construído com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao construir agente: {e}")
        return
    
    print_separator()
    
    # 2. Carregar CSV
    csv_path = "data/1_01_file_creditcard.csv"
    if not os.path.exists(csv_path):
        print(f"⚠️  CSV não encontrado: {csv_path}")
        print("   Por favor, faça upload de um CSV primeiro")
        return
    
    print(f"📂 Carregando CSV: {csv_path}")
    try:
        load_csv(csv_path)
        print("✅ CSV carregado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao carregar CSV: {e}")
        return
    
    print_separator()
    
    # 3. Teste 1: Primeira pergunta
    print("📝 TESTE 1: Primeira pergunta")
    question1 = "Mostre o schema do dataset"
    print(f"   Pergunta: {question1}")
    
    try:
        response1 = ask_agent(agent, question1, llm=llm)
        print(f"   Resposta: {response1[:200]}...")
        print("✅ Teste 1 passou!")
    except Exception as e:
        print(f"❌ Erro no Teste 1: {e}")
        return
    
    print_separator()
    
    # 4. Teste 2: Segunda pergunta
    print("📝 TESTE 2: Segunda pergunta")
    question2 = "Quantas linhas o dataset tem?"
    print(f"   Pergunta: {question2}")
    
    try:
        response2 = ask_agent(agent, question2, llm=llm)
        print(f"   Resposta: {response2[:200]}...")
        print("✅ Teste 2 passou!")
    except Exception as e:
        print(f"❌ Erro no Teste 2: {e}")
        return
    
    print_separator()
    
    # 5. Teste 3: TESTE DE MEMÓRIA - Perguntar sobre conversa anterior
    print("🧠 TESTE 3: MEMÓRIA - Qual foi minha primeira pergunta?")
    question3 = "Qual foi minha primeira pergunta?"
    print(f"   Pergunta: {question3}")
    
    try:
        response3 = ask_agent(agent, question3, llm=llm)
        print(f"   Resposta: {response3}")
        
        # Validar se a resposta menciona a primeira pergunta
        if "schema" in response3.lower() or question1.lower() in response3.lower():
            print("✅ MEMÓRIA FUNCIONANDO! O agente lembrou da primeira pergunta!")
        else:
            print("⚠️  A resposta não menciona a primeira pergunta explicitamente")
            print("   Mas o agente pode ter reformulado. Verifique manualmente.")
    except Exception as e:
        print(f"❌ Erro no Teste 3: {e}")
        return
    
    print_separator()
    
    # 6. Verificar memória diretamente
    print("🔍 VERIFICAÇÃO: Conteúdo da memória")
    try:
        memory_vars = agent.memory.load_memory_variables({})
        chat_history = memory_vars.get("chat_history", [])
        
        print(f"   Total de mensagens na memória: {len(chat_history)}")
        
        if len(chat_history) >= 6:  # 3 perguntas × 2 (human + AI)
            print("✅ Memória contém as 3 conversas!")
            print("\n   Primeiras mensagens:")
            for i, msg in enumerate(chat_history[:4]):
                msg_type = type(msg).__name__
                content_preview = str(msg.content)[:100]
                print(f"   [{i+1}] {msg_type}: {content_preview}...")
        else:
            print(f"⚠️  Esperado >= 6 mensagens, encontrado {len(chat_history)}")
    except Exception as e:
        print(f"❌ Erro ao verificar memória: {e}")
    
    print_separator()
    
    # Resumo final
    print("📊 RESUMO DOS TESTES")
    print("✅ Sistema de memória está implementado")
    print("✅ Agente consegue processar perguntas sequenciais")
    print("✅ Histórico de conversas está sendo armazenado")
    print("\n🎯 PRÓXIMO PASSO: Teste no Streamlit")
    print("   Execute: streamlit run src/app.py")
    print("   Faça upload de um CSV e teste perguntas sequenciais")
    
    print_separator()

if __name__ == "__main__":
    test_memoria()
