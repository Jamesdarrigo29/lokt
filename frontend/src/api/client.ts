const API_BASE = "http://localhost:8000/api";

export interface PolicyAttributes {
  id: number;
  company: string;
  source: string;
  effective_date: string | null;
  data_collected: string[] | null;
  shares_with_third_parties: boolean | null;
  third_parties_named: string[] | null;
  sells_data: boolean | null;
  retention_period: string | null;
  user_rights: string[] | null;
  uses_cookies_tracking: boolean | null;
  children_data_collected: boolean | null;
  gdpr_mentioned: boolean | null;
  ccpa_mentioned: boolean | null;
  breach_notification: string | null;
  international_transfer: string | null;
  contact_email: string | null;
  risk_flags: string[] | null;
  summary: string | null;
  created_at: string;
}

export interface ChatSource {
  index: number;
  content: string;
  source: string;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  insufficient_context: boolean;
}

async function handle<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export function fetchPolicies(): Promise<PolicyAttributes[]> {
  return fetch(`${API_BASE}/policies`).then((r) => handle<PolicyAttributes[]>(r));
}

export function uploadPdf(company: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  return fetch(`${API_BASE}/upload?company=${encodeURIComponent(company)}`, {
    method: "POST",
    body: formData,
  }).then((r) => handle(r));
}

export function analyzeUrl(company: string, url: string) {
  return fetch(`${API_BASE}/analyze-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ company, url }),
  }).then((r) => handle(r));
}

export function sendChatMessage(question: string, company?: string): Promise<ChatResponse> {
  return fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, company: company || null }),
  }).then((r) => handle<ChatResponse>(r));
}
