"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { useHash } from "@/lib/use-hash";
import { request } from "@/lib/api";
import { useSession } from "@/components/session";
import { Button } from "@/components/ui/button";
export function AuthForm({ signup = false }: { signup?: boolean }) {
  const { refresh } = useSession();
  const router = useRouter();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const hash = useHash();
  const fragment = /^#invite=[A-Za-z0-9_-]{32,128}$/.test(hash) ? hash : "";
  const lock = useRef(false);
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (lock.current) return; lock.current = true; setBusy(true); setError("");
    const data = new FormData(event.currentTarget);
    try {
      await request(`/api/v1/auth/${signup ? "register" : "login"}`, { method: "POST", body: JSON.stringify({ email: data.get("email"), password: data.get("password"), ...(signup ? { display_name: data.get("name") } : {}) }) });
      await refresh();
      router.push(fragment ? `/invitations/accept#token=${fragment.slice(8)}` : "/");
    } catch(e) { setError(e instanceof Error ? e.message : "Could not sign in."); lock.current = false; setBusy(false); }
  }
  return <div className="page-content narrow auth-page"><p className="eyebrow">YOUR IDEAS BELONG HERE</p><h1 className="page-title">{signup ? "Create your account" : "Welcome back"}</h1><p className="page-description">{signup ? "A thoughtful space for you and your team." : "Sign in to continue building with your team."}</p><form onSubmit={submit} className="standard-form" aria-busy={busy}>
    {signup && <label>Display name<input name="name" autoComplete="name" required maxLength={80} disabled={busy} /></label>}
    <label>Email<input name="email" type="email" autoComplete="email" required maxLength={320} disabled={busy} /></label><label>Password<input name="password" type="password" autoComplete={signup ? "new-password" : "current-password"} required minLength={signup ? 12 : 1} maxLength={128} disabled={busy} /></label>
    {signup && <p className="form-note">Use 12 to 128 characters. Email verification and password recovery are not available yet.</p>}{error && <p role="alert" className="error-message">{error}</p>}
    <Button type="submit" disabled={busy}>{busy ? "Please wait…" : signup ? "Create account" : "Sign in"}</Button><p className="form-note">{signup ? "Already have an account?" : "New to ORBA?"} <Link href={`${signup ? "/signin" : "/signup"}${fragment}`}>{signup ? "Sign in" : "Create an account"}</Link></p>
  </form></div>;
}
