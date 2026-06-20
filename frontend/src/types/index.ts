export type RepoStatus = "queued"|"cloning"|"parsing"|"detecting"|"generating_docs"|"complexity"|"diagrams"|"indexing"|"complete"|"failed";
export type DocType = "summary"|"architecture"|"folder"|"setup_guide"|"api_docs"|"readme"|"recruiter"|"interview";
export type DiagramType = "component"|"dataflow"|"api_flow"|"database";

export interface Repo { id:string; url:string; name:string; owner:string; status:RepoStatus; created_at:string; }
export interface Job  { id:string; repo_id:string; status:string; step:string; progress:number; error:string|null; }
export interface Analysis { id:string; repo_id:string; arch_type:string|null; languages:string[]; frameworks:string[]; databases:string[]; auth_methods:string[]; design_patterns:string[]; package_managers:string[]; deployment_configs:string[]; file_count:number; loc_total:number; }
export interface Document { id:string; repo_id:string; doc_type:DocType; content:string; tokens_used:number; created_at:string; }
export interface ComplexityScore { id:string; repo_id:string; overall:number; maintainability:number; documentation:number; architecture:number; test_coverage:number; tech_debt:number; strengths:string[]; weaknesses:string[]; suggestions:string[]; hotspots:string[]; }
export interface MermaidDiagram  { id:string; repo_id:string; diagram_type:DiagramType; source:string; created_at:string; }
export interface OnboardingGuide { id:string; repo_id:string; day1:string; day2:string; day3:string; key_files:any[]; checklist:string[]; }
export interface Comparison { id:string; repo_a_id:string; repo_b_id:string; score_matrix:any; summary:string|null; tech_stack_diff:any; status:string; }
export interface ChatSession { id:string; repo_id:string; mode:string; created_at:string; }
export interface ChatMessage  { id:string; session_id:string; role:"user"|"assistant"; content:string; created_at:string; }
