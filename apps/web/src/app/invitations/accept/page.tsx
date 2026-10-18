"use client";
import Link from "next/link";
import { useState } from "react";
import { useHash } from "@/lib/use-hash";
import { useRouter } from "next/navigation";
import { request, type Workspace } from "@/lib/api";
import { useSession } from "@/components/session";
import { Button } from "@/components/ui/button";
export default function AcceptInvitation() {
  const { user, refresh } = useSession(); const router = useRouter();
  const hash = useHash();
  const value = new URLSearchParams(hash.slice(1)).get("token") ?? "";
  const token = /^[A-Za-z0-9_-]{32,128}$/.test(value) ? value : "";
  const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  async function accept() { setBusy(true); setError(""); try { const space = await request<Workspace>("/api/v1/invitations/accept", { method: "POST", body: JSON.stringify({ token }) }); history.replaceState(null, "", "/invitations/accept"); sessionStorage.setItem("orba-workspace", space.id); await refresh(); router.push("/projects"); } catch(e) { setError(e instanceof Error ? e.message : "Could not accept invitation."); setBusy(false); } }
  return <div className="page-content narrow"><p className="eyebrow">BUILD SOMETHING TOGETHER</p><h1 className="page-title">Join a workspace</h1><p className="page-description">Sign in with the email this invitation was addressed to. Joining grants only the role chosen by the inviter.</p>{(error || !token) && <p role="alert" className="error-message">{error || "This invitation link is invalid."}</p>}{token && (user ? <div className="standard-form"><p>Signed in as {user.email}</p><Button disabled={busy} onClick={() => void accept()}>{busy ? "Joining…" : "Accept invitation"}</Button></div> : <div className="workspace-actions"><Button asChild><Link href={`/signin#invite=${token}`}>Sign in to accept</Link></Button><Link href={`/signup#invite=${token}`}>Create an account to accept</Link></div>)}</div>;
}

