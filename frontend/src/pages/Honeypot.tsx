import { useEffect, useState } from 'react';
import { Shield, Play, Square, Activity, Server, Globe, RefreshCw } from 'lucide-react';
import { honeypot } from '../services/api';
import toast from 'react-hot-toast';

export default function Honeypot() {
  const [events, setEvents] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [serviceFilter, setServiceFilter] = useState('');

  const fetch = async () => {
    try {
      const data = await honeypot.events({ page, page_size: 30, service: serviceFilter || undefined });
      setEvents(data.items);
      setTotal(data.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
    honeypot.stats().then(setStats).catch(() => {});
    honeypot.status().then(setStatus).catch(() => {});
  }, [page, serviceFilter]);

  const handleStart = async () => {
    try {
      await honeypot.start();
      toast.success('Honeypots started');
      honeypot.status().then(setStatus);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to start');
    }
  };

  const handleStop = async () => {
    try {
      await honeypot.stop();
      toast.success('Honeypots stopped');
      honeypot.status().then(setStatus);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to stop');
    }
  };

  const severityColor = (s: string) => {
    const map: Record<string, string> = {
      CRITICAL: 'text-red-400 bg-red-500/10 border-red-500/20',
      HIGH: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
      MEDIUM: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
      LOW: 'text-cyber-accent bg-cyber-accent/10 border-cyber-accent/20',
    };
    return map[s] || 'text-gray-500 bg-gray-500/10';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Honeypot</h1>
          <p className="text-gray-500 mt-1">Low-interaction SSH/HTTP/MySQL honeypot to catch attackers in real-time</p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleStart} disabled={status?.running} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyber-success/10 text-cyber-success text-sm border border-cyber-success/20 disabled:opacity-50">
            <Play className="w-4 h-4" /> Start
          </button>
          <button onClick={handleStop} disabled={!status?.running} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-500/10 text-red-400 text-sm border border-red-500/20 disabled:opacity-50">
            <Square className="w-4 h-4" /> Stop
          </button>
        </div>
      </div>

      {status && (
        <div className="glass p-4 flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2"><Shield className={`w-4 h-4 ${status.running ? 'text-cyber-success' : 'text-gray-500'}`} /><span className={`${status.running ? 'text-cyber-success' : 'text-gray-500'}`}>{status.running ? 'Active' : 'Stopped'}</span></div>
          {status.running && <span className="text-gray-400">Ports: {Object.keys(status.services || {}).join(', ')}</span>}
        </div>
      )}

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="stat-card"><div className="flex items-center gap-2"><Activity className="w-4 h-4 text-cyber-accent" /><p className="text-sm text-gray-500">Total Events</p></div><p className="text-2xl font-bold text-white mt-1">{stats.total_events}</p></div>
          <div className="stat-card"><div className="flex items-center gap-2"><Server className="w-4 h-4 text-cyber-warning" /><p className="text-sm text-gray-500">SSH Attacks</p></div><p className="text-2xl font-bold text-cyber-warning mt-1">{stats.by_service?.ssh || 0}</p></div>
          <div className="stat-card"><div className="flex items-center gap-2"><Globe className="w-4 h-4 text-cyber-accent" /><p className="text-sm text-gray-500">HTTP Probe</p></div><p className="text-2xl font-bold text-cyber-accent mt-1">{stats.by_service?.http || 0}</p></div>
          <div className="stat-card"><div className="flex items-center gap-2"><Shield className="w-4 h-4 text-cyber-danger" /><p className="text-sm text-gray-500">Unique IPs</p></div><p className="text-2xl font-bold text-cyber-danger mt-1">{stats.top_attacker_ips?.length || 0}</p></div>
        </div>
      )}

      <div className="flex gap-3">
        <select value={serviceFilter} onChange={(e) => setServiceFilter(e.target.value)} className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm">
          <option value="">All Services</option>
          <option value="ssh">SSH</option>
          <option value="http">HTTP</option>
          <option value="mysql">MySQL</option>
        </select>
        <button onClick={fetch} className="px-4 py-2.5 rounded-xl bg-gray-800 text-gray-300 border border-gray-700"><RefreshCw className="w-4 h-4" /></button>
      </div>

      <div className="glass overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead><tr className="border-b border-gray-800/50">
              <th className="text-left p-3 text-sm font-medium text-gray-500">Time</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Service</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Source IP</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Port</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Attack Type</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Severity</th>
            </tr></thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id} className="border-b border-gray-800/30 hover:bg-gray-800/20">
                  <td className="p-3 text-xs font-mono text-gray-500">{e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : '-'}</td>
                  <td className="p-3"><span className="text-sm text-gray-200">{e.service}</span></td>
                  <td className="p-3 text-sm font-mono text-gray-400">{e.source_ip}</td>
                  <td className="p-3 text-sm text-gray-500">{e.destination_port}</td>
                  <td className="p-3 text-sm text-gray-300">{e.attack_type || '-'}</td>
                  <td className="p-3"><span className={`px-2 py-0.5 rounded text-xs font-medium border ${severityColor(e.severity)}`}>{e.severity}</span></td>
                </tr>
              ))}
              {events.length === 0 && <tr><td colSpan={6} className="p-12 text-center text-gray-500">No honeypot events yet. Start the honeypot to begin capturing attacks.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
