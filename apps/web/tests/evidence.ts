import { mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { randomUUID } from "node:crypto";

const directory = process.env.ORBA_TEST_EVIDENCE_DIR ?? resolve("../../docs/evidence/manual", `${Date.now()}-${randomUUID()}`);
export function evidencePath(name:string) {
  mkdirSync(directory,{recursive:true});
  return resolve(directory,name);
}
