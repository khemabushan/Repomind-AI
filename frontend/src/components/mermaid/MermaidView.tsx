import { useEffect, useRef } from "react";
import mermaid from "mermaid";

mermaid.initialize({
  startOnLoad: false,
  theme: "dark",
  securityLevel: "loose",
  flowchart: { curve: "basis", useMaxWidth: true },
});

let counter = 0;

export default function MermaidView({ source }: { source: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const id = useRef(`mermaid-${++counter}`);

  useEffect(() => {
    if (!ref.current || !source) return;
    ref.current.innerHTML = "";
    const cleaned = source.trim();
    mermaid.render(id.current, cleaned).then(({ svg }) => {
      if (ref.current) ref.current.innerHTML = svg;
    }).catch(err => {
      if (ref.current) ref.current.innerHTML = `<pre class="text-red-400 text-xs p-4 bg-red-500/10 rounded-lg overflow-auto">${cleaned}\n\nRender error: ${err.message}</pre>`;
    });
    id.current = `mermaid-${++counter}`;
  }, [source]);

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 overflow-auto">
      <div ref={ref} className="mermaid-container flex justify-center"/>
    </div>
  );
}
