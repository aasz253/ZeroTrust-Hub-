import { useEffect, useState } from 'react';
import { Play, Plus, Trash2, ToggleLeft, ToggleRight, History, Shield, Activity } from 'lucide-react';
import { soar } from '../services/api';
import type { Playbook, PlaybookExecution } from '../types';
import toast from 'react-hot-toast';

export default function SOARPlaybooks() {
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [executions, setExecutions] = useState<PlaybookExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', trigger_type: 'all_threats', auto_run: false, actions: [{ type: 'log_event', config: {} }] });

  const fetch = async () => {
    try {
      const data = await soar.playbooks();
      setPlaybooks(data.items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetch(); }, []);

  const handleToggle = async (id: number) => {
    await soar.toggle(id);
    fetch();
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this playbook?')) return;
    try {
      await soar.delete(id);
      toast.success('Playbook deleted');
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Delete failed');
    }
  };

  const handleCreate = async () => {
    try {
      await soar.create(form);
      toast.success('Playbook created');
      setShowCreate(false);
      setForm({ name: '', description: '', trigger_type: 'all_threats', auto_run: false, actions: [{ type: 'log_event', config: {} }] });
      fetch();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Create failed');
    }
  };

  const loadHistory = async () => {
    try {
      const data = await soar.executions({ page: 1, page_size: 20 });
      setExecutions(data.items);
      setShowHistory(true);
    } catch (e) {
      console.error(e);
    }
  };

  const triggerLabels: Record<string, string> = {
    all_threats: 'All Threats',
    severity_threshold: 'Severity Threshold',
    threat_type: 'Threat Type',
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-accent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">SOAR Playbooks</h1>
          <p className="text-gray-500 mt-1">Security Orchestration, Automation and Response</p>
        </div>
        <div className="flex gap-2">
          <button onClick={loadHistory} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm border border-gray-700 hover:bg-gray-700">
            <History className="w-4 h-4" /> History
          </button>
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20 hover:bg-cyber-accent/20">
            <Plus className="w-4 h-4" /> New Playbook
          </button>
        </div>
      </div>

      <div className="grid gap-4">
        {playbooks.map((p) => (
          <div key={p.id} className="glass p-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <Shield className={`w-5 h-5 mt-0.5 ${p.is_active ? 'text-cyber-success' : 'text-gray-500'}`} />
                <div>
                  <h3 className="text-lg font-semibold text-white">{p.name}</h3>
                  <p className="text-sm text-gray-500 mt-0.5">{p.description || 'No description'}</p>
                  <div className="flex gap-3 mt-2">
                    <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400">{triggerLabels[p.trigger_type] || p.trigger_type}</span>
                    <span className="text-xs text-gray-500">{p.actions_count} action{p.actions_count !== 1 ? 's' : ''}</span>
                    {p.auto_run && <span className="text-xs text-cyber-accent">Auto-run</span>}
                  </div>
                </div>
              </div>
              <div className="flex gap-1">
                <button onClick={() => handleToggle(p.id)} className={`p-2 rounded-lg ${p.is_active ? 'text-cyber-success hover:bg-green-500/10' : 'text-gray-500 hover:bg-gray-700'}`} title={p.is_active ? 'Deactivate' : 'Activate'}>
                  {p.is_active ? <ToggleRight className="w-5 h-5" /> : <ToggleLeft className="w-5 h-5" />}
                </button>
                <button onClick={() => handleDelete(p.id)} className="p-2 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
        {playbooks.length === 0 && (
          <div className="glass p-12 text-center">
            <Shield className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500">No playbooks yet. Create your first automated response playbook.</p>
          </div>
        )}
      </div>

      {showCreate && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowCreate(false)}>
          <div className="glass max-w-lg w-full p-6 space-y-4" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-white">Create Playbook</h2>
            <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Playbook name" className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm" />
            <input type="text" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description (optional)" className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm" />
            <select value={form.trigger_type} onChange={(e) => setForm({ ...form, trigger_type: e.target.value })} className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-gray-300 text-sm">
              <option value="all_threats">All Threats</option>
              <option value="severity_threshold">Severity Threshold</option>
              <option value="threat_type">Threat Type</option>
            </select>
            <label className="flex items-center gap-2 text-sm text-gray-400">
              <input type="checkbox" checked={form.auto_run} onChange={(e) => setForm({ ...form, auto_run: e.target.checked })} className="rounded bg-gray-800 border-gray-600" />
              Auto-run on trigger
            </label>
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setShowCreate(false)} className="px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm">Cancel</button>
              <button onClick={handleCreate} disabled={!form.name} className="px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20 disabled:opacity-50">Create</button>
            </div>
          </div>
        </div>
      )}

      {showHistory && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowHistory(false)}>
          <div className="glass max-w-2xl w-full p-6 space-y-4 max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Execution History</h2>
              <button onClick={() => setShowHistory(false)} className="text-gray-500 hover:text-white">✕</button>
            </div>
            {executions.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No executions yet</p>
            ) : (
              executions.map((e) => (
                <div key={e.id} className="flex items-center justify-between p-3 bg-gray-900/50 rounded-xl">
                  <div>
                    <p className="text-sm text-gray-200">Playbook #{e.playbook_id}</p>
                    <p className="text-xs text-gray-500">Triggered by: {e.triggered_by} • {e.created_at ? new Date(e.created_at).toLocaleString() : '-'}</p>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    e.status === 'completed' ? 'text-green-400 bg-green-500/10 border border-green-500/20' :
                    e.status === 'failed' ? 'text-red-400 bg-red-500/10 border border-red-500/20' :
                    'text-yellow-400 bg-yellow-500/10 border border-yellow-500/20'
                  }`}>{e.status}</span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
