import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { repoApi } from "@/services/api";
import { formatDate, statusColor } from "@/lib/utils";
import type { Repo } from "@/types";

const FEATURES = [
  { icon: "🏗️", title: "Architecture Analysis", desc: "Detect patterns, frameworks, databases, auth" },
  { icon: "📄", title: "Auto Documentation",   desc: "Summary, README, API docs, setup guide" },
  { icon: "💬", title: "RAG Chat",              desc: "Ask any question about the codebase" },
  { icon: "📊", title: "Complexity Score",      desc: "Maintainability, tech debt, hotspots" },
  { icon: "🎯", title: "Recruiter Mode",        desc: "Resume bullets, STAR answers, elevator pitch" },
  { icon: "🎓", title: "Interview Prep",        desc: "Beginner → advanced Q&A from your code" },
  { icon: "🚀", title: "Onboarding Guide",      desc: "3-day learning path for new devs" },
  { icon: "⚖️", title: "Repo Comparison",       desc: "Side-by-side analysis of two repos" },
];

export default function Home() {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data: repos } = useQuery({
    queryKey: ["repos"],
    queryFn: () => repoApi.listRepos().then(r => r.data as Repo[]),
    refetchInterval: 5000,
  });

  const submit = useMutation({
    mutationFn: () => repoApi.submit(url),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["repos"] });
      navigate(`/repo/${res.data.repo_id}?job=${res.data.job_id}`);
    },
    onError: (e: Error) => setError(e.message),
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!url.includes("github.com")) { setError("Please enter a valid GitHub URL"); return; }
    submit.mutate();
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 to-gray-900 text-white">
      <nav className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">RepoMind AI</span>
        <button onClick={() => navigate("/compare")} className="text-sm text-gray-400 hover:text-white transition-colors">Compare Repos</button>
      </nav>

      <div className="max-w-4xl mx-auto px-6 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-1.5 text-sm text-blue-400 mb-8">
          <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />AI-Powered Repository Intelligence
        </div>
        <h1 className="text-5xl font-bold mb-6 leading-tight">
          Understand any GitHub repo<br />
          <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">in seconds</span>
        </h1>
        <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
          Paste a GitHub URL. Get architecture diagrams, documentation, complexity analysis, recruiter content, and a chat interface — automatically.
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-2xl mx-auto mb-3">
          <input value={url} onChange={e => { setUrl(e.target.value); setError(""); }}
            placeholder="https://github.com/owner/repository"
            className="flex-1 px-5 py-3.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm" />
          <button type="submit" disabled={submit.isPending}
            className="px-8 py-3.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-xl font-medium text-sm transition-colors whitespace-nowrap flex items-center gap-2">
            {submit.isPending ? <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/>Analyzing…</> : "Analyze Repository →"}
          </button>
        </form>
        {error && <p className="text-red-400 text-sm">{error}</p>}
      </div>

      <div className="max-w-5xl mx-auto px-6 pb-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {FEATURES.map(f => (
            <div key={f.title} className="bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/[0.08] transition-colors">
              <div className="text-2xl mb-2">{f.icon}</div>
              <div className="font-medium text-sm mb-1">{f.title}</div>
              <div className="text-xs text-gray-500">{f.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {repos && repos.length > 0 && (
        <div className="max-w-4xl mx-auto px-6 pb-20">
          <h2 className="text-lg font-semibold mb-4 text-gray-300">Recent Analyses</h2>
          <div className="space-y-2">
            {repos.slice(0,8).map(repo => (
              <button key={repo.id} onClick={() => navigate(`/repo/${repo.id}`)}
                className="w-full flex items-center justify-between bg-white/5 border border-white/10 rounded-xl px-5 py-3.5 hover:bg-white/[0.08] transition-colors text-left">
                <div>
                  <span className="font-medium text-sm">{repo.owner}/{repo.name}</span>
                  <span className="text-xs text-gray-500 ml-3">{formatDate(repo.created_at)}</span>
                </div>
                <span className={`text-xs font-medium capitalize ${statusColor(repo.status)}`}>{repo.status}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
