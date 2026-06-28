import { Server, Monitor, Activity, Globe, Wifi, Shield } from 'lucide-react';

const mockHosts = [
  { ip: '10.0.1.1', name: 'Gateway', status: 'online', ports: [80, 443, 22], os: 'Linux' },
  { ip: '10.0.1.10', name: 'Web Server', status: 'online', ports: [80, 443], os: 'Ubuntu 22.04' },
  { ip: '10.0.1.20', name: 'Database', status: 'online', ports: [5432, 22], os: 'Debian 12' },
  { ip: '10.0.1.30', name: 'Mail Server', status: 'online', ports: [25, 587, 993], os: 'CentOS 9' },
  { ip: '10.0.1.50', name: 'Dev Workstation', status: 'offline', ports: [22], os: 'Windows 11' },
  { ip: '192.168.1.100', name: 'Unknown Device', status: 'suspicious', ports: [22, 3389, 445], os: 'Unknown' },
];

export default function NetworkMonitor() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Network Monitor</h1>
        <p className="text-gray-500 mt-1">Real-time network monitoring and device inventory</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Active Hosts', value: '42', icon: Monitor, color: 'text-cyber-success' },
          { label: 'Open Ports', value: '1,247', icon: Activity, color: 'text-cyber-accent' },
          { label: 'Suspicious IPs', value: '3', icon: Shield, color: 'text-cyber-danger' },
          { label: 'Live Connections', value: '156', icon: Globe, color: 'text-cyber-warning' },
        ].map((stat) => (
          <div key={stat.label} className="stat-card">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
              </div>
              <stat.icon className={`w-5 h-5 ${stat.color} opacity-50`} />
            </div>
          </div>
        ))}
      </div>

      <div className="glass overflow-hidden">
        <div className="p-4 border-b border-gray-800/50">
          <h2 className="text-lg font-semibold text-white">Device Inventory</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800/50">
                <th className="text-left p-4 text-sm font-medium text-gray-500">Host</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">IP Address</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Open Ports</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">OS</th>
              </tr>
            </thead>
            <tbody>
              {mockHosts.map((host) => (
                <tr key={host.ip} className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <Server className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-200">{host.name}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-sm font-mono text-gray-400">{host.ip}</span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      host.status === 'online' ? 'text-green-400 bg-green-500/10 border border-green-500/20' :
                      host.status === 'suspicious' ? 'text-red-400 bg-red-500/10 border border-red-500/20' :
                      'text-gray-500 bg-gray-500/10 border border-gray-500/20'
                    }`}>
                      {host.status}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex gap-1 flex-wrap">
                      {host.ports.map((port) => (
                        <span key={port} className="px-1.5 py-0.5 rounded text-xs bg-gray-800 text-gray-400 font-mono">
                          {port}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="p-4 text-sm text-gray-400">{host.os}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
