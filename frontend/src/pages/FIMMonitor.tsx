import { useEffect, useState } from 'react';
import { Search, Shield, FileText, AlertTriangle, RefreshCw, Plus, Check } from 'lucide-react';
import { fim } from '../services/api';
import type { FimEntry } from '../types';
import toast from 'react-hot-toast';

export default function FIMMonitor() {
  const [entries, setEntries] = useState<FimEntry[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [criticalOnly, setCriticalOnly] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [showAdd, setShowAdd] = useState(false);
  const [newPath, setNewPath] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);

  const fetch = async () => {
    try {
      const data = await fim.entries({ page, page_size: 50, status_filter: statusFilter || undefined, critical_only: criticalOnly || undefined });
      setEntries(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
    fim.stats().then(setStats).catch(() => {});
  }, [page, statusFilter, criticalOnly]);

  const handleScan = async () => {
    setScanning(true);
    try {
      const data = await fim.scan();
      toast.success(`Scanned ${data.scanned} files, ${data.changed} changed`);
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Scan failed');
    } finally {
      setScanning(false);
    }
  };

  const handleAdd = async () => {
    if (!newPath) return;
    try {
      await fim.add(newPath);
      toast.success('Path added');
      setShowAdd(false);
      setNewPath('');
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Add failed');
    }
  };

  const statusColor = (s: string) => {
    const map: Record<string, string> = {
      changed: 'text-red-400 bg-red-500/10 border-red-500/20',
      monitored: 'text-green-400 bg-green-500/10 border-green-500/20',
      new: 'text-cyber-accent bg-cyber-accent/10 border-cyber-accent/20',
      missing: 'text-gray-500 bg-gray-500/10 border-gray-500/20',
    };
    return map[s] || 'text-gray-500 bg-gray-500/10 border-gray-500/20';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">File Integrity Monitor</h1>
          <p className="text-gray-500 mt-1">Detect unauthorized file changes with SHA-256 hashing</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowAdd(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm border border-gray-700 hover:bg-gray-700">
            <Plus className="w-4 h-4" /> Add Path
          </button>
          <button onClick={handleScan} disabled={scanning} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20 hover:bg-cyber-accent/20 disabled:opacity-50">
            <RefreshCw className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} /> {scanning ? 'Scanning...' : 'Scan Now'}
          </button>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="stat-card">
            <div className="flex items-center gap-2"><FileText className="w-4 h-4 text-cyber-accent" /><p className="text-sm text-gray-500">Monitored</p></div>
            <p className="text-2xl font-bold text-white mt-1">{stats.total_files}</p>
          </div>
          <div className="stat-card">
            <div className="flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-cyber-danger" /><p className="text-sm text-gray-500">Changed</p></div>
            <p className="text-2xl font-bold text-cyber-danger mt-1">{stats.changed}</p>
          </div>
          <div className="stat-card">
            <div className="flex items-center gap-2"><Shield className="w-4 h-4 text-cyber-warning" /><p className="text-sm text-gray-500">Critical</p></div>
            <p className="text-2xl font-bold text-cyber-warning mt-1">{stats.critical}</p>
          </div>
          <div className="stat-card">
            <div className="flex items-center gap-2"><Check className="w-4 h-4 text-cyber-success" /><p className="text-sm text-gray-500">Clean</p></div>
            <p className="text-2xl font-bold text-cyber-success mt-1">{stats.monitored}</p>
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm">
          <option value="">All Status</option>
          <option value="monitored">Monitored</option>
          <option value="changed">Changed</option>
          <option value="new">New</option>
          <option value="missing">Missing</option>
        </select>
        <button onClick={() => setCriticalOnly(!criticalOnly)} className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm border ${
          criticalOnly ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' : 'bg-gray-800 text-gray-400 border-gray-700'
        }`}>
          <Shield className="w-4 h-4" /> Critical Only
        </button>
      </div>

      <div className="glass overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800/50">
                <th className="text-left p-3 text-sm font-medium text-gray-500">File</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Size</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Owner</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Permissions</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Changes</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Last Checked</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e) => (
                <tr key={e.id} className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors">
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <FileText className={`w-4 h-4 ${e.is_critical ? 'text-cyber-warning' : 'text-gray-500'}`} />
                      <span className="text-sm text-gray-200">{e.file_name}</span>
                    </div>
                    <p className="text-xs text-gray-600 font-mono truncate max-w-[300px]">{e.file_path}</p>
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${statusColor(e.status)}`}>{e.status}</span>
                  </td>
                  <td className="p-3 text-sm text-gray-400 font-mono">{e.file_size ? `${(e.file_size / 1024).toFixed(1)} KB` : '-'}</td>
                  <td className="p-3 text-sm text-gray-400">{e.owner || '-'}</td>
                  <td className="p-3 text-sm font-mono text-gray-500">{e.permissions || '-'}</td>
                  <td className="p-3">
                    <span className={`text-sm font-mono ${e.change_count > 0 ? 'text-cyber-danger' : 'text-gray-500'}`}>{e.change_count || 0}</span>
                  </td>
                  <td className="p-3 text-xs text-gray-500">{e.last_checked ? new Date(e.last_checked).toLocaleString() : '-'}</td>
                </tr>
              ))}
              {entries.length === 0 && (
                <tr><td colSpan={7} className="p-12 text-center text-gray-500">No monitored files. Add a path or run a scan.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button disabled={page <= 1} onClick={() => setPage(p => p - 1)} className="px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm disabled:opacity-50">Previous</button>
          <span className="text-sm text-gray-500">Page {page} of {pages}</span>
          <button disabled={page >= pages} onClick={() => setPage(p => p + 1)} className="px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm disabled:opacity-50">Next</button>
        </div>
      )}

      {showAdd && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowAdd(false)}>
          <div className="glass max-w-lg w-full p-6 space-y-4" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-white">Add Monitored Path</h2>
            <input type="text" value={newPath} onChange={(e) => setNewPath(e.target.value)} placeholder="/etc/passwd" className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm font-mono" />
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowAdd(false)} className="px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm">Cancel</button>
              <button onClick={handleAdd} disabled={!newPath} className="px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20 disabled:opacity-50">Add</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
