import Link from "next/link";
export default function NotFound() { return <div className="state-box"><h1>Page not found</h1><p>This page doesn’t exist in your workspace.</p><Link href="/" className="back-link">Return to Chat</Link></div>; }
