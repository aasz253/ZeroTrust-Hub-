import { useEffect, useState } from 'react';
import { Bell, CheckCheck, AlertTriangle, Info, XCircle, Shield } from 'lucide-react';
import { notifications as notificationsApi } from '../services/api';
import type { Notification } from '../types';

const severityIcons: Record<string, any> = {
  CRITICAL: XCircle,
  HIGH: AlertTriangle,
  MEDIUM: Shield,
  LOW: Info,
};

const severityColors: Record<string, string> = {
  CRITICAL: 'border-l-red-500 bg-red-500/5',
  HIGH: 'border-l-orange-500 bg-orange-500/5',
  MEDIUM: 'border-l-yellow-500 bg-yellow-500/5',
  LOW: 'border-l-cyan-500 bg-cyan-500/5',
  INFO: 'border-l-gray-500 bg-gray-500/5',
};

export default function Notifications() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetch = async () => {
    try {
      const d = await notificationsApi.list();
      setData(d);
    } catch {} finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetch(); }, []);

  const markRead = async (id: number) => {
    await notificationsApi.markRead(id);
    fetch();
  };

  const markAllRead = async () => {
    await notificationsApi.markAllRead();
    fetch();
  };

  if (loading) return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-accent" /></div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Notifications</h1>
          <p className="text-gray-500 mt-1">Security alerts and system notifications</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-400">{data?.unread || 0} unread</span>
          {data?.unread > 0 && (
            <button onClick={markAllRead} className="btn-primary text-sm flex items-center gap-2">
              <CheckCheck className="w-4 h-4" /> Mark All Read
            </button>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {data?.items?.length === 0 ? (
          <div className="glass p-12 text-center">
            <Bell className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-500">No notifications</p>
          </div>
        ) : (
          data?.items?.map((notif: Notification) => {
            const Icon = severityIcons[notif.severity] || Info;
            return (
              <div
                key={notif.id}
                onClick={() => !notif.is_read && markRead(notif.id)}
                className={`glass p-4 border-l-4 cursor-pointer transition-all hover:bg-cyber-card/90 ${
                  severityColors[notif.severity] || severityColors.INFO
                } ${notif.is_read ? 'opacity-60' : ''}`}
              >
                <div className="flex items-start gap-4">
                  <Icon className={`w-5 h-5 mt-0.5 ${
                    notif.severity === 'CRITICAL' ? 'text-red-400' :
                    notif.severity === 'HIGH' ? 'text-orange-400' :
                    notif.severity === 'MEDIUM' ? 'text-yellow-400' : 'text-cyan-400'
                  }`} />
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-sm font-medium text-white">{notif.title}</h3>
                        {notif.message && <p className="text-sm text-gray-400 mt-1">{notif.message}</p>}
                      </div>
                      <span className="text-xs text-gray-600 flex-shrink-0 ml-4">
                        {new Date(notif.created_at).toLocaleString()}
                      </span>
                    </div>
                    {notif.category && (
                      <span className="inline-block mt-2 px-2 py-0.5 rounded text-xs bg-gray-800 text-gray-500">
                        {notif.category}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
