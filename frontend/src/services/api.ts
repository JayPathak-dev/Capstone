import {
  DashboardSummary,
  Project,
  Alert,
  RiskDetail,
  BenchmarkingData,
  ChatResponse,
} from '../types';

const API_BASE = '/api/v1';

export async function fetchHealth(): Promise<any> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch system health');
  return res.json();
}

export async function fetchDashboardSummary(
  sector?: string,
  region?: string
): Promise<DashboardSummary> {
  const params = new URLSearchParams();
  if (sector && sector !== 'ALL') params.append('sector', sector);
  if (region && region !== 'ALL') params.append('region', region);

  const res = await fetch(`${API_BASE}/dashboard/summary?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch dashboard summary');
  return res.json();
}

export async function fetchProjects(params: {
  skip?: number;
  limit?: number;
  search?: string;
  sector?: string;
  region?: string;
  risk_level?: string;
  status?: string;
  sort_by?: string;
  sort_order?: string;
}): Promise<{ total: number; page: number; page_size: number; items: Project[] }> {
  const query = new URLSearchParams();
  if (params.skip !== undefined) query.append('skip', params.skip.toString());
  if (params.limit !== undefined) query.append('limit', params.limit.toString());
  if (params.search) query.append('search', params.search);
  if (params.sector && params.sector !== 'ALL') query.append('sector', params.sector);
  if (params.region && params.region !== 'ALL') query.append('region', params.region);
  if (params.risk_level && params.risk_level !== 'ALL') query.append('risk_level', params.risk_level);
  if (params.status && params.status !== 'ALL') query.append('status', params.status);
  if (params.sort_by) query.append('sort_by', params.sort_by);
  if (params.sort_order) query.append('sort_order', params.sort_order);

  const res = await fetch(`${API_BASE}/projects?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function fetchProjectDetails(projectId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/projects/${projectId}`);
  if (!res.ok) throw new Error(`Failed to fetch project details for ${projectId}`);
  return res.json();
}

export async function fetchProjectRisk(projectId: string): Promise<RiskDetail> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/risk`);
  if (!res.ok) throw new Error(`Failed to fetch risk details for ${projectId}`);
  return res.json();
}

export async function triggerProjectPrediction(projectId: string): Promise<RiskDetail> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/predict`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Failed to re-run prediction for ${projectId}`);
  return res.json();
}

export async function fetchAlerts(params: {
  skip?: number;
  limit?: number;
  severity?: string;
  status?: string;
  project_id?: string;
}): Promise<{ total: number; items: Alert[] }> {
  const query = new URLSearchParams();
  if (params.skip !== undefined) query.append('skip', params.skip.toString());
  if (params.limit !== undefined) query.append('limit', params.limit.toString());
  if (params.severity && params.severity !== 'ALL') query.append('severity', params.severity);
  if (params.status && params.status !== 'ALL') query.append('status', params.status);
  if (params.project_id) query.append('project_id', params.project_id);

  const res = await fetch(`${API_BASE}/alerts?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch alerts');
  return res.json();
}

export async function updateAlertStatus(
  alertId: string,
  status: string,
  resolutionNotes?: string
): Promise<Alert> {
  const res = await fetch(`${API_BASE}/alerts/${alertId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, resolution_notes: resolutionNotes }),
  });
  if (!res.ok) throw new Error(`Failed to update alert ${alertId}`);
  return res.json();
}

export async function fetchBenchmarking(
  projectId: string,
  cohortSize: number = 5
): Promise<BenchmarkingData> {
  const res = await fetch(
    `${API_BASE}/benchmarking?project_id=${encodeURIComponent(projectId)}&cohort_size=${cohortSize}`
  );
  if (!res.ok) throw new Error(`Failed to fetch benchmarking for ${projectId}`);
  return res.json();
}

export async function sendAssistantMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/assistant/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
  if (!res.ok) throw new Error('Failed to get assistant response');
  return res.json();
}

export async function previewCsv(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/data/import/preview`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to preview CSV file');
  return res.json();
}

export async function commitCsv(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/data/import/commit`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to commit CSV file');
  return res.json();
}

export async function fetchModelStatus(): Promise<any> {
  const res = await fetch(`${API_BASE}/models/status`);
  if (!res.ok) throw new Error('Failed to fetch model status');
  return res.json();
}
