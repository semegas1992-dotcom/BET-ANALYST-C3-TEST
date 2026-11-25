const {test}=require("node:test"),a=require("node:assert/strict"),m=require("./preview-backup.js");
test("duplicate backup keys refused",()=>a.throws(()=>m.decode('{"schema":"QUARANTINE_PREVIEW_BACKUP_V1","previews":[],"previews":[]}')));
test("prototype key refused",()=>a.throws(()=>m.decode('{"schema":"QUARANTINE_PREVIEW_BACKUP_V1","previews":[],"__proto__":{}}')));
