"use client";
import { Button } from "@/components/ui/button";
export default function ErrorPage({ reset }: { reset: () => void }) { return <div className="state-box"><h1>Something went wrong</h1><p>Your workspace couldn’t be displayed. Try loading it again.</p><Button onClick={reset}>Try again</Button></div>; }
