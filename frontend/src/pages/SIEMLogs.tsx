import { useEffect, useState } from 'react';
import { Search, Filter, Activity, Globe, Clock, AlertTriangle, RefreshCw } from 'lucide-react';
import { siem } from '../services/api';
import type { SiemLog } from '../types';

export default function SIEMLogs() {
  const [logs, setLogs] = useState<SiemLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [severity, setSeverity] = useState('');
  const [sourceIp, setSourceIp] = useState('');
  const [program, setProgram] = useState('');
  const [stats, setStats] = useState<any>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetch = async () => {
    try {
      const data = await siem.logs({ page, page_size: 50, search: search || undefined, severity: severity || undefined, source_ip: sourceIp || undefined, program: program || undefined });
      setLogs(data.items);
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
    siem.stats().then(setStats).catch(() => {});
  }, [page, severity, sourceIp, program]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetch, 10000);
    return () => clearInterval(interval);
  }, [autoRefresh, page]);

  const severityColor = (s: string | null) => {
    const map: Record<string, string> = {
      EMERGENCY: 'text-red-400 bg-red-500/10 border-red-500/20',
      ALERT: 'text-red-400 bg-red-500/10 border-red-500/20',
      CRITICAL: 'text-red-400 bg-red-500/10 border-red-500/20',
      ERROR: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
      WARNING: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
      NOTICE: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
      INFO: 'text-cyber-accent bg-cyber-accent/10 border-cyber-accent/20',
      DEBUG: 'text-gray-500 bg-gray-500/10 border-gray-500/20',
    };
    return map[s || ''] || 'text-gray-500 bg-gray-500/10 border-gray-500/20';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">SIEM Logs</h1>
          <p className="text-gray-500 mt-1">Security Information and Event Management</p>
        </div>
        <button onClick={() => setAutoRefresh(!autoRefresh)} className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm border ${
          autoRefresh ? 'bg-cyber-accent/10 text-cyber-accent border-cyber-accent/20' : 'bg-gray-800 text-gray-400 border-gray-700'
        }`}>
          <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} /> Auto
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="stat-card">
            <div className="flex items-center gap-2"><Activity className="w-4 h-4 text-cyber-accent" /><p className="text-sm text-gray-500">Total Logs</p></div>
            <p className="text-2xl font-bold text-white mt-1">{stats.total_logs}</p>
          </div>
          <div className="stat-card">
            <div className="flex items-center gap-2"><Clock className="w-4 h-4 text-cyber-warning" /><p className="text-sm text-gray-500">Last Hour</p></div>
            <p className="text-2xl font-bold text-cyber-warning mt-1">{stats.last_hour}</p>
          </div>
          <div className="stat-card">
            <div className="flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-cyber-danger" /><p className="text-sm text-gray-500">Critical/Error</p></div>
            <p className="text-2xl font-bold text-cyber-danger mt-1">{(stats.severity_distribution?.CRITICAL || 0) + (stats.severity_distribution?.ERROR || 0)}</p>
          </div>
          <div className="stat-card">
            <div className="flex items-center gap-2"><Globe className="w-4 h-4 text-cyber-success" /><p className="text-sm text-gray-500">Sources</p></div>
            <p className="text-2xl font-bold text-cyber-success mt-1">{stats.top_source_ips?.length || 0}</p>
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetch()}
            placeholder="Search messages..." className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm"
          />
        </div>
        <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm">
          <option value="">All Severities</option>
          <option value="EMERGENCY">Emergency</option>
          <option value="ALERT">Alert</option>
          <option value="CRITICAL">Critical</option>
          <option value="ERROR">Error</option>
          <option value="WARNING">Warning</option>
          <option value="NOTICE">Notice</option>
          <option value="INFO">Info</option>
        </select>
        <input type="text" value={sourceIp} onChange={(e) => setSourceIp(e.target.value)} placeholder="Source IP..." className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm w-36" />
        <input type="text" value={program} onChange={(e) => setProgram(e.target.value)} placeholder="Program..." className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm w-36" />
      </div>

      <div className="glass overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800/50">
                <th className="text-left p-3 text-sm font-medium text-gray-500">Time</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Severity</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Source</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Program</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Message</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors">
                  <td className="p-3 text-xs font-mono text-gray-500 whitespace-nowrap">
                    {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : '-'}
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${severityColor(log.severity)}`}>
                      {log.severity || 'UNKNOWN'}
                    </span>
                  </td>
                  <td className="p-3 text-sm font-mono text-gray-400">{log.source_ip || '-'}</td>
                  <td className="p-3 text-sm text-gray-400">{log.program || '-'}</td>
                  <td className="p-3 text-sm text-gray-300 max-w-md truncate">{log.message}</td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr><td colSpan={5} className="p-12 text-center text-gray-500">No logs found. Start the SIEM syslog receiver to collect events.</td></tr>
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
    </div>
  );
}
