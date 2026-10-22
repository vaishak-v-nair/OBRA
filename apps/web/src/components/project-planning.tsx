"use client";

import { useState } from "react";
import type { Project } from "@/lib/api";
import { Architecture } from "@/components/architecture";
import { ProductPlan } from "@/components/product-plan";

export function ProjectPlanning({project}:{project:Project}) {
  const [view,setView]=useState<"product"|"architecture"|"graph">("product");
  const [opened,setOpened]=useState(false);
  return <div className="project-planning"><nav className="planning-nav" aria-label="Project planning views">{([['product','Product Plan'],['architecture','Architecture'],['graph','Task Graph']] as const).map(([key,title])=><button key={key} type="button" aria-current={view===key?"page":undefined} onClick={()=>{setView(key);if(key!=="product")setOpened(true);}}>{title}</button>)}</nav><div hidden={view!=="product"}><ProductPlan project={project}/></div>{opened&&<div hidden={view==="product"}><Architecture project={project} view={view==="graph"?"graph":"architecture"} active={view!=="product"} onProductPlan={()=>setView("product")}/></div>}</div>;
}
