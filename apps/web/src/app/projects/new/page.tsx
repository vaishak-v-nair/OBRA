import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { ProjectForm } from "@/components/project-form";
export default function NewProject() { return <div className="page-content narrow"><Link href="/projects" className="back-link"><ArrowLeft size={16} /> All projects</Link><p className="eyebrow">MAKE ROOM FOR YOUR NEXT IDEA</p><h1 className="page-title">Create a project</h1><p className="page-description">A name, an idea, and a place to begin.</p><ProjectForm compact /></div>; }
