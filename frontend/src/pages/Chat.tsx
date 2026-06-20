import { useState, useRef, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { chatApi, repoApi } from "@/services/api";
import ReactMarkdown from "react-markdown";

const SUGGESTIONS = [
  "Explain the overall architecture",
  "How does authentication work?",
  "What does the database schema look like?",
  "Explain the API flow",
  "How is the project structured?",
  "What design patterns are used?",
];

export default function Chat() {
  const { repoId } = useParams<{repoId:string}>();
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState<string|null>(null);
  const [messages, setMessages] = useState<{role:string;content:string}[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const { data: repo } = useQuery({
    queryKey: ["repo", repoId],
    queryFn: () => repoApi.getRepo(repoId!).then(r => r.data),
    enabled: !!repoId,
  });

  useEffect(() => {
    if (repoId && !sessionId) {
      chatApi.createSession(repoId).then(r => setSessionId(r.data.id)).catch(console.error);
    }
  }, [repoId]);

  useEffect(() => { bottomRef.current?.scrollIntoView({behavior:"smooth"}); }, [messages]);

  async function send(msg?: string) {
    const text = msg ?? input.trim();
    if (!text || !sessionId || loading) return;
    setInput("");
    setMessages(m => [...m, {role:"user", content:text}]);
    setLoading(true);
    try {
      const res = await chatApi.sendMessage(sessionId, text);
      setMessages(m => [...m, {role:"assistant", content:res.data.content}]);
    } catch(e: any) {
      setMessages(m => [...m, {role:"assistant", content:`Error: ${e.message}`}]);
    } finally { setLoading(false); }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      <header className="border-b border-white/10 px-6 py-4 flex items-center gap-4 flex-shrink-0">
        <button onClick={() => navigate(`/repo/${repoId}`)} className="text-gray-400 hover:text-white text-sm">← Back</button>
        <div>
          <h1 className="font-semibold">Chat with {repo?.owner}/{repo?.name}</h1>
          <p className="text-xs text-gray-500">RAG-powered Q&A — powered by your actual codebase</p>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="max-w-2xl mx-auto">
            <p className="text-gray-400 text-center mb-8">Ask anything about this codebase. I have full context of every file.</p>
            <div className="grid grid-cols-2 gap-3">
              {SUGGESTIONS.map(s => (
                <button key={s} onClick={() => send(s)}
                  className="text-left px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors">
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 max-w-4xl mx-auto ${m.role==="user"?"justify-end":""}`}>
            {m.role==="assistant" && (
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-sm flex-shrink-0">AI</div>
            )}
            <div className={`rounded-2xl px-4 py-3 max-w-2xl text-sm ${m.role==="user"?"bg-blue-600 text-white":"bg-white/5 border border-white/10 text-gray-100"}`}>
              {m.role==="assistant"
                ? <div className="prose prose-invert prose-sm max-w-none"><ReactMarkdown>{m.content}</ReactMarkdown></div>
                : m.content
              }
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 max-w-4xl mx-auto">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-sm flex-shrink-0">AI</div>
            <div className="bg-white/5 border border-white/10 rounded-2xl px-4 py-3">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:"0ms"}}/>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:"150ms"}}/>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:"300ms"}}/>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef}/>
      </div>

      <div className="border-t border-white/10 px-6 py-4">
        <form onSubmit={e => { e.preventDefault(); send(); }} className="flex gap-3 max-w-4xl mx-auto">
          <input value={input} onChange={e => setInput(e.target.value)}
            placeholder="Ask about the codebase…" disabled={loading || !sessionId}
            className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm disabled:opacity-50"/>
          <button type="submit" disabled={!input.trim()||loading||!sessionId}
            className="px-5 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-xl text-sm font-medium transition-colors">Send</button>
        </form>
      </div>
    </div>
  );
}
