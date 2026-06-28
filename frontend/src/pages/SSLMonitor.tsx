import { useEffect, useState } from 'react';
import { Shield, Plus, Search, RefreshCw, AlertTriangle, Check, X, Globe, Trash2 } from 'lucide-react';
import { ssl } from '../services/api';
import toast from 'react-hot-toast';

export default function SSLMonitor() {
  const [certs, setCerts] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [newDomain, setNewDomain] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const fetch = async () => {
    try {
      const data = await ssl.certificates({ page, page_size: 30, search: search || undefined, status: statusFilter || undefined });
      setCerts(data.items);
      setTotal(data.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
    ssl.stats().then(setStats).catch(() => {});
  }, [page, statusFilter]);

  const handleScan = async () => {
    if (!newDomain) return;
    try {
      const result = await ssl.scan(newDomain);
      toast.success(`Scanned ${newDomain}: ${result.status}`);
      setShowAdd(false);
      setNewDomain('');
      fetch();
      ssl.stats().then(setStats);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Scan failed');
    }
  };

  const handleScanAll = async () => {
    try {
      const result = await ssl.scanAll();
      toast.success(`Scanned ${result.scanned} certificates`);
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Scan all failed');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Remove this certificate from monitoring?')) return;
    try {
      await ssl.deleteCert(id);
      toast.success('Removed');
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Delete failed');
    }
  };

  const statusColor = (s: string) => ({
    valid: 'text-green-400 bg-green-500/10 border-green-500/20',
    expiring: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
    expired: 'text-red-400 bg-red-500/10 border-red-500/20',
    weak: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
    error: 'text-gray-500 bg-gray-500/10 border-gray-500/20',
  }[s] || 'text-gray-500 bg-gray-500/10');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">SSL/TLS Certificate Monitor</h1>
          <p className="text-gray-500 mt-1">Track expiry, weak ciphers, misconfigurations across your domains</p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleScanAll} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm border border-gray-700">
            <RefreshCw className="w-4 h-4" /> Rescan All
          </button>
          <button onClick={() => setShowAdd(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20">
            <Plus className="w-4 h-4" /> Add Domain
          </button>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="stat-card"><p className="text-sm text-gray-500">Total</p><p className="text-2xl font-bold text-white mt-1">{stats.total}</p></div>
          <div className="stat-card"><p className="text-sm text-gray-500">Valid</p><p className="text-2xl font-bold text-cyber-success mt-1">{stats.valid}</p></div>
          <div className="stat-card"><p className="text-sm text-gray-500">Expiring</p><p className="text-2xl font-bold text-cyber-warning mt-1">{stats.expiring_soon}</p></div>
          <div className="stat-card"><p className="text-sm text-gray-500">Expired</p><p className="text-2xl font-bold text-cyber-danger mt-1">{stats.expired}</p></div>
          <div className="stat-card"><p className="text-sm text-gray-500">Weak Cipher</p><p className="text-2xl font-bold text-orange-400 mt-1">{stats.weak_ciphers}</p></div>
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && fetch()} placeholder="Search domains..." className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm" />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm">
          <option value="">All Status</option>
          <option value="valid">Valid</option>
          <option value="expiring">Expiring Soon</option>
          <option value="expired">Expired</option>
          <option value="weak">Weak Cipher</option>
          <option value="error">Error</option>
        </select>
      </div>

      <div className="grid gap-4">
        {certs.map((c) => (
          <div key={c.id} className="glass p-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <Globe className={`w-5 h-5 mt-1 ${c.is_expired ? 'text-cyber-danger' : c.is_expiring_soon ? 'text-cyber-warning' : 'text-cyber-success'}`} />
                <div>
                  <h3 className="text-lg font-semibold text-white">{c.domain} <span className="text-sm text-gray-500">:{c.port}</span></h3>
                  <div className="flex gap-2 mt-1">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${statusColor(c.status)}`}>{c.status}</span>
                    {c.is_self_signed && <span className="px-2 py-0.5 rounded text-xs bg-gray-800 text-gray-400">Self-signed</span>}
                    {c.is_wildcard && <span className="px-2 py-0.5 rounded text-xs bg-cyber-accent/10 text-cyber-accent">Wildcard</span>}
                    {c.weak_cipher && <span className="px-2 py-0.5 rounded text-xs bg-red-500/10 text-red-400">Weak cipher</span>}
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <span className={`text-2xl font-bold ${c.days_remaining > 30 ? 'text-cyber-success' : c.days_remaining > 0 ? 'text-cyber-warning' : 'text-cyber-danger'}`}>{c.days_remaining}d</span>
                <button onClick={() => handleDelete(c.id)} className="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-500 hover:text-red-400"><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 text-sm">
              <div><span className="text-gray-500">Issuer</span><p className="text-gray-300 truncate">{c.issuer || '-'}</p></div>
              <div><span className="text-gray-500">Subject</span><p className="text-gray-300 truncate">{c.subject || '-'}</p></div>
              <div><span className="text-gray-500">Valid Until</span><p className={`${c.is_expired ? 'text-red-400' : 'text-gray-300'}`}>{c.valid_to ? new Date(c.valid_to).toLocaleDateString() : '-'}</p></div>
              <div><span className="text-gray-500">Protocol</span><p className="text-gray-300">{c.protocol_version || '-'} / {c.cipher_suite || '-'}</p></div>
            </div>
          </div>
        ))}
        {certs.length === 0 && (
          <div className="glass p-12 text-center">
            <Shield className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500">No certificates monitored. Add a domain to begin SSL/TLS monitoring.</p>
          </div>
        )}
      </div>

      {showAdd && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowAdd(false)}>
          <div className="glass max-w-md w-full p-6 space-y-4" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-white">Add Domain</h2>
            <input value={newDomain} onChange={(e) => setNewDomain(e.target.value)} placeholder="example.com" className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm font-mono" />
            <p className="text-xs text-gray-500">The system will scan common SSL ports (443, 8443, 993, etc.)</p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowAdd(false)} className="px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm">Cancel</button>
              <button onClick={handleScan} disabled={!newDomain} className="px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20 disabled:opacity-50">Scan & Add</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
