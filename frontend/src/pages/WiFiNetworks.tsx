import { useEffect, useState } from 'react';
import { Wifi, WifiOff, RefreshCw, Signal, Lock, Unlock, Zap, Power } from 'lucide-react';
import { api } from '../services/api';
import toast from 'react-hot-toast';

interface WiFiNetwork {
  ssid: string;
  signal: number;
  signal_percent: number;
  security: string;
  channel: string;
}

interface ActiveConnection {
  ssid: string | null;
  interface: string | null;
  status: string;
}

export default function WiFiNetworks() {
  const [networks, setNetworks] = useState<WiFiNetwork[]>([]);
  const [active, setActive] = useState<ActiveConnection | null>(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const data = await api.get('/wifi/scan').then(r => r.data);
      setNetworks(data.networks || []);
      setActive(data.active_connection);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to scan WiFi');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleScan = async () => {
    setScanning(true);
    await fetchData();
    setScanning(false);
    toast.success('WiFi scan complete');
  };

  const handleConnect = async (ssid: string) => {
    if (connecting) return;
    setConnecting(ssid);
    try {
      const pwd = showPassword === ssid ? password : '';
      await api.post('/wifi/connect', { ssid, password: pwd });
      toast.success(`Connected to ${ssid}`);
      setShowPassword(null);
      setPassword('');
      fetchData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Connection failed');
    } finally {
      setConnecting(null);
    }
  };

  const handleDisconnect = async () => {
    try {
      await api.post('/wifi/disconnect');
      toast.success('Disconnected');
      fetchData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Disconnect failed');
    }
  };

  const getSignalIcon = (level: number) => {
    if (level >= 60) return Zap;
    if (level >= 30) return Signal;
    return Wifi;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">WiFi Networks</h1>
          <p className="text-gray-500 mt-1">Scan, connect, and manage wireless networks</p>
        </div>
        <button onClick={handleScan} disabled={scanning} className="btn-primary flex items-center gap-2">
          <RefreshCw className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} />
          {scanning ? 'Scanning...' : 'Scan'}
        </button>
      </div>

      {active?.ssid && (
        <div className="glass p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Wifi className="w-5 h-5 text-cyber-success" />
            <div>
              <p className="text-sm text-gray-200">
                Connected to <span className="font-semibold text-cyber-accent">{active.ssid}</span>
              </p>
              <p className="text-xs text-gray-500">Interface: {active.interface}</p>
            </div>
          </div>
          <button onClick={handleDisconnect} className="btn-secondary flex items-center gap-2 text-sm">
            <Power className="w-4 h-4" /> Disconnect
          </button>
        </div>
      )}

      {!active?.ssid && (
        <div className="glass p-4 flex items-center gap-3">
          <WifiOff className="w-5 h-5 text-gray-500" />
          <p className="text-sm text-gray-400">Not connected to any WiFi network</p>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-accent" />
        </div>
      ) : (
        <div className="glass overflow-hidden">
          <div className="p-4 border-b border-gray-800/50">
            <h2 className="text-lg font-semibold text-white">
              Available Networks ({networks.length})
            </h2>
          </div>
          <div className="divide-y divide-gray-800/30">
            {networks.map((net) => {
              const SignalIcon = getSignalIcon(net.signal_percent);
              const isActive = active?.ssid === net.ssid;
              return (
                <div key={net.ssid} className={`p-4 flex items-center justify-between hover:bg-gray-800/20 transition-colors ${isActive ? 'bg-cyber-accent/5' : ''}`}>
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <SignalIcon className={`w-5 h-5 flex-shrink-0 ${
                      net.signal_percent >= 60 ? 'text-cyber-success' :
                      net.signal_percent >= 30 ? 'text-cyber-warning' : 'text-gray-500'
                    }`} />
                    <div className="min-w-0">
                      <p className="text-sm text-gray-200 truncate">
                        {net.ssid}
                        {isActive && <span className="ml-2 text-xs text-cyber-accent">(Connected)</span>}
                      </p>
                      <div className="flex items-center gap-3 text-xs text-gray-500 mt-0.5">
                        <span>Signal: {net.signal_percent}%</span>
                        <span>Ch: {net.channel}</span>
                        <span className="flex items-center gap-1">
                          {net.security === 'Open' || net.security === '' ? (
                            <><Unlock className="w-3 h-3 text-green-400" /> Open</>
                          ) : (
                            <><Lock className="w-3 h-3 text-yellow-400" /> Secured</>
                          )}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="w-32 flex items-center gap-2">
                    {net.security !== 'Open' && showPassword === net.ssid && (
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                        className="input-field text-xs py-1.5 flex-1 min-w-0"
                      />
                    )}
                    {isActive ? (
                      <button onClick={handleDisconnect} className="px-3 py-1.5 rounded-lg text-xs bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20">
                        Disconnect
                      </button>
                    ) : (
                      <button
                        onClick={() => {
                          if (net.security !== 'Open' && showPassword !== net.ssid) {
                            setShowPassword(net.ssid);
                          } else {
                            handleConnect(net.ssid);
                          }
                        }}
                        disabled={connecting === net.ssid}
                        className="px-3 py-1.5 rounded-lg text-xs bg-cyber-accent/10 text-cyber-accent hover:bg-cyber-accent/20 border border-cyber-accent/20 disabled:opacity-50 whitespace-nowrap"
                      >
                        {connecting === net.ssid ? 'Connecting...' : 'Connect'}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
