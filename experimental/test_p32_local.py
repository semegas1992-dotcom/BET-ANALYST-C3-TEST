import unittest,json,threading
from http.server import ThreadingHTTPServer
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from unittest.mock import patch
from p32_local import Handler
from p32_dynamic import generate_registered
class LocalBridgeTests(unittest.TestCase):
    def test_loopback(self):
        server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        base="http://127.0.0.1:"+str(server.server_port)
        def get(path,host="127.0.0.1:8767"):
            return urlopen(Request(base+path,headers={"Host":host}),timeout=10)
        try:
            with get("/") as r:
                self.assertIn(b"BET ANALYST",r.read())
            with patch("p32_local.generate_registered",wraps=generate_registered) as engine:
                for sport in ("football","nba","tennis"):
                    with get("/report/"+sport) as r:
                        data=json.load(r)
                        self.assertEqual(data["scope"],"DYNAMIC_REGISTERED_SYNTHETIC")
                        self.assertEqual(data["report"]["qualification"],"BLOCKED")
                        self.assertEqual(len(data["report"]["sections"]),7)
                        self.assertEqual(r.headers["Cache-Control"],"no-store")
                self.assertEqual(engine.call_count,3)
            for path,host,code in (("/report/real","127.0.0.1:8767",404),("/","external.example",403)):
                with self.assertRaises(HTTPError) as e:
                    get(path,host)
                self.assertEqual(e.exception.code,code)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
