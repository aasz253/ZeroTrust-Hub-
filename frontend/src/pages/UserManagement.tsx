import { useEffect, useState } from 'react';
import { Users, Shield, Trash2, UserCheck, UserX } from 'lucide-react';
import { users as usersApi } from '../services/api';
import type { User } from '../types';

export default function UserManagement() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    usersApi.list().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  const toggleActive = async (user: User) => {
    await usersApi.update(user.id, { is_active: !user.is_active });
    const d = await usersApi.list();
    setData(d);
  };

  const deleteUser = async (id: number) => {
    await usersApi.delete(id);
    const d = await usersApi.list();
    setData(d);
  };

  if (loading) return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-accent" /></div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">User Management</h1>
        <p className="text-gray-500 mt-1">Manage users, roles, and permissions</p>
      </div>

      <div className="glass overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800/50">
                <th className="text-left p-4 text-sm font-medium text-gray-500">User</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Email</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Role</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left p-4 text-sm font-medium text-gray-500">Last Login</th>
                <th className="text-right p-4 text-sm font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.items?.map((user: User) => (
                <tr key={user.id} className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-cyber-secondary/10 border border-cyber-secondary/20 flex items-center justify-center">
                        <Users className="w-4 h-4 text-cyber-secondary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-200">{user.full_name || user.username}</p>
                        <p className="text-xs text-gray-500">@{user.username}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-4 text-sm text-gray-400">{user.email}</td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${
                      user.role === 'admin' ? 'text-cyber-secondary bg-cyber-secondary/10 border border-cyber-secondary/20' :
                      user.role === 'analyst' ? 'text-cyber-accent bg-cyber-accent/10 border border-cyber-accent/20' :
                      'text-gray-400 bg-gray-500/10 border border-gray-500/20'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`flex items-center gap-1 text-xs ${user.is_active ? 'text-green-400' : 'text-red-400'}`}>
                      {user.is_active ? <UserCheck className="w-3 h-3" /> : <UserX className="w-3 h-3" />}
                      {user.is_active ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                  <td className="p-4 text-sm text-gray-500">
                    {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                  </td>
                  <td className="p-4">
                    <div className="flex justify-end gap-2">
                      <button onClick={() => toggleActive(user)} className={`p-1.5 rounded-lg transition-colors ${
                        user.is_active ? 'text-gray-500 hover:text-red-400' : 'text-gray-500 hover:text-green-400'
                      }`}>
                        {user.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                      </button>
                      <button onClick={() => deleteUser(user.id)} className="p-1.5 rounded-lg text-gray-500 hover:text-red-400 transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
