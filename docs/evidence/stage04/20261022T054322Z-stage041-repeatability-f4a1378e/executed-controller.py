"""Fixed-size unpaid execution controller. No model/readiness command exists here."""
import json
from datetime import datetime, UTC
from pathlib import Path
from uuid import uuid4
from scripts import verification as v
from scripts import architect_verification as stage
from scripts.architect_preflight import preflight_result

stage.validate(stage.latest("A"), "A")
source = v.source_manifest()
assert source["sha256"] == "f6a3a687995bf53c8ad553a0bc7be2e59d1c1144acc2e7e5f39ced2b700a54cb"
root = stage.EVIDENCE / (datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-stage041-repeatability-" + uuid4().hex[:8])
root.mkdir()
(root/"executed-controller.py").write_bytes(Path(__file__).read_bytes())
value = {"stage":"stage04.1", "execution_class":"fixed_five_no_generation_preflights", "paid_authorized":False, "started_at":v.utc(), "source_start":source, "gate_a_receipt":str(stage.latest("A")), "gate_a_sha256":v.digest(stage.latest("A")), "commands":[], "preflight_receipts":[], "result":"FAIL"}
env = v.deterministic_env()
exit_code = 1
try:
    for name, argv, deadline in [
        ("standalone-navigation", ["pwsh","-NoProfile","-File","scripts/verify-architect-preflight.ps1","-Mode","navigation"],1100),
        ("isolated-false-success", v.UV+["python","-m","scripts.architect_false_success"],180),
    ]:
        row=v.run_command(name,argv,v.ROOT,env,root/(name+".log"),deadline)
        value["commands"].append(row)
        if row["exit_code"]:raise v.EvidenceError(name+" failed; inspect original log before another verification.")
    for index in range(1,6):
        before=set(stage.EVIDENCE.glob("*-unpaid-preflight-*/receipt.json"))
        name="clean-preflight-"+str(index)
        row=v.run_command(name,["pwsh","-NoProfile","-File","scripts/verify-architect-preflight.ps1"],v.ROOT,env,root/(name+".log"),240)
        value["commands"].append(row)
        created=set(stage.EVIDENCE.glob("*-unpaid-preflight-*/receipt.json"))-before
        item={"attempt":index,"exit_code":row["exit_code"],"result":"FAIL"}
        if len(created)==1:
            path=created.pop();receipt=json.loads(path.read_text(encoding="utf-8"));item.update(receipt=str(path),sha256=v.digest(path))
            if row["exit_code"]==0 and receipt["result"]=="PASS":
                assert receipt["source_start"]==receipt["source_end"]==source
                for file,sha in receipt["artifacts"].items():assert v.digest(path.parent/file)==sha
                proof=preflight_result(path.parent)["preflight"]
                item.update(result="PASS",project_id=proof["project_id"],workspace_id=proof["workspace_id"],actor_id=proof["actor_id"],plan_id=proof["source_plan_id"],version=proof["source_version"],revision=proof["source_revision"],source_hash=proof["source_hash"],generation_budget=proof["generation_budget"])
        value["preflight_receipts"].append(item)
    items=value["preflight_receipts"]
    assert len(items)==5 and all(item["result"]=="PASS" for item in items)
    for key in ("project_id","workspace_id","actor_id","plan_id"):assert len({item[key] for item in items})==5
    assert v.source_manifest()==source
    value["result"]="PASS";exit_code=0
except (ValueError,AssertionError,OSError,KeyError,TypeError) as error:
    value["reason"]=str(error) if isinstance(error,v.EvidenceError) else type(error).__name__
finally:
    value.update(completed_at=v.utc(),exit_code=exit_code,source_end=v.source_manifest(),real_provider_generation_requests=0)
    value["artifacts"]={p.name:v.digest(p) for p in root.iterdir() if p.is_file()}
    v.write_new(root/"receipt.json",value)
    print(json.dumps({"result":value["result"],"exit_code":exit_code,"receipt":str(root/"receipt.json"),"preflight_attempts":len(value["preflight_receipts"])}),flush=True)
raise SystemExit(exit_code)
