"use client";
import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { request, type Workspace } from "@/lib/api";
import { useSession } from "@/components/session";
import { Button } from "@/components/ui/button";
export default function NewWorkspace() {
  const { refresh } = useSession(); const router = useRouter(); const lock = useRef(false);
  const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (lock.current) return; lock.current = true; setBusy(true); setError("");
    const name = new FormData(event.currentTarget).get("name");
    try { const space = await request<Workspace>("/api/v1/workspaces", { method: "POST", body: JSON.stringify({ name }) }); sessionStorage.setItem("orba-workspace", space.id); await refresh(); router.push("/"); }
    catch(e) { setError(e instanceof Error ? e.message : "Could not create workspace."); lock.current = false; setBusy(false); }
  }
  return <div className="page-content narrow"><p className="eyebrow">MAKE SPACE FOR YOUR TEAM</p><h1 className="page-title">Create a workspace</h1><p className="page-description">You’ll be its Owner. Invite teammates when you’re ready.</p><form onSubmit={submit} className="standard-form"><label>Workspace name<input name="name" required maxLength={100} disabled={busy} /></label>{error && <p role="alert" className="error-message">{error}</p>}<Button type="submit" disabled={busy}>{busy ? "Creating…" : "Create workspace"}</Button></form></div>;
}
