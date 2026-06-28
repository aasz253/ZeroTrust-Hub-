export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_mfa_enabled: boolean;
  role: string;
  last_login: string | null;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResponse extends AuthTokens {
  user: User;
}

export interface DashboardStats {
  threat_score: number;
  active_alerts: number;
  critical_vulnerabilities: number;
  devices_online: number;
  security_health: number;
  total_scans: number;
  total_threats: number;
  total_vulnerabilities: number;
  recent_activities: Activity[];
  vulnerability_severity: Record<string, number>;
  threat_types: Record<string, number>;
  scan_history: { date: string; count: number }[];
  top_threats: Threat[];
  ai_recommendations: string[];
}

export interface Activity {
  id: number;
  action: string;
  resource: string;
  created_at: string;
}

export interface Threat {
  id: number;
  indicator: string;
  indicator_type: string;
  threat_type: string | null;
  severity: string;
  confidence: number | null;
  source: string | null;
  description: string | null;
  mitre_attack_id: string | null;
  mitre_tactic: string | null;
  mitre_technique: string | null;
  is_active: boolean;
  first_seen: string | null;
  last_seen: string | null;
  created_at: string;
}

export interface Vulnerability {
  id: number;
  cve_id: string;
  title: string;
  description: string;
  severity: string;
  cvss_score: number;
  affected_vendor: string | null;
  affected_product: string | null;
  published_date: string | null;
  remediation: string | null;
}

export interface Scan {
  id: number;
  target: string;
  scan_type: string;
  status: string;
  progress: number;
  severity: string | null;
  findings_count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface MalwareReport {
  id: number;
  file_name: string;
  file_hash_sha256: string;
  file_size: number | null;
  file_type: string | null;
  risk_score: number | null;
  risk_level: string | null;
  threat_family: string | null;
  detection_ratio: string | null;
  ai_analysis: string | null;
  recommended_action: string | null;
  analyzed_at: string | null;
  created_at: string;
}

export interface AIResponse {
  response: string;
  conversation_id: number;
  tokens_used: number | null;
}

export interface Conversation {
  id: number;
  title: string | null;
  context_type: string | null;
  context_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  role: string;
  content: string;
  created_at: string;
}

export interface Report {
  id: number;
  title: string;
  report_type: string;
  format: string;
  status: string;
  severity: string | null;
  summary: string | null;
  created_at: string;
}

export interface ReportDetail extends Report {
  executive_summary: string | null;
  technical_findings: any;
  risk_assessment: any;
  recommendations: any;
  file_path: string | null;
  generated_at: string | null;
}

export interface Notification {
  id: number;
  title: string;
  message: string | null;
  notification_type: string | null;
  severity: string;
  category: string | null;
  link: string | null;
  is_read: boolean;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
