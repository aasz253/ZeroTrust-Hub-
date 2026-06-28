import { useEffect, useState } from 'react';
import { Shield, AlertTriangle, Bug, Monitor, Activity, Zap, Server, Globe } from 'lucide-react';
import { dashboard } from '../services/api';
import type { DashboardStats } from '../types';

const severityColors: Record<string, string> = {
  CRITICAL: 'text-red-400 bg-red-500/10 border-red-500/20',
  HIGH: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  MEDIUM: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  LOW: 'text-green-400 bg-green-500/10 border-green-500/20',
};

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboard.stats().then(setStats).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-accent" />
      </div>
    );
  }

  const statCards = [
    { label: 'Threat Score', value: `${stats?.threat_score || 0}%`, icon: Shield, color: 'text-cyber-danger', gradient: 'from-red-500/10 to-transparent' },
    { label: 'Active Alerts', value: stats?.active_alerts || 0, icon: AlertTriangle, color: 'text-cyber-warning', gradient: 'from-yellow-500/10 to-transparent' },
    { label: 'Critical Vulnerabilities', value: stats?.critical_vulnerabilities || 0, icon: Bug, color: 'text-cyber-danger', gradient: 'from-red-500/10 to-transparent' },
    { label: 'Devices Online', value: stats?.devices_online || 0, icon: Monitor, color: 'text-cyber-success', gradient: 'from-green-500/10 to-transparent' },
    { label: 'Security Health', value: `${stats?.security_health || 0}%`, icon: Activity, color: 'text-cyber-accent', gradient: 'from-cyan-500/10 to-transparent' },
    { label: 'Total Scans', value: stats?.total_scans || 0, icon: Server, color: 'text-cyber-secondary', gradient: 'from-purple-500/10 to-transparent' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white glitch-text">
          <span className="text-cyber-accent neon-text">$</span> Security Dashboard
        </h1>
        <p className="text-gray-500 mt-1 font-mono text-sm">
          <span className="text-cyber-accent">~$</span> Real-time security overview and threat monitoring
          <span className="animate-pulse ml-1 text-cyber-accent">_</span>
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {statCards.map((card) => (
          <div key={card.label} className={`stat-card bg-gradient-to-br ${card.gradient}`}>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500">{card.label}</p>
                <p className={`text-2xl font-bold mt-1 ${card.color}`}>{card.value}</p>
              </div>
              <card.icon className={`w-5 h-5 ${card.color} opacity-50`} />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Vulnerability Severity</h2>
          <div className="space-y-3">
            {Object.entries(stats?.vulnerability_severity || {}).map(([severity, count]) => (
              <div key={severity} className="flex items-center gap-3">
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${severityColors[severity] || 'text-gray-400 bg-gray-500/10'}`}>
                  {severity}
                </span>
                <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      severity === 'CRITICAL' ? 'bg-red-500' :
                      severity === 'HIGH' ? 'bg-orange-500' :
                      severity === 'MEDIUM' ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(100, (count as number) * 20)}%` }}
                  />
                </div>
                <span className="text-sm text-gray-400 w-8 text-right">{count as number}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Threat Types</h2>
          <div className="space-y-3">
            {Object.entries(stats?.threat_types || {}).map(([type, count]) => (
              <div key={type} className="flex items-center gap-3">
                <Globe className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-300 flex-1 capitalize">{type.replace(/-/g, ' ')}</span>
                <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full rounded-full bg-cyber-secondary transition-all duration-500" style={{ width: `${Math.min(100, (count as number) * 15)}%` }} />
                </div>
                <span className="text-sm text-gray-400 w-8 text-right">{count as number}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass p-6">
          <h2 className="text-lg font-semibold text-white mb-4">AI Recommendations</h2>
          <div className="space-y-3">
            {(stats?.ai_recommendations || []).map((rec, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-cyber-accent/5 border border-cyber-accent/10">
                <Zap className="w-4 h-4 text-cyber-accent mt-0.5 flex-shrink-0" />
                <p className="text-sm text-gray-300">{rec}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="glass p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Top Threats</h2>
          <div className="space-y-3">
            {(stats?.top_threats || []).map((threat) => (
              <div key={threat.id} className="flex items-center justify-between p-3 rounded-xl bg-gray-800/30">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-4 h-4 text-cyber-warning" />
                  <div>
                    <p className="text-sm text-gray-200">{threat.indicator}</p>
                    <p className="text-xs text-gray-500">{threat.threat_type}</p>
                  </div>
                </div>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${severityColors[threat.severity] || ''}`}>
                  {threat.severity}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
