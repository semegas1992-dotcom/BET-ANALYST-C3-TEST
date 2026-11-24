import unittest
from nba_history import normalize, summarize, stamp, collect
from unittest.mock import patch, MagicMock
import json
from urllib.error import HTTPError, URLError
from nba_history import request_json

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

    def test_opponent_total(self):
        g=game()
        g["visitor_team"]["full_name"]="Opponent"
        rows,_=normalize([g],1,self.cutoff)
        self.assertEqual(rows[0]["opponent_id"],2)
        self.assertEqual(rows[0]["opponent_name"],"Opponent")
        self.assertEqual(summarize(rows)["season"]["total"],210)
    def test_accounting(self):
        exclusions=[]
        rows,issues=normalize([game(),game(),game(2,status="Scheduled"),game(3,date="2026-11-24T01:00:00Z")],1,self.cutoff,exclusions)
        self.assertEqual(len(rows)+len(issues)+len(exclusions),4)
        self.assertEqual([x["reason"] for x in exclusions],["not_final","same_utc_day"])
    def test_wrong_season(self):
        g=game(); g["season"]=2025
        rows,issues=normalize([g],1,self.cutoff,season=2026)
        self.assertFalse(rows)
        self.assertEqual(issues[0]["reason"],"season mismatch")
    def test_utc(self):
        self.assertEqual(stamp("2026-11-24T01:00:00+02:00").isoformat(),"2026-11-23T23:00:00+00:00")
    @patch("nba_history.time.sleep")
    @patch("nba_history.urllib.request.urlopen")
    def test_pagination(self, urlopen, sleep):
        pages=[{"data":[game()],"meta":{"next_cursor":2}},{"data":[game(2)],"meta":{}}]
        responses=[]
        for page in pages:
            response=MagicMock()
            response.__enter__.return_value.read.return_value=json.dumps(page)
            responses.append(response)
        urlopen.side_effect=responses
        trace=[]
        self.assertEqual(len(collect(1,2026,self.cutoff,"test",trace)),2)
        self.assertEqual(len(trace),2)
        self.assertEqual(len(trace[0]["sha256"]),64)
        self.assertIsNone(trace[-1]["next_cursor"])
    @patch("nba_history.time.sleep")
    @patch("nba_history.urllib.request.urlopen")
    def test_cursor_loop(self, urlopen, sleep):
        urlopen.return_value.__enter__.return_value.read.return_value=json.dumps({"data":[],"meta":{"next_cursor":2}})
        with self.assertRaisesRegex(ValueError,"pagination loop"):
            collect(1,2026,self.cutoff,"test")

    @patch("nba_history.time.sleep")
    @patch("nba_history.urllib.request.urlopen")
    def test_retry_429(self, urlopen, sleep):
        response=MagicMock()
        response.__enter__.return_value.read.return_value='{"data":[]}'
        urlopen.side_effect=[HTTPError("https://example.com",429,"limit",{"Retry-After":"75"},None),response]
        events=[]
        self.assertEqual(request_json("https://example.com","test",events),{"data":[]})
        sleep.assert_called_once_with(75)
        self.assertEqual(events[0]["http_code"],429)
    @patch("nba_history.time.sleep")
    @patch("nba_history.urllib.request.urlopen")
    def test_no_retry_401(self, urlopen, sleep):
        urlopen.side_effect=HTTPError("https://example.com",401,"auth",{},None)
        with self.assertRaises(HTTPError): request_json("https://example.com","test")
        self.assertEqual(urlopen.call_count,1)
        sleep.assert_not_called()
    @patch("nba_history.time.sleep")
    @patch("nba_history.urllib.request.urlopen")
    def test_retry_exhausted(self, urlopen, sleep):
        urlopen.side_effect=HTTPError("https://example.com",503,"unavailable",{},None)
        events=[]
        with self.assertRaises(HTTPError): request_json("https://example.com","test",events)
        self.assertEqual(urlopen.call_count,3)
        self.assertEqual([x["delay_seconds"] for x in events],[15,30,None])
    @patch("nba_history.time.sleep")
    @patch("nba_history.urllib.request.urlopen")
    def test_network_retry(self, urlopen, sleep):
        response=MagicMock()
        response.__enter__.return_value.read.return_value='{}'
        urlopen.side_effect=[URLError("temporary"),response]
        self.assertEqual(request_json("https://example.com","test"),{})
        sleep.assert_called_once_with(15)
    @patch("nba_history.time.sleep")
    @patch("nba_history.urllib.request.urlopen")
    def test_long_retry_after_stops(self, urlopen, sleep):
        urlopen.side_effect=HTTPError("https://example.com",429,"limit",{"Retry-After":"300"},None)
        with self.assertRaises(HTTPError): request_json("https://example.com","test")
        sleep.assert_not_called()

if __name__=="__main__": unittest.main()


