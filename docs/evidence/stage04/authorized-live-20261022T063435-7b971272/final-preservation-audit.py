"""Final preservation/profile/artifact verification; no external requests."""
import json,os,re,socket,subprocess
from pathlib import Path
from urllib.parse import unquote
from scripts import verification as v
from scripts import architect_verification as stage
from orba.config import Settings
os.environ.update(ORBA_ARCHITECT_MODEL="gemini-3.6-flash",ORBA_ARCHITECT_THINKING_LEVEL="minimal",WEB_CONCURRENCY="1")
folder=v.ROOT/"docs/evidence/stage04/authorized-live-20261022T063435-7b971272"
intake=json.loads(Path("C:/Users/vaish/.gstack/projects/OBRA/stage041/authorized-live/20261022T063435-7b971272/intake.json").read_text(encoding="utf-8"))
current=v.source_manifest()
assert current==intake["source"]
a=stage.validate(stage.latest("A"),"A",current)
b=stage.validate(stage.latest("B"),"B",current)
changed=[name for name,sha in intake["preexisting_evidence"].items() if not(v.ROOT/name).is_file() or v.digest(v.ROOT/name)!=sha]
assert changed==[str(Path("docs/evidence/stage04/latest-B.json"))]
assert all((v.ROOT/name).is_file() and v.digest(v.ROOT/name)==sha for name,sha in intake["credential_file_hashes"].items())
head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=v.ROOT,text=True).strip()
index=subprocess.check_output(["git","diff","--cached","--name-only"],cwd=v.ROOT,text=True)
status=subprocess.check_output(["git","status","--short"],cwd=v.ROOT,text=True)
assert head==intake["git_head"] and not index.strip()
ports={}
for port in (3001,8001):
    with socket.socket() as probe:ports[str(port)]=probe.connect_ex(("127.0.0.1",port))==0
assert not any(ports.values())
links=0
for name in ["README.md","docs/ROADMAP.md","docs/VERIFICATION.md","docs/VERIFICATION_STAGE041_LIVE.md"]:
    path=v.ROOT/name
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)",path.read_text(encoding="utf-8")):
        target=match.group(1).strip("<>").split("#")[0]
        if not target or "://" in target or target.startswith("mailto:"):continue
        dest=(path.parent/unquote(target)).resolve()
        assert dest.exists() or dest==(folder/"final-preservation.json").resolve(),f"Missing document link in {name}"
        links+=1
settings=Settings();values=[]
for config in (settings,settings.architect_settings()):
    secret=config.pm_api_key
    if secret:
        token=secret.get_secret_value() if hasattr(secret,"get_secret_value") else str(secret)
        if len(token)>=16:values.append(token.encode())
newfiles=[path for path in (v.ROOT/"docs/evidence").rglob("*") if path.is_file() and str(path.relative_to(v.ROOT)) not in intake["preexisting_evidence"] and path.name!="gate.lock"]
newfiles += [v.ROOT/name for name in ["README.md","docs/ROADMAP.md","docs/VERIFICATION.md","docs/VERIFICATION_STAGE041_LIVE.md"]]
assert not any(token in path.read_bytes() for token in values for path in newfiles),"Credential value detected in new public documentation/evidence"
value={"result":"PASS","recorded_at":v.utc(),"source_sha256":current["sha256"],"source_file_count":len(current["files"]),"source_unchanged":True,"gate_a_revalidated":"PASS","gate_b_revalidated":"PASS","gate_a_receipt_sha256":v.digest(stage.latest("A")),"gate_b_receipt_sha256":v.digest(stage.latest("B")),"preexisting_evidence_files":len(intake["preexisting_evidence"]),"immutable_evidence_files_unchanged":len(intake["preexisting_evidence"])-len(changed),"only_advanced_control_pointer":changed,"runtime_gate_lock_excluded":True,"credential_files_unchanged":True,"resolved_credential_value_scan":"PASS","new_evidence_and_docs_scanned":len(newfiles),"implementation_changed":False,"git_head":head,"git_index_empty":True,"working_tree_status_entries":len(status.splitlines()),"working_tree_status":status,"service_ports_in_use":ports,"local_document_links_valid":links,"generation_request_count":1,"automatic_retries":0,"authorization_consumed":True,"stage05_started":False,"documentation_scope":["README.md","docs/ROADMAP.md","docs/VERIFICATION.md","docs/VERIFICATION_STAGE041_LIVE.md"],"documentation_sha256":{name:v.digest(v.ROOT/name) for name in ["README.md","docs/ROADMAP.md","docs/VERIFICATION.md","docs/VERIFICATION_STAGE041_LIVE.md"]},"learning":"Keep C's recorded model/thinking overrides when recalculating strict profile-bound verdicts; readiness metadata and unpaid preflight alone are not live proof."}
v.write_new(folder/"final-preservation.json",value)
assert (folder/"final-preservation.json").is_file()
print(json.dumps({key:val for key,val in value.items() if key!="working_tree_status"},indent=2))
