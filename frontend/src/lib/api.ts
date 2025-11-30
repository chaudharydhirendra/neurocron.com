/**
 * NeuroCron API Client
 * Type-safe API interactions
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8100";

interface ApiError {
  detail: string;
  status: number;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: "An error occurred",
        status: response.status,
      }));
      throw new Error(error.detail);
    }

    return response.json();
  }

  // Auth
  async login(email: string, password: string) {
    return this.request<{
      access_token: string;
      refresh_token: string;
      token_type: string;
    }>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async register(name: string, email: string, password: string) {
    return this.request<{ id: string; email: string }>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({ full_name: name, email, password }),
    });
  }

  // Organizations
  async getOrganizations() {
    return this.request<any[]>("/api/v1/organizations");
  }

  async createOrganization(data: { name: string; description?: string }) {
    return this.request<any>("/api/v1/organizations", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Campaigns
  async getCampaigns(orgId: string) {
    return this.request<any[]>(`/api/v1/campaigns?org_id=${orgId}`);
  }

  async createCampaign(orgId: string, data: any) {
    return this.request<any>(`/api/v1/campaigns?org_id=${orgId}`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getCampaign(campaignId: string) {
    return this.request<any>(`/api/v1/campaigns/${campaignId}`);
  }

  // Copilot
  async chat(message: string, orgId?: string) {
    return this.request<{
      message: string;
      actions?: any[];
      suggestions?: string[];
    }>("/api/v1/copilot/chat", {
      method: "POST",
      body: JSON.stringify({ content: message, org_id: orgId }),
    });
  }
}

export const api = new ApiClient(API_URL);
export default api;

