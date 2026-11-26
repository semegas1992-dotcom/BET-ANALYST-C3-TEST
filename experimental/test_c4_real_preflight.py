import unittest,json,hashlib,copy
from c4_real_preflight import preflight

class RealPreflightTests(unittest.TestCase):
    def setUp(self):
        self.raw=json.dumps({"event_id":"fixture-1","value":2}).encode()
        self.sha=hashlib.sha256(self.raw).hexdigest()
        self.m={"event_id":"fixture-1","cutoff":"2026-11-26T12:00:00Z","kickoff":"2026-11-26T18:00:00Z","sources":[],"mappings":[{"source_pointer":"/value","target":"goals","type":"integer","unit":"count","record_id":"r1","transformation":"identity","missing_policy":"reject","event_end":"2026-11-25T18:00:00Z","available_at":"2026-11-25T19:00:00Z","captured_at":"2026-11-26T11:00:00Z"}]}
    def test_locked(self):
        out=preflight(self.raw,self.sha,self.m)
        self.assertIs(out["engine_access"],False)
        self.assertEqual(out["qualification"],"BLOCKED")
        self.assertIn("SOURCES_MISSING",out["issues"])
        self.assertNotIn("MAPPING_INVALID",out["issues"])
    def test_integrity(self):
        with self.assertRaises(ValueError):preflight(self.raw,"0"*64,self.m)
    def test_late(self):
        self.m["mappings"][0]["captured_at"]="2026-11-26T13:00:00Z"
        self.assertIn("MAPPING_INVALID",preflight(self.raw,self.sha,self.m)["issues"])
    def test_pointer(self):
        self.m["mappings"][0]["source_pointer"]="/absent"
        self.assertIn("MAPPING_INVALID",preflight(self.raw,self.sha,self.m)["issues"])
    def test_identity(self):
        self.m["event_id"]="other"
        self.assertIn("EVENT_ID_NOT_BOUND",preflight(self.raw,self.sha,self.m)["issues"])
    def test_cutoff(self):
        self.m["kickoff"]=self.m["cutoff"]
        self.assertIn("KICKOFF_OR_CUTOFF_INVALID",preflight(self.raw,self.sha,self.m)["issues"])
    def test_empty(self):
        self.m["mappings"]=[]
        self.assertIn("MAPPING_EMPTY",preflight(self.raw,self.sha,self.m)["issues"])

if __name__=="__main__":unittest.main()
