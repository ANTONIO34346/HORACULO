// App.js
import React, { useState } from 'react';
import { 
  Radar, Activity, Zap, Terminal, Search, 
  AlertTriangle, Lock, Cpu, Coins, Skull, 
  Rocket, Shield, Eye 
} from 'lucide-react';
import { 
  ScatterChart, Scatter, XAxis, YAxis, Tooltip, 
  ResponsiveContainer, ReferenceLine 
} from 'recharts';

// ==========================================
// CONFIGURAÇÃO DE CORES
// ==========================================
const COLORS = {
  GOLD: '#FFD700', RED: '#EF4444', ORANGE: '#F97316', 
  GREEN: '#10B981', PURPLE: '#A855F7', BG: '#0f172a'
};

// ==========================================
// MOCK DATA (ATUALIZADO COM CRIPTO)
// ==========================================
const MOCK_PAYLOAD = {
  screen_arbitrage: {
    points: [
      { x: 0.8, y: 0.95, source: "Reuters", sentiment: 0.8 },
      { x: -0.4, y: 0.6, source: "CNN", sentiment: -0.4 },
    ],
    eden: { detected: true, source: "Reuters" },
    conflict_intensity: 0.85
  },
  screen_stress: { mood: "Medo", is_trap: true, entropy: 1.9 },
  screen_intelligence: { coordination: 0.72, clusters: [] },
  screen_portal: { summary: "Resumo Macro...", hard_data: { percentages: [], monetary: [] }, stats: { time: "1.42s" } },
  // 🔹 NOVO PAYLOAD DO SATÉLITE
  screen_crypto: {
    asset: "SOLANA",
    action_signal: { code: "TRAP / FAKE PUMP", color: "#FACC15", icon: "eye" }, // Yellow
    metrics: { conflict_intensity: 0.88, sentiment_gap: 0.65, is_panic: false },
    hard_data: { monetary: ["$142.50"], percentages: ["+12%"] },
    signals: [
      { source: "Whale Alert", text: "🚨 500,000 SOL transferred to Binance" },
      { source: "X (Alpha)", text: "Retail is euphoric, funding rates too high." }
    ]
  }
};

// ==========================================
// 5ª TELA: CRYPTO SATELLITE (NOVA)
// ==========================================
const ScreenCrypto = ({ data }) => {
  const { action_signal, metrics, hard_data, signals } = data;
  
  // Mapeamento de Ícones Dinâmicos
  const IconMap = {
    "skull": <Skull size={80} color={action_signal.color} />,
    "rocket": <Rocket size={80} color={action_signal.color} />,
    "shield": <Shield size={80} color={action_signal.color} />,
    "eye": <Eye size={80} color={action_signal.color} />
  };

  return (
    <div className="h-full flex flex-col p-4 relative overflow-hidden">
      {/* Background Glow baseado no sinal */}
      <div className="absolute inset-0 opacity-10 pointer-events-none" 
           style={{ backgroundColor: action_signal.color }}></div>

      <div className="flex justify-between items-center mb-6 relative z-10">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Coins className="text-purple-400"/> SATELLITE: {data.asset}
        </h2>
        <span className="font-mono text-xs text-slate-500">LIVE FEED RSS+ONCHAIN</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full relative z-10">
        
        {/* ESQUERDA: COCKPIT DE DECISÃO */}
        <div className="flex flex-col gap-4">
          {/* 1. O SINAL MESTRE */}
          <div className="flex-1 bg-slate-900/80 border-2 rounded-2xl flex flex-col items-center justify-center p-6 shadow-2xl transition-all duration-500"
               style={{ borderColor: action_signal.color }}>
            <div className="animate-pulse mb-4">
              {IconMap[action_signal.icon] || <Activity size={80} color={action_signal.color}/>}
            </div>
            <h1 className="text-4xl font-black tracking-tighter text-center" style={{ color: action_signal.color }}>
              {action_signal.code}
            </h1>
            <p className="text-slate-400 text-sm mt-2 font-mono">ACTION SIGNAL</p>
          </div>

          {/* 2. MÉTRICAS RÁPIDAS */}
          <div className="bg-slate-800 p-4 rounded-xl border border-slate-700">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>NARRATIVE CONFLICT (WHALES vs RETAIL)</span>
              <span>{(metrics.conflict_intensity * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-slate-700 h-2 rounded-full mb-4">
              <div className="h-2 rounded-full transition-all duration-1000"
                   style={{ width: `${metrics.conflict_intensity * 100}%`, backgroundColor: action_signal.color }}></div>
            </div>
            <div className="flex gap-2">
              {hard_data.monetary.map((m, i) => (
                 <span key={i} className="bg-slate-900 text-white text-xs px-2 py-1 rounded font-mono border border-slate-700">{m}</span>
              ))}
              {hard_data.percentages.map((p, i) => (
                 <span key={i} className="bg-slate-900 text-green-400 text-xs px-2 py-1 rounded font-mono border border-slate-700">{p}</span>
              ))}
            </div>
          </div>
        </div>

        {/* DIREITA: FEED DE SINAIS ISOLADOS */}
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 overflow-y-auto">
          <h3 className="text-slate-400 text-xs font-bold mb-4 flex items-center gap-2">
            <Activity size={12}/> SINAIS DETECTADOS
          </h3>
          {signals.map((s, i) => (
            <div key={i} className="mb-3 p-3 bg-slate-900 rounded border-l-2 border-slate-700 hover:border-purple-500 transition-colors">
              <div className="flex justify-between items-center mb-1">
                <span className="text-purple-400 text-[10px] font-bold uppercase">{s.source}</span>
              </div>
              <p className="text-slate-300 text-sm leading-snug line-clamp-2">{s.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ... (ScreenArbitrage, ScreenIntelligence, ScreenStress mantêm-se iguais ao anterior) ...

// TELA PORTAL (ATUALIZADA)
const ScreenPortal = ({ onSearch, loading, logs, result }) => {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("MACRO"); // MACRO | CRYPTO

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) onSearch(query, mode);
  };

  return (
    <div className="h-full p-6 flex flex-col max-w-4xl mx-auto justify-center">
      <div className="text-center mb-10">
        <h1 className="text-5xl font-black text-white tracking-tighter mb-2">HORACULO</h1>
        <p className="text-slate-400">Sistema de Inteligência Assimétrica</p>
      </div>

      {/* Mode Switcher */}
      <div className="flex justify-center gap-4 mb-6">
        <button onClick={() => setMode("MACRO")} className={`px-4 py-2 rounded-full text-xs font-bold transition ${mode==="MACRO" ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-500'}`}>MACRO MARKET</button>
        <button onClick={() => setMode("CRYPTO")} className={`px-4 py-2 rounded-full text-xs font-bold transition ${mode==="CRYPTO" ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-500'}`}>CRYPTO SATELLITE</button>
      </div>

      <form onSubmit={handleSubmit} className="relative w-full max-w-lg mx-auto">
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={mode === "CRYPTO" ? "Ex: SOL, BTC, ETH..." : "Ex: Oil, Gold, FED..."}
          className={`w-full bg-slate-900 text-white text-lg p-4 pl-12 rounded-xl border-2 outline-none transition shadow-2xl ${mode==="CRYPTO" ? 'border-purple-900 focus:border-purple-500' : 'border-slate-800 focus:border-blue-500'}`}
          disabled={loading}
        />
        <Search className="absolute left-4 top-5 text-slate-500" />
        <button 
          type="submit" 
          disabled={loading}
          className={`absolute right-2 top-2 px-6 py-2 rounded-lg font-bold transition text-white ${loading ? 'bg-slate-700' : (mode==="CRYPTO" ? 'bg-purple-600 hover:bg-purple-500' : 'bg-blue-600 hover:bg-blue-500')}`}
        >
          {loading ? 'SCANNING...' : 'IGNITE'}
        </button>
      </form>

      {/* Logs Area */}
      {loading && (
        <div className="mt-8 bg-slate-950 p-4 rounded-lg font-mono text-xs text-green-400 h-32 overflow-y-auto border border-slate-800 w-full max-w-lg mx-auto">
          {logs.map((log, i) => <div key={i}>{`> ${log}`}</div>)}
          <div className="animate-pulse">_</div>
        </div>
      )}
    </div>
  );
};

// APP CONTROLLER
export default function HoraculoApp() {
  const [activeScreen, setActiveScreen] = useState('portal');
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [data, setData] = useState(null);

  const handleSearch = async (query, mode) => {
    setLoading(true);
    setLogs([]);
    setData(null);

    // Lógica de Logs Simulada
    addLog(`Iniciando motor em modo: ${mode}...`);
    await sleep(500);
    
    if (mode === 'CRYPTO') {
       addLog("Conectando ao Satélite Cripto (Isolado)...");
       addLog("Lendo Whale Alert & RSS Feeds...");
       addLog("C++ Core: Detectando manipulação de preço...");
    } else {
       addLog("Conectando NewsAPI Global...");
       addLog("C++ Core: Vetorizando narrativas macro...");
    }
    await sleep(1000);
    addLog("Finalizando análise...");

    // AQUI ENTRA O FETCH REAL:
    // const endpoint = mode === 'CRYPTO' ? '/analyze/crypto' : '/analyze/submit';
    // const res = await fetch(endpoint, ...);
    
    // MOCK PARA DEMO
    setData(MOCK_PAYLOAD);
    setLoading(false);
    
    // Auto-navegação inteligente
    setActiveScreen(mode === 'CRYPTO' ? 'crypto' : 'arbitrage');
  };

  const addLog = (msg) => setLogs(p => [...p, msg]);
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 font-sans overflow-hidden">
      {/* SIDEBAR */}
      <div className="w-20 bg-slate-900 border-r border-slate-800 flex flex-col items-center py-6 gap-6 z-20">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center font-bold text-white">H</div>
        
        <NavBtn icon={<Search size={24}/>} active={activeScreen === 'portal'} onClick={() => setActiveScreen('portal')} />
        <div className="w-full h-px bg-slate-800 my-2"></div>
        <NavBtn icon={<Radar size={24}/>} active={activeScreen === 'arbitrage'} onClick={() => setActiveScreen('arbitrage')} />
        <NavBtn icon={<Lock size={24}/>} active={activeScreen === 'intelligence'} onClick={() => setActiveScreen('intelligence')} />
        <NavBtn icon={<Activity size={24}/>} active={activeScreen === 'stress'} onClick={() => setActiveScreen('stress')} />
        <div className="w-full h-px bg-slate-800 my-2"></div>
        {/* BOTÃO DA 5ª TELA */}
        <NavBtn icon={<Coins size={24}/>} active={activeScreen === 'crypto'} onClick={() => setActiveScreen('crypto')} color="text-purple-400" />
      </div>

      {/* CONTENT */}
      <div className="flex-1 relative">
        {activeScreen === 'portal' && <ScreenPortal onSearch={handleSearch} loading={loading} logs={logs} />}
        {data && activeScreen === 'arbitrage' && <ScreenArbitrage data={data.screen_arbitrage} />} // Requer componente anterior
        {data && activeScreen === 'crypto' && <ScreenCrypto data={data.screen_crypto} />}
        {/* Outras telas... */}
      </div>
    </div>
  );
}

const NavBtn = ({ icon, active, onClick, color }) => (
  <button onClick={onClick} className={`p-3 rounded-xl transition-all ${active ? 'bg-slate-800 text-white scale-110 shadow-lg' : 'text-slate-500 hover:text-white'} ${color}`}>
    {icon}
  </button>
);
