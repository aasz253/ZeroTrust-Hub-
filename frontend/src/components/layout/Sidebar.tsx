import { NavLink } from 'react-router-dom';
import {
  Shield, Activity, Globe, Search, AlertTriangle, Bug,
  Key, MessageSquare, FileText, Bell, Settings, Users,
  FileSearch, LayoutDashboard, BarChart3, Radio,
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/threats', icon: AlertTriangle, label: 'Threat Intelligence' },
  { to: '/network', icon: Radio, label: 'Network Monitor' },
  { to: '/scanner', icon: Search, label: 'Vulnerability Scanner' },
  { to: '/cves', icon: Bug, label: 'CVE Explorer' },
  { to: '/malware', icon: FileSearch, label: 'Malware Scanner' },
  { to: '/password', icon: Key, label: 'Password Analyzer' },
  { to: '/ai-assistant', icon: MessageSquare, label: 'AI Assistant' },
  { to: '/reports', icon: FileText, label: 'Reports' },
  { to: '/notifications', icon: Bell, label: 'Notifications' },
];

const adminItems = [
  { to: '/admin/users', icon: Users, label: 'User Management' },
  { to: '/admin/audit-logs', icon: Activity, label: 'Audit Logs' },
  { to: '/admin/settings', icon: Settings, label: 'Settings' },
];

export default function Sidebar() {
  const user = useAuthStore((s) => s.user);

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-cyber-card/90 backdrop-blur-xl border-r border-gray-800/50 z-50 overflow-y-auto scrollbar-thin">
      <div className="p-6 border-b border-gray-800/50">
        <NavLink to="/dashboard" className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-cyber-accent" />
          <div>
            <h1 className="text-lg font-bold text-white">ZeroTrust</h1>
            <p className="text-xs text-gray-500">Security Hub</p>
          </div>
        </NavLink>
      </div>

      <nav className="p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm transition-all duration-200 ${
                isActive
                  ? 'bg-cyber-accent/10 text-cyber-accent border border-cyber-accent/20'
                  : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200'
              }`
            }
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </NavLink>
        ))}

        {user?.role === 'admin' && (
          <>
            <div className="pt-4 pb-2">
              <p className="px-4 text-xs font-semibold uppercase tracking-wider text-gray-500">
                Admin
              </p>
            </div>
            {adminItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm transition-all duration-200 ${
                    isActive
                      ? 'bg-cyber-secondary/10 text-cyber-secondary border border-cyber-secondary/20'
                      : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200'
                  }`
                }
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </NavLink>
            ))}
          </>
        )}
      </nav>
    </aside>
  );
}
