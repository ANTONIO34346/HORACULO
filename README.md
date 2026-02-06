# HORACULO — Detecção de Padrões em Notícias com IA

> Sistema de análise em tempo real que detecta manipulação, conflitos narrativos e sinais de oportunidade em notícias financeiras.

## 🎯 O Que Faz

**Horaculo** analisa múltiplas fontes de notícias simultaneamente e:

✅ Detecta **conflitos narrativos** (quando fontes dizem coisas contraditórias)  
✅ Identifica **manipulação coordenada** (quando várias fontes falam a mesma coisa suspeita)  
✅ Calcula **psicologia do mercado** (medo, euforia, armadilhas)  
✅ Extrai **dados duros** (valores, percentuais, eventos)  
✅ Memoriza **histórico de fontes** (qual fonte foi certa antes?)  
✅ Gera **sinais de oportunidade** (EDEN SIGNALS)  

## 🚀 Quick Start (3 minutos)

### Opção 1: Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/horaculo.git
cd horaculo

# Suba com Docker Compose
docker-compose up

# Em outro terminal, rode a análise
python python/run_horaculo.py --newsapi_key YOUR_KEY --query "oil OR petroleum"
```

### Opção 2: Local (Python)

```bash
# Instale dependências
pip install -r requirements.txt

# Compile o motor C++
python setup.py build_ext --inplace

# Configure as variáveis de ambiente
export NEWSAPI_KEY="sua_chave_aqui"
export OPENAI_API_KEY="sua_chave_openai"  # Opcional

# Execute
python python/run_horaculo.py --query "apple stock"
```

## 📊 Exemplo de Uso

```bash
# Análise de petróleo
python run_horaculo.py --query "oil OR petroleum OR OPEC"

# Análise com resumo OpenAI
python run_horaculo.py --query "Federal Reserve" --use_openai --openai_key sk-xxx

# Custom threshold
python run_horaculo.py --query "gold prices" --newsapi_key xxx
```

## 📈 Output

Você recebe um JSON estruturado com:

```json
{
  "verdict": {
    "winner_source": "Reuters",
    "intensity": 0.85,
    "entropy": 1.92,
    "inconclusive": false
  },
  "eden_signal": {
    "detected": true,
    "source": "Reuters",
    "confidence": 0.92
  },
  "psychology": {
    "mood": "Medo",
    "is_trap": true,
    "is_crowded": false,
    "asymmetry_level": 0.67
  },
  "summary": "Análise estratégica em linguagem natural...",
  "hard_data": {
    "percentages": ["+12.5%", "-8.3%"],
    "monetary": ["$142.50", "$8.2B"]
  },
  "ui": {
    "screen_arbitrage": {...},
    "screen_intelligence": {...},
    "screen_stress": {...},
    "screen_portal": {...}
  }
}
```

## 🏗️ Arquitetura

### Stack Técnico

| Camada | Tecnologia | Função |
|--------|-----------|--------|
| **Frontend** | React + Tailwind | 5 telas de dashboard |
| **Backend** | Python 3.9+ | Orquestração do pipeline |
| **Motor** | C++ + AVX2 | Análise de embeddings INT8 |
| **Persistência** | SQLite / Postgres | Memória de fontes |
| **Infra** | Docker Compose | Deploy em 1 comando |

### Pipeline de Análise

```
NewsAPI/RSS Feeds
    ↓
[Ingest] → Extrai texto, fonte, timestamp
    ↓
[Embeddings] → Vetoriza claims com HuggingFace
    ↓
[Dedupe] → Remove duplicatas (similarity > 0.92)
    ↓
[C++ Core] → Cosine similarity com AVX2 + INT8 quantização
    ↓
[Memory] → Atualiza perfil de credibilidade da fonte
    ↓
[Psychology] → Analisa sentimento + coordenação
    ↓
[Summary] → Gera insights com HuggingFace ou OpenAI
    ↓
JSON Estruturado + Alertas Telegram
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Obrigatório
NEWSAPI_KEY=seu_token_newsapi  # Grátis em https://newsapi.org

# Opcional
OPENAI_API_KEY=sk-xxx           # Para resumos premium
DATABASE_URL=postgresql://...   # Postgres em produção
TELEGRAM_BOT_TOKEN=xxx          # Para alertas
```

### Arquivos Principais

```
horaculo/
├── python/
│   ├── run_horaculo.py          # CLI entry point
│   ├── orchestrator.py          # Pipeline principal
│   ├── app/
│   │   ├── alerts.py            # Telegram notifications
│   │   ├── anti_manipulation.py # Detecção de coordenação
│   │   ├── cache.py             # Redis/local cache
│   │   ├── claim_extract.py     # NLP para claims
│   │   ├── clustering.py        # K-means no embeddings
│   │   ├── crypto.py            # Análise de cripto
│   │   ├── data_extractor.py    # Extrai números e datas
│   │   ├── dedupe.py            # Remove duplicatas
│   │   ├── embeddings.py        # HuggingFace vectors
│   │   ├── ingest.py            # Fetch de NewsAPI
│   │   ├── memory.py            # SQLite/Postgres
│   │   ├── psychology.py        # Análise psicológica
│   │   ├── sentiment.py         # Sentiment scores
│   │   └── summarizer.py        # Resumos com HF ou OpenAI
│   └── requirements.txt
├── src/
│   └── core.cpp                 # Motor C++ com AVX2
├── app/
│   ├── App.js                   # React frontend
│   ├── App.jss                  # Mobile variant
│   └── package.json
├── docker-compose.yml           # Deploy pronto
└── README.md
```

## 📊 Conceitos-Chave

### EDEN SIGNAL
Detectado quando:
- **Fonte confiável** (histórico >85% correto)
- **Conflito baixo** (intensidade <50%)
- **Padrão emergente** (consenso em baixa intensidade)

Significa: Oportunidade detectada por observador confiável em ambiente consensual.

### Entropy (Entropia)
Mede divergência de opiniões:
- **Baixa (<0.8):** Consenso forte (pode ser manipulação)
- **Alta (>1.8):** Caos narrativo (informação incompleta)
- **Ótima (0.8-1.8):** Mercado refletindo incerteza real

### Coordination Score
Mede se múltiplas fontes estão "lendo do mesmo roteiro":
- **< 0.3:** Narrativas independentes (saudável)
- **> 0.7:** Coordenação suspeita (bandwagon)

## 🎨 Frontend

### 5 Telas Disponíveis

1. **Portal** — Busca e logs em tempo real
2. **Radar Arbitrage** — Scatter plot de sentimento vs confiabilidade
3. **Intelligence** — Clusters de narrativas + coordination score
4. **Stress** — Psicologia do mercado (mood, traps, crowding)
5. **Crypto** — Satélite isolado para análise de blockchain

Acesse em: `http://localhost:3000`

## 💻 Compilar C++

```bash
# Requer: GCC/Clang + Python dev headers
cd src
g++ -O3 -march=native -shared -fPIC core.cpp -o core.so \
    `python3 -m pybind11 --includes` \
    `python3-config --includes --ldflags`

# Ou use setup.py
python setup.py build_ext --inplace
```

## 🚨 Alertas Telegram

Horaculo envia alertas automáticos quando:
- EDEN SIGNAL detectado
- Intensidade de conflito > 0.6
- Coordenação suspeita > 0.8

Configure:
```python
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
export TELEGRAM_CHAT_ID="123456789"
```

## 📈 Performance

- **Latência:** ~1.4s por query (10 fontes)
- **Memória:** ~150MB (sqlite in-memory) / ~500MB (postgres)
- **CPU:** Single-threaded, otimizado com AVX2
- **Throughput:** ~100 queries/min em máquina padrão

## 🔐 Segurança

- ✅ Sem API key hardcoded (env vars)
- ✅ SQLite com WAL mode (crash-safe)
- ✅ Validação de embeddings (NaN checks)
- ✅ Rate limiting em NewsAPI (60/min free)

## 📚 Como Contribuir

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/xyz`)
3. Commit (`git commit -m 'Add xyz'`)
4. Push (`git push origin feature/xyz`)
5. Abra um PR

## 🙋 Suporte

- **Docs:** [Documentação Completa](./docs/README.md)
- **Issues:** GitHub Issues
  

## 📝 Licença

MIT License — Use livremente em projetos comerciais e open source.

## 🎓 Inspiração

Horaculo é baseado em pesquisa de:
- Detecção de fake news (Stanford News Lab)
- Análise de sentimento em mercados financeiros
- Teoria da Psicologia do Mercado

## 🌟 Roadmap

- [ ] Suporte a múltiplas moedas (cripto + forex)
- [ ] ML retraining automático (feedback dos sinais)
- [ ] WebSocket para real-time streaming
- [ ] Mobile app (React Native)
- [ ] Integração com trading bots

---

**Feito com ❤️ por [ANTÔNIO]**

*"A verdade emerge quando observamos múltiplas perspectivas."*

