import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = 'http://localhost:8000/api';

const PRIORITY_COLORS = { P0: '#ff4444', P1: '#ff8800', P2: '#ffcc00', P3: '#44bb44' };
const STATUS_COLORS = { OPEN: '#ff4444', INVESTIGATING: '#ff8800', RESOLVED: '#4488ff', CLOSED: '#44bb44' };
const RCA_CATEGORIES = ['DB_FAILURE', 'NETWORK_ISSUE', 'MEMORY_LEAK', 'CONFIG_ERROR', 'INFRA_FAILURE', 'CODE_BUG', 'THIRD_PARTY', 'UNKNOWN'];

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [selected, setSelected] = useState(null);
  const [signals, setSignals] = useState([]);
  const [showRCA, setShowRCA] = useState(false);
  const [health, setHealth] = useState(null);
  const [rca, setRca] = useState({ incident_start: '', incident_end: '', root_cause_category: 'DB_FAILURE', fix_applied: '', prevention_steps: '' });
  const [msg, setMsg] = useState('');

  const fetchIncidents = async () => {
    try {
      const res = await axios.get(`${API}/incidents/`);
      setIncidents(res.data);
    } catch (e) { console.error(e); }
  };

  const fetchHealth = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/health`);
      setHealth(res.data);
    } catch (e) { setHealth({ status: 'unreachable' }); }
  };

  useEffect(() => {
    fetchIncidents();
    fetchHealth();
    const interval = setInterval(fetchIncidents, 5000);
    return () => clearInterval(interval);
  }, []);

  const selectIncident = async (inc) => {
    setSelected(inc);
    setShowRCA(false);
    setMsg('');
    try {
      const res = await axios.get(`${API}/signals/raw/${inc.component_id}`);
      setSignals(res.data);
    } catch (e) { setSignals([]); }
  };

  const advanceStatus = async () => {
    try {
      await axios.patch(`${API}/incidents/${selected.id}/status`, { status: 'next' });
      setMsg('✅ Status updated!');
      fetchIncidents();
      setTimeout(() => selectIncident(selected), 500);
    } catch (e) {
      setMsg('❌ ' + (e.response?.data?.detail || 'Error'));
    }
  };

  const submitRCA = async () => {
    if (!rca.incident_start || !rca.incident_end) {
      setMsg('❌ Please fill in both incident start and end times');
      return;
    }
    if (rca.fix_applied.length < 10) {
      setMsg('❌ Fix Applied must be at least 10 characters');
      return;
    }
    if (rca.prevention_steps.length < 10) {
      setMsg('❌ Prevention Steps must be at least 10 characters');
      return;
    }
    try {
      const payload = {
        incident_start: new Date(rca.incident_start).toISOString(),
        incident_end: new Date(rca.incident_end).toISOString(),
        root_cause_category: rca.root_cause_category,
        fix_applied: rca.fix_applied,
        prevention_steps: rca.prevention_steps
      };
      await axios.post(`${API}/incidents/${selected.id}/rca`, payload);
      setMsg('✅ RCA submitted successfully!');
      setShowRCA(false);
      fetchIncidents();
    } catch (e) {
      setMsg('❌ ' + (e.response?.data?.detail || 'Error submitting RCA'));
    }
  };

  const ingestSignal = async () => {
    try {
      await axios.post(`${API}/signals/ingest`, {
        component_id: 'POSTGRES_PRIMARY_01',
        component_type: 'RDBMS',
        error_code: 'TEST_ERROR',
        message: 'Manual test signal from dashboard'
      });
      setMsg('✅ Test signal sent!');
      setTimeout(fetchIncidents, 2000);
    } catch (e) { setMsg('❌ Error sending signal'); }
  };

  const s = {
    app: { fontFamily: 'monospace', background: '#0d1117', minHeight: '100vh', color: '#c9d1d9', padding: 16 },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #30363d', paddingBottom: 12, marginBottom: 16 },
    title: { color: '#58a6ff', fontSize: 22, margin: 0 },
    health: { fontSize: 12, color: health?.status === 'healthy' ? '#44bb44' : '#ff4444' },
    layout: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 },
    card: { background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 16 },
    incCard: (p, sel) => ({ background: sel ? '#1f2937' : '#161b22', border: `1px solid ${PRIORITY_COLORS[p] || '#30363d'}`, borderRadius: 6, padding: 12, marginBottom: 8, cursor: 'pointer' }),
    badge: (color) => ({ background: color, color: '#000', padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 'bold', marginRight: 6 }),
    btn: (color) => ({ background: color, color: '#fff', border: 'none', padding: '8px 16px', borderRadius: 6, cursor: 'pointer', margin: 4, fontWeight: 'bold' }),
    input: { background: '#0d1117', border: '1px solid #30363d', color: '#c9d1d9', padding: 8, borderRadius: 4, width: '100%', marginBottom: 8, boxSizing: 'border-box' },
    label: { fontSize: 12, color: '#8b949e', display: 'block', marginBottom: 4 },
    sigItem: { background: '#0d1117', border: '1px solid #30363d', borderRadius: 4, padding: 8, marginBottom: 6, fontSize: 12 },
    msg: { padding: 8, background: '#1f2937', borderRadius: 4, marginTop: 8, fontSize: 13 }
  };

  return (
    <div style={s.app}>
      <div style={s.header}>
        <h1 style={s.title}>🚨 Incident Management System</h1>
        <div>
          <span style={s.health}>● {health?.status?.toUpperCase() || 'CHECKING'}</span>
          <button style={{...s.btn('#238636'), marginLeft: 12}} onClick={ingestSignal}>+ Test Signal</button>
        </div>
      </div>

      <div style={s.layout}>
        <div style={s.card}>
          <h3 style={{color:'#58a6ff', marginTop:0}}>🔴 Live Incidents ({incidents.length})</h3>
          {incidents.length === 0 && <p style={{color:'#8b949e'}}>No incidents. Send a signal to create one.</p>}
          {[...incidents].sort((a,b) => ({P0:0,P1:1,P2:2,P3:3}[a.priority]||3) - ({P0:0,P1:1,P2:2,P3:3}[b.priority]||3)).map(inc => (
            <div key={inc.id} style={s.incCard(inc.priority, selected?.id === inc.id)} onClick={() => selectIncident(inc)}>
              <div style={{marginBottom:6}}>
                <span style={s.badge(PRIORITY_COLORS[inc.priority])}>{inc.priority}</span>
                <span style={s.badge(STATUS_COLORS[inc.status])}>{inc.status}</span>
                {inc.has_rca && <span style={s.badge('#6f42c1')}>RCA ✓</span>}
              </div>
              <div style={{fontSize:13, fontWeight:'bold'}}>{inc.title}</div>
              <div style={{fontSize:11, color:'#8b949e', marginTop:4}}>
                📡 {inc.signal_count} signals | 🕐 {new Date(inc.created_at).toLocaleString()}
                {inc.mttr_minutes && ` | ⚡ MTTR: ${inc.mttr_minutes}m`}
              </div>
            </div>
          ))}
        </div>

        <div style={s.card}>
          {!selected ? (
            <div style={{color:'#8b949e', textAlign:'center', marginTop:40}}>
              <div style={{fontSize:40}}>👈</div>
              <p>Select an incident to view details</p>
            </div>
          ) : (
            <>
              <h3 style={{color:'#58a6ff', marginTop:0}}>📋 Incident Detail</h3>
              <div style={{marginBottom:12}}>
                <span style={s.badge(PRIORITY_COLORS[selected.priority])}>{selected.priority}</span>
                <span style={s.badge(STATUS_COLORS[selected.status])}>{selected.status}</span>
              </div>
              <div style={{fontSize:13, marginBottom:8}}><b>{selected.title}</b></div>
              <div style={{fontSize:12, color:'#8b949e', marginBottom:12}}>
                Component: {selected.component_id} | Signals: {selected.signal_count}
                {selected.mttr_minutes && <span> | MTTR: {selected.mttr_minutes} min</span>}
              </div>

              <div style={{marginBottom:12}}>
                {selected.status !== 'CLOSED' && (
                  <button style={s.btn('#1f6feb')} onClick={advanceStatus}>▶ Advance Status</button>
                )}
                {!selected.has_rca && (
                  <button style={s.btn('#6f42c1')} onClick={() => { setShowRCA(!showRCA); setMsg(''); }}>📝 Submit RCA</button>
                )}
              </div>

              {msg && <div style={s.msg}>{msg}</div>}

              {showRCA && (
                <div style={{background:'#0d1117', border:'1px solid #6f42c1', borderRadius:6, padding:12, marginBottom:12}}>
                  <h4 style={{color:'#6f42c1', marginTop:0}}>📝 Root Cause Analysis</h4>
                  <label style={s.label}>Incident Start *</label>
                  <input style={s.input} type="datetime-local" onChange={e => setRca({...rca, incident_start: e.target.value})} />
                  <label style={s.label}>Incident End *</label>
                  <input style={s.input} type="datetime-local" onChange={e => setRca({...rca, incident_end: e.target.value})} />
                  <label style={s.label}>Root Cause Category *</label>
                  <select style={s.input} onChange={e => setRca({...rca, root_cause_category: e.target.value})}>
                    {RCA_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                  <label style={s.label}>Fix Applied (min 10 chars) *</label>
                  <textarea style={{...s.input, height:60}} placeholder="Describe what was done to fix the issue..." onChange={e => setRca({...rca, fix_applied: e.target.value})} />
                  <label style={s.label}>Prevention Steps (min 10 chars) *</label>
                  <textarea style={{...s.input, height:60}} placeholder="Describe steps to prevent recurrence..." onChange={e => setRca({...rca, prevention_steps: e.target.value})} />
                  <button style={s.btn('#6f42c1')} onClick={submitRCA}>Submit RCA</button>
                </div>
              )}

              <h4 style={{color:'#58a6ff'}}>📡 Raw Signals ({signals.length})</h4>
              <div style={{maxHeight:250, overflowY:'auto'}}>
                {signals.length === 0 && <p style={{color:'#8b949e', fontSize:12}}>No signals found</p>}
                {signals.map((sig, i) => (
                  <div key={i} style={s.sigItem}>
                    <span style={{color:'#ff4444'}}>{sig.error_code}</span> — {sig.message}
                    <div style={{color:'#8b949e', fontSize:11, marginTop:2}}>
                      {sig.latency_ms && `⏱ ${sig.latency_ms}ms | `}{sig.ingested_at}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
