import { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Save, Key, Bot, Search, Shield } from 'lucide-react';
import { settings as settingsApi } from '../services/api';
import toast from 'react-hot-toast';

export default function Settings() {
  const [data, setData] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    settingsApi.get().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  const updateSetting = async (key: string, value: string) => {
    try {
      await settingsApi.update(key, value);
      setData((prev) => ({ ...prev, [key]: { ...prev[key], value } }));
      toast.success(`${key} updated`);
    } catch {
      toast.error('Failed to update setting');
    }
  };

  const categories = [...new Set(Object.values(data).map((s: any) => s.category))];

  if (loading) return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-accent" /></div>;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">System Settings</h1>
        <p className="text-gray-500 mt-1">Configure system parameters and integrations</p>
      </div>

      {categories.map((category) => (
        <div key={category} className="glass p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white capitalize flex items-center gap-2">
            {category === 'ai' && <Bot className="w-5 h-5 text-cyber-accent" />}
            {category === 'scanner' && <Search className="w-5 h-5 text-cyber-accent" />}
            {category === 'general' && <SettingsIcon className="w-5 h-5 text-cyber-accent" />}
            {category === 'cve' && <Shield className="w-5 h-5 text-cyber-accent" />}
            {category}
          </h2>

          {Object.entries(data)
            .filter(([_, s]) => (s as any).category === category)
            .map(([key, setting]) => (
              <div key={key} className="flex items-center justify-between py-3 border-b border-gray-800/30 last:border-0">
                <div>
                  <p className="text-sm text-gray-200">{key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}</p>
                  <p className="text-xs text-gray-500">{(setting as any).description}</p>
                </div>
                <div className="flex items-center gap-3">
                  {(setting as any).type === 'boolean' ? (
                    <button
                      onClick={() => updateSetting(key, (setting as any).value === 'true' ? 'false' : 'true')}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        (setting as any).value === 'true' ? 'bg-cyber-accent' : 'bg-gray-700'
                      }`}
                    >
                      <div className={`w-5 h-5 rounded-full bg-white transition-transform ${
                        (setting as any).value === 'true' ? 'translate-x-6' : 'translate-x-0.5'
                      }`} />
                    </button>
                  ) : (
                    <div className="flex items-center gap-2">
                      <input
                        type={key.includes('key') || key.includes('secret') ? 'password' : 'text'}
                        defaultValue={(setting as any).value}
                        onBlur={(e) => updateSetting(key, e.target.value)}
                        className="input-field w-48 text-sm"
                      />
                      <button onClick={() => {
                        const input = document.querySelector(`[data-key="${key}"]`) as HTMLInputElement;
                        if (input) updateSetting(key, input.value);
                      }} className="p-2 rounded-lg text-gray-500 hover:text-cyber-accent transition-colors">
                        <Save className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
        </div>
      ))}
    </div>
  );
}
