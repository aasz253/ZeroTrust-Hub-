import { useState } from 'react';
import { User, Shield, Key, Save } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { auth } from '../services/api';
import toast from 'react-hot-toast';

export default function Profile() {
  const user = useAuthStore((s) => s.user);
  const [passwords, setPasswords] = useState({ current: '', new: '', confirm: '' });

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwords.new !== passwords.confirm) {
      toast.error('Passwords do not match');
      return;
    }
    try {
      await auth.changePassword(passwords.current, passwords.new);
      toast.success('Password changed');
      setPasswords({ current: '', new: '', confirm: '' });
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to change password');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Profile</h1>
        <p className="text-gray-500 mt-1">Manage your account settings</p>
      </div>

      <div className="glass p-6 space-y-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-cyber-secondary/10 border border-cyber-secondary/20 flex items-center justify-center">
            <User className="w-8 h-8 text-cyber-secondary" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">{user?.full_name || user?.username}</h2>
            <p className="text-sm text-gray-400">{user?.email}</p>
            <span className="inline-block mt-1 px-2 py-0.5 rounded text-xs font-medium text-cyber-accent bg-cyber-accent/10 border border-cyber-accent/20 capitalize">
              {user?.role}
            </span>
          </div>
        </div>
      </div>

      <div className="glass p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Key className="w-5 h-5 text-cyber-accent" /> Change Password
        </h3>
        <form onSubmit={changePassword} className="space-y-4">
          <input
            type="password"
            value={passwords.current}
            onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
            placeholder="Current password"
            className="input-field"
            required
          />
          <input
            type="password"
            value={passwords.new}
            onChange={(e) => setPasswords({ ...passwords, new: e.target.value })}
            placeholder="New password"
            className="input-field"
            required
          />
          <input
            type="password"
            value={passwords.confirm}
            onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
            placeholder="Confirm new password"
            className="input-field"
            required
          />
          <button type="submit" className="btn-primary flex items-center gap-2">
            <Save className="w-4 h-4" /> Update Password
          </button>
        </form>
      </div>
    </div>
  );
}
