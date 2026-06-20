import type { ComplexityScore } from "@/types";

function ScoreGauge({ label, value, color }: { label: string; value: number; color: string }) {
  const r = 28, circ = 2 * Math.PI * r;
  const offset = circ - (value / 100) * circ;
  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="72" height="72" viewBox="0 0 72 72">
        <circle cx="36" cy="36" r={r} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="6"/>
        <circle cx="36" cy="36" r={r} fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={circ} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 36 36)" style={{transition:"stroke-dashoffset 1s ease"}}/>
        <text x="36" y="40" textAnchor="middle" fill="white" fontSize="14" fontWeight="600">{value}</text>
      </svg>
      <span className="text-xs text-gray-400 text-center">{label}</span>
    </div>
  );
}

export default function ComplexityPanel({ complexity }: { complexity?: ComplexityScore }) {
  if (!complexity) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-3"/>
        <p className="text-gray-500 text-sm">Computing complexity metrics…</p>
      </div>
    </div>
  );

  const overallColor = complexity.overall >= 70 ? "#22c55e" : complexity.overall >= 40 ? "#f59e0b" : "#ef4444";

  return (
    <div className="space-y-8 max-w-3xl">
      {/* Overall score */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-6 text-center">
        <div className="relative w-32 h-32 mx-auto mb-4">
          <svg width="128" height="128" viewBox="0 0 128 128">
            <circle cx="64" cy="64" r="54" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="10"/>
            <circle cx="64" cy="64" r="54" fill="none" stroke={overallColor} strokeWidth="10"
              strokeDasharray={2*Math.PI*54} strokeDashoffset={2*Math.PI*54*(1-complexity.overall/100)}
              strokeLinecap="round" transform="rotate(-90 64 64)" style={{transition:"stroke-dashoffset 1.2s ease"}}/>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold">{complexity.overall}</span>
            <span className="text-xs text-gray-400">/100</span>
          </div>
        </div>
        <h2 className="text-xl font-semibold">Overall Repository Score</h2>
        <p className="text-gray-400 text-sm mt-1">
          {complexity.overall >= 70 ? "Good quality codebase" : complexity.overall >= 40 ? "Average quality — some improvements needed" : "Needs significant improvement"}
        </p>
      </div>

      {/* Sub-scores */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
        <h3 className="font-semibold mb-6">Detailed Metrics</h3>
        <div className="grid grid-cols-4 gap-6">
          <ScoreGauge label="Maintainability" value={complexity.maintainability} color="#3b82f6"/>
          <ScoreGauge label="Documentation"  value={complexity.documentation}  color="#8b5cf6"/>
          <ScoreGauge label="Architecture"   value={complexity.architecture}    color="#06b6d4"/>
          <ScoreGauge label="Tech Debt" value={100-complexity.tech_debt} color="#f59e0b"/>
        </div>
        <div className="mt-4 flex items-center justify-center gap-2 text-sm text-gray-400 bg-white/5 rounded-xl px-4 py-2 w-fit mx-auto">
          <span>Test Coverage</span>
          <span className="font-medium text-white">{complexity.test_coverage.toFixed(1)}%</span>
        </div>
      </div>

      {/* Strengths / Weaknesses */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-green-500/5 border border-green-500/20 rounded-2xl p-5">
          <h3 className="font-semibold text-green-400 mb-3">✅ Strengths</h3>
          <ul className="space-y-2">
            {complexity.strengths.map((s,i) => <li key={i} className="text-sm text-gray-300 flex gap-2"><span className="text-green-400 flex-shrink-0">•</span>{s}</li>)}
          </ul>
        </div>
        <div className="bg-red-500/5 border border-red-500/20 rounded-2xl p-5">
          <h3 className="font-semibold text-red-400 mb-3">⚠️ Weaknesses</h3>
          <ul className="space-y-2">
            {complexity.weaknesses.map((w,i) => <li key={i} className="text-sm text-gray-300 flex gap-2"><span className="text-red-400 flex-shrink-0">•</span>{w}</li>)}
          </ul>
        </div>
      </div>

      {/* Suggestions */}
      <div className="bg-blue-500/5 border border-blue-500/20 rounded-2xl p-5">
        <h3 className="font-semibold text-blue-400 mb-3">💡 Improvement Suggestions</h3>
        <ol className="space-y-2">
          {complexity.suggestions.map((s,i) => (
            <li key={i} className="text-sm text-gray-300 flex gap-3">
              <span className="text-blue-400 font-medium w-5 flex-shrink-0">{i+1}.</span>{s}
            </li>
          ))}
        </ol>
      </div>

      {/* Hotspot files */}
      {complexity.hotspots.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
          <h3 className="font-semibold mb-3">🔥 Complexity Hotspots</h3>
          <div className="space-y-1.5">
            {complexity.hotspots.map((f,i) => (
              <div key={i} className="flex items-center gap-2 text-sm bg-white/5 px-3 py-2 rounded-lg">
                <span className="text-red-400">⚠️</span>
                <code className="text-gray-300 text-xs">{f}</code>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
