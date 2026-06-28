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

export interface Device {
  id: number;
  ip_address: string;
  hostname: string | null;
  mac_address: string | null;
  status: string;
  open_ports: number[];
  os: string | null;
  os_version: string | null;
  vendor: string | null;
  device_type: string | null;
  risk_score: number;
  first_seen: string | null;
  last_seen: string | null;
  is_active: boolean;
  tags: string[];
  notes: string | null;
  created_at: string;
}

export interface NetworkStats {
  total_devices: number;
  online_count: number;
  offline_count: number;
  suspicious_count: number;
  open_ports_total: number;
  risk_score_avg: number;
  wifi_ssid: string | null;
  gateway_ip: string | null;
  interface_name: string | null;
}

export interface SiemLog {
  id: number;
  timestamp: string;
  source_ip: string | null;
  hostname: string | null;
  facility: string | null;
  severity: string | null;
  program: string | null;
  message: string;
  raw: string;
  tags: string[];
}

export interface EdrProcess {
  pid: number;
  name: string;
  exe: string | null;
  cmdline: string;
  username: string | null;
  cpu_percent: number;
  memory_percent: number;
  connections: any[];
  is_suspicious: boolean;
  anomaly_reason: string | null;
}

export interface Playbook {
  id: number;
  name: string;
  description: string;
  trigger_type: string;
  trigger_config: any;
  is_active: boolean;
  auto_run: boolean;
  actions_count: number;
  created_at: string;
}

export interface PlaybookExecution {
  id: number;
  playbook_id: number;
  triggered_by: string;
  status: string;
  result: any;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface FimEntry {
  id: number;
  file_path: string;
  file_name: string;
  status: string;
  current_hash: string | null;
  previous_hash: string | null;
  file_size: number | null;
  permissions: string | null;
  owner: string | null;
  last_checked: string | null;
  last_changed: string | null;
  change_count: number;
  is_critical: boolean;
}

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
