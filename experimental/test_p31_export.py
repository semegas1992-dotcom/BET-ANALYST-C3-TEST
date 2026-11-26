import unittest,json
from p31_export import export
class P31Export(unittest.TestCase):
    def test_export(self):
        data=export()
        self.assertEqual(set(data),{"football","nba","tennis"})
        self.assertEqual(data,export())
        for v in data.values():
            self.assertEqual(len(v["report"]["sections"]),7)
            self.assertEqual(v["report"]["qualification"],"BLOCKED")
        print("P31_EXPORT "+json.dumps(data,sort_keys=True,separators=(",",":")),flush=True)
