const {test}=require("node:test"),assert=require("node:assert/strict"),{inspectArchive,parseStrict}=require("./archive-import.js"),{hash}=require("./native-import.js");
test("duplicate keys",()=>assert.throws(()=>parseStrict('{"a":1,"a":2}')));
test("prototype",()=>assert.throws(()=>parseStrict('{"__proto__":1}')));
test("nonfinite",()=>assert.throws(()=>parseStrict('1e999')));
test("byte hash decimal distinction",async()=>assert.notEqual(await hash('{"x":1.0}'),await hash('{"x":1}')));
test("missing expected",async()=>await assert.rejects(inspectArchive('{}')));
test("corruption",async()=>await assert.rejects(inspectArchive('{}',await hash('{ }'))));
test("unknown schema",async()=>await assert.rejects(inspectArchive('{}',await hash('{}'))));
