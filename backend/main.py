import os
import json
import time
import logging
import threading
from datetime import datetime, timezone
from functools import lru_cache
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


GROQ_API_KEY       = os.getenv("GROQ_API_KEY")         # required — set in Render env vars
GROQ_MODEL         = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_HISTORY        = int(os.getenv("MAX_HISTORY", "10"))  # max past turns kept in context
KB_PATH            = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.json")
#QUERY_LOG_PATH     = os.path.join(os.path.dirname(__file__), "data", "query_log.jsonl")
QUERY_LOG_PATH     = os.getenv("QUERY_LOG_PATH", "/tmp/query_log.jsonl")


GROQ_MODELS = [
    GROQ_MODEL,                  # primary (llama-3.3-70b-versatile by default)
    "llama-3.1-8b-instant",  # fallback 1 — confirmed active, very fast
    "gemma2-9b-it",          # fallback 2 — confirmed active, Google model
    "llama3-8b-8192",        # fallback 3 — confirmed active, separate quota
]

groq_client = Groq(api_key=GROQ_API_KEY)

# ── Thread lock — prevents garbled writes if two requests arrive simultaneously
_log_lock = threading.Lock()

# ── Groq call with automatic model fallback ────────────────────────────────────

def call_groq_with_fallback(
    messages: list,
    stream:   bool = False,
) -> tuple:
    last_error = None
    for model in GROQ_MODELS:
        try:
            response = groq_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
                stream=stream,
            )
            if model != GROQ_MODELS[0]:
                log.info(f"Fallback model used: {model}")
            return response, model
        except Exception as e:
            err_str = str(e)
            if "rate_limit_exceeded" in err_str or "429" in err_str:
                log.warning(f"Rate limit hit on {model} — trying next model...")
                last_error = e
                continue
            # Non-rate-limit error — don't retry
            raise e

    # All models exhausted
    log.error("All Groq models rate-limited.")
    raise last_error

def log_query(
    question:   str,
    reply:      str,
    latency_ms: int,
    ip:         str,
    session_id: str | None = None,
) -> None:
    """
    Append one JSON line to data/query_log.jsonl every time someone asks a question.

    Each line looks like:
    {
        "timestamp":  "2025-03-01T14:32:05+00:00",   <- ISO 8601 UTC
        "date":       "2025-03-01",                   <- easy to filter by day
        "time":       "14:32:05",                     <- easy to read at a glance
        "ip":         "123.45.67.89",                 <- rough visitor identity
        "session_id": "abc123",                       <- ties multi-turn conversations
        "question":   "What projects is Aman working on?",
        "reply":      "Aman is currently working on...",
        "latency_ms": 843
    }

    JSONL (JSON Lines) = one JSON object per line.
    Easy to read later with:  pd.read_json("query_log.jsonl", lines=True)
    """
    now = datetime.now(tz=timezone.utc)
    entry = {
        "timestamp":  now.isoformat(),
        "date":       now.strftime("%Y-%m-%d"),
        "time":       now.strftime("%H:%M:%S"),
        "ip":         ip,
        "session_id": session_id,
        "question":   question,
        "reply":      reply,
        "latency_ms": latency_ms,
    }
    try:
        os.makedirs(os.path.dirname(QUERY_LOG_PATH), exist_ok=True)
        with _log_lock:                        # one writer at a time
            with open(QUERY_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        log.warning(f"Failed to write query log: {e}") 

# ── Knowledge base loader ──────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def load_knowledge_base() -> str:
    """
    Load knowledge_base.json once and cache it for the lifetime of the process.
    Returns all chunk content joined as a single string ready to embed in a prompt.
    To force a reload (e.g. after a redeploy), restart the server.
    """
    if not os.path.exists(KB_PATH):
        raise FileNotFoundError(
            f"knowledge_base.json not found at {KB_PATH}. "
            "Run build_knowledge_base.py first."
        )
    with open(KB_PATH, encoding="utf-8") as f:
        chunks: list[dict] = json.load(f)

    parts = []
    for chunk in chunks:
        source  = chunk.get("source", "unknown")
        content = chunk.get("content", "")
        parts.append(f"[{source}]\n{content}")

    kb_text = "\n\n" + ("─" * 60 + "\n\n").join(parts)
    log.info(f"Knowledge base loaded: {len(chunks)} chunks, ~{len(kb_text)//4:,} tokens")
    return kb_text


def build_system_prompt(kb_text: str) -> str:
    return f"""You are an AI assistant embedded in Aman Kumar's portfolio website.
Your sole purpose is to help recruiters, hiring managers, and developers learn about
Aman's skills, projects, experience, and coding activity.

════════════════════════════════════════════════════════════
SCOPE — READ THIS FIRST
════════════════════════════════════════════════════════════
You ONLY answer questions that are related to one of these topics:
  - Aman's skills, technologies, and tools
  - Aman's projects, repos, and GitHub activity
  - Aman's education, experience, and background
  - Aman's LeetCode / competitive programming activity
  - Job fit assessments and role matching for Aman
  - Professional questions a recruiter or hiring manager would ask

If the user's message is NOT related to any of the above — for example: general
knowledge questions, coding help, news, opinions, math, jokes, or anything unrelated
to Aman's professional profile — respond with exactly this and nothing more:

  "That's outside what I can help with here. I'm specifically designed to answer
   questions about Aman Kumar's professional profile, skills, and experience.
   Feel free to ask me anything about his background or how he fits a role!"

════════════════════════════════════════════════════════════
GENERAL GUIDELINES
════════════════════════════════════════════════════════════
- Be professional, warm, and genuinely enthusiastic about Aman's work.
- Answer ONLY based on the knowledge base below. Do not invent details.
- If a question is in scope but the answer isn't in the knowledge base, say:
  "I don't have that detail on hand, but you can reach Aman directly via
   the contact details in his profile."
- When mentioning projects, always include the GitHub link if available.
- Format responses in plain text. Use bullet points only when listing multiple items.

════════════════════════════════════════════════════════════
GOOD FIT / GENERAL PROFILE QUESTIONS
════════════════════════════════════════════════════════════
If someone asks whether Aman would be a good fit, a good hire, or asks for a
general summary of his strengths — be confident and positive. Lead with his
strongest qualities backed by evidence from the knowledge base. Never hedge
unnecessarily. Example triggers: "is he a good fit?", "would you recommend him?",
"what makes him stand out?", "should we hire him?", "give me a summary of Aman".

Response style for these questions:
- Open with a confident, positive statement about his overall profile.
- Back it up with 2–3 specific strengths from the knowledge base (projects, stats, skills).
- Close with an encouraging line inviting the recruiter to explore further or reach out.

════════════════════════════════════════════════════════════
JOB DESCRIPTION DETECTION & MATCHING
════════════════════════════════════════════════════════════
If the user's message contains or resembles a job description (signals: a list of
required skills, "we are looking for", "requirements", "responsibilities",
"qualifications", "years of experience", "must have", "nice to have", or a structured
role description), treat it as a JOB MATCH REQUEST and respond with this structure:

1. ROLE FIT SUMMARY
   One confident sentence: Aman is a strong fit, and briefly say why.

2. MATCHING SKILLS & EXPERIENCE
   Map each requirement to concrete evidence from the knowledge base.
   Name projects, link repos, cite metrics. Do not be vague.
   ✅ <Requirement> — <Specific evidence from knowledge base>

3. GAPS (only if 1–3 skills are missing)
   Do NOT say he lacks them. Instead:
   🔄 <Skill> — Aman is actively building hands-on experience in this through a current project.

   If MORE than 3 skills are missing, say:
   "Some requirements fall outside what I have detailed information on.
    I'd recommend reaching out to Aman directly to discuss his full background."

4. CLOSING
   One short confident sentence encouraging the recruiter to reach out.

════════════════════════════════════════════════════════════
KNOWLEDGE BASE
════════════════════════════════════════════════════════════
{kb_text}
════════════════════════════════════════════════════════════
"""


# ── Lifespan: pre-warm the KB cache on startup ─────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        load_knowledge_base()
        log.info("Knowledge base pre-warmed ✓")
    except FileNotFoundError as e:
        log.warning(str(e))
    yield


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Portfolio RAG API",
    description="Vectorless RAG chatbot for Aman Kumar's portfolio",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to your GitHub Pages URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ────────────────────────────────────────────────────────────────────

class Message(BaseModel):
    role:    str    # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message:    str           = Field(..., min_length=1, max_length=10000)
    history:    list[Message] = Field(default_factory=list)
    session_id: str | None    = Field(default=None)  # frontend can pass a UUID to group turns

class ChatResponse(BaseModel):
    reply:      str
    model:      str
    latency_ms: int


# ── Helper ─────────────────────────────────────────────────────────────────────

def _get_ip(request: Request) -> str:
    """
    Extract the real client IP.
    Render (and most proxies) put the original IP in X-Forwarded-For.
    Falls back to the direct connection IP if the header is absent.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def _build_messages(system_prompt: str, history: list[Message], user_message: str) -> list:
    trimmed = history[-(MAX_HISTORY * 2):]
    return (
        [{"role": "system", "content": system_prompt}]
        + [{"role": m.role, "content": m.content} for m in trimmed]
        + [{"role": "user", "content": user_message}]
    )


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Ping endpoint — used by UptimeRobot to prevent Render cold starts."""
    return {"status": "ok", "model": GROQ_MODEL}


@app.get("/kb-stats")
def kb_stats():
    """Quick check on knowledge base size."""
    try:
        kb = load_knowledge_base()
        return {"chars": len(kb), "approx_tokens": len(kb) // 4}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/queries")
def get_queries(date: str | None = None, limit: int = 100):
    """
    Read back the query log so you can review what recruiters asked.

    Usage:
        GET /queries                    -> last 100 questions (all dates)
        GET /queries?date=2025-03-01    -> all questions on one specific date
        GET /queries?limit=20           -> last 20 questions

    Returns a list of query objects sorted newest-first.
    """
    if not os.path.exists(QUERY_LOG_PATH):
        return {"total": 0, "queries": []}

    with _log_lock:
        with open(QUERY_LOG_PATH, encoding="utf-8") as f:
            lines = f.readlines()

    entries = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            if date and entry.get("date") != date:
                continue
            entries.append(entry)
        except json.JSONDecodeError:
            continue

    # Newest first, then apply limit
    entries.reverse()
    entries = entries[:limit]

    return {"total": len(entries), "queries": entries}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request):
    """
    Main chat endpoint.
    Accepts the current user message + optional conversation history.
    Returns the assistant reply, and logs the Q&A to query_log.jsonl.
    """
    try:
        kb_text = load_knowledge_base()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    messages = _build_messages(build_system_prompt(kb_text), req.history, req.message)

    t0 = time.perf_counter()
    try:
        response, model_used = call_groq_with_fallback(messages, stream=False)
    except Exception as e:
        log.error(f"Groq API error: {e}")
        raise HTTPException(status_code=502, detail=f"LLM error: {str(e)}")

    latency_ms = int((time.perf_counter() - t0) * 1000)
    reply      = response.choices[0].message.content.strip()

    # ── Log the question + reply for later review 
    log_query(
        question=req.message,
        reply=reply,
        latency_ms=latency_ms,
        ip=_get_ip(request),
        session_id=req.session_id,
        model=model_used,
    )

    # ── Log to Vercel 
    log.info(
        f"Chat query handled | session={req.session_id} | latency={latency_ms}ms | model={model_used}\n"
        f"Question: {req.message[:500]}\n"
        f"Reply: {reply[:1000]}"
    )

    #log.info(f"chat | {latency_ms}ms | in={len(req.message)} | out={len(reply)}")
    return ChatResponse(reply=reply, model=model_used, latency_ms=latency_ms)


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest, request: Request):
    """
    Streaming version of /chat — returns tokens as SSE (Server-Sent Events).
    Also logs the full question + assembled reply once streaming is complete.
    """
    try:
        kb_text = load_knowledge_base()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    messages   = _build_messages(build_system_prompt(kb_text), req.history, req.message)
    ip         = _get_ip(request)
    t0         = time.perf_counter()
    full_reply = []   # collect tokens so we can log the complete reply at the end

    async def token_generator() -> AsyncGenerator[str, None]:
        model_used = GROQ_MODELS[0]
        try:
            stream, model_used = call_groq_with_fallback(messages, stream=True)
            for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                if token:
                    full_reply.append(token)
                    yield f"data: {json.dumps({'token': token})}\n\n"

            # ── Log after stream fully completes ───────────────
            reply_text = "".join(full_reply)
            log_query(
                question=req.message,
                reply=reply_text,
                latency_ms=int((time.perf_counter() - t0) * 1000),
                ip=ip,
                session_id=req.session_id,
                model=model_used,
            )
            # ── Log in vercel after stream fully completes ───────────────
            latency = int((time.perf_counter() - t0) * 1000)
            log.info(f"Chat query handled | session={req.session_id} | ip={ip} | latency={latency}ms | model={model_used}\n"
                f"Question: {req.message[:500]}\n"
                f"Reply: {reply_text[:1000]}"
            )
            
            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")

    
