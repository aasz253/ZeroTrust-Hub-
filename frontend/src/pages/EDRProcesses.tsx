import { useEffect, useState } from 'react';
import { Search, Filter, Activity, Cpu, AlertTriangle, Server, RefreshCw } from 'lucide-react';
import { edr } from '../services/api';
import type { EdrProcess } from '../types';

export default function EDRProcesses() {
  const [processes, setProcesses] = useState<EdrProcess[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [suspiciousOnly, setSuspiciousOnly] = useState(false);
  const [selected, setSelected] = useState<EdrProcess | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetch = async () => {
    try {
      const data = await edr.processes({ suspicious_only: suspiciousOnly, search: search || undefined });
      setProcesses(data.items);
      setStats(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
    edr.stats().then(setStats).catch(() => {});
  }, [suspiciousOnly]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetch, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">EDR Process Monitor</h1>
          <p className="text-gray-500 mt-1">Endpoint Detection & Response - Real-time process monitoring</p>
        </div>
        <button onClick={() => setAutoRefresh(!autoRefresh)} className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm border ${
          autoRefresh ? 'bg-cyber-accent/10 text-cyber-accent border-cyber-accent/20' : 'bg-gray-800 text-gray-400 border-gray-700'
        }`}>
          <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} /> Live
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="stat-card">
            <div className="flex items-center gap-2"><Server className="w-4 h-4 text-cyber-accent" /><p className="text-sm text-gray-500">Total</p></div>
            <p className="text-2xl font-bold text-white mt-1">{stats.total_processes || stats.total || 0}</p>
          </div>
          <div className="stat-card">
            <div className="flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-cyber-danger" /><p className="text-sm text-gray-500">Suspicious</p></div>
            <p className="text-2xl font-bold text-cyber-danger mt-1">{stats.suspicious_count || 0}</p>
          </div>
          <div className="stat-card">
            <div className="flex items-center gap-2"><Cpu className="w-4 h-4 text-cyber-warning" /><p className="text-sm text-gray-500">High CPU</p></div>
            <p className="text-2xl font-bold text-cyber-warning mt-1">{stats.high_cpu_count || 0}</p>
          </div>
          <div className="stat-card">
            <div className="flex items-center gap-2"><Activity className="w-4 h-4 text-cyber-warning" /><p className="text-sm text-gray-500">High Memory</p></div>
            <p className="text-2xl font-bold text-cyber-warning mt-1">{stats.high_memory_count || 0}</p>
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && fetch()} placeholder="Search processes..." className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm" />
        </div>
        <button onClick={() => { setSuspiciousOnly(!suspiciousOnly); }} className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm border ${
          suspiciousOnly ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-gray-800 text-gray-400 border-gray-700'
        }`}>
          <Filter className="w-4 h-4" /> Suspicious Only
        </button>
        <button onClick={fetch} className="px-4 py-2.5 rounded-xl bg-gray-800 text-gray-300 text-sm border border-gray-700 hover:bg-gray-700">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="glass overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800/50">
                <th className="text-left p-3 text-sm font-medium text-gray-500">PID</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Name</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">User</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">CPU%</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">MEM%</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Command</th>
              </tr>
            </thead>
            <tbody>
              {processes.map((p) => (
                <tr key={p.pid} className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors cursor-pointer" onClick={() => setSelected(selected?.pid === p.pid ? null : p)}>
                  <td className="p-3 text-sm font-mono text-gray-400">{p.pid}</td>
                  <td className="p-3">
                    <span className={`text-sm ${p.is_suspicious ? 'text-cyber-danger font-semibold' : 'text-gray-200'}`}>
                      {p.name}
                    </span>
                  </td>
                  <td className="p-3 text-sm text-gray-400">{p.username || '-'}</td>
                  <td className="p-3">
                    <span className={`text-sm font-mono ${p.cpu_percent > 50 ? 'text-cyber-danger' : p.cpu_percent > 20 ? 'text-cyber-warning' : 'text-gray-400'}`}>
                      {p.cpu_percent?.toFixed(1)}%
                    </span>
                  </td>
                  <td className="p-3">
                    <span className={`text-sm font-mono ${p.memory_percent > 20 ? 'text-cyber-danger' : p.memory_percent > 10 ? 'text-cyber-warning' : 'text-gray-400'}`}>
                      {p.memory_percent?.toFixed(1)}%
                    </span>
                  </td>
                  <td className="p-3">
                    {p.is_suspicious ? (
                      <span className="px-2 py-0.5 rounded text-xs font-medium text-red-400 bg-red-500/10 border border-red-500/20">Suspicious</span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-xs font-medium text-cyber-success bg-green-500/10 border border-green-500/20">Normal</span>
                    )}
                  </td>
                  <td className="p-3 text-xs font-mono text-gray-500 max-w-[200px] truncate">{p.cmdline || '-'}</td>
                </tr>
              ))}
              {processes.length === 0 && (
                <tr><td colSpan={7} className="p-12 text-center text-gray-500">No processes found. Try disabling the filter.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selected && (
        <div className="glass p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">
              {selected.name} <span className="text-sm text-gray-500 font-mono">(PID {selected.pid})</span>
            </h2>
            <button onClick={() => setSelected(null)} className="text-gray-500 hover:text-white">✕</button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><span className="text-xs text-gray-500">Executable</span><p className="text-sm text-gray-200 font-mono">{selected.exe || '-'}</p></div>
            <div><span className="text-xs text-gray-500">User</span><p className="text-sm text-gray-200">{selected.username || '-'}</p></div>
            <div><span className="text-xs text-gray-500">CPU Usage</span><p className={`text-sm font-mono ${selected.cpu_percent > 50 ? 'text-cyber-danger' : 'text-gray-200'}`}>{selected.cpu_percent?.toFixed(1)}%</p></div>
            <div><span className="text-xs text-gray-500">Memory Usage</span><p className={`text-sm font-mono ${selected.memory_percent > 20 ? 'text-cyber-danger' : 'text-gray-200'}`}>{selected.memory_percent?.toFixed(1)}%</p></div>
          </div>
          <div><span className="text-xs text-gray-500">Command Line</span><p className="text-sm text-gray-200 font-mono break-all">{selected.cmdline || '-'}</p></div>
          {selected.anomaly_reason && (
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20">
              <span className="text-xs text-red-400 font-semibold">Anomaly</span>
              <p className="text-sm text-red-300 mt-1">{selected.anomaly_reason}</p>
            </div>
          )}
          {selected.connections && selected.connections.length > 0 && (
            <div><span className="text-xs text-gray-500">Network Connections</span>
              {selected.connections.map((c: any, i: number) => (
                <p key={i} className="text-sm font-mono text-gray-400">{c.laddr?.ip}:{c.laddr?.port} → {c.raddr?.ip}:{c.raddr?.port} ({c.status})</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
