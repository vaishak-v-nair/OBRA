"use client";
import { ArrowUp, GitFork, LoaderCircle, Paperclip } from "lucide-react";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { projects } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { useSession } from "@/components/session";

export function ProjectForm({ compact = false }: { compact?: boolean }) {
  const router = useRouter();
  const { workspace } = useSession();
  const [description, setDescription] = useState("");
  const [title, setTitle] = useState("");
  const [busy, setBusy] = useState(false);
  const submitting = useRef(false);
  const [error, setError] = useState("");
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting.current) return;
    if (!workspace || workspace.role === "viewer") { setError("Your workspace role does not permit project creation."); return; }
    if (!description.trim() || (compact && !title.trim())) { setError("Enter a project description and title."); return; }
    submitting.current = true;
    setBusy(true); setError("");
    try {
      const derivedTitle = description.trim().split("\n")[0].slice(0, 120);
      const project = await projects.create(compact ? title.trim() : derivedTitle, description.trim(), workspace.id);
      router.push(`/projects/${project.id}`);
    } catch (err) { setError(err instanceof Error ? err.message : "Could not create project."); setBusy(false); submitting.current = false; }
  }
  return <form onSubmit={submit} className="project-form" aria-label="Create project" aria-busy={busy}>
    {compact && <div className="title-field"><label htmlFor="project-title">Project title</label><input id="project-title" value={title} onChange={(e) => setTitle(e.target.value)} required maxLength={120} disabled={busy || workspace?.role === "viewer"} placeholder="Give your idea a name" /></div>}
    <div className="composer"><label htmlFor="description" className={compact ? "field-label" : "sr-only"}>Project description</label><textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Describe what you’d like to build..." required maxLength={10000} disabled={busy || workspace?.role === "viewer"} aria-describedby="create-help" rows={compact ? 6 : 4} /><div className="composer-toolbar"><div className="composer-tools"><span title="Attachments are coming in a later stage"><Button type="button" variant="ghost" size="icon" disabled aria-label="Attachments coming in a later stage"><Paperclip /></Button></span><span title="GitHub integration is coming in a later stage"><Button type="button" variant="ghost" size="icon" disabled aria-label="GitHub integration coming in a later stage"><GitFork /></Button></span><span className="composer-tool-label">Start with an idea</span></div><Button type="submit" size={compact ? "default" : "icon"} disabled={busy || workspace?.role === "viewer"} aria-label="Create project">{busy ? <LoaderCircle className="animate-spin" /> : <ArrowUp />}{compact && (busy ? "Creating…" : "Create project")}</Button></div></div>
    {error && <div className="error-message" role="alert">{error}</div>}<p id="create-help" className="form-help">{compact ? "Your project is saved in this local workspace." : "Your description creates a project. AI collaboration is coming in a later stage."}</p>
  </form>;
}


