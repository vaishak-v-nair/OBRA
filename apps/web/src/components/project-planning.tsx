"use client";

import { useState } from "react";
import type { Project } from "@/lib/api";
import { Architecture } from "@/components/architecture";
import { ProductPlan } from "@/components/product-plan";
import { ExecutionPlan } from "@/components/execution-plan";

export function ProjectPlanning({project}:{project:Project}) {
  const [view,setView]=useState<"product"|"architecture"|"graph"|"execution">("product");
  const [opened,setOpened]=useState(false);
  return <div className="project-planning"><nav className="planning-nav" aria-label="Project planning views">{([['product','Product Plan'],['architecture','Architecture'],['graph','Task Graph'],['execution','Execution Plan']] as const).map(([key,title])=><button key={key} type="button" aria-current={view===key?"page":undefined} onClick={()=>{setView(key);if(key==="architecture"||key==="graph")setOpened(true);}}>{title}</button>)}</nav><div hidden={view!=="product"}><ProductPlan project={project}/></div>{opened&&<div hidden={view==="product"||view==="execution"}><Architecture project={project} view={view==="graph"?"graph":"architecture"} active={view==="architecture"||view==="graph"} onProductPlan={()=>setView("product")}/></div>}{view==="execution"&&<ExecutionPlan project={project} onArchitecture={()=>{setOpened(true);setView("architecture");}}/>}</div>;
}
