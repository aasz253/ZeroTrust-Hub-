import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { useUIStore } from '../../store/uiStore';

export default function Layout() {
  const { pathname } = useLocation();
  const setSidebarOpen = useUIStore((s) => s.setSidebarOpen);

  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname, setSidebarOpen]);

  return (
    <div className="min-h-screen bg-cyber-bg">
      <div className="scanline-overlay" />
      <Sidebar />
      <Header />
      <main className="lg:ml-64 pt-16 min-h-screen">
        <div className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
