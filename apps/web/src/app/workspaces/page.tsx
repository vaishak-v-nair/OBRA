"use client";
import Link from "next/link";
import { useSession } from "@/components/session";
import { Button } from "@/components/ui/button";
export default function Workspaces() {
  const { workspaces, select } = useSession();
  return <div className="page-content"><div className="page-heading"><div><p className="eyebrow">A PLACE TO BUILD TOGETHER</p><h1 className="page-title">Workspaces</h1><p className="page-description">Separate projects, shared purpose. Choose your space.</p></div><Button asChild><Link href="/workspaces/new">Create workspace</Link></Button></div>{!workspaces.length ? <div className="state-box"><h2>Your first workspace awaits</h2><p>Create a space or accept an invitation from your team.</p></div> : <div className="project-grid">{workspaces.map((space) => <section className="project-card" key={space.id}><span className="status-badge">{space.role}</span><h2>{space.name}</h2><div className="workspace-actions"><Button variant="outline" onClick={() => select(space.id)}>Open workspace</Button><Link href={`/workspaces/${space.id}`}>Workspace settings</Link></div></section>)}</div>}</div>;
}
