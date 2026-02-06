# python/run_horaculo.py
import os
import argparse
import sys

# Adiciona o diretório 'app' ao path para garantir que as importações internas funcionem
# se estiver a executar a partir da pasta 'python/'
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    # Tenta importar do pacote app (estrutura recomendada)
    from app.orchestrator import run_query
except ImportError:
    # Fallback se os ficheiros estiverem todos na mesma pasta
    from orchestrator import run_query

def main():
    parser = argparse.ArgumentParser(description="Horaculo V2 CLI Runner")
    parser.add_argument("--newsapi_key", default=os.getenv("NEWSAPI_KEY"), help="API Key for NewsAPI")
    parser.add_argument("--query", default="oil OR petroleum OR OPEC", help="Search query for analysis")
    parser.add_argument("--use_openai", action="store_true", help="Use OpenAI for summarization instead of local model")
    parser.add_argument("--openai_key", default=os.getenv("OPENAI_API_KEY"), help="OpenAI API Key")
    
    args = parser.parse_args()

    print(f"--- Iniciando Horaculo V2 ---")
    print(f"Query: {args.query}")
    print(f"Mode: {'OpenAI (GPT)' if args.use_openai else 'Local (HuggingFace)'}")

    try:
        # A função run_query do orchestrator já lida com:
        # 1. Fetch (NewsAPI ou RSS Fallback)
        # 2. Embeddings & Dedupe
        # 3. Análise C++ (Core)
        # 4. Sentimento & Resumo
        res = run_query(
            query=args.query, 
            newsapi_key=args.newsapi_key, 
            use_openai=args.use_openai, 
            openai_key=args.openai_key
        )

        print("\n=== VEREDICTO (Core C++) ===")
        verdict = res.get("verdict", {})
        print(f"Conflito Detectado: {verdict.get('is_conflict')}")
        print(f"Fonte Vencedora:    {verdict.get('winner_source')}")
        print(f"Intensidade:        {verdict.get('intensity'):.4f}")
        print(f"Manipulação:        {verdict.get('manipulation')}")

        if res.get("eden_signal", {}).get("detected"):
            print(f"\n*** EDEN'S INSIGHT DETECTADO ***")
            print(f"Fonte do Sinal: {res['eden_signal']['source']}")

        print("\n=== RELATÓRIO ESTRATÉGICO ===\n")
        print(res.get("summary"))
        
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Falha na execução do pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
