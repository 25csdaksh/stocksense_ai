import {
  PortfolioCopilotRequest,
  PortfolioCopilotResponse,
  DailyPortfolioBrief,
  UserResearchMemory,
  PortfolioAlert,
  AlertRule,
  AlertEvent,
} from '@/types/portfolio-copilot';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getAuthHeaders(): HeadersInit {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export const portfolioCopilotApi = {
  async query(req: PortfolioCopilotRequest): Promise<PortfolioCopilotResponse> {
    const res = await fetch(`${API_BASE}/api/v1/ai/portfolio/query`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(req),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Portfolio copilot query failed' }));
      throw new Error(err.detail || `Query failed: ${res.statusText}`);
    }
    return res.json();
  },

  async getDailyBrief(portfolioId?: string): Promise<DailyPortfolioBrief> {
    const url = portfolioId
      ? `${API_BASE}/api/v1/ai/portfolio/daily-brief?portfolio_id=${encodeURIComponent(portfolioId)}`
      : `${API_BASE}/api/v1/ai/portfolio/daily-brief`;

    const res = await fetch(url, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch daily brief' }));
      throw new Error(err.detail || `Fetch daily brief failed: ${res.statusText}`);
    }
    return res.json();
  },

  streamQuery(
    req: PortfolioCopilotRequest,
    onMessage: (event: { type: string; payload: any }) => void,
    onError?: (error: Error) => void,
    onComplete?: () => void
  ): () => void {
    const controller = new AbortController();
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

    fetch(`${API_BASE}/api/v1/ai/portfolio/query/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(req),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`SSE Stream error: ${response.statusText}`);
        }
        if (!response.body) {
          throw new Error('ReadableStream not supported.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6).trim();
              if (dataStr === '[DONE]') {
                if (onComplete) onComplete();
                return;
              }
              try {
                const parsed = JSON.parse(dataStr);
                onMessage(parsed);
              } catch (e) {
                console.warn('Failed to parse SSE line:', dataStr);
              }
            }
          }
        }
        if (onComplete) onComplete();
      })
      .catch((err) => {
        if (err.name !== 'AbortError' && onError) {
          onError(err);
        }
      });

    return () => controller.abort();
  },
};

export const researchMemoryApi = {
  async getMemories(symbol?: string, query?: string, limit: number = 20): Promise<UserResearchMemory[]> {
    const params = new URLSearchParams();
    if (symbol) params.set('symbol', symbol);
    if (query) params.set('query', query);
    if (limit) params.set('limit', limit.toString());

    const res = await fetch(`${API_BASE}/api/v1/ai/portfolio/memory?${params.toString()}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch research memories' }));
      throw new Error(err.detail || 'Failed to fetch research memories');
    }
    return res.json();
  },

  async getMemory(memoryId: string): Promise<UserResearchMemory> {
    const res = await fetch(`${API_BASE}/api/v1/ai/portfolio/memory/${encodeURIComponent(memoryId)}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch research memory' }));
      throw new Error(err.detail || 'Failed to fetch research memory');
    }
    return res.json();
  },
};

export const portfolioAlertsApi = {
  async getAlerts(unreadOnly: boolean = false): Promise<PortfolioAlert[]> {
    const res = await fetch(`${API_BASE}/api/v1/ai/portfolio/alerts?unread_only=${unreadOnly}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch portfolio alerts' }));
      throw new Error(err.detail || 'Failed to fetch alerts');
    }
    return res.json();
  },

  async getAlertRules(): Promise<AlertRule[]> {
    const res = await fetch(`${API_BASE}/api/v1/ai/portfolio/alerts/rules`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch alert rules' }));
      throw new Error(err.detail || 'Failed to fetch alert rules');
    }
    return res.json();
  },

  async createAlertRule(rule: Partial<AlertRule>): Promise<AlertRule> {
    const res = await fetch(`${API_BASE}/api/v1/ai/portfolio/alerts/rules`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(rule),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to create alert rule' }));
      throw new Error(err.detail || 'Failed to create alert rule');
    }
    return res.json();
  },

  async deleteAlertRule(ruleId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/v1/ai/portfolio/alerts/rules/${encodeURIComponent(ruleId)}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to delete alert rule' }));
      throw new Error(err.detail || 'Failed to delete alert rule');
    }
  },

  async acknowledgeAlert(alertId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/v1/ai/portfolio/alerts/${encodeURIComponent(alertId)}/ack`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to acknowledge alert' }));
      throw new Error(err.detail || 'Failed to acknowledge alert');
    }
  },
};
