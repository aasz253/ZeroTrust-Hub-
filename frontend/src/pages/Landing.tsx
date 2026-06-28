import { Link } from 'react-router-dom';
import {
  Shield, ArrowRight, Activity, Search, Bot,
  FileText, AlertTriangle, Globe, Star,
} from 'lucide-react';

const features = [
  { icon: Activity, title: 'Real-time Monitoring', desc: 'Continuous threat detection and security monitoring with live dashboards' },
  { icon: Search, title: 'Vulnerability Scanner', desc: 'Comprehensive scanning with CVSS scoring and remediation guidance' },
  { icon: Bot, title: 'AI Assistant', desc: 'AI-powered security analysis and recommendations' },
  { icon: Globe, title: 'Threat Intelligence', desc: 'Global threat feed integration with MITRE ATT&CK mapping' },
  { icon: FileText, title: 'Incident Reports', desc: 'Automated report generation with PDF/CSV export' },
  { icon: AlertTriangle, title: 'CVE Explorer', desc: 'Real-time CVE database with AI explanations' },
];

const stats = [
  { value: '10K+', label: 'Threats Analyzed' },
  { value: '99.9%', label: 'Uptime' },
  { value: '50K+', label: 'CVEs Indexed' },
  { value: '24/7', label: 'Monitoring' },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-cyber-bg">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyber-accent/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyber-secondary/5 rounded-full blur-3xl" />
      </div>

      <header className="relative z-10 border-b border-gray-800/50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-7 h-7 text-cyber-accent" />
            <span className="text-lg font-bold text-white">ZeroTrust Hub</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/login" className="text-gray-400 hover:text-white transition-colors">Sign In</Link>
            <Link to="/register" className="btn-primary">Get Started</Link>
          </div>
        </div>
      </header>

      <main className="relative z-10">
        <section className="max-w-7xl mx-auto px-6 pt-24 pb-20 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyber-accent/10 border border-cyber-accent/20 text-cyber-accent text-sm mb-8">
            <Star className="w-4 h-4" />
            AI-Powered Security Operations Center
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white leading-tight mb-6">
            Enterprise-Grade
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyber-accent to-cyber-secondary">
              Cybersecurity Platform
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
            ZeroTrust Hub provides AI-powered threat intelligence, vulnerability management,
            and real-time security monitoring for modern enterprises.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link to="/register" className="btn-primary text-lg px-8 py-3 flex items-center gap-2">
              Start Free Trial <ArrowRight className="w-5 h-5" />
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-3">
              View Demo
            </Link>
          </div>
        </section>

        <section className="max-w-7xl mx-auto px-6 py-16">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <p className="text-3xl font-bold text-cyber-accent">{stat.value}</p>
                <p className="text-gray-500 mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="max-w-7xl mx-auto px-6 py-16">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Everything You Need for{' '}
            <span className="text-cyber-accent">Security Operations</span>
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <div key={feature.title} className="glass p-8 hover:border-cyber-accent/20 transition-all">
                <feature.icon className="w-10 h-10 text-cyber-accent mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <footer className="border-t border-gray-800/50 py-8 text-center text-sm text-gray-600">
          ZeroTrust Hub &copy; {new Date().getFullYear()}. All rights reserved.
        </footer>
      </main>
    </div>
  );
}
