import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Layers3 } from "lucide-react";
const sections: Record<string, string> = { skills: "Skills", contribute: "Contribute", workspaces: "Workspaces", activity: "Activity", settings: "Settings" };
export default async function Later({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  const title = sections[section];
  if (!title) notFound();
  return <div className="page-content"><p className="eyebrow">THE WORKSPACE IS TAKING SHAPE</p><h1 className="page-title">{title}</h1><div className="state-box"><Layers3 size={36} strokeWidth={1.3} /><h2>Coming in a later stage</h2><p>This area is planned. No services are connected here yet.</p><Link href="/" className="back-link"><ArrowLeft size={16} /> Back to Chat</Link></div></div>;
}
