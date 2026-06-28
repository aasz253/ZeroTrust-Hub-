import { useEffect, useState } from 'react';
import { Server, Monitor, Activity, Globe, Shield, Wifi, Network } from 'lucide-react';
import { network } from '../services/api';
import type { Device, NetworkStats } from '../types';

export default function NetworkMonitor() {
  const [stats, setStats] = useState<NetworkStats | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      network.stats(),
      network.devices(),
    ]).then(([s, d]) => {
      setStats(s);
      setDevices(d.items);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

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
        <h1 className="text-2xl font-bold text-white">Network Monitor</h1>
        <p className="text-gray-500 mt-1">Real-time network monitoring and device inventory</p>
      </div>

      <div className="glass p-4 flex flex-wrap items-center gap-4 text-sm">
        {stats?.wifi_ssid && (
          <div className="flex items-center gap-2 text-gray-400">
            <Wifi className="w-4 h-4 text-cyber-accent" />
            <span>SSID: <span className="text-gray-200 font-mono">{stats.wifi_ssid}</span></span>
          </div>
        )}
        {stats?.gateway_ip && (
          <div className="flex items-center gap-2 text-gray-400">
            <Network className="w-4 h-4 text-cyber-accent" />
            <span>Gateway: <span className="text-gray-200 font-mono">{stats.gateway_ip}</span></span>
          </div>
        )}
        {stats?.interface_name && (
          <div className="flex items-center gap-2 text-gray-400">
            <Server className="w-4 h-4 text-cyber-accent" />
            <span>Interface: <span className="text-gray-200 font-mono">{stats.interface_name}</span></span>
          </div>
        )}
        <span className="text-gray-600 ml-auto">Last scanned: real-time</span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Active Hosts', value: stats?.online_count ?? 0, icon: Monitor, color: 'text-cyber-success' },
          { label: 'Open Ports', value: stats?.open_ports_total ?? 0, icon: Activity, color: 'text-cyber-accent' },
          { label: 'Suspicious Devices', value: stats?.suspicious_count ?? 0, icon: Shield, color: 'text-cyber-danger' },
          { label: 'Total Devices', value: stats?.total_devices ?? 0, icon: Globe, color: 'text-cyber-warning' },
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
        <div className="p-4 border-b border-gray-800/50 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Device Inventory</h2>
          <span className="text-xs text-gray-500">Discovered via ARP + port scan</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800/50">
                <th className="text-left p-4 text-sm font-medium text-gray-500">Host</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">IP Address</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">MAC</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Open Ports</th>
              </tr>
            </thead>
            <tbody>
              {devices.map((device) => (
                <tr key={device.ip_address} className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <Server className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-200">{device.hostname || device.ip_address}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-sm font-mono text-gray-400">{device.ip_address}</span>
                  </td>
                  <td className="p-4">
                    <span className="text-xs font-mono text-gray-500">{device.mac_address || 'N/A'}</span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      device.status === 'online' ? 'text-green-400 bg-green-500/10 border border-green-500/20' :
                      device.status === 'suspicious' ? 'text-red-400 bg-red-500/10 border border-red-500/20' :
                      'text-gray-500 bg-gray-500/10 border border-gray-500/20'
                    }`}>
                      {device.status}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex gap-1 flex-wrap">
                      {(device.open_ports || []).map((port: number) => (
                        <span key={port} className="px-1.5 py-0.5 rounded text-xs bg-gray-800 text-gray-400 font-mono">
                          {port}
                        </span>
                      ))}
                      {(device.open_ports || []).length === 0 && (
                        <span className="text-xs text-gray-600">None detected</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {devices.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-12 text-center text-gray-500">
                    No devices discovered on the local network. Devices are detected via ARP table and port scanning.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
