import unittest
from nba_history import normalize, summarize, stamp

def game(i=1, date="2026-11-20T01:00:00Z", status="Final", x=110, y=100, h=1,a=2):
    return {"id":i,"datetime":date,"status":status,"home_team":{"id":h},"visitor_team":{"id":a},"home_team_score":x,"visitor_team_score":y}

class HistoryTests(unittest.TestCase):
    cutoff=stamp("2026-11-24T05:00:00Z")
    def test_scores(self):
        rows,issues=normalize([game(),game(2,x=90,y=100,h=2,a=1)],1,self.cutoff)
        self.assertFalse(issues)
        s=summarize(rows)
        self.assertEqual(s["season"]["wins"],2)
        self.assertEqual(s["season"]["pf"],105)
        self.assertEqual(s["season"]["margin"],10)
        self.assertEqual(s["away"]["n"],1)
    def test_exclusions(self):
        rows,issues=normalize([game(),game(),game(2,status="Scheduled"),game(3,date="2026-11-25T01:00:00Z"),game(4,x=0),game(5,h=3,a=4),game(6,date="2026-11-24T01:00:00Z")],1,self.cutoff)
        self.assertEqual(len(rows),1)
        self.assertEqual(len(issues),3)
    def test_empty(self):
        self.assertIsNone(summarize([])["season"]["pf"])
    def test_sample(self):
        rows,_=normalize([game(i) for i in range(1,18)],1,self.cutoff)
        self.assertEqual(summarize(rows)["L15"]["n"],15)

if __name__=="__main__": unittest.main()
