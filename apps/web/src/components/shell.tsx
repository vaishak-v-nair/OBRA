"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTheme } from "next-themes";
import { Activity, ArrowUpRight, Blocks, ChevronRight, FolderKanban, GitPullRequest, Menu, MessageSquare, Moon, PanelLeftClose, Plus, Settings2, Sun, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { AuthGate, useSession } from "@/components/session";

const links = [
  { name: "Chat", href: "/", icon: MessageSquare },
  { name: "Projects", href: "/projects", icon: FolderKanban },
  { name: "Skills", href: "/skills", icon: Blocks },
  { name: "Contribute", href: "/contribute", icon: GitPullRequest },
  { name: "Workspaces", href: "/workspaces", icon: PanelLeftClose },
  { name: "Activity", href: "/activity", icon: Activity },
];
export function Shell({ children }: { children: React.ReactNode }) {
  const { user, workspace, workspaces, select, signout, logoutWarning } = useSession();
  const [accountError, setAccountError] = useState("");
  const path = usePathname();
  const { resolvedTheme, setTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const sidebarRef = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!open) return;
    const previous = document.activeElement as HTMLElement | null;
    const controls = () => Array.from(sidebarRef.current?.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), select:not([disabled]), input:not([disabled]), textarea:not([disabled]), summary, [tabindex="0"]') ?? []).filter((el) => el.getClientRects().length > 0 && el.checkVisibility());
    controls()[0]?.focus();
    function keydown(event: KeyboardEvent) {
      if (event.key === "Escape") { event.preventDefault(); setOpen(false); }
      if (event.key === "Tab") {
        const items = controls();
        if (event.shiftKey && document.activeElement === items[0]) { event.preventDefault(); items.at(-1)?.focus(); }
        else if (!event.shiftKey && document.activeElement === items.at(-1)) { event.preventDefault(); items[0]?.focus(); }
      }
    }
    document.addEventListener("keydown", keydown);
    return () => { document.removeEventListener("keydown", keydown); previous?.focus(); };
  }, [open]);
  const current = links.find((item) => item.href === "/" ? path === "/" : path.startsWith(item.href))?.name ?? "Settings";
  return <div className="app-shell">
    <a href="#main" className="skip-link">Skip to content</a>
    {open && <button className="mobile-backdrop" aria-label="Close navigation" onClick={() => setOpen(false)} />}
    <aside ref={sidebarRef} id="sidebar" className={cn("sidebar", open && "is-open")} role={open ? "dialog" : undefined} aria-modal={open ? true : undefined} aria-label="Workspace navigation">
      <div className="brand-row"><Link href="/" className="brand" onClick={() => setOpen(false)}><span className="brand-mark" aria-hidden="true">o</span>orba<span className="brand-period">.</span></Link><Button variant="ghost" size="icon" className="mobile-only" aria-label="Close navigation" onClick={() => setOpen(false)}><X /></Button></div>
      <div className="workspace-label"><span className="workspace-avatar">{workspace?.name[0] ?? "O"}</span><div className="workspace-choice"><label htmlFor="workspace-select">Workspace</label><select id="workspace-select" value={workspace?.id ?? ""} onChange={(event) => { select(event.target.value); setOpen(false); }} disabled={!workspaces.length}><option value="" disabled>Select workspace</option>{workspaces.map((space) => <option value={space.id} key={space.id}>{space.name}</option>)}</select></div></div>
      {workspace && workspace.role !== "viewer" && <Button asChild className="new-project"><Link href="/projects/new" onClick={() => setOpen(false)}><Plus /> New project</Link></Button>}
      <p className="nav-caption">WORKSPACE</p>
      <nav aria-label="Main navigation">{links.map(({ name, href, icon: Icon }) => {
        const active = href === "/" ? path === "/" : path.startsWith(href);
        return <Link key={name} href={href} onClick={() => setOpen(false)} aria-current={active ? "page" : undefined} className={cn("nav-link", active && "active")}><Icon size={18} /><span>{name}</span>{active && <ChevronRight size={14} className="nav-chevron" />}</Link>;
      })}</nav>
      <div className="sidebar-bottom"><div className="foundation-note"><span className="tiny-label">A PLACE TO BEGIN</span><p>Big ideas start<br />with a little space.</p><ArrowUpRight size={18} aria-hidden="true" /></div><Link className={cn("nav-link", path === "/settings" && "active")} href="/settings" onClick={() => setOpen(false)} aria-current={path === "/settings" ? "page" : undefined}><Settings2 size={18} />Settings</Link><div className="profile-row"><span className="workspace-avatar">{user?.display_name[0] ?? "O"}</span>{user ? <details className="account-menu"><summary>Account · {user.display_name}</summary><p>{user.email}</p><Button variant="outline" onClick={async () => { try { await signout(); setOpen(false); } catch(e) { setAccountError(e instanceof Error ? e.message : "Could not sign out."); } }}>Sign out</Button>{accountError && <p role="alert">{accountError}</p>}</details> : <Link href="/signin">Sign in</Link>}</div></div>
    </aside>
    <div className="main-column" inert={open}><header className="topbar"><div className="breadcrumb"><Button variant="ghost" size="icon" className="mobile-only" aria-label="Open navigation" aria-expanded={open} aria-controls="sidebar" onClick={() => setOpen(true)}><Menu /></Button><span>Workspace</span><ChevronRight size={14} /><strong>{current}</strong></div><div className="topbar-actions"><span className="local-label">Product planning</span><Button variant="ghost" size="icon" aria-label="Toggle color theme" onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}><Sun className="dark:hidden" /><Moon className="hidden dark:block" /></Button></div></header>
      <main id="main" tabIndex={-1}>{logoutWarning && <p role="alert" className="error-message">{logoutWarning}</p>}<AuthGate>{children}</AuthGate></main><footer className="app-footer"><span>Built for the way you think.</span><span>Local development workspace</span></footer></div>
  </div>;
}





