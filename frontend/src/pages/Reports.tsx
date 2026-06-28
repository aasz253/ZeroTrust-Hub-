import { useEffect, useState } from 'react';
import { FileText, Download, Plus, Trash2, File as FileIcon } from 'lucide-react';
import { reports as reportsApi } from '../services/api';
import type { Report } from '../types';

export default function Reports() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ title: '', report_type: 'security' });

  const fetch = () => {
    reportsApi.list().then(setData).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { fetch(); }, []);

  const createReport = async (e: React.FormEvent) => {
    e.preventDefault();
    await reportsApi.create(form);
    setShowCreate(false);
    setForm({ title: '', report_type: 'security' });
    fetch();
  };

  const deleteReport = async (id: number) => {
    await reportsApi.delete(id);
    fetch();
  };

  if (loading) return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-accent" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Reports</h1>
          <p className="text-gray-500 mt-1">Security incident reports and documentation</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> New Report
        </button>
      </div>

      {showCreate && (
        <form onSubmit={createReport} className="glass p-6 space-y-4">
          <input
            type="text"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Report title"
            className="input-field"
            required
          />
          <select value={form.report_type} onChange={(e) => setForm({ ...form, report_type: e.target.value })} className="input-field">
            <option value="security">Security Report</option>
            <option value="vulnerability">Vulnerability Assessment</option>
            <option value="incident">Incident Report</option>
            <option value="compliance">Compliance Report</option>
          </select>
          <div className="flex gap-3">
            <button type="submit" className="btn-primary">Create</button>
            <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 rounded-xl border border-gray-700 text-gray-400 hover:text-white">Cancel</button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data?.items?.map((report: Report) => (
          <div key={report.id} className="glass p-6 space-y-4">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-cyber-accent/10">
                  <FileText className="w-5 h-5 text-cyber-accent" />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-white">{report.title}</h3>
                  <p className="text-xs text-gray-500 capitalize">{report.report_type}</p>
                </div>
              </div>
              {report.severity && (
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  report.severity === 'CRITICAL' ? 'text-red-400 bg-red-500/10' :
                  report.severity === 'HIGH' ? 'text-orange-400 bg-orange-500/10' :
                  'text-yellow-400 bg-yellow-500/10'
                }`}>
                  {report.severity}
                </span>
              )}
            </div>
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{new Date(report.created_at).toLocaleDateString()}</span>
              <span className="capitalize">{report.status}</span>
            </div>
            <div className="flex gap-2">
              <button className="p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 text-gray-400 hover:text-white transition-colors">
                <Download className="w-4 h-4" />
              </button>
              <button onClick={() => deleteReport(report.id)} className="p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 text-gray-400 hover:text-red-400 transition-colors">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
