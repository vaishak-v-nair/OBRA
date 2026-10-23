"use client";

import { useId, useState } from "react";
import type { RunDetail } from "@/lib/orchestration";

/** Immutable snapshot diagram; the synchronized native task list supports keyboards. */
export function ExecutionGraph({ run }: { run: RunDetail }) {
  const [selected, setSelected] = useState("");
  const marker = useId().replaceAll(":", "");
  const task = run.tasks.find(item => item.key === selected) ?? run.tasks[0];
  const node = run.graph.nodes.find(item => item.key === task?.key);
  const positions = new Map(run.graph.topological_order.map((key, index) => [key, { x: 24 + (index % 2) * 270, y: 24 + Math.floor(index / 2) * 115 }]));
  const choose = (key: string) => setSelected(key);
  return <section aria-label="Orchestration task graph" className="task-graph">
    <h3>Task dependencies and eligibility</h3>
    <p className="form-note">A → B means B waits for A to complete with verified evidence. Eligibility is a dependency fact. No executor is connected.</p>
    <details className="task-diagram" open><summary>Saved dependency diagram</summary><div className="task-svg-scroll"><svg role="img" aria-label="Persisted orchestration dependency graph" viewBox={`0 0 560 ${Math.max(160, Math.ceil(run.tasks.length / 2) * 115 + 20)}`}><defs><marker id={marker} markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="currentColor" /></marker></defs>
      {run.graph.edges.map(edge => { const a = positions.get(edge.prerequisite), b = positions.get(edge.dependent); return a && b ? <path key={`${edge.prerequisite}-${edge.dependent}`} d={`M${a.x + 112} ${a.y + 72} C${a.x + 112} ${a.y + 100},${b.x + 112} ${b.y - 20},${b.x + 112} ${b.y}`} markerEnd={`url(#${marker})`} className="task-edge" /> : null; })}
      {run.tasks.map(item => { const position = positions.get(item.key); return position ? <g key={item.key} transform={`translate(${position.x},${position.y})`} className={item.key === task?.key ? "task-node selected" : "task-node"} onClick={() => choose(item.key)}><rect width="230" height="72" rx="10" /><text x="12" y="24">{item.definition.title.slice(0, 27)}</text><text x="12" y="48" className="task-node-meta">{item.execution_status === "cancelled" ? "Cancelled" : "Not executed"} · {item.definition.priority}</text></g> : null; })}
    </svg></div></details>
    <div className="task-layout"><nav className="task-list" aria-label="Orchestration tasks">{run.tasks.map(item => <button key={item.id} type="button" aria-pressed={task?.id === item.id} onClick={() => choose(item.key)}><strong>{item.definition.title}</strong><span>{item.definition.category} · {item.definition.priority}</span><span>Eligibility: {item.execution_status === "cancelled" ? "not dispatchable (cancelled)" : item.eligibility === "eligible" ? "eligible for future dispatch" : "waiting for prerequisites"}</span><span>Execution: {item.execution_status.replaceAll("_", " ")}</span></button>)}</nav>
      {task && <article className="task-detail" aria-label="Selected orchestration task"><h4>{task.definition.title}</h4><p>{task.definition.description}</p><p><strong>Scope:</strong> {task.definition.scope}</p><p data-testid="task-blocker">{node?.explanation}</p><p>Execution: <strong>{task.execution_status.replaceAll("_", " ")}</strong>. No completion evidence exists.</p><h5>Acceptance criteria</h5><ol>{task.definition.acceptance_criteria.map((text, index) => <li key={index}>{text}</li>)}</ol><h5>Requirement traceability</h5><p>Stories: {task.definition.story_refs.join(", ") || "None"}</p><p>Requirements: {task.definition.requirement_refs.join(", ") || "None"}</p><p>Source criteria: {task.definition.criterion_refs.join(", ") || "None"}</p><h5>Prerequisites</h5><p>{node?.prerequisites.join(", ") || "No prerequisites"}</p><h5>Dependents</h5><p>{node?.dependents.join(", ") || "No direct dependents"}</p><p>Transitive impact: {node?.impact.join(", ") || "None"}</p><p className="form-note">Source task: {task.source_task_id}. Task definitions and dependency edges are immutable run snapshots.</p></article>}
    </div>
  </section>;
}
