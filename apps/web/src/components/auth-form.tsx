"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import { useHash } from "@/lib/use-hash";
import { ApiError, request } from "@/lib/api";
import { useSession } from "@/components/session";
import { Button } from "@/components/ui/button";
export function AuthForm({ signup = false }: { signup?: boolean }) {
  const { refresh, loading } = useSession();
  const router = useRouter();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [passwordInvalid, setPasswordInvalid] = useState(false);
  const passwordInput = useRef<HTMLInputElement>(null);
  const passwordHelpId = useId();
  const passwordErrorId = useId();
  const hash = useHash();
  const fragment = /^#invite=[A-Za-z0-9_-]{32,128}$/.test(hash) ? hash : "";
  const lock = useRef(false);
  useEffect(() => {
    if (passwordInvalid && !busy) passwordInput.current?.focus();
  }, [passwordInvalid, busy]);
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (lock.current || loading) return;
    const data = new FormData(event.currentTarget);
    const password = String(data.get("password") ?? "");
    // Count Unicode code points like the API, preserving the exact value.
    // Native maxlength counts UTF-16 units and can silently clip pasted input.
    const length = Array.from(password).length;
    if (length < (signup ? 15 : 1) || length > 128) {
      setError(signup ? "Use a password of 15 to 128 characters." : "Use a password of 1 to 128 characters.");
      setPasswordInvalid(true);
      return;
    }
    lock.current = true; setBusy(true); setError(""); setPasswordInvalid(false);
    try {
      await request(`/api/v1/auth/${signup ? "register" : "login"}`, { method: "POST", body: JSON.stringify({ email: data.get("email"), password, ...(signup ? { display_name: data.get("name") } : {}) }) });
      await refresh();
      router.push(fragment ? `/invitations/accept#token=${fragment.slice(8)}` : "/");
    } catch(e) { setError(e instanceof Error ? e.message : "Could not sign in."); setPasswordInvalid(e instanceof ApiError && e.details.some(({ field }) => field === "body.password")); lock.current = false; setBusy(false); }
  }
  return <div className="page-content narrow auth-page"><p className="eyebrow">YOUR IDEAS BELONG HERE</p><h1 className="page-title">{signup ? "Create your account" : "Welcome back"}</h1><p className="page-description">{signup ? "A thoughtful space for you and your team." : "Sign in to continue building with your team."}</p><form method="post" onSubmit={submit} className="standard-form" aria-busy={busy || loading}>
    {loading && <p role="status">Checking current session…</p>}
    {signup && <label>Display name<input name="name" autoComplete="name" required maxLength={80} disabled={busy || loading} /></label>}
    <label>Email<input name="email" type="email" autoComplete="email" required maxLength={320} disabled={busy || loading} /></label><label>Password<input ref={passwordInput} name="password" type="password" autoComplete={signup ? "new-password" : "current-password"} required minLength={signup ? 15 : 1} aria-describedby={[signup ? passwordHelpId : "", passwordInvalid ? passwordErrorId : ""].filter(Boolean).join(" ") || undefined} aria-invalid={passwordInvalid || undefined} onInput={() => { if (passwordInvalid) { setPasswordInvalid(false); setError(""); } }} disabled={busy || loading} /></label>
    {signup && <><p id={passwordHelpId} className="form-note">Use 15 to 128 characters. Passphrases and password managers are welcome.</p><p className="form-note">Email verification and password recovery are not available yet.</p></>}{error && <p id={passwordErrorId} role="alert" className="error-message">{error}</p>}
    <Button type="submit" disabled={busy || loading}>{busy ? "Please wait…" : signup ? "Create account" : "Sign in"}</Button><p className="form-note">{signup ? "Already have an account?" : "New to ORBA?"} <Link href={`${signup ? "/signin" : "/signup"}${fragment}`}>{signup ? "Sign in" : "Create an account"}</Link></p>
  </form></div>;
}
