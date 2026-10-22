"""Post-attempt read-only independent SQL audit. No model calls or mutations."""
import json
from uuid import UUID
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from scripts import verification as v
from scripts.prepare_tests import TEST_URL
from scripts.test_database import guard_test_url
from orba.db import make_engine
from orba.architect_models import ArchitectRun, ArchitectureVersion, ArchitectureComponent, EngineeringTask, TaskDependency, RequirementTrace
from orba.pm_models import ProductPlan, ProductManagerRun
from orba.architect_repository import read_document, document_hash
from orba.pm_repository import read_document as source_document, content_hash as source_hash
from orba.architect_traceability import coverage
from orba.task_graph import analyze
folder=v.ROOT/"docs/evidence/stage04/authorized-live-20261022T063435-7b971272"
proof=json.loads((v.ROOT/"docs/evidence/stage04/20261022T063526Z-B-ee98c2e7/live-proof.json").read_text(encoding="utf-8"))
guard_test_url(TEST_URL)
engine=make_engine(TEST_URL)
try:
    with engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        with connection.begin():
            connection.execute(text("SET TRANSACTION READ ONLY"))
            with Session(bind=connection) as db:
                run=db.get(ArchitectRun,UUID(proof["run_id"]))
                artifact=db.get(ArchitectureVersion,UUID(proof["architecture_id"]))
                plan=db.get(ProductPlan,UUID(proof["source_plan_id"]))
                assert run.status=="succeeded" and run.error_category is None
                assert artifact.state=="approved" and artifact.approved_at and str(artifact.approved_by)==proof["initiator_id"]
                assert (artifact.version,artifact.revision)==(1,2)
                assert (run.project_id,run.workspace_id)==(artifact.project_id,UUID(proof["preflight"]["workspace_id"]))
                assert (run.source_plan_id,run.source_version,run.source_revision,run.source_hash)==(plan.id,plan.version,plan.revision,plan.content_hash)
                assert (artifact.source_plan_id,artifact.source_version,artifact.source_revision,artifact.source_hash)==(plan.id,1,1,proof["source_hash"])
                assert plan.state=="approved" and str(plan.approved_by)==proof["initiator_id"] and plan.approved_at
                document=read_document(db,artifact)
                source=source_document(db,plan)
                assert source_hash(source)==plan.content_hash
                assert document_hash(document)==artifact.content_hash==proof["approved_api_hash"]
                graph=analyze(document.tasks)
                assert graph==analyze(document.tasks)
                assert graph["valid"] and graph["execution_performed"] is False
                positions={key:index for index,key in enumerate(graph["topological_order"])}
                assert all(positions[edge["prerequisite"]]<positions[edge["dependent"]] for edge in graph["edges"])
                report=coverage(document,source)
                assert report["approvable"] and not report["unaccounted_gaps"]
                assert all(item.planning_state in {"proposed","needs_clarification"} for item in document.tasks)
                assert all(item.status=="proposed" for item in document.api_design.endpoints)
                counts={model.__tablename__:db.scalar(select(func.count()).select_from(model).where(model.architecture_id==artifact.id)) for model in [ArchitectureComponent,EngineeringTask,TaskDependency,RequirementTrace]}
                assert counts==proof["approved_sql"]["counts"]
                total_runs=db.scalar(select(func.count()).select_from(ArchitectRun))
                pm_runs=db.scalar(select(func.count()).select_from(ProductManagerRun))
                assert total_runs==1 and pm_runs==0
                value={"result":"PASS","checked_at":v.utc(),"transaction_read_only":db.scalar(text("SHOW transaction_read_only")),"isolation_level":db.scalar(text("SHOW transaction_isolation")),"run_id":str(run.id),"run_status":run.status,"architecture_id":str(artifact.id),"workspace_id":str(run.workspace_id),"source_plan_id":str(plan.id),"source_version":plan.version,"source_revision":plan.revision,"source_hash":plan.content_hash,"source_approved_by":str(plan.approved_by),"source_approved_at":str(plan.approved_at),"state":artifact.state,"version":artifact.version,"revision":artifact.revision,"approved_by":str(artifact.approved_by),"approved_at":str(artifact.approved_at),"content_hash":artifact.content_hash,"counts":counts,"total_architect_runs":total_runs,"total_pm_runs":pm_runs,"proposed_sections":{"technology_decisions":len(document.technologies),"components":len(document.components),"database_entities":len(document.database_design.entities),"api_endpoints":len(document.api_design.endpoints),"security_threats":len(document.security.threats),"risks":len(document.risks),"open_decisions":len(document.open_decisions)},"graph":graph,"coverage":report,"planning_states":{task.key:task.planning_state for task in document.tasks},"architecture_schema_validated":True,"source_hash_validated":True,"execution_performed":False,"generation_requests_dispatched_by_audit":0}
                v.write_new(folder/"independent-sql.json",value)
                print(json.dumps(value,default=str))
finally:
    engine.dispose()
