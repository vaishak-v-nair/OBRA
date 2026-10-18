"use client";
import Link from "next/link";
import { ArrowUpRight, FolderKanban, LoaderCircle, Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { projects, type Project } from "@/lib/api";
import { useSession } from "@/components/session";
import { Button } from "@/components/ui/button";
export default function Projects() {
  const { workspace } = useSession();
  const [items, setItems] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [offset, setOffset] = useState(0);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    projects.list(workspace!.id, offset).then((data) => { if (active) setItems(data); }).catch((e: Error) => { if (active) setError(e.message); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [offset, attempt, workspace]);
  function load(nextOffset: number) { setLoading(true); setError(""); setOffset(nextOffset); setAttempt((n) => n + 1); }
  return <div className="page-content"><div className="page-heading"><div><p className="eyebrow">IDEAS WITH A HOME</p><h1 className="page-title">Projects</h1><p className="page-description">Your next chapter, and everything you’re building.</p></div>{workspace?.role !== "viewer" && <Button asChild><Link href="/projects/new"><Plus /> New project</Link></Button>}</div>
    {loading ? <div className="state-box" role="status"><LoaderCircle className="animate-spin" />Loading projects…</div> : error ? <div className="state-box"><h2>Projects couldn’t be loaded</h2><p role="alert">{error}</p><Button variant="outline" onClick={() => load(offset)}>Try again</Button></div> : !items.length ? <div className="state-box"><FolderKanban size={36} strokeWidth={1.3} /><h2>{offset ? "You’ve reached the end" : "Every project starts with an idea"}</h2><p>{offset ? "Return to the previous page to see your projects." : "Create your first project and give your next idea a home."}</p>{!offset && workspace?.role !== "viewer" && <Button asChild><Link href="/projects/new"><Plus /> Create your first project</Link></Button>}</div> : <div className="project-grid">{items.map((project) => <Link className="project-card" key={project.id} href={`/projects/${project.id}`}><div className="project-card-top"><span className="project-icon"><FolderKanban size={21} /></span><span className="status-badge">Created</span></div><h2>{project.title}</h2><p>{project.description}</p><div className="project-card-footer"><time dateTime={project.created_at}>{new Date(project.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}</time><ArrowUpRight size={18} /></div></Link>)}</div>}
    {!loading && !error && (offset > 0 || items.length === 50) && <div className="pagination"><Button variant="outline" disabled={!offset} onClick={() => load(Math.max(0, offset - 50))}>Previous</Button><span>Page {offset / 50 + 1}</span><Button variant="outline" disabled={items.length < 50} onClick={() => load(offset + 50)}>Next</Button></div>}
  </div>;
}

