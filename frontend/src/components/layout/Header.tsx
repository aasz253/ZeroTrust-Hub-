import { Bell, LogOut, User, Shield, Menu } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { notifications as notificationsApi } from '../../services/api';

export default function Header() {
  const { user, logout } = useAuthStore();
  const { toggleSidebar } = useUIStore();
  const navigate = useNavigate();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    const fetchUnread = async () => {
      try {
        const data = await notificationsApi.list({ is_read: false, page_size: 1 });
        setUnread(data.unread || 0);
      } catch {}
    };
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="fixed top-0 left-0 lg:left-64 right-0 h-16 bg-cyber-card/70 backdrop-blur-xl border-b border-gray-800/50 z-30">
      <div className="flex items-center justify-between h-full px-4 lg:px-8">
        <div className="flex items-center gap-3">
          <button
            onClick={toggleSidebar}
            className="lg:hidden p-2 rounded-xl hover:bg-gray-800/50 text-gray-400 hover:text-white transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>
          <Shield className="w-5 h-5 text-cyber-accent/60 hidden sm:block" />
          <span className="text-sm text-gray-400 hidden sm:block">Security Operations Center</span>
        </div>

        <div className="flex items-center gap-2 sm:gap-4">
          <button
            onClick={() => navigate('/dashboard/notifications')}
            className="relative p-2 rounded-xl hover:bg-gray-800/50 transition-colors"
          >
            <Bell className="w-5 h-5 text-gray-400" />
            {unread > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-cyber-danger rounded-full text-[10px] flex items-center justify-center font-bold">
                {unread > 9 ? '9+' : unread}
              </span>
            )}
          </button>

          <div className="flex items-center gap-2 sm:gap-3 pl-2 sm:pl-4 border-l border-gray-800/50">
            <button onClick={() => navigate('/dashboard/profile')} className="hidden sm:block text-right hover:opacity-80">
              <p className="text-sm font-medium text-gray-200">{user?.full_name || user?.username}</p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </button>
            <button
              onClick={() => navigate('/dashboard/profile')}
              className="w-9 h-9 rounded-xl bg-cyber-secondary/20 border border-cyber-secondary/30 flex items-center justify-center hover:bg-cyber-secondary/30 transition-colors"
            >
              <User className="w-4 h-4 text-cyber-secondary" />
            </button>
            <button
              onClick={handleLogout}
              className="p-2 rounded-xl hover:bg-gray-800/50 transition-colors text-gray-500 hover:text-cyber-danger"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
