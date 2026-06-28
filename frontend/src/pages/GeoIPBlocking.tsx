import { useEffect, useState } from 'react';
import { Globe, Plus, Trash2, ToggleLeft, ToggleRight, Search, RefreshCw, Shield, AlertTriangle } from 'lucide-react';
import { geoip } from '../services/api';
import toast from 'react-hot-toast';

const COUNTRIES = [
  { code: 'CN', name: 'China' }, { code: 'RU', name: 'Russia' }, { code: 'KP', name: 'North Korea' },
  { code: 'IR', name: 'Iran' }, { code: 'SY', name: 'Syria' }, { code: 'CU', name: 'Cuba' },
  { code: 'VE', name: 'Venezuela' }, { code: 'BY', name: 'Belarus' }, { code: 'MM', name: 'Myanmar' },
  { code: 'SD', name: 'Sudan' }, { code: 'ZW', name: 'Zimbabwe' }, { code: 'ER', name: 'Eritrea' },
  { code: 'AF', name: 'Afghanistan' }, { code: 'IQ', name: 'Iraq' }, { code: 'LY', name: 'Libya' },
  { code: 'SO', name: 'Somalia' }, { code: 'SS', name: 'South Sudan' }, { code: 'YE', name: 'Yemen' },
];

export default function GeoIPBlocking() {
  const [rules, setRules] = useState<any[]>([]);
  const [hits, setHits] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState('');
  const [lookupIP, setLookupIP] = useState('');
  const [lookupResult, setLookupResult] = useState<any>(null);

  const fetch = async () => {
    try {
      const [r, h, s] = await Promise.all([geoip.rules(), geoip.hits({ page: 1 }), geoip.stats()]);
      setRules(r.items);
      setHits(h.items);
      setStats(s);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetch(); }, []);

  const handleAdd = async () => {
    if (!selectedCountry) return;
    const country = COUNTRIES.find(c => c.code === selectedCountry);
    try {
      await geoip.create({ country_code: selectedCountry, country_name: country?.name || selectedCountry });
      toast.success('GeoIP rule added');
      setShowAdd(false);
      setSelectedCountry('');
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to add');
    }
  };

  const handleToggle = async (id: number) => {
    try {
      await geoip.toggle(id);
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Toggle failed');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Remove this rule?')) return;
    try {
      await geoip.deleteRule(id);
      toast.success('Rule removed');
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Delete failed');
    }
  };

  const handleLookup = async () => {
    if (!lookupIP) return;
    try {
      const result = await geoip.lookup(lookupIP);
      setLookupResult(result);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Lookup failed');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-accent" /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Geo-IP Blocking</h1>
          <p className="text-gray-500 mt-1">Block or flag traffic from high-risk countries via ip-api.com GeoIP</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20">
          <Plus className="w-4 h-4" /> Block Country
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="stat-card"><div className="flex items-center gap-2"><Globe className="w-4 h-4 text-cyber-accent" /><p className="text-sm text-gray-500">Blocked Countries</p></div><p className="text-2xl font-bold text-white mt-1">{stats.blocked_countries?.length || 0}</p></div>
          <div className="stat-card"><div className="flex items-center gap-2"><Shield className="w-4 h-4 text-cyber-success" /><p className="text-sm text-gray-500">Active Rules</p></div><p className="text-2xl font-bold text-cyber-success mt-1">{stats.active_rules}</p></div>
          <div className="stat-card"><div className="flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-cyber-danger" /><p className="text-sm text-gray-500">Blocked Hits</p></div><p className="text-2xl font-bold text-cyber-danger mt-1">{stats.total_hits}</p></div>
        </div>
      )}

      <div className="glass p-4">
        <h2 className="text-sm font-semibold text-gray-400 mb-3">IP Lookup</h2>
        <div className="flex gap-3">
          <input value={lookupIP} onChange={(e) => setLookupIP(e.target.value)} placeholder="Enter IP address..." className="flex-1 px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm font-mono" />
          <button onClick={handleLookup} className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gray-800 text-gray-300 border border-gray-700">Lookup</button>
        </div>
        {lookupResult && (
          <div className="mt-3 p-3 bg-gray-900/50 rounded-xl">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div><span className="text-gray-500">Country</span><p className="text-gray-200">{lookupResult.country_name || 'Unknown'} ({lookupResult.country_code || '-'})</p></div>
              <div><span className="text-gray-500">City</span><p className="text-gray-200">{lookupResult.city || '-'}</p></div>
              <div><span className="text-gray-500">ISP</span><p className="text-gray-200">{lookupResult.isp || '-'}</p></div>
              <div><span className="text-gray-500">Blocked</span><p className={lookupResult.is_blocked ? 'text-red-400' : 'text-green-400'}>{lookupResult.is_blocked ? 'Yes' : 'No'}</p></div>
            </div>
          </div>
        )}
      </div>

      <div className="glass overflow-hidden">
        <div className="p-4 border-b border-gray-800/50"><h2 className="text-lg font-semibold text-white">Blocking Rules</h2></div>
        <table className="w-full">
          <thead><tr className="border-b border-gray-800/50">
            <th className="text-left p-3 text-sm font-medium text-gray-500">Country</th>
            <th className="text-left p-3 text-sm font-medium text-gray-500">Code</th>
            <th className="text-left p-3 text-sm font-medium text-gray-500">Action</th>
            <th className="text-left p-3 text-sm font-medium text-gray-500">Hits</th>
            <th className="text-left p-3 text-sm font-medium text-gray-500">Active</th>
            <th className="text-left p-3 text-sm font-medium text-gray-500"></th>
          </tr></thead>
          <tbody>
            {rules.map((r) => (
              <tr key={r.id} className="border-b border-gray-800/30 hover:bg-gray-800/20">
                <td className="p-3 text-sm text-gray-200">{r.country_name}</td>
                <td className="p-3"><span className="text-sm font-mono text-gray-400">{r.country_code}</span></td>
                <td className="p-3"><span className={`px-2 py-0.5 rounded text-xs font-medium border ${r.action === 'block' ? 'text-red-400 bg-red-500/10 border-red-500/20' : 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20'}`}>{r.action}</span></td>
                <td className="p-3 text-sm text-gray-500">{r.hit_count}</td>
                <td className="p-3">{r.is_active ? <ToggleRight className="w-5 h-5 text-cyber-success" /> : <ToggleLeft className="w-5 h-5 text-gray-500" />}</td>
                <td className="p-3"><div className="flex gap-1">
                  <button onClick={() => handleToggle(r.id)} className="p-1.5 rounded-lg hover:bg-gray-700 text-gray-500"><ToggleLeft className="w-4 h-4" /></button>
                  <button onClick={() => handleDelete(r.id)} className="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-500 hover:text-red-400"><Trash2 className="w-4 h-4" /></button>
                </div></td>
              </tr>
            ))}
            {rules.length === 0 && <tr><td colSpan={6} className="p-12 text-center text-gray-500">No GeoIP blocking rules. Add countries to block.</td></tr>}
          </tbody>
        </table>
      </div>

      <div className="glass overflow-hidden">
        <div className="p-4 border-b border-gray-800/50"><h2 className="text-lg font-semibold text-white">Recent Blocks</h2></div>
        <table className="w-full">
          <thead><tr className="border-b border-gray-800/50">
            <th className="text-left p-3 text-sm font-medium text-gray-500">Time</th>
            <th className="text-left p-3 text-sm font-medium text-gray-500">IP</th>
            <th className="text-left p-3 text-sm font-medium text-gray-500">Country</th>
            <th className="text-left p-3 text-sm font-medium text-gray-500">Action</th>
          </tr></thead>
          <tbody>
            {hits.map((h) => (
              <tr key={h.id} className="border-b border-gray-800/30 hover:bg-gray-800/20">
                <td className="p-3 text-xs font-mono text-gray-500">{h.timestamp ? new Date(h.timestamp).toLocaleString() : '-'}</td>
                <td className="p-3 text-sm font-mono text-gray-400">{h.ip_address}</td>
                <td className="p-3"><span className="text-sm text-gray-400">{h.country_name} ({h.country_code})</span></td>
                <td className="p-3"><span className={`px-2 py-0.5 rounded text-xs font-medium border ${h.action === 'blocked' ? 'text-red-400 bg-red-500/10 border-red-500/20' : ''}`}>{h.action}</span></td>
              </tr>
            ))}
            {hits.length === 0 && <tr><td colSpan={4} className="p-8 text-center text-gray-500">No blocked traffic yet</td></tr>}
          </tbody>
        </table>
      </div>

      {showAdd && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowAdd(false)}>
          <div className="glass max-w-md w-full p-6 space-y-4" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-white">Block Country</h2>
            <select value={selectedCountry} onChange={(e) => setSelectedCountry(e.target.value)} className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm">
              <option value="">Select a country...</option>
              {COUNTRIES.map((c) => <option key={c.code} value={c.code}>{c.name} ({c.code})</option>)}
            </select>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowAdd(false)} className="px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm">Cancel</button>
              <button onClick={handleAdd} disabled={!selectedCountry} className="px-4 py-2 rounded-xl bg-red-500/10 text-red-400 text-sm border border-red-500/20 disabled:opacity-50">Block</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
