import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Shield, ArrowLeft, Send } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSent(true);
    toast.success('Password reset link sent');
  };

  return (
    <div className="min-h-screen bg-cyber-bg flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-cyber-accent/10 border border-cyber-accent/20 mb-4">
            <Shield className="w-8 h-8 text-cyber-accent" />
          </div>
          <h1 className="text-2xl font-bold text-white">Reset Password</h1>
          <p className="text-gray-500 mt-1">We'll send you a reset link</p>
        </div>

        <form onSubmit={handleSubmit} className="glass p-8 space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field"
              placeholder="your@email.com"
              required
            />
          </div>

          <button type="submit" disabled={sent} className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50">
            {sent ? 'Email Sent' : 'Send Reset Link'}
            <Send className="w-4 h-4" />
          </button>

          <Link to="/login" className="flex items-center justify-center gap-2 text-sm text-gray-500 hover:text-cyber-accent">
            <ArrowLeft className="w-4 h-4" /> Back to Sign In
          </Link>
        </form>
      </div>
    </div>
  );
}
