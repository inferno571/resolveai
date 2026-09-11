/**
 * ResolveAI — API Client
 *
 * Centralized HTTP client for all backend API calls.
 */

const API_BASE = 'http://localhost:8000/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// ── Types ─────────────────────────────────────────────────────────

export interface ResolveRequest {
  problem: string;
  tool?: string;
  operating_system?: string;
  version?: string;
  error_log?: string;
}

export interface ResolutionStep {
  step_number: number;
  instruction: string;
  code?: string;
  warning?: string;
}

export interface Citation {
  source: string;
  title: string;
  url?: string;
  relevant_text: string;
}

export interface CaseSimilarityResult {
  case: CaseData;
  total_score: number;
  component_scores: Record<string, number>;
  match_explanation: string;
}

export interface ResolveResponse {
  query_id: string;
  diagnosis: string;
  confidence: string;
  steps: ResolutionStep[];
  citations: Citation[];
  similar_cases: CaseSimilarityResult[];
  warnings: string[];
  llm_provider_used: string;
  retrieval_metadata: Record<string, number>;
}

export interface CaseData {
  id: string;
  problem: string;
  tool: string;
  operating_system: string;
  version: string;
  error_code: string;
  symptoms: string;
  attempted_steps: string;
  supporting_evidence: string;
  verified_solution: string;
  outcome: string;
  source_url: string;
  verification_status: string;
  created_at: string;
}

export interface FeedbackRequest {
  query_id: string;
  resolved: boolean;
  corrected_solution?: string;
  rating?: number;
}

export interface HealthStatus {
  status: string;
  ollama_connected: boolean;
  ollama_model_loaded: boolean;
  gemini_configured: boolean;
  chroma_documents: number;
  casebase_size: number;
  embedding_model: string;
}

export interface SystemMetrics {
  total_queries: number;
  total_cases: number;
  verified_cases: number;
  total_feedback: number;
  positive_feedback_rate: number;
  avg_rating: number;
  cases_by_tool: Record<string, number>;
  cases_by_os: Record<string, number>;
}

export interface DocumentMeta {
  id: string;
  title: string;
  source: string;
  url: string;
  chunk_count: number;
  ingested_at: string;
}

// ── API Functions ─────────────────────────────────────────────────

export const api = {
  // Resolution
  resolve: (data: ResolveRequest, mode = 'full', provider?: string) => {
    const params = new URLSearchParams({ mode });
    if (provider) params.set('provider', provider);
    return request<ResolveResponse>(`/resolve?${params}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Feedback
  submitFeedback: (data: FeedbackRequest) =>
    request('/feedback', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getFeedback: (queryId: string) =>
    request(`/feedback/${queryId}`),

  // Cases
  getCases: (params?: { tool?: string; operating_system?: string; verification_status?: string; limit?: number; offset?: number }) => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) searchParams.set(k, String(v));
      });
    }
    const qs = searchParams.toString();
    return request<CaseData[]>(`/cases${qs ? `?${qs}` : ''}`);
  },

  getCaseById: (id: string) =>
    request<CaseData>(`/cases/${id}`),

  getCaseStats: () =>
    request<{ total_cases: number; verified_cases: number; by_tool: Record<string, number>; by_os: Record<string, number> }>('/cases/stats'),

  createCase: (data: Partial<CaseData>) =>
    request<CaseData>('/cases', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  deleteCase: (id: string) =>
    request(`/cases/${id}`, { method: 'DELETE' }),

  // Documents
  getDocuments: () =>
    request<DocumentMeta[]>('/documents'),

  ingestDocument: (formData: FormData) =>
    fetch(`${API_BASE}/documents/ingest`, {
      method: 'POST',
      body: formData,
    }).then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail);
      }
      return res.json();
    }),

  deleteDocument: (id: string) =>
    request(`/documents/${id}`, { method: 'DELETE' }),

  // Admin
  getHealth: () =>
    request<HealthStatus>('/admin/health'),

  getConfig: () =>
    request<Record<string, any>>('/admin/config'),

  updateConfig: (data: Record<string, unknown>) =>
    request('/admin/config', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  getMetrics: () =>
    request<SystemMetrics>('/admin/metrics'),

  testLLM: (provider: string) =>
    request<{ status: string; provider: string; model?: string; response?: string; latency_ms?: number; error?: string }>(`/admin/test-llm?provider=${provider}`, {
      method: 'POST',
    }),
};
