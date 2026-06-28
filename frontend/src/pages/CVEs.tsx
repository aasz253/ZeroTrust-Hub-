import { useEffect, useState } from 'react';
import { Search, Bug, ExternalLink } from 'lucide-react';
import { cves } from '../services/api';
import type { Vulnerability } from '../types';

const severityColors: Record<string, string> = {
  CRITICAL: 'text-red-400 bg-red-500/10 border-red-500/20',
  HIGH: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  MEDIUM: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  LOW: 'text-green-400 bg-green-500/10 border-green-500/20',
};

export default function CVEs() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [severity, setSeverity] = useState('');
  const [selected, setSelected] = useState<Vulnerability | null>(null);
  const [page, setPage] = useState(1);

  useEffect(() => {
    setLoading(true);
    cves.search({ query: search || undefined, severity: severity || undefined, page })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [search, severity, page]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">CVE Explorer</h1>
        <p className="text-gray-500 mt-1">Search and analyze Common Vulnerabilities and Exposures</p>
      </div>

      <div className="flex flex-wrap gap-4 items-center">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search CVE ID, title, or description..."
            className="input-field pl-10"
          />
        </div>
        <select value={severity} onChange={(e) => { setSeverity(e.target.value); setPage(1); }} className="input-field w-40">
          <option value="">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-800/50">
                  <th className="text-left p-4 text-sm font-medium text-gray-500">CVE ID</th>
                  <th className="text-left p-4 text-sm font-medium text-gray-500">Title</th>
                  <th className="text-left p-4 text-sm font-medium text-gray-500">Severity</th>
                  <th className="text-left p-4 text-sm font-medium text-gray-500">CVSS</th>
                </tr>
              </thead>
              <tbody>
                {data?.items?.map((vuln: Vulnerability) => (
                  <tr
                    key={vuln.id}
                    onClick={() => setSelected(vuln)}
                    className={`border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors cursor-pointer ${
                      selected?.id === vuln.id ? 'bg-cyber-accent/5' : ''
                    }`}
                  >
                    <td className="p-4">
                      <span className="text-sm font-mono text-cyber-accent">{vuln.cve_id}</span>
                    </td>
                    <td className="p-4 text-sm text-gray-300">{vuln.title}</td>
                    <td className="p-4">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${severityColors[vuln.severity] || ''}`}>
                        {vuln.severity}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`text-sm font-bold ${
                        vuln.cvss_score >= 9 ? 'text-red-400' :
                        vuln.cvss_score >= 7 ? 'text-orange-400' :
                        vuln.cvss_score >= 4 ? 'text-yellow-400' : 'text-green-400'
                      }`}>
                        {vuln.cvss_score}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data && (
            <div className="flex items-center justify-between p-4 border-t border-gray-800/50">
              <span className="text-sm text-gray-500">
                Page {data.page} of {data.pages} ({data.total} results)
              </span>
              <div className="flex gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage(p => p - 1)}
                  className="px-3 py-1.5 text-sm rounded-lg bg-gray-800/50 text-gray-400 hover:text-white disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  disabled={page >= (data?.pages || 1)}
                  onClick={() => setPage(p => p + 1)}
                  className="px-3 py-1.5 text-sm rounded-lg bg-gray-800/50 text-gray-400 hover:text-white disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="glass p-6">
          {selected ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-lg font-mono font-bold text-cyber-accent">{selected.cve_id}</span>
                <Bug className="w-5 h-5 text-cyber-accent" />
              </div>
              <h3 className="text-white font-semibold">{selected.title}</h3>
              <p className="text-sm text-gray-400">{selected.description}</p>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-xl bg-gray-800/50">
                  <p className="text-xs text-gray-500">Severity</p>
                  <span className={`text-sm font-bold ${severityColors[selected.severity]?.split(' ')[0] || ''}`}>
                    {selected.severity}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-gray-800/50">
                  <p className="text-xs text-gray-500">CVSS Score</p>
                  <p className="text-2xl font-bold text-white">{selected.cvss_score}</p>
                </div>
              </div>

              {selected.affected_vendor && (
                <div className="space-y-2">
                  <p className="text-sm text-gray-500">Affected: {selected.affected_vendor} {selected.affected_product}</p>
                </div>
              )}

              {selected.remediation && (
                <div className="p-4 rounded-xl bg-green-500/5 border border-green-500/20">
                  <p className="text-xs text-green-400 font-medium mb-1">Remediation</p>
                  <p className="text-sm text-gray-300">{selected.remediation}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <Bug className="w-12 h-12 text-gray-600 mb-3" />
              <p className="text-gray-500">Select a CVE to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
