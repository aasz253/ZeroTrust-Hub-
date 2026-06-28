import { useState } from 'react';
import { Key, Shield, AlertTriangle, CheckCircle, Info, Zap } from 'lucide-react';

function calculateEntropy(password: string): number {
  let pool = 0;
  if (/[a-z]/.test(password)) pool += 26;
  if (/[A-Z]/.test(password)) pool += 26;
  if (/\d/.test(password)) pool += 10;
  if (/[^a-zA-Z0-9]/.test(password)) pool += 32;
  return password.length * Math.log2(pool || 1);
}

function estimateCrackTime(entropy: number): string {
  const guessesPerSecond = 1e9;
  const seconds = Math.pow(2, entropy) / guessesPerSecond;
  if (seconds < 1) return 'less than a second';
  if (seconds < 60) return `${Math.round(seconds)} seconds`;
  if (seconds < 3600) return `${Math.round(seconds / 60)} minutes`;
  if (seconds < 86400) return `${Math.round(seconds / 3600)} hours`;
  if (seconds < 31536000) return `${Math.round(seconds / 86400)} days`;
  return `${Math.round(seconds / 31536000)} years`;
}

const commonPasswords = new Set([
  'password', '123456', '12345678', 'qwerty', 'admin', 'letmein',
  'welcome', 'monkey', 'dragon', 'master', '123123', 'password1',
]);

export default function PasswordAnalyzer() {
  const [password, setPassword] = useState('');
  const [visible, setVisible] = useState(false);

  const entropy = password ? calculateEntropy(password) : 0;
  const crackTime = password ? estimateCrackTime(entropy) : '';
  const isCommon = commonPasswords.has(password.toLowerCase());
  const hasLower = /[a-z]/.test(password);
  const hasUpper = /[A-Z]/.test(password);
  const hasDigit = /\d/.test(password);
  const hasSpecial = /[^a-zA-Z0-9]/.test(password);
  const length = password.length;

  const getStrength = () => {
    if (!password) return { label: 'N/A', color: 'text-gray-500', bar: 'w-0', bg: 'bg-gray-700' };
    if (isCommon || length < 6) return { label: 'Very Weak', color: 'text-red-400', bar: 'w-1/5', bg: 'bg-red-500' };
    if (entropy < 28) return { label: 'Weak', color: 'text-orange-400', bar: 'w-2/5', bg: 'bg-orange-500' };
    if (entropy < 36) return { label: 'Moderate', color: 'text-yellow-400', bar: 'w-3/5', bg: 'bg-yellow-500' };
    if (entropy < 60) return { label: 'Strong', color: 'text-cyber-accent', bar: 'w-4/5', bg: 'bg-cyber-accent' };
    return { label: 'Very Strong', color: 'text-green-400', bar: 'w-full', bg: 'bg-green-500' };
  };

  const strength = getStrength();

  const recommendations = [];
  if (length < 12) recommendations.push('Use at least 12 characters');
  if (!hasLower) recommendations.push('Add lowercase letters');
  if (!hasUpper) recommendations.push('Add uppercase letters');
  if (!hasDigit) recommendations.push('Add numbers');
  if (!hasSpecial) recommendations.push('Add special characters');
  if (isCommon) recommendations.push('Avoid common passwords');

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Password Analyzer</h1>
        <p className="text-gray-500 mt-1">Check password strength and get AI-powered recommendations</p>
      </div>

      <div className="glass p-8 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">Enter Password to Analyze</label>
          <div className="relative">
            <input
              type={visible ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field pr-10 font-mono text-lg"
              placeholder="Type a password..."
            />
            <button
              onClick={() => setVisible(!visible)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
            >
              <Key className="w-4 h-4" />
            </button>
          </div>
        </div>

        {password && (
          <>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className={`text-lg font-bold ${strength.color}`}>{strength.label}</span>
                <span className="text-sm text-gray-500">Entropy: {entropy.toFixed(1)} bits</span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div className={`h-full rounded-full transition-all duration-500 ${strength.bg}`} style={{ width: password ? `${Math.min(100, (entropy / 80) * 100)}%` : '0%' }} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-gray-800/50">
                <p className="text-xs text-gray-500">Password Length</p>
                <p className="text-xl font-bold text-white">{length}</p>
              </div>
              <div className="p-4 rounded-xl bg-gray-800/50">
                <p className="text-xs text-gray-500">Est. Crack Time</p>
                <p className="text-xl font-bold text-white">{crackTime}</p>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-2">
              {[
                { label: 'Lowercase', check: hasLower },
                { label: 'Uppercase', check: hasUpper },
                { label: 'Numbers', check: hasDigit },
                { label: 'Special', check: hasSpecial },
              ].map((item) => (
                <div key={item.label} className={`p-3 rounded-xl text-center ${
                  item.check ? 'bg-green-500/10 border border-green-500/20' : 'bg-gray-800/30 border border-gray-700/30'
                }`}>
                  {item.check ? (
                    <CheckCircle className="w-5 h-5 text-green-400 mx-auto mb-1" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-gray-600 mx-auto mb-1" />
                  )}
                  <p className={`text-xs ${item.check ? 'text-green-400' : 'text-gray-600'}`}>{item.label}</p>
                </div>
              ))}
            </div>

            {recommendations.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-cyber-accent">
                  <Zap className="w-4 h-4" />
                  <span className="text-sm font-medium">Recommendations</span>
                </div>
                {recommendations.map((rec, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm text-gray-400">
                    <Info className="w-3 h-3 text-cyber-accent mt-0.5" />
                    <span>{rec}</span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
