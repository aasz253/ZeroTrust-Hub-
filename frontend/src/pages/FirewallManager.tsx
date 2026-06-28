import { useEffect, useState } from 'react';
import { Shield, Plus, Trash2, ToggleLeft, ToggleRight, RefreshCw, Info } from 'lucide-react';
import { firewall } from '../services/api';
import toast from 'react-hot-toast';

export default function FirewallManager() {
  const [rules, setRules] = useState<any[]>([]);
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [filter, setFilter] = useState('');
  const [form, setForm] = useState({ name: '', action: 'block', direction: 'inbound', protocol: 'any', source_ip: '', destination_ip: '', source_port: '', destination_port: '', interface: '', description: '', log_hits: false });

  const fetch = async () => {
    try {
      const data = await firewall.rules({ action: filter || undefined });
      setRules(data.items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
    firewall.status().then(setStatus).catch(() => {});
  }, [filter]);

  const handleToggle = async (id: number) => {
    try {
      await firewall.toggle(id);
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Toggle failed');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this rule?')) return;
    try {
      await firewall.deleteRule(id);
      toast.success('Rule deleted');
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Delete failed');
    }
  };

  const handleCreate = async () => {
    try {
      const payload = {
        ...form,
        source_port: form.source_port ? parseInt(form.source_port) : null,
        destination_port: form.destination_port ? parseInt(form.destination_port) : null,
        source_ip: form.source_ip || null,
        destination_ip: form.destination_ip || null,
        interface: form.interface || null,
      };
      await firewall.create(payload);
      toast.success('Rule created and applied');
      setShowCreate(false);
      setForm({ name: '', action: 'block', direction: 'inbound', protocol: 'any', source_ip: '', destination_ip: '', source_port: '', destination_port: '', interface: '', description: '', log_hits: false });
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Create failed');
    }
  };

  const actionColor = (a: string) => ({
    allow: 'text-green-400 bg-green-500/10 border-green-500/20',
    block: 'text-red-400 bg-red-500/10 border-red-500/20',
    rate_limit: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  }[a] || '');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Firewall Rule Manager</h1>
          <p className="text-gray-500 mt-1">Visual iptables/nftables management with allow/block/rate-limit rules</p>
        </div>
        <div className="flex gap-2">
          {status && <span className="px-3 py-2 rounded-xl bg-gray-800 text-gray-400 text-sm">{status.firewall_type}</span>}
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20">
            <Plus className="w-4 h-4" /> Add Rule
          </button>
        </div>
      </div>

      <div className="flex gap-3">
        <select value={filter} onChange={(e) => setFilter(e.target.value)} className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm">
          <option value="">All Actions</option>
          <option value="allow">Allow</option>
          <option value="block">Block</option>
          <option value="rate_limit">Rate Limit</option>
        </select>
        <button onClick={fetch} className="px-4 py-2.5 rounded-xl bg-gray-800 text-gray-300 border border-gray-700"><RefreshCw className="w-4 h-4" /></button>
      </div>

      <div className="glass overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead><tr className="border-b border-gray-800/50">
              <th className="text-left p-3 text-sm font-medium text-gray-500">Name</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Action</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Direction</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Protocol</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Source</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Destination</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Port</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Hits</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500">Active</th>
              <th className="text-left p-3 text-sm font-medium text-gray-500"></th>
            </tr></thead>
            <tbody>
              {rules.map((r) => (
                <tr key={r.id} className="border-b border-gray-800/30 hover:bg-gray-800/20">
                  <td className="p-3 text-sm text-gray-200">{r.name}</td>
                  <td className="p-3"><span className={`px-2 py-0.5 rounded text-xs font-medium border ${actionColor(r.action)}`}>{r.action}</span></td>
                  <td className="p-3 text-sm text-gray-400">{r.direction}</td>
                  <td className="p-3 text-sm text-gray-400">{r.protocol}</td>
                  <td className="p-3 text-sm font-mono text-gray-500">{r.source_ip || 'Any'}</td>
                  <td className="p-3 text-sm font-mono text-gray-500">{r.destination_ip || 'Any'}</td>
                  <td className="p-3 text-sm font-mono text-gray-500">{r.destination_port || 'Any'}</td>
                  <td className="p-3 text-sm text-gray-500">{r.hit_count}</td>
                  <td className="p-3">{r.is_active ? <ToggleRight className="w-5 h-5 text-cyber-success" /> : <ToggleLeft className="w-5 h-5 text-gray-500" />}</td>
                  <td className="p-3">
                    <div className="flex gap-1">
                      <button onClick={() => handleToggle(r.id)} className="p-1.5 rounded-lg hover:bg-gray-700 text-gray-500"><ToggleLeft className="w-4 h-4" /></button>
                      {!r.is_system && <button onClick={() => handleDelete(r.id)} className="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-500 hover:text-red-400"><Trash2 className="w-4 h-4" /></button>}
                    </div>
                  </td>
                </tr>
              ))}
              {rules.length === 0 && <tr><td colSpan={10} className="p-12 text-center text-gray-500">No firewall rules. Create your first rule to control network traffic.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      {showCreate && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowCreate(false)}>
          <div className="glass max-w-lg w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-white">New Firewall Rule</h2>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Rule name" className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm" />
            <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description" className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm" />
            <div className="grid grid-cols-2 gap-3">
              <select value={form.action} onChange={(e) => setForm({ ...form, action: e.target.value })} className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm">
                <option value="allow">Allow</option>
                <option value="block">Block</option>
                <option value="rate_limit">Rate Limit</option>
              </select>
              <select value={form.direction} onChange={(e) => setForm({ ...form, direction: e.target.value })} className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm">
                <option value="inbound">Inbound</option>
                <option value="outbound">Outbound</option>
                <option value="forward">Forward</option>
              </select>
            </div>
            <select value={form.protocol} onChange={(e) => setForm({ ...form, protocol: e.target.value })} className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm">
              <option value="any">Any Protocol</option>
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
              <option value="icmp">ICMP</option>
            </select>
            <div className="grid grid-cols-2 gap-3">
              <input value={form.source_ip} onChange={(e) => setForm({ ...form, source_ip: e.target.value })} placeholder="Source IP" className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm font-mono" />
              <input value={form.destination_ip} onChange={(e) => setForm({ ...form, destination_ip: e.target.value })} placeholder="Destination IP" className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm font-mono" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <input value={form.source_port} onChange={(e) => setForm({ ...form, source_port: e.target.value })} placeholder="Source port" type="number" className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm" />
              <input value={form.destination_port} onChange={(e) => setForm({ ...form, destination_port: e.target.value })} placeholder="Dest port" type="number" className="px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm" />
            </div>
            <label className="flex items-center gap-2 text-sm text-gray-400">
              <input type="checkbox" checked={form.log_hits} onChange={(e) => setForm({ ...form, log_hits: e.target.checked })} className="rounded bg-gray-800 border-gray-600" />
              Log hits
            </label>
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setShowCreate(false)} className="px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm">Cancel</button>
              <button onClick={handleCreate} disabled={!form.name} className="px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20 disabled:opacity-50">Create & Apply</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
