"use client";
import Link from "next/link";
import { useSession } from "@/components/session";
export default function Settings() { const { user, workspace } = useSession(); return <div className="page-content"><p className="eyebrow">YOUR ACCOUNT</p><h1 className="page-title">Settings</h1><section className="overview-panel"><h2>{user?.display_name}</h2><p className="page-description">{user?.email}</p><p className="form-note">Use the account menu to sign out and revoke this session.</p>{workspace && <Link className="back-link" href={`/workspaces/${workspace.id}`}>Manage {workspace.name}</Link>}</section></div>; }
