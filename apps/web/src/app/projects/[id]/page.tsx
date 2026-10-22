"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, ArrowUpRight, CalendarDays, FolderKanban, Layers3, LoaderCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { projects, type Project } from "@/lib/api";
import { useSession } from "@/components/session";
import { ProjectEditor } from "@/components/project-editor";
import { ProjectPlanning } from "@/components/project-planning";
import { Button } from "@/components/ui/button";
export default function ProjectDetail() {
  const { workspace } = useSession();
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project>();
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => { let active = true; projects.get(id).then((data) => { if (active) { if (data.workspace_id === workspace?.id) setProject(data); else setError("Project not found in this workspace."); } }).catch((e: Error) => { if (active) setError(e.message); }); return () => { active = false; }; }, [id, attempt, workspace]);
  return <div className="page-content" data-testid="project-detail" data-project-id={project?.id} data-workspace-id={project?.workspace_id}><Link href="/projects" className="back-link"><ArrowLeft size={16} /> All projects</Link>{error ? <div className="state-box"><h1>Project couldn’t be opened</h1><p role="alert">{error}</p><Button variant="outline" onClick={() => { setError(""); setAttempt((n) => n + 1); }}>Try again</Button></div> : !project ? <div className="state-box" role="status"><LoaderCircle className="animate-spin" />Loading project…</div> : <><div className="detail-heading"><span className="project-icon large"><FolderKanban size={28} /></span><div><p className="eyebrow">PROJECT OVERVIEW</p><h1 className="page-title">{project.title}</h1></div><span className="status-badge">Created</span></div><div className="detail-meta"><CalendarDays size={15} /><span>Created <time dateTime={project.created_at}>{new Date(project.created_at).toLocaleString()}</time></span></div><section className="overview-panel"><h2>Where it begins</h2><p className="section-subtitle">Your original project description</p><p className="original-description">{project.description}</p><ProjectEditor project={project} saved={setProject} /></section><ProjectPlanning project={project} /><section className="future-panel"><Layers3 size={26} strokeWidth={1.4} /><div><h2>Room for what comes next</h2><p>Task execution, additional agents, and delivery evidence belong to later stages.</p><span className="later-label">Coming in a later stage</span></div><ArrowUpRight className="future-arrow" size={20} /></section></>}</div>;
}


