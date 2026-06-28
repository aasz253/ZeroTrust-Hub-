import { useState, useEffect } from 'react';
import { Shield, Key, Check, X, Copy, Download } from 'lucide-react';
import { mfa } from '../services/api';
import toast from 'react-hot-toast';

export default function MFASetup() {
  const [status, setStatus] = useState<{ enabled: boolean; has_secret: boolean } | null>(null);
  const [step, setStep] = useState<'idle' | 'setup' | 'verify'>('idle');
  const [secret, setSecret] = useState('');
  const [uri, setUri] = useState('');
  const [codes, setCodes] = useState<string[]>([]);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    mfa.status().then(setStatus).catch(console.error).finally(() => setLoading(false));
  }, []);

  const handleSetup = async () => {
    try {
      const data = await mfa.setup();
      setSecret(data.secret);
      setUri(data.uri);
      setCodes(data.recovery_codes);
      setStep('setup');
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Setup failed');
    }
  };

  const handleVerify = async () => {
    try {
      await mfa.verifySetup(code);
      toast.success('MFA enabled successfully');
      setStep('idle');
      setStatus({ enabled: true, has_secret: true });
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Invalid code');
    }
  };

  const handleDisable = async () => {
    if (!confirm('Disable MFA? This reduces account security.')) return;
    try {
      await mfa.disable();
      toast.success('MFA disabled');
      setStatus({ enabled: false, has_secret: false });
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to disable');
    }
  };

  const copyCodes = () => {
    navigator.clipboard.writeText(codes.join('\n'));
    toast.success('Recovery codes copied');
  };

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
        <h1 className="text-2xl font-bold text-white">Multi-Factor Authentication</h1>
        <p className="text-gray-500 mt-1">Add an extra layer of security to your account</p>
      </div>

      <div className="glass p-6">
        <div className="flex items-center gap-4 mb-6">
          <Shield className={`w-10 h-10 ${status?.enabled ? 'text-cyber-success' : 'text-gray-500'}`} />
          <div>
            <h2 className="text-lg font-semibold text-white">
              {status?.enabled ? 'MFA is Active' : 'MFA is Disabled'}
            </h2>
            <p className="text-sm text-gray-500">
              {status?.enabled
                ? 'Your account is protected with time-based one-time passwords'
                : 'Enable MFA to protect your account with 2-factor authentication'}
            </p>
          </div>
          {status?.enabled ? (
            <button onClick={handleDisable} className="ml-auto px-4 py-2 rounded-xl bg-red-500/10 text-red-400 text-sm border border-red-500/20 hover:bg-red-500/20">
              Disable
            </button>
          ) : (
            <button onClick={handleSetup} className="ml-auto px-4 py-2 rounded-xl bg-cyber-accent/10 text-cyber-accent text-sm border border-cyber-accent/20 hover:bg-cyber-accent/20">
              Set Up MFA
            </button>
          )}
        </div>
      </div>

      {step === 'setup' && (
        <>
          <div className="glass p-6 space-y-6">
            <h2 className="text-lg font-semibold text-white">1. Scan QR Code</h2>
            <p className="text-sm text-gray-500">
              Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
            </p>
            <div className="flex justify-center">
              <div className="bg-white p-4 rounded-xl">
                <img src={uri} alt="QR Code" className="w-48 h-48" />
              </div>
            </div>
            <p className="text-sm text-gray-400 text-center">
              Or enter this key manually: <code className="text-cyber-accent bg-gray-800 px-2 py-0.5 rounded">{secret}</code>
            </p>
          </div>

          <div className="glass p-6 space-y-4">
            <h2 className="text-lg font-semibold text-white">2. Save Recovery Codes</h2>
            <p className="text-sm text-gray-500">
              Store these codes in a safe place. Each code can only be used once.
            </p>
            <div className="bg-gray-900/50 rounded-xl p-4 font-mono text-sm space-y-1">
              {codes.map((c, i) => (
                <div key={i} className="text-gray-300">{c}</div>
              ))}
            </div>
            <div className="flex gap-2">
              <button onClick={copyCodes} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm hover:bg-gray-700">
                <Copy className="w-4 h-4" /> Copy Codes
              </button>
              <button onClick={() => { const blob = new Blob([codes.join('\n')], { type: 'text/plain' }); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'zerotrust-recovery-codes.txt'; a.click(); }} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-800 text-gray-300 text-sm hover:bg-gray-700">
                <Download className="w-4 h-4" /> Download
              </button>
            </div>
          </div>

          <div className="glass p-6 space-y-4">
            <h2 className="text-lg font-semibold text-white">3. Verify Setup</h2>
            <p className="text-sm text-gray-500">
              Enter the 6-digit code from your authenticator app to confirm setup
            </p>
            <div className="flex gap-3">
              <input
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                className="flex-1 max-w-[200px] px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white font-mono text-lg text-center"
                maxLength={6}
              />
              <button onClick={handleVerify} disabled={code.length !== 6} className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-cyber-accent/10 text-cyber-accent border border-cyber-accent/20 hover:bg-cyber-accent/20 disabled:opacity-50">
                <Check className="w-4 h-4" /> Verify
              </button>
              <button onClick={() => setStep('idle')} className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gray-800 text-gray-300 text-sm hover:bg-gray-700">
                <X className="w-4 h-4" /> Cancel
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
