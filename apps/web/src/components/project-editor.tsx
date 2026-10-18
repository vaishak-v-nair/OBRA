"use client";
import { useState } from "react";
import { request, type Project } from "@/lib/api";
import { useSession } from "@/components/session";
import { Button } from "@/components/ui/button";
export function ProjectEditor({ project, saved }: { project: Project; saved: (project: Project) => void }) {
  const { workspace } = useSession();
  const [editing, setEditing] = useState(false); const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  if (workspace?.role === "viewer") return <p className="form-note">Viewer access · You can read this project.</p>;
  if (!editing) return <Button variant="outline" className="mt-5" onClick={() => setEditing(true)}>Edit project</Button>;
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (busy) return; setBusy(true); setError(""); const data = new FormData(event.currentTarget);
    try { const result = await request<Project>(`/api/v1/projects/${project.id}`, { method: "PATCH", body: JSON.stringify({ title: data.get("title"), description: data.get("description") }) }); saved(result); setEditing(false); }
    catch(e) { setError(e instanceof Error ? e.message : "Could not save project."); } finally { setBusy(false); }
  }
  return <form className="standard-form" onSubmit={submit}><label>Project title<input name="title" defaultValue={project.title} maxLength={120} required disabled={busy} /></label><label>Project description<textarea name="description" defaultValue={project.description} maxLength={10000} required disabled={busy} /></label>{error && <p role="alert" className="error-message">{error}</p>}<div className="workspace-actions"><Button type="submit" disabled={busy}>Save project</Button><Button type="button" variant="outline" disabled={busy} onClick={() => setEditing(false)}>Cancel</Button></div></form>;
}
