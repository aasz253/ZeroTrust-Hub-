import { useEffect, useState } from 'react';
import { Activity, ClipboardList } from 'lucide-react';
import { auditLogs } from '../services/api';

export default function AuditLogs() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    auditLogs.list().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-accent" /></div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Audit Logs</h1>
        <p className="text-gray-500 mt-1">System activity and security audit trail</p>
      </div>

      <div className="glass overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800/50">
                <th className="text-left p-4 text-sm font-medium text-gray-500">Time</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Action</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Resource</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Details</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">IP</th>
              </tr>
            </thead>
            <tbody>
              {data?.items?.map((log: any) => (
                <tr key={log.id} className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors">
                  <td className="p-4 text-sm text-gray-500 whitespace-nowrap">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-200">{log.action}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-sm text-gray-400">{log.resource}</span>
                    {log.resource_id && (
                      <span className="text-xs text-gray-600 ml-1">#{log.resource_id}</span>
                    )}
                  </td>
                  <td className="p-4 text-sm text-gray-500 max-w-xs truncate">{log.details}</td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      log.status === 'success' ? 'text-green-400 bg-green-500/10' :
                      log.status === 'failure' ? 'text-red-400 bg-red-500/10' :
                      'text-gray-400 bg-gray-500/10'
                    }`}>
                      {log.status}
                    </span>
                  </td>
                  <td className="p-4 text-sm font-mono text-gray-500">{log.ip_address || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
