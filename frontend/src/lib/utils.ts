import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", { month:"short", day:"numeric", year:"numeric" });
}
export function statusColor(s: string): string {
  if (s === "complete") return "text-green-500";
  if (s === "failed")   return "text-red-500";
  if (s === "queued")   return "text-gray-400";
  return "text-amber-500";
}
export function statusLabel(step: string): string {
  const MAP: Record<string,string> = {
    init:"Initializing", cloning:"Cloning repository", parsing:"Reading source files",
    detecting:"Detecting architecture", generating_summary:"Generating summary",
    generating_architecture:"Analyzing architecture", generating_folder:"Explaining folders",
    generating_setup_guide:"Writing setup guide", generating_api_docs:"Documenting APIs",
    generating_readme:"Generating README", generating_recruiter:"Writing recruiter content",
    generating_interview:"Generating interview questions", onboarding:"Creating onboarding guide",
    complexity:"Analyzing code complexity", diagrams:"Generating diagrams",
    indexing:"Building RAG index", done:"Complete",
  };
  return MAP[step] ?? step.replace(/_/g," ");
}
