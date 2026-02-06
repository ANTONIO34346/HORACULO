// App.jss (React Native)
import React, { useState } from 'react';
import { 
  StyleSheet, Text, View, TextInput, TouchableOpacity, 
  ScrollView, SafeAreaView, StatusBar, Dimensions 
} from 'react-native';
import { Svg, Circle, Line, Rect, G, Text as SvgText } from 'react-native-svg';
// Certifique-se de ter instalado: lucide-react-native
import { 
  Radar, Zap, Activity, Terminal, Search, Lock, 
  Coins, Skull, Rocket, Shield, Eye 
} from 'lucide-react-native';

const COLORS = {
  BG: '#020617', PANEL: '#1e293b', ACCENT: '#3b82f6', 
  GOLD: '#FFD700', RED: '#ef4444', GREEN: '#22c55e', 
  PURPLE: '#a855f7', TEXT: '#e2e8f0', MUTED: '#64748b'
};

// ==========================================
// 5ª TELA: CRYPTO SATELLITE (MOBILE)
// ==========================================
const ScreenCrypto = ({ data }) => {
  const signal = data.action_signal;

  // Renderiza ícone dinamicamente
  const renderIcon = () => {
    switch(signal.icon) {
      case 'skull': return <Skull size={80} color={signal.color} />;
      case 'rocket': return <Rocket size={80} color={signal.color} />;
      case 'eye': return <Eye size={80} color={signal.color} />;
      default: return <Shield size={80} color={signal.color} />;
    }
  };

  return (
    <ScrollView style={styles.screenContainer} contentContainerStyle={{paddingBottom: 40}}>
      {/* HEADER ESPECÍFICO */}
      <View style={{flexDirection:'row', alignItems:'center', marginBottom: 20}}>
        <Coins size={20} color={COLORS.PURPLE} style={{marginRight: 10}}/>
        <Text style={[styles.headerTitle, {marginBottom:0, color: COLORS.PURPLE}]}>CRYPTO SATELLITE</Text>
      </View>

      {/* 1. SINAL MESTRE (HERO) */}
      <View style={[styles.heroBox, { borderColor: signal.color, backgroundColor: signal.color + '10' }]}>
        {renderIcon()}
        <Text style={[styles.actionCode, { color: signal.color }]}>{signal.code}</Text>
        <Text style={styles.heroLabel}>AI DECISION</Text>
      </View>

      {/* 2. PROGRESSO DE CONFLITO */}
      <View style={styles.card}>
        <View style={{flexDirection:'row', justifyContent:'space-between'}}>
          <Text style={styles.cardLabel}>WHALE vs RETAIL CLASH</Text>
          <Text style={[styles.statValue, {fontSize: 14}]}>{(data.metrics.conflict_intensity * 100).toFixed(0)}%</Text>
        </View>
        <View style={styles.progressBarBg}>
          <View style={[styles.progressBarFill, { 
            width: `${data.metrics.conflict_intensity * 100}%`,
            backgroundColor: signal.color 
          }]} />
        </View>
      </View>

      {/* 3. HARD DATA CHIPS */}
      <View style={{flexDirection: 'row', flexWrap: 'wrap', marginBottom: 20}}>
        {data.hard_data.monetary.map((val, i) => (
          <View key={i} style={styles.chip}><Text style={styles.chipText}>💰 {val}</Text></View>
        ))}
        {data.hard_data.percentages.map((pct, i) => (
          <View key={i} style={styles.chip}><Text style={[styles.chipText, {color: COLORS.GREEN}]}>📈 {pct}</Text></View>
        ))}
      </View>

      {/* 4. FEED DE SINAIS */}
      <Text style={styles.sectionHeader}>DETECTED SIGNALS</Text>
      {data.signals.map((s, i) => (
        <View key={i} style={styles.listItem}>
          <View style={{width: 3, height: '100%', backgroundColor: COLORS.PURPLE, marginRight: 10}} />
          <View style={{flex: 1}}>
            <Text style={{color: COLORS.PURPLE, fontSize: 10, fontWeight: 'bold'}}>{s.source.toUpperCase()}</Text>
            <Text style={styles.listText} numberOfLines={3}>{s.text}</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

// ... (Componentes ScreenRadar, ScreenStress mantêm-se) ...

// COMPONENTE PRINCIPAL APP
export default function App() {
  const [tab, setTab] = useState('portal');
  const [data, setData] = useState(null); // Em produção, iniciar com null
  const [loading, setLoading] = useState(false);

  // Payload Mockado para Demo
  const MOCK_DATA = {
    screen_crypto: {
      metrics: { conflict_intensity: 0.82 },
      action_signal: { code: "TRAP DETECTED", color: "#FACC15", icon: "eye" },
      hard_data: { monetary: ["$64,200"], percentages: ["-2.4%"] },
      signals: [{ source: "Whale Alert", text: "1,000 BTC moved to Coinbase." }]
    },
    screen_arbitrage: { /* ... dados macro ... */ }
  };

  const handleSearch = (q) => {
    setLoading(true);
    // Simula API
    setTimeout(() => {
      setData(MOCK_DATA);
      setLoading(false);
      // Se a query parece cripto, vai para cripto, senão radar
      if (['btc','eth','sol','crypto'].some(x => q.toLowerCase().includes(x))) {
        setTab('crypto');
      } else {
        setTab('radar');
      }
    }, 1500);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={COLORS.BG} />
      
      <View style={styles.content}>
        {tab === 'portal' && <ScreenPortal onSearch={handleSearch} loading={loading} />}
        {tab === 'radar' && data && <ScreenRadar data={data.screen_arbitrage}/>}
        {tab === 'crypto' && data && <ScreenCrypto data={data.screen_crypto}/>}
        {/* Outras telas... */}
      </View>

      {/* TAB BAR COM 5 BOTÕES */}
      <View style={styles.tabBar}>
        <TabBtn icon={Terminal} label="Portal" active={tab==='portal'} onPress={()=>setTab('portal')} />
        <TabBtn icon={Radar} label="Radar" active={tab==='radar'} onPress={()=>setTab('radar')} />
        <TabBtn icon={Activity} label="Stress" active={tab==='stress'} onPress={()=>setTab('stress')} />
        <TabBtn icon={Lock} label="Intel" active={tab==='intel'} onPress={()=>setTab('intel')} />
        <TabBtn icon={Coins} label="Crypto" active={tab==='crypto'} onPress={()=>setTab('crypto')} color={COLORS.PURPLE}/>
      </View>
    </SafeAreaView>
  );
}

const TabBtn = ({ icon: Icon, label, active, onPress, color }) => (
  <TouchableOpacity style={styles.tabBtn} onPress={onPress}>
    <Icon size={22} color={active ? (color || COLORS.ACCENT) : COLORS.MUTED} />
    <Text style={[styles.tabLabel, {color: active ? (color || COLORS.ACCENT) : COLORS.MUTED}]}>{label}</Text>
  </TouchableOpacity>
);

// ESTILOS ADICIONAIS
const styles = StyleSheet.create({
  // ... (estilos anteriores mantidos) ...
  container: { flex: 1, backgroundColor: COLORS.BG },
  content: { flex: 1, padding: 20 },
  headerTitle: { fontSize: 20, fontWeight: 'bold', color: COLORS.TEXT, marginBottom: 20 },
  
  // Crypto Styles
  heroBox: { padding: 30, borderRadius: 20, alignItems: 'center', borderWidth: 2, marginBottom: 20 },
  actionCode: { fontSize: 28, fontWeight: '900', marginTop: 10, textAlign: 'center' },
  heroLabel: { color: COLORS.MUTED, marginTop: 5, fontSize: 10, letterSpacing: 2 },
  
  chip: { backgroundColor: COLORS.PANEL, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, marginRight: 8, borderWidth: 1, borderColor: '#334155' },
  chipText: { color: COLORS.TEXT, fontSize: 12, fontWeight: 'bold' },
  
  // TabBar Update
  tabBar: { flexDirection: 'row', backgroundColor: COLORS.PANEL, paddingVertical: 10, borderTopWidth: 1, borderTopColor: '#334155' },
  tabBtn: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  tabLabel: { fontSize: 9, marginTop: 4, fontWeight: 'bold' }
});
