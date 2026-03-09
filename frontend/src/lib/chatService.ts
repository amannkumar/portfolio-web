const API_URL = import.meta.env.VITE_API_URL ?? "";
const SESSION_ID = crypto.randomUUID(); // one UUID per page load — groups turns in the query log

// ── Types ──────────────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  provider?: string;
  model?: string;
}

export interface ChatResponse {
  reply: string;
  model: string;
  latency_ms: number;
}

// ── Service ────────────────────────────────────────────────────────────────────

class ChatService {
  private history: ChatMessage[] = [];

  async sendMessage(userMessage: string): Promise<ChatResponse> {
    const recentHistory = this.history.slice(-10).map((m) => ({
      role: m.role,
      content: m.content,
    }));

    const res = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: userMessage,
        history: recentHistory,
        session_id: SESSION_ID,
      }),
    });

    if (!res.ok) {
      const text = await res.text().catch(() => res.statusText);
      throw new Error(`API error ${res.status}: ${text}`);
    }

    const data: ChatResponse = await res.json();

    // Keep local history in sync so context window grows correctly
    this.history.push({
      role: "user",
      content: userMessage,
      timestamp: new Date(),
    });
    this.history.push({
      role: "assistant",
      content: data.reply,
      timestamp: new Date(),
      model: data.model,
    });

    return data;
  }

  clearHistory(): void {
    this.history = [];
  }

  getHistory(): ChatMessage[] {
    return [...this.history];
  }
}

// Singleton — one instance shared across the whole app
export const chatService = new ChatService();

export const QUICK_QUESTIONS = [
  "What does Aman work on?",
  "What are his main technical skills?",
  "What projects has he built recently?",
];
