HORACULO — Financial News Narrative Analysis Engine
Horaculo is an open-source system for analyzing coordination, divergence, and entropy across financial news sources.
It ingests multiple articles simultaneously and quantifies narrative alignment using embedding similarity, clustering techniques, and historical source weighting.
The system is designed for research and quantitative experimentation.
Overview
Financial markets react not only to numerical data but also to narratives.
Different outlets may:
Emphasize different aspects of the same event
Converge on similar framing
Diverge significantly in interpretation
Horaculo attempts to quantify these structural patterns using embedding-based similarity analysis.
This project does not claim to detect intentional manipulation.
It measures structural alignment and divergence across sources.
Core Features
Multi-source ingestion (NewsAPI / RSS)
Claim-level embedding generation (HuggingFace)
High-performance cosine similarity engine (C++ + AVX2)
INT8 embedding quantization
Clustering and entropy estimation
Cross-source coordination scoring
Rolling credibility model per source
Structured JSON output for downstream systems
Optional React dashboard
Telegram alert integration
Architecture
Analysis Pipeline
Copiar código

NewsAPI / RSS
    ↓
Ingestion (text, source, timestamp)
    ↓
Claim Extraction
    ↓
Embedding Generation (HuggingFace)
    ↓
Deduplication (similarity threshold)
    ↓
C++ Similarity Engine (AVX2 + INT8)
    ↓
Clustering + Entropy Metrics
    ↓
Credibility Weighting
    ↓
Structured JSON Output
C++ Core
The similarity engine is implemented in C++ for performance-critical operations.
Optimizations include:
INT8 quantization (4× memory reduction)
AVX2 SIMD vectorized cosine similarity
PyBind11 integration with Python
Benchmark
~1.4s per query (10–20 sources)
~100 queries/minute
~150MB memory footprint (SQLite mode)
Python-only baseline: ~12 seconds
Current implementation is single-threaded.
Installation
Option 1 — Docker (Recommended)
Bash
Copiar código
git clone https://github.com/your-username/horaculo.git
cd horaculo
docker-compose up
Run analysis:
Bash
Copiar código
python python/run_horaculo.py --newsapi_key YOUR_KEY --query "oil OR petroleum"
Option 2 — Local Setup
Bash
Copiar código
pip install -r requirements.txt
python setup.py build_ext --inplace

export NEWSAPI_KEY="your_key"
export OPENAI_API_KEY="optional"

python python/run_horaculo.py --query "apple stock"
Example CLI Usage
Bash
Copiar código
python run_horaculo.py --query "oil OR OPEC"
python run_horaculo.py --query "Federal Reserve" --use_openai
python run_horaculo.py --query "gold prices"
Example Output
Json
Copiar código
{
  "verdict": {
    "dominant_source": "Reuters",
    "intensity": 0.85,
    "entropy": 1.92,
    "inconclusive": false
  },
  "coordination": {
    "score": 0.72,
    "crowded": false
  },
  "hard_data": {
    "percentages": ["+12.5%", "-8.3%"],
    "monetary": ["$142.50", "$8.2B"]
  }
}
Source Credibility Model
Each source maintains a rolling credibility profile:
Json
Copiar código
{
  "source": "Reuters",
  "total_scans": 342,
  "consensus_hits": 289,
  "credibility_score": 0.85
}
Weights are dynamically adjusted based on historical agreement patterns.
Evaluation Strategy
Horaculo does not rely on labeled “manipulation” datasets.
Evaluation focuses on structural consistency and reproducibility.
1. Reproducibility Tests
Stability of coordination score across short time windows
Entropy drift analysis
Cluster persistence measurement
2. Cross-Embedding Comparison
Run queries with different embedding models and compare:
Cluster similarity
Coordination variance
Entropy stability
3. Historical Event Backtesting
Analyze known macro events:
FOMC announcements
OPEC meetings
Earnings releases
Measure structural changes in entropy and coordination.
4. Synthetic Stress Testing
Inject duplicated or paraphrased articles to validate:
Deduplication threshold behavior
Quantization precision
Cluster sensitivity
5. Performance Validation
Compare C++ AVX2 vs Python baseline
Measure cosine deviation under INT8 quantization
Benchmark scaling behavior
Environment Variables
Copiar código

NEWSAPI_KEY=your_newsapi_token
OPENAI_API_KEY=optional
DATABASE_URL=postgresql://...
TELEGRAM_BOT_TOKEN=optional
TELEGRAM_CHAT_ID=optional
Build C++ Core Manually
Bash
Copiar código
cd src
g++ -O3 -march=native -shared -fPIC core.cpp -o core.so \
    `python3 -m pybind11 --includes` \
    `python3-config --includes --ldflags`
Limitations
No labeled ground truth for coordination detection
Entropy modeling is heuristic-based
Embedding model selection impacts clustering quality
NewsAPI rate limits apply
Single-threaded C++ core
Not intended as financial advice
This project is intended for research and experimentation.
Roadmap
Multi-threaded similarity engine
FAISS benchmarking comparison
Streaming ingestion mode (WebSocket)
Expanded asset coverage (crypto, forex)
Automated retraining pipeline
Contributing
Fork the repository
Create a branch (git checkout -b feature/xyz)
Commit changes
Open a pull request
License
MIT
