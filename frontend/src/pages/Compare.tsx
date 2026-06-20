import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { compareApi } from "@/services/api";
import ReactMarkdown from "react-markdown";

type Status = "idle"|"loading"|"polling"|"done"|"failed";

function ScoreBar({ label, a, b, maxVal=100 }: { label:string; a:number; b:number; maxVal?:number }) {
  const pctA = Math.round((a/maxVal)*100);
  const pctB = Math.round((b/maxVal)*100);
  const winner = a >= b ? "A" : "B";
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs text-gray-400">
        <span>{label}</span>
        <span className={`font-medium ${winner==="A"?"text-blue-400":"text-purple-400"}`}>Winner: Repo {winner}</span>
      </div>
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <span className="text-xs text-blue-400 w-12">Repo A</span>
          <div className="flex-1 bg-white/10 rounded-full h-2">
            <div className="h-full bg-blue-500 rounded-full transition-all duration-700" style={{width:`${pctA}%`}}/>
          </div>
          <span className="text-xs text-gray-400 w-8">{a}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-purple-400 w-12">Repo B</span>
          <div className="flex-1 bg-white/10 rounded-full h-2">
            <div className="h-full bg-purple-500 rounded-full transition-all duration-700" style={{width:`${pctB}%`}}/>
          </div>
          <span className="text-xs text-gray-400 w-8">{b}</span>
        </div>
      </div>
    </div>
  );
}

export default function Compare() {
  const navigate = useNavigate();
  const [urlA, setUrlA] = useState("");
  const [urlB, setUrlB] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [compId, setCompId] = useState<string|null>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  async function startCompare(e: React.FormEvent) {
    e.preventDefault();
    if (!urlA.includes("github.com") || !urlB.includes("github.com")) {
      setError("Both fields must be valid GitHub URLs"); return;
    }
    setError(""); setStatus("loading");
    try {
      const res = await compareApi.start(urlA, urlB);
      setCompId(res.data.comparison_id);
      setStatus("polling");
    } catch(e: any) { setError(e.message); setStatus("failed"); }
  }

  useEffect(() => {
    if (status !== "polling" || !compId) return;
    const iv = setInterval(async () => {
      try {
        const res = await compareApi.getResult(compId);
        const c = res.data;
        if (c.status === "complete") { setResult(c); setStatus("done"); clearInterval(iv); }
        if (c.status === "failed") { setError("Comparison failed"); setStatus("failed"); clearInterval(iv); }
      } catch(_) {}
    }, 4000);
    return () => clearInterval(iv);
  }, [status, compId]);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <button onClick={() => navigate("/")} className="text-gray-400 hover:text-white text-sm">← Back</button>
          <h1 className="text-2xl font-bold">Repository Comparison</h1>
        </div>

        <form onSubmit={startCompare} className="bg-white/5 border border-white/10 rounded-2xl p-6 mb-8">
          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Repository A</label>
              <input value={urlA} onChange={e=>setUrlA(e.target.value)} placeholder="https://github.com/owner/repo-a"
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"/>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Repository B</label>
              <input value={urlB} onChange={e=>setUrlB(e.target.value)} placeholder="https://github.com/owner/repo-b"
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 text-sm"/>
            </div>
          </div>
          {error && <p className="text-red-400 text-sm mb-3">{error}</p>}
          <button type="submit" disabled={status==="loading"||status==="polling"}
            className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90 disabled:opacity-50 rounded-xl font-medium text-sm transition-opacity">
            {status==="loading"?"Submitting…":status==="polling"?"Analyzing both repos…":"Compare Repositories →"}
          </button>
        </form>

        {(status==="loading"||status==="polling") && (
          <div className="text-center py-12">
            <div className="w-12 h-12 border-4 border-blue-600/30 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"/>
            <p className="text-gray-400">{status==="loading"?"Submitting repositories…":"Analyzing and comparing — this may take a few minutes…"}</p>
          </div>
        )}

        {result && (
          <div className="space-y-8">
            {/* Score matrix */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h2 className="font-semibold text-lg mb-6">Quality Scores</h2>
              <div className="space-y-6">
                {[
                  {label:"Overall Quality", a:result.score_matrix?.overall?.a??0, b:result.score_matrix?.overall?.b??0},
                  {label:"Maintainability", a:result.score_matrix?.maintainability?.a??0, b:result.score_matrix?.maintainability?.b??0},
                  {label:"Documentation",  a:result.score_matrix?.documentation?.a??0,  b:result.score_matrix?.documentation?.b??0},
                  {label:"Test Coverage %",a:result.score_matrix?.test_coverage?.a??0,  b:result.score_matrix?.test_coverage?.b??0},
                  {label:"Lines of Code",  a:result.score_matrix?.loc?.a??0,            b:result.score_matrix?.loc?.b??0, maxVal:Math.max(result.score_matrix?.loc?.a??1, result.score_matrix?.loc?.b??1)},
                ].map(s => <ScoreBar key={s.label} {...s}/>)}
              </div>
            </div>

            {/* Tech stacks */}
            <div className="grid md:grid-cols-2 gap-6">
              {["a","b"].map(side => (
                <div key={side} className={`bg-white/5 border rounded-2xl p-5 ${side==="a"?"border-blue-500/30":"border-purple-500/30"}`}>
                  <h3 className={`font-semibold mb-4 ${side==="a"?"text-blue-400":"text-purple-400"}`}>Repo {side.toUpperCase()}</h3>
                  <div className="space-y-3">
                    {["frameworks","languages","databases"].map(k => {
                      const items = result.score_matrix?.tech_stack?.[side]?.[k] ?? [];
                      return items.length > 0 ? (
                        <div key={k}>
                          <p className="text-xs text-gray-500 capitalize mb-1">{k}</p>
                          <div className="flex flex-wrap gap-1.5">
                            {items.map((f: string) => (
                              <span key={f} className={`text-xs px-2 py-0.5 rounded-full ${side==="a"?"bg-blue-500/20 text-blue-300":"bg-purple-500/20 text-purple-300"}`}>{f}</span>
                            ))}
                          </div>
                        </div>
                      ) : null;
                    })}
                  </div>
                </div>
              ))}
            </div>

            {/* Summary */}
            {result.summary && (
              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <h2 className="font-semibold text-lg mb-4">Analysis Summary</h2>
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown>{result.summary}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
