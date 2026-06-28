import { useEffect, useState } from 'react';
import { Shield, Globe, Search, Activity, AlertTriangle, Plus, Trash2, ToggleLeft, ToggleRight } from 'lucide-react';
import { dns } from '../services/api';
import toast from 'react-hot-toast';

export default function DNSSecurity() {
  const [domains, setDomains] = useState<any[]>([]);
  const [queries, setQueries] = useState<any[]>([]);
  const [blockerRules, setBlockerRules] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'domains' | 'queries' | 'rules'>('domains');
  const [showAdd, setShowAdd] = useState(false);
  const [newDomain, setNewDomain] = useState('');
  const [showRule, setShowRule] = useState(false);
  const [newRule, setNewRule] = useState({ domain: '', pattern_type: 'exact', category: '', description: '' });
  const [checkDomain, setCheckDomain] = useState('');
  const [checkResult, setCheckResult] = useState<any>(null);

  const fetch = async () => {
    try {
      const results = await Promise.all([
        dns.domains({ page_size: 50 }),
        dns.queries({ page_size: 20 }),
        dns.blockerRules(),
        dns.stats(),
      ]);
      setDomains(results[0].items);
      setQueries(results[1].items);
      setBlockerRules(results[2].items);
      setStats(results[3]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetch(); }, []);

  const handleAddDomain = async () => {
    if (!newDomain) return;
    try {
      await dns.addDomain({ domain: newDomain });
      toast.success('Malicious domain added');
      setShowAdd(false);
      setNewDomain('');
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to add');
    }
  };

  const handleToggleDomain = async (id: number) => {
    try { await dns.toggleDomain(id); fetch(); } catch (e) {}
  };

  const handleDeleteDomain = async (id: number) => {
    if (!confirm('Remove this domain?')) return;
    try { await dns.deleteDomain(id); toast.success('Removed'); fetch(); } catch (e) {}
  };

  const handleAddRule = async () => {
    try {
      await dns.createBlockerRule(newRule);
      toast.success('Blocker rule added');
      setShowRule(false);
      setNewRule({ domain: '', pattern_type: 'exact', category: '', description: '' });
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to add rule');
    }
  };

  const handleDeleteRule = async (id: number) => {
    if (!confirm('Remove this rule?')) return;
    try { await dns.deleteBlockerRule(id); toast.success('Rule removed'); fetch(); } catch (e) {}
  };

  const handleCheck = async () => {
    if (!checkDomain) return;
    try {
      const result = await dns.check(checkDomain);
      setCheckResult(result);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Check failed');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-accent" /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">DNS Security</h1>
          <p className="text-gray-500 mt-1">Query log analysis, malicious domain blocking, Pi-hole-style integration</p>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="stat-card"><div className="flex items-center gap-2"><Activity className="w-4 h-4 text-cyber-accent" /><p className="text-sm text-gray-500">Queries Analyzed</p></div><p className="text-2xl font-bold text-white mt-1">{stats.total_queries}</p></div>
          <div className="stat-card"><div className="flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-cyber-danger" /><p className="text-sm text-gray-500">Malicious</p></div><p className="text-2xl font-bold text-cyber-danger mt-1">{stats.malicious}</p></div>
          <div className="stat-card"><div className="flex items-center gap-2"><Shield className="w-4 h-4 text-cyber-success" /><p className="text-sm text-gray-500">Blocked</p></div><p className="text-2xl font-bold text-cyber-success mt-1">{stats.blocked}</p></div>
          <div className="stat-card"><div className="flex items-center gap-2"><Globe className="w-4 h-4 text-cyber-warning" /><p className="text-sm text-gray-500">Blocked Domains</p></div><p className="text-2xl font-bold text-cyber-warning mt-1">{stats.malicious_domains}</p></div>
        </div>
      )}

      <div className="glass p-4">
        <h2 className="text-sm font-semibold text-gray-400 mb-3">DNS Lookup</h2>
        <div className="flex gap-3">
          <input value={checkDomain} onChange={(e) => setCheckDomain(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleCheck()} placeholder="Check a domain..." className="flex-1 px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm font-mono" />
          <button onClick={handleCheck} className="px-4 py-2.5 rounded-xl bg-gray-800 text-gray-300 border border-gray-700">Check</button>
        </div>
        {checkResult && (
          <div className={`mt-3 p-3 rounded-xl ${checkResult.malicious ? 'bg-red-500/10' : 'bg-green-500/10'}`}>
            <div className="flex items-center gap-2">
              <span className={`text-sm font-semibold ${checkResult.malicious ? 'text-red-400' : 'text-green-400'}`}>
                {checkResult.malicious ? 'MALICIOUS' : 'CLEAN'}
              </span>
              <span className="text-sm text-gray-400">{checkResult.domain} → {checkResult.resolved_ip || 'unresolved'}</span>
            </div>
            {checkResult.malicious && <p className="text-xs text-gray-500 mt-1">Type: {checkResult.threat_type} | Confidence: {Math.round(checkResult.confidence * 100)}%</p>}
          </div>
        )}
      </div>

      <div className="flex gap-2 border-b border-gray-800">
        {(['domains', 'queries', 'rules'] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)} className={`px-4 py-2.5 text-sm font-medium transition-colors ${tab === t ? 'text-cyber-accent border-b-2 border-cyber-accent' : 'text-gray-500 hover:text-gray-300'}`}>
            {t === 'domains' ? 'Malicious Domains' : t === 'queries' ? 'Query Log' : 'Blocker Rules'}
          </button>
        ))}
        <div className="ml-auto">
          {tab === 'domains' && <button onClick={() => setShowAdd(true)} className="flex items-center gap-2 px-4 py-2 text-sm text-cyber-accent"><Plus className="w-4 h-4" /> Add</button>}
          {tab === 'rules' && <button onClick={() => setShowRule(true)} className="flex items-center gap-2 px-4 py-2 text-sm text-cyber-accent"><Plus className="w-4 h-4" /> Add Rule</button>}
        </div>
      </div>

      {tab === 'domains' && (
        <div className="glass overflow-hidden">
          <table className="w-full">
            <thead><tr className="border-b border-gray-800/50">
              <th className="text-left p-3 text-sm font-medium text-gray-500">Domain</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Type</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Severity</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Source</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Confidence</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Active</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500"></th>
            </tr></thead>
            <tbody>
              {domains.map((d) => (
                <tr key={d.id} className="border-b border-gray-800/30 hover:bg-gray-800/20">
                  <td className="p-3 text-sm font-mono text-gray-200">{d.domain}</td>
                  <td className="p-3 text-sm text-gray-400">{d.threat_type}</td>
                  <td className="p-3"><span className={`px-2 py-0.5 rounded text-xs font-medium border ${d.severity === 'CRITICAL' ? 'text-red-400 bg-red-500/10' : d.severity === 'HIGH' ? 'text-orange-400 bg-orange-500/10' : 'text-yellow-400 bg-yellow-500/10'}`}>{d.severity}</span></td>
                  <td className="p-3 text-sm text-gray-400">{d.source}</td>
                  <td className="p-3 text-sm text-gray-400">{(d.confidence * 100).toFixed(0)}%</td>
                  <td className="p-3">{d.is_active ? <ToggleRight className="w-5 h-5 text-cyber-success" /> : <ToggleLeft className="w-5 h-5 text-gray-500" />}</td>
                  <td className="p-3"><div className="flex gap-1">
                    <button onClick={() => handleToggleDomain(d.id)} className="p-1.5 rounded-lg hover:bg-gray-700 text-gray-500"><ToggleLeft className="w-4 h-4" /></button>
                    <button onClick={() => handleDeleteDomain(d.id)} className="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-500 hover:text-red-400"><Trash2 className="w-4 h-4" /></button>
                  </div></td>
                </tr>
              ))}
              {domains.length === 0 && <tr><td colSpan={7} className="p-8 text-center text-gray-500">No malicious domains in database</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'queries' && (
        <div className="glass overflow-hidden">
          <table className="w-full">
            <thead><tr className="border-b border-gray-800/50">
              <th className="text-left p-3 text-sm font-medium text-gray-500">Time</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Source</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Domain</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Type</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Response</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Status</th>
            </tr></thead>
            <tbody>
              {queries.map((q) => (
                <tr key={q.id} className="border-b border-gray-800/30 hover:bg-gray-800/20">
                  <td className="p-3 text-xs font-mono text-gray-500">{q.timestamp ? new Date(q.timestamp).toLocaleTimeString() : '-'}</td>
                  <td className="p-3 text-sm font-mono text-gray-400">{q.source_ip || '-'}</td>
                  <td className="p-3 text-sm font-mono text-gray-200">{q.domain}</td>
                  <td className="p-3 text-sm text-gray-400">{q.query_type}</td>
                  <td className="p-3 text-sm font-mono text-gray-500">{q.response_ip || '-'}</td>
                  <td className="p-3">
                    {q.is_blocked ? <span className="px-2 py-0.5 rounded text-xs font-medium border text-red-400 bg-red-500/10 border-red-500/20">Blocked</span> :
                     q.is_malicious ? <span className="px-2 py-0.5 rounded text-xs font-medium border text-orange-400 bg-orange-500/10 border-orange-500/20">Malicious</span> :
                     <span className="px-2 py-0.5 rounded text-xs font-medium border text-green-400 bg-green-500/10 border-green-500/20">Clean</span>}
                  </td>
                </tr>
              ))}
              {queries.length === 0 && <tr><td colSpan={6} className="p-8 text-center text-gray-500">No DNS queries logged yet</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'rules' && (
        <div className="glass overflow-hidden">
          <table className="w-full">
            <thead><tr className="border-b border-gray-800/50">
              <th className="text-left p-3 text-sm font-medium text-gray-500">Pattern</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Type</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Category</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Action</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Hits</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Active</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500"></th>
            </tr></thead>
            <tbody>
              {blockerRules.map((r) => (
                <tr key={r.id} className="border-b border-gray-800/30 hover:bg-gray-800/20">
                  <td className="p-3 text-sm font-mono text-gray-200">{r.domain}</td>
                  <td className="p-3 text-sm text-gray-400">{r.pattern_type}</td>
                  <td className="p-3 text-sm text-gray-400">{r.category || '-'}</td>
                  <td className="p-3"><span className={`px-2 py-0.5 rounded text-xs font-medium border ${r.action === 'block' ? 'text-red-400 bg-red-500/10' : 'text-yellow-400 bg-yellow-500/10'}`}>{r.action}</span></td>
                  <td className="p-3 text-sm text-gray-500">{r.hit_count}</td>
                  <td className="p-3">{r.is_active ? <ToggleRight className="w-5 h-5 text-cyber-success" /> : <ToggleLeft className="w-5 h-5 text-gray-500" />}</td>
                  <td className="p-3"><button onClick={() => handleDeleteRule(r.id)} className="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-500 hover:text-red-400"><Trash2 className="w-4 h-4" /></button></td>
                </tr>
              ))}
              {blockerRules.length === 0 && <tr><td colSpan={7} className="p-8 text-center text-gray-500">No blocker rules configured</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      {showAdd && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowAdd(false)}>
          <div className="glass max-w-md w-full p-6 space-y-4" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-white">Add Malicious Domain</h2>
            <input value={newDomain} onChange={(e) => setNewDomain(e.target.value)} placeholder="evil.com" className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm font-mono" />
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowAdd(false)} className="px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm">Cancel</button>
              <button onClick={handleAddDomain} disabled={!newDomain} className="px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20 disabled:opacity-50">Add</button>
            </div>
          </div>
        </div>
      )}

      {showRule && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowRule(false)}>
          <div className="glass max-w-md w-full p-6 space-y-4" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-white">Add Blocker Rule</h2>
            <input value={newRule.domain} onChange={(e) => setNewRule({ ...newRule, domain: e.target.value })} placeholder="Domain pattern" className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm font-mono" />
            <select value={newRule.pattern_type} onChange={(e) => setNewRule({ ...newRule, pattern_type: e.target.value })} className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm">
              <option value="exact">Exact Match</option>
              <option value="suffix">Suffix Match</option>
              <option value="contains">Contains</option>
            </select>
            <input value={newRule.category} onChange={(e) => setNewRule({ ...newRule, category: e.target.value })} placeholder="Category (e.g., malware, phishing)" className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm" />
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowRule(false)} className="px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm">Cancel</button>
              <button onClick={handleAddRule} disabled={!newRule.domain} className="px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20 disabled:opacity-50">Create</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
