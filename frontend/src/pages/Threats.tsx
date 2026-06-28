import { useEffect, useState } from 'react';
import { AlertTriangle, Globe, Search, Shield } from 'lucide-react';
import { threats as threatsApi } from '../services/api';
import type { Threat, PaginatedResponse } from '../types';

const severityColors: Record<string, string> = {
  CRITICAL: 'severity-critical',
  HIGH: 'severity-high',
  MEDIUM: 'severity-medium',
  LOW: 'severity-low',
};

export default function Threats() {
  const [data, setData] = useState<PaginatedResponse<Threat> | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');

  useEffect(() => {
    threatsApi.list({ page: 1, severity: severityFilter || undefined })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [severityFilter]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-accent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Threat Intelligence</h1>
        <p className="text-gray-500 mt-1">Monitor and analyze cyber threats in real-time</p>
      </div>

      <div className="flex flex-wrap gap-4 items-center">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search threats..."
            className="input-field pl-10"
          />
        </div>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="input-field w-40"
        >
          <option value="">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Shield className="w-4 h-4" />
          <span>{data?.total || 0} threats detected</span>
        </div>
      </div>

      <div className="glass overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800/50">
                <th className="text-left p-4 text-sm font-medium text-gray-500">Indicator</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Type</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Severity</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Source</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Confidence</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((threat) => (
                <tr key={threat.id} className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <Globe className="w-4 h-4 text-cyber-accent" />
                      <span className="text-sm font-mono text-gray-200">{threat.indicator}</span>
                    </div>
                  </td>
                  <td className="p-4 text-sm text-gray-400">{threat.indicator_type}</td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${severityColors[threat.severity] || ''}`}>
                      {threat.severity}
                    </span>
                  </td>
                  <td className="p-4 text-sm text-gray-400">{threat.source || 'Unknown'}</td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            threat.confidence && threat.confidence > 0.8 ? 'bg-green-500' :
                            threat.confidence && threat.confidence > 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${(threat.confidence || 0) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">{Math.round((threat.confidence || 0) * 100)}%</span>
                    </div>
                  </td>
                  <td className="p-4 text-sm text-gray-500">
                    {threat.last_seen ? new Date(threat.last_seen).toLocaleDateString() : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
