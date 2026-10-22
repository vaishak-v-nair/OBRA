"use client";
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { advanceAuthEpoch, ApiError, request, type User, type Workspace } from "@/lib/api";
import { Button } from "@/components/ui/button";

type SessionState = { user: User | null; workspaces: Workspace[]; workspace: Workspace | null; loading: boolean; error: string; logoutWarning: string; refresh: () => Promise<void>; select: (id: string) => void; signout: () => Promise<void> };
const Context = createContext<SessionState | null>(null);
async function readSession() { const account = await request<User>("/api/v1/auth/me"); const spaces = await request<Workspace[]>("/api/v1/workspaces"); return { account, spaces }; }
export function useSession() { const context = useContext(Context); if (!context) throw new Error("Missing session provider"); return context; }
export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [logoutWarning, setLogoutWarning] = useState("");
  const generation = useRef(0);
  const router = useRouter();
  const apply = useCallback(({ account, spaces }: { account: User; spaces: Workspace[] }) => {
    setError(""); setLogoutWarning(""); setUser(account); setWorkspaces(spaces);
    const preference = sessionStorage.getItem("orba-workspace");
    setSelected((old) => spaces.find((space) => space.id === (preference ?? old))?.id ?? spaces[0]?.id ?? "");
  }, []);
  const failure = useCallback((e: unknown) => {
    setUser(null); setWorkspaces([]); setSelected("");
    if (!(e instanceof ApiError && e.status === 401)) setError(e instanceof Error ? e.message : "Could not check your session.");
  }, []);
  const refresh = useCallback(async () => {
    advanceAuthEpoch();
    const current = ++generation.current;
    try {
      const data = await readSession();
      if (current !== generation.current) return;
      apply(data);
    } catch (e) {
      if (current !== generation.current) return;
      failure(e);
    } finally { if (current === generation.current) setLoading(false); }
  }, [apply, failure]);
  useEffect(() => {
    let active = true;
    const current = ++generation.current;
    readSession().then((data) => { if (active && current === generation.current) apply(data); }).catch((e: unknown) => { if (active && current === generation.current) failure(e); }).finally(() => { if (active && current === generation.current) setLoading(false); });
    const expired = () => { advanceAuthEpoch(); generation.current++; setUser(null); setWorkspaces([]); setSelected(""); };
    window.addEventListener("orba-session-expired", expired);
    return () => { active = false; window.removeEventListener("orba-session-expired", expired); };
  }, [apply, failure]);
  const workspace = workspaces.find((space) => space.id === selected) ?? null;
  function select(id: string) { if (workspaces.some((space) => space.id === id)) { const go=()=>{sessionStorage.setItem("orba-workspace", id); setSelected(id); router.push("/projects");}; if(window.dispatchEvent(new CustomEvent("orba-draft-navigation",{cancelable:true,detail:go})))go(); } }
  async function signout() {
    advanceAuthEpoch();
    generation.current++; setUser(null); setWorkspaces([]); setSelected(""); sessionStorage.removeItem("orba-workspace");
    try { await request<void>("/api/v1/auth/logout", { method: "POST" }); setLogoutWarning(""); router.push("/signin"); }
    catch { setLogoutWarning("Protected content was cleared locally. Server sign-out could not be confirmed. Reconnect and sign in to check your session."); }
  }
  return <Context.Provider value={{ user, workspaces, workspace, loading, error, logoutWarning, refresh, select, signout }}>{children}</Context.Provider>;
}

export function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, workspace, loading, error, refresh } = useSession();
  const path = usePathname();
  const publicPage = ["/signin", "/signup", "/invitations/accept"].includes(path);
  let content = children;
  if (!publicPage) {
    if (loading) content = <div className="state-box" role="status">Checking your session…</div>;
    else if (error) content = <div className="state-box"><h1>Workspace unavailable</h1><p role="alert">{error}</p><Button onClick={() => void refresh()}>Try again</Button></div>;
    else if (!user) content = <div className="state-box"><h1>Sign in to your workspace</h1><p>Your session may have expired. Sign in to continue.</p><Button asChild><Link href="/signin">Sign in</Link></Button><Link href="/signup">Create an account</Link></div>;
    else if (!workspace && !path.startsWith("/workspaces") && path !== "/settings") content = <div className="state-box"><h1>A home for your ideas</h1><p>Create a workspace to start building, or accept a teammate’s invitation.</p><Button asChild><Link href="/workspaces/new">Create workspace</Link></Button></div>;
  }
  // Key clears all protected component state immediately on account/workspace change.
  return <div key={`${user?.id ?? "guest"}:${workspace?.id ?? "none"}:${path}`}>{content}</div>;
}


