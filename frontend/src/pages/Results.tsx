import { useState } from "react";
import { useParams, useSearchParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { repoApi } from "@/services/api";
import { useJobPoller } from "@/hooks/useJobPoller";
import { statusLabel } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import MermaidView from "@/components/mermaid/MermaidView";
import ComplexityPanel from "@/components/complexity/ComplexityPanel";
import type { Document, Analysis, ComplexityScore, MermaidDiagram, OnboardingGuide } from "@/types";

const TABS = [
  {id:"summary",label:"Summary",icon:"📋"},
  {id:"architecture",label:"Architecture",icon:"🏗️"},
  {id:"folder",label:"Folders",icon:"📁"},
  {id:"setup_guide",label:"Setup",icon:"⚙️"},
  {id:"api_docs",label:"API Docs",icon:"🔌"},
  {id:"readme",label:"README",icon:"📖"},
  {id:"recruiter",label:"Recruiter",icon:"🎯"},
  {id:"interview",label:"Interview",icon:"🎓"},
  {id:"onboarding",label:"Onboarding",icon:"🚀"},
  {id:"diagrams",label:"Diagrams",icon:"📊"},
  {id:"complexity",label:"Complexity",icon:"🔬"},
];

export default function Results() {
  const { repoId } = useParams<{repoId:string}>();
  const [sp] = useSearchParams();
  const navigate = useNavigate();
  const jobId = sp.get("job");
  const [tab, setTab] = useState("summary");
  const [ready, setReady] = useState(false);

  const job = useJobPoller(jobId, () => setReady(true));

  const { data: repo } = useQuery({
    queryKey: ["repo", repoId],
    queryFn: () => repoApi.getRepo(repoId!).then(r => r.data),
    enabled: !!repoId, refetchInterval: ready ? false : 3000,
  });

  const isDone = ready || repo?.status === "complete";

  const { data: docs }       = useQuery({ queryKey: ["docs",repoId], queryFn: () => repoApi.getDocs(repoId!).then(r => r.data as Document[]), enabled: isDone });
  const { data: analysis }   = useQuery({ queryKey: ["analysis",repoId], queryFn: () => repoApi.getAnalysis(repoId!).then(r => r.data as Analysis), enabled: isDone });
  const { data: complexity }  = useQuery({ queryKey: ["complexity",repoId], queryFn: () => repoApi.getComplexity(repoId!).then(r => r.data as ComplexityScore), enabled: isDone });
  const { data: diagrams }   = useQuery({ queryKey: ["diagrams",repoId], queryFn: () => repoApi.getDiagrams(repoId!).then(r => r.data as MermaidDiagram[]), enabled: isDone });
  const { data: onboarding } = useQuery({ queryKey: ["onboarding",repoId], queryFn: () => repoApi.getOnboarding(repoId!).then(r => r.data as OnboardingGuide), enabled: isDone });

  if (!isDone || !repo) return <ProgressScreen job={job} />;

  const doc = (t: string) => docs?.find(d => d.doc_type === t);

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      <header className="border-b border-white/10 px-6 py-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate("/")} className="text-gray-400 hover:text-white text-sm">← Back</button>
          <div>
            <h1 className="font-semibold">{repo.owner}/{repo.name}</h1>
            {analysis && <p className="text-xs text-gray-500">{analysis.languages.slice(0,3).join(" · ")} · {analysis.file_count} files · {analysis.loc_total.toLocaleString()} LOC</p>}
          </div>
        </div>
        <div className="flex items-center gap-3">
          {analysis && analysis.frameworks.slice(0,3).map(f => (
            <span key={f} className="text-xs bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-full">{f}</span>
          ))}
          <button onClick={() => navigate(`/repo/${repoId}/chat`)} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors">💬 Chat</button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-48 border-r border-white/10 flex-shrink-0 overflow-y-auto">
          <nav className="p-2 space-y-0.5">
            {TABS.map(t => (
              <button key={t.id} onClick={() => setTab(t.id)}
                className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm transition-colors text-left ${tab===t.id?"bg-blue-600 text-white":"text-gray-400 hover:text-white hover:bg-white/5"}`}>
                <span>{t.icon}</span><span>{t.label}</span>
              </button>
            ))}
          </nav>
        </aside>

        <main className="flex-1 overflow-y-auto p-6">
          {tab==="diagrams" && <DiagramsTab diagrams={diagrams}/>}
          {tab==="complexity" && <ComplexityPanel complexity={complexity}/>}
          {tab==="onboarding" && <OnboardingTab guide={onboarding}/>}
          {!["diagrams","complexity","onboarding"].includes(tab) && <MdTab content={doc(tab)?.content} label={tab}/>}
        </main>
      </div>
    </div>
  );
}

function ProgressScreen({job}: {job: any}) {
  const p = job?.progress ?? 0;
  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-blue-600/30 border-t-blue-500 rounded-full animate-spin mx-auto mb-6"/>
        <h2 className="text-2xl font-semibold mb-2">Analyzing Repository</h2>
        <p className="text-gray-400 mb-6">{statusLabel(job?.step ?? "init")}</p>
        <div className="w-80 bg-white/10 rounded-full h-2 overflow-hidden mx-auto">
          <div className="h-full bg-gradient-to-r from-blue-600 to-purple-600 rounded-full transition-all duration-500" style={{width:`${p}%`}}/>
        </div>
        <p className="text-xs text-gray-500 mt-2">{p}%</p>
        {job?.status==="failed" && <p className="text-red-400 text-sm mt-4">Analysis failed: {job.error}</p>}
      </div>
    </div>
  );
}

function MdTab({content, label}: {content?: string; label: string}) {
  if (!content) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-3"/>
        <p className="text-gray-500 text-sm">Generating {label.replace(/_/g," ")}…</p>
      </div>
    </div>
  );
  return <div className="prose prose-invert prose-sm max-w-none"><ReactMarkdown>{content}</ReactMarkdown></div>;
}

function DiagramsTab({diagrams}: {diagrams?: MermaidDiagram[]}) {
  const [i, setI] = useState(0);
  if (!diagrams?.length) return <div className="text-gray-500 text-sm">Generating diagrams…</div>;
  return (
    <div>
      <div className="flex gap-2 mb-6 flex-wrap">
        {diagrams.map((d,idx) => (
          <button key={d.id} onClick={() => setI(idx)}
            className={`px-4 py-2 rounded-lg text-sm capitalize transition-colors ${idx===i?"bg-blue-600 text-white":"bg-white/5 text-gray-400 hover:text-white"}`}>
            {d.diagram_type.replace("_"," ")}
          </button>
        ))}
      </div>
      <MermaidView source={diagrams[i].source} key={diagrams[i].id}/>
    </div>
  );
}

function OnboardingTab({guide}: {guide?: OnboardingGuide}) {
  const [day, setDay] = useState<1|2|3>(1);
  if (!guide) return <div className="text-gray-500 text-sm">Generating onboarding guide…</div>;
  const content = day===1?guide.day1:day===2?guide.day2:guide.day3;
  return (
    <div>
      <div className="flex gap-3 mb-6">
        {([1,2,3] as const).map(d => (
          <button key={d} onClick={() => setDay(d)}
            className={`px-5 py-2.5 rounded-xl font-medium text-sm transition-colors ${day===d?"bg-blue-600 text-white":"bg-white/5 text-gray-400 hover:text-white"}`}>
            Day {d}
          </button>
        ))}
      </div>
      <div className="prose prose-invert prose-sm max-w-none"><ReactMarkdown>{content}</ReactMarkdown></div>
      {day===1 && guide.key_files.length>0 && (
        <div className="mt-8">
          <h3 className="font-semibold mb-3">Key Files to Study</h3>
          <div className="space-y-1">
            {guide.key_files.map((f,i) => (
              <div key={i} className="flex items-center gap-2 text-sm bg-white/5 px-3 py-2 rounded-lg">
                <span className="text-blue-400">📄</span>
                <code className="text-blue-300">{typeof f==="string"?f:JSON.stringify(f)}</code>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
