import json, os, sys
from scripts import verification as v
from scripts import architect_verification as stage
folder=v.ROOT / "docs/evidence/stage04/authorized-live-20261022T063435-7b971272"
expected="f6a3a687995bf53c8ad553a0bc7be2e59d1c1144acc2e7e5f39ced2b700a54cb"
assert v.source_manifest()["sha256"]==expected
v.write_new(folder/"execution-started.json", {"started_at":v.utc(), "one_shot":True,"authorization_consumed_on_termination":True,"maximum_model_generation_requests":1})
env=dict(os.environ)
env.update(ORBA_ARCHITECT_MODEL="gemini-3.6-flash",ORBA_ARCHITECT_THINKING_LEVEL="minimal",WEB_CONCURRENCY="1",PYTHONIOENCODING="utf-8")
rows=[]
exit_code=1
try:
    infra=v.run_command("database",["docker","compose","-f","infra/compose.yaml","--profile","test","up","-d","--wait","test-postgres"],v.ROOT,env,folder/"database.log",90)
    rows.append(infra)
    if infra["exit_code"]:
        exit_code=infra["exit_code"]
    else:
        live=v.run_command("authorized-architect-live",["pwsh","-NoProfile","-File","scripts/verify-architect-live.ps1","-AllowPaid"],v.ROOT,env,folder/"authorized-architect-live.log",800)
        rows.append(live)
        exit_code=live["exit_code"]
finally:
    v.write_new(folder/"execution-receipt.json",{"completed_at":v.utc(),"commands":rows,"actual_exit_code":exit_code,"source_after":v.source_manifest(),"authorization_consumed":True,"automatic_retry_commands":0,"artifacts":{p.name:v.digest(p) for p in folder.iterdir() if p.is_file()}})
sys.exit(exit_code)
