#!/usr/bin/env python
# -*- coding: utf-8 -*-"
# vim: set expandtab tabstop=4 shiftwidth=4:
"""
This file is part of the XSSer project, https://xsser.03c8.net

Copyright (c) 2010/2026 | psy <epsylon@riseup.net>

xsser is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation version 3 of the License.

xsser is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along
with xsser; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os, sys, unittest, tempfile, subprocess, threading, http.server, datetime, json
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

class TestImports(unittest.TestCase):
    def test_core_modules(self):
        import core.main, core.options, core.dork, core.encdec, core.curlcontrol
        import core.crawler, core.imagexss, core.update, core._ensure, core.threadpool
    def test_fuzzing(self):
        import core.fuzzing.vectors, core.fuzzing.DCP, core.fuzzing.DOM
        import core.fuzzing.HTTPsr, core.fuzzing.heuristic
    def test_exporters(self):
        import core.post.xml_exporter, core.post.pdf_exporter

class TestOptions(unittest.TestCase):
    def setUp(self):
        from core.options import XSSerOptions
        self.o = XSSerOptions()
    def test_version(self):
        self.assertIn('1.9', self.o.version)
        self.assertIn('Bl4ck Swarm', self.o.version)
    def test_total_vectors(self):
        self.assertGreaterEqual(int(self.o.total_vectors), 1515)
    def test_parse_many_options(self):
        args = ["-u", "http://127.0.0.1/a?q=XSS", "--auto", "--Cloudflare", "--Wordfence",
                "--Dou", "--Cas", "--Uni", "--Coo", "--Xsa", "--Xsr", "--Dom", "--Dcp",
                "--pdf", "r.pdf", "--xml", "r.xml", "--save", "--Fp", "alert(1)",
                "--auth-type", "basic", "--auth-cred", "u:p", "--auth-cert", "k,c",
                "--threads", "3", "--Hex", "--reverse-check", "--statistics", "--heuristic",
                "--Anchor", "--B64", "--Ifr", "--Onm", "--Dos"]
        opts = self.o.get_options(args)
        self.assertTrue(opts)
        self.assertEqual(opts.url, "http://127.0.0.1/a?q=XSS")
        self.assertTrue(opts.cloudflare)
        self.assertTrue(opts.wordfence)
        self.assertTrue(opts.Dou)
        self.assertTrue(opts.reversecheck)
        self.assertEqual(opts.acert, "k,c")
        self.assertEqual(opts.filepdf, "r.pdf")
    def test_dorking_engine_option(self):
        opts = self.o.get_options(["-d", "news.php?id=", "--De", "ecosia"])
        self.assertEqual(opts.dork_engine, "ecosia")

class TestEncoders(unittest.TestCase):
    def setUp(self):
        from core.encdec import EncoderDecoder
        self.e = EncoderDecoder()
    def test_legacy_encoders(self):
        self.assertEqual(self.e._hexEncode("A"), "%41")
        self.assertEqual(self.e._decEncode("A"), "&#65")
        self.assertEqual(self.e._fromCharCodeEncode("AB"), "65,66")
    def test_new_encoders(self):
        self.assertEqual(self.e._doubleUrlEncode("<"), "%253C")
        self.assertIn("&lt;", self.e._htmlEntityEncode("<svg>"))
        self.assertEqual(self.e._mixedCaseEncode("abcd"), "AbCd")
        self.assertEqual(self.e._jsUnicodeEncode("A"), "\\u0041")
        self.assertEqual(self.e._jsHexEncode("A"), "\\x41")
        self.assertEqual(self.e._jsOctalEncode("A"), "\\101")
    def test_encmap_keys(self):
        for k in ["Str", "Hex", "Hes", "Une", "Dec", "Mix", "Dou", "Ent", "Cas", "Uni", "Xhx", "Ocb"]:
            self.assertIn(k, self.e.encmap)
            self.assertTrue(callable(self.e.encmap[k]))

class TestVectors(unittest.TestCase):
    def test_counts(self):
        import core.fuzzing.vectors as v, core.fuzzing.DCP as d
        import core.fuzzing.DOM as m, core.fuzzing.HTTPsr as h, core.fuzzing.heuristic as e
        self.assertGreaterEqual(len(v.vectors), 1450)
        self.assertGreaterEqual(len(d.DCPvectors), 22)
        self.assertGreaterEqual(len(m.DOMvectors), 27)
        self.assertGreaterEqual(len(h.HTTPrs_vectors), 16)
        self.assertGreaterEqual(len(e.heuristic_test), 41)
    def test_dicts_wellformed(self):
        import core.fuzzing.vectors as v
        for x in v.vectors:
            self.assertIn('payload', x)
            self.assertIn('browser', x)
    def test_modern_vectors_present(self):
        import core.fuzzing.vectors as v
        payloads = [x['payload'] for x in v.vectors]
        self.assertIn("<details open ontoggle=PAYLOAD>test</details>", payloads)
        self.assertIn("{{$eval.constructor('PAYLOAD')()}}", payloads)

class TestImageXSS(unittest.TestCase):
    def test_all_formats(self):
        from core.imagexss import ImageInjections
        inj = ImageInjections('')
        sigs = {'svg': b'<?xml', 'gif': b'GIF89a', 'png': b'\x89PNG', 'jpg': b'\xff\xd8'}
        for ext, sig in sigs.items():
            fn = tempfile.mktemp(suffix='.' + ext)
            inj.image_xss(fn, "alert(1)")
            with open(fn, 'rb') as f:
                data = f.read()
            self.assertTrue(data.startswith(sig), ext)
            os.remove(fn)

class TestExporters(unittest.TestCase):
    def _fake(self):
        class O:
            url = "http://127.0.0.1/a?q=XSS"; target = None; dork = None; readfile = None
            statistics = True; onm = ifr = b64 = dos = doss = finalremote = finalpayload = False
        class F:
            options = O(); special_vector_type = None; time = datetime.datetime.now()
            success_connection = 1; not_connection = 0; forwarded_connection = 0; other_connection = 0
            hash_found = [('"><svg onload=alert(1)>', '[HTML5]', 'url', 'h', 'p', 'x', 'http://127.0.0.1/a?q=XSS')]
            hash_notfound = []
            def apply_postprocessing(self, *a):
                return "http://127.0.0.1/final"
        return F()
    def test_xml(self):
        from core.post.xml_exporter import xml_reporting
        import xml.etree.ElementTree as ET
        fn = tempfile.mktemp(suffix='.xml')
        xml_reporting(self._fake()).print_xml_results(fn)
        ET.parse(fn)
        os.remove(fn)
    def test_pdf(self):
        from core.post.pdf_exporter import pdf_reporting
        fn = tempfile.mktemp(suffix='.pdf')
        pdf_reporting(self._fake()).print_pdf_results(fn)
        with open(fn, 'rb') as f:
            self.assertEqual(f.read(4), b'%PDF')
        os.remove(fn)

class TestDorker(unittest.TestCase):
    def test_engines(self):
        from core.dork import Dorker
        self.assertEqual(Dorker('duck').search_engines,
                         ['bing', 'duck', 'brave', 'mojeek', 'yahoo', 'startpage', 'ecosia'])
    def test_query_string(self):
        from core.dork import Dorker
        sep, q = Dorker('duck')._query_string("news.php?id=")
        self.assertIn('instreamset', q)
        self.assertIn('news.php?id=', q)

class TestCurl(unittest.TestCase):
    def test_instantiate(self):
        from core.curlcontrol import Curl
        self.assertIsNotNone(Curl())
    def test_acert_attr(self):
        from core.curlcontrol import Curl
        self.assertTrue(hasattr(Curl, 'acert'))
    def test_no_weak_tls(self):
        src = open(os.path.join(ROOT, "core", "curlcontrol.py")).read()
        self.assertNotIn("SSLVERSION_SSLv2", src)
        self.assertNotIn("SSLVERSION_SSLv3", src)

class TestCrawler(unittest.TestCase):
    def test_form_extraction(self):
        from core.crawler import Crawler
        class FP:
            _landing = False; crawled_urls = []; _reporters = []
        c = Crawler(FP())
        c._max = 1000; c._depth = 3; c._path = "http://t/"; c.verbose = 0
        html = '<a href="/p.php?id=1">x</a><form action="/s.php"><input name="q" value="v"></form>'
        c._get_done("http://t", 3, 0, "http://t/", html, "text/html; charset=utf-8")
        urls = FP.crawled_urls
        self.assertTrue(any('p.php?id=XSS' in u for u in urls))
        self.assertTrue(any('s.php' in u and 'q=XSS' in u for u in urls))

class TestReverseCheck(unittest.TestCase):
    def test_option(self):
        from core.options import XSSerOptions
        opts = XSSerOptions().get_options(["--reverse-check", "-u", "http://127.0.0.1"])
        self.assertTrue(opts.reversecheck)
    def test_hub_machinery(self):
        from core.tokenhub import HubThread
        from core.reporter import XSSerReporter
        self.assertTrue(HubThread)
        self.assertTrue(XSSerReporter)

class TestIntegration(unittest.TestCase):
    def test_end_to_end_reflected_xss(self):
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                q = parse_qs(urlparse(self.path).query)
                r = "".join(v[0] for v in q.values())
                b = ("<html><body>Q: " + r + "</body></html>").encode('utf-8', 'replace')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', str(len(b)))
                self.end_headers()
                self.wfile.write(b)
            def log_message(self, *a):
                pass
        srv = http.server.HTTPServer(('127.0.0.1', 0), H)
        port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            r = subprocess.run([sys.executable, "xsser", "-u", "http://127.0.0.1:%d/?q=XSS" % port,
                                "--auto", "--auto-set", "10", "--threads", "6", "--timeout", "8"],
                               cwd=ROOT, capture_output=True, text=True, timeout=150)
            out = r.stdout + r.stderr
        finally:
            srv.shutdown()
        self.assertIn("Vulnerable", out)

class TestCookieInjection(unittest.TestCase):
    def test_coo_header_injection(self):
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                cookie = self.headers.get("Cookie", "")
                b = ("<html><body>Session: " + cookie + "</body></html>").encode('utf-8', 'replace')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', str(len(b)))
                self.end_headers()
                self.wfile.write(b)
            def log_message(self, *a):
                pass
        srv = http.server.HTTPServer(('127.0.0.1', 0), H)
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            r = subprocess.run([sys.executable, "xsser", "-u", "http://127.0.0.1:%d/" % port,
                                "--Coo", "--auto", "--auto-set", "8", "--threads", "4", "--timeout", "8"],
                               cwd=ROOT, capture_output=True, text=True, timeout=120)
            out = r.stdout + r.stderr
        finally:
            srv.shutdown()
        self.assertIn("COO", out)

_MOCK = {}

def setUpModule():
    class _H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = parse_qs(urlparse(self.path).query)
            refl = " ".join(v[0] for v in q.values())
            c = self.headers.get("Cookie", ""); u = self.headers.get("User-Agent", ""); r = self.headers.get("Referer", "")
            b = ("<html><body>S:" + refl + " C:" + c + " U:" + u + " R:" + r + "<a href='/view.php?name=bob'>p</a></body></html>").encode("utf-8", "replace")
            self.send_response(200); self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0) or 0); self.rfile.read(n)
            b = b"<html><body>posted</body></html>"
            self.send_response(200); self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        def log_message(self, *a):
            pass
    srv = http.server.HTTPServer(("127.0.0.1", 0), _H)
    _MOCK["srv"] = srv
    _MOCK["port"] = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

def tearDownModule():
    if _MOCK.get("srv"):
        _MOCK["srv"].shutdown()
        _MOCK["srv"].server_close()

def _url():
    return "http://127.0.0.1:%d/?q=XSS" % _MOCK["port"]

def _run(args, timeout=60):
    r = subprocess.run([sys.executable, "xsser"] + args + ["--debug"], cwd=ROOT,
                       capture_output=True, text=True, timeout=timeout)
    return r.stdout + r.stderr

class TestVectorSelection(unittest.TestCase):
    def test_payload_own_code(self):
        base = "http://127.0.0.1:%d/" % _MOCK["port"]
        out = _run(["-u", base, "-g", "/?q=XSS", "--payload", "<script>alert(XSS)</script>", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
        self.assertIn("FOUND", out)
    def test_auto(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "3", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
        self.assertIn("Vulnerable", out)
    def test_auto_set_limit(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "2", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
    def test_auto_info(self):
        out = _run(["-u", _url(), "--auto", "--auto-info", "--auto-set", "3", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
    def test_auto_random(self):
        out = _run(["-u", _url(), "--auto", "--auto-random", "--auto-set", "3", "--timeout", "5"])
        self.assertNotIn("Traceback", out)

class TestFinalInjection(unittest.TestCase):
    def test_fp_own_code(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "3", "--Fp", "alert(9)", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
    def test_fr_remote_script(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "3", "--Fr", "http://127.0.0.1/e.js", "--timeout", "5"])
        self.assertNotIn("Traceback", out)

class TestSpecialFinal(unittest.TestCase):
    def _flag(self, flag):
        return _run(["-u", _url(), "--auto", "--auto-set", "3", flag, "--timeout", "5"])
    def test_anchor(self):
        self.assertNotIn("Traceback", self._flag("--Anchor"))
    def test_b64(self):
        self.assertNotIn("Traceback", self._flag("--B64"))
    def test_onm(self):
        self.assertNotIn("Traceback", self._flag("--Onm"))
    def test_ifr(self):
        self.assertNotIn("Traceback", self._flag("--Ifr"))
    def test_dos(self):
        self.assertNotIn("Traceback", self._flag("--Dos"))
    def test_doss(self):
        self.assertNotIn("Traceback", self._flag("--Doss"))

class TestFullAnalysis(unittest.TestCase):
    def test_crawler_plus_auto(self):
        base = "http://127.0.0.1:%d/" % _MOCK["port"]
        out = _run(["-u", base, "-c", "4", "--auto", "--auto-set", "3", "--threads", "5", "--timeout", "6"], timeout=110)
        self.assertNotIn("Traceback", out)
        self.assertIn("CRAWLER", out)
        self.assertIn("FOUND", out)

class TestNewIO(unittest.TestCase):
    def test_json_output(self):
        base = "http://127.0.0.1:%d/?q=XSS" % _MOCK["port"]
        jf = tempfile.mktemp(suffix=".json")
        out = _run(["-u", base, "--auto", "--auto-set", "3", "--timeout", "5", "--json", jf])
        self.assertNotIn("Traceback", out)
        with open(jf) as f:
            d = json.load(f)
        self.assertEqual(d["version"], "1.9")
        self.assertIn("vulnerabilities", d)
        self.assertGreaterEqual(len(d["vulnerabilities"]), 1)
        os.remove(jf)
    def test_stdin_pipe_mode(self):
        base = "http://127.0.0.1:%d/?q=XSS" % _MOCK["port"]
        r = subprocess.run([sys.executable, "xsser", "--auto", "--auto-set", "2", "--timeout", "5", "--debug"],
                           cwd=ROOT, input=base + "\n", capture_output=True, text=True, timeout=60)
        out = r.stdout + r.stderr
        self.assertNotIn("Traceback", out)
        self.assertIn("FOUND", out)
    def test_reqfile(self):
        port = _MOCK["port"]
        rf = tempfile.mktemp(suffix=".txt")
        with open(rf, "w") as f:
            f.write("GET /?q=XSS HTTP/1.1\nHost: 127.0.0.1:%d\nUser-Agent: t/1.0\nCookie: sid=1\n\n" % port)
        out = _run(["-r", rf, "--auto", "--auto-set", "2", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
        self.assertIn("FOUND", out)
        os.remove(rf)

_REC = []

class _RecordHandler(http.server.BaseHTTPRequestHandler):
    def _log(self):
        _REC.append({"method": self.command, "path": self.path,
                     "ua": self.headers.get("User-Agent", ""),
                     "referer": self.headers.get("Referer", ""),
                     "cookie": self.headers.get("Cookie", ""),
                     "xff": self.headers.get("X-Forwarded-For", ""),
                     "xclient": self.headers.get("X-Client-IP", ""),
                     "xtest": self.headers.get("X-Test", "")})
    def do_GET(self):
        self._log()
        q = parse_qs(urlparse(self.path).query)
        refl = " ".join(v[0] for v in q.values())
        b = ("<html><body>S:" + refl + "</body></html>").encode("utf-8", "replace")
        self.send_response(200); self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_HEAD(self):
        self._log()
        self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers()
    def log_message(self, *a):
        pass

class _TraceHandler(http.server.BaseHTTPRequestHandler):
    def do_TRACE(self):
        b = ("TRACE %s HTTP/1.1\r\nHost: x\r\n" % self.path).encode("utf-8", "replace")
        self.send_response(200); self.send_header("Content-Type", "message/http")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a):
        pass

class _NoTraceHandler(http.server.BaseHTTPRequestHandler):
    def do_TRACE(self):
        self.send_response(405); self.send_header("Content-Length", "0"); self.end_headers()
    def log_message(self, *a):
        pass

class _BlindHandler(http.server.BaseHTTPRequestHandler):
    store = []
    def _send(self, s):
        b = s.encode("utf-8", "replace")
        self.send_response(200); self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/check":
            self._send("<html><body>G:" + "|".join(_BlindHandler.store) + "</body></html>")
        else:
            for v in parse_qs(u.query).values():
                _BlindHandler.store.append(v[0])
            self._send("<html><body>stored</body></html>")
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0) or 0); self.rfile.read(n)
        self._send("<html><body>stored</body></html>")
    def log_message(self, *a):
        pass

class _BasicAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        import base64
        auth = self.headers.get("Authorization", "")
        ok = False
        if auth.startswith("Basic "):
            try:
                ok = base64.b64decode(auth.split(" ", 1)[1]).decode("utf-8", "replace") == "admin:s3cr3t"
            except Exception:
                ok = False
        if not ok:
            self.send_response(401); self.send_header("WWW-Authenticate", 'Basic realm="x"')
            self.send_header("Content-Length", "0"); self.end_headers(); return
        q = parse_qs(urlparse(self.path).query); refl = " ".join(v[0] for v in q.values())
        b = ("<html><body>S:" + refl + "</body></html>").encode("utf-8", "replace")
        self.send_response(200); self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a):
        pass

class _RedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/reflect":
            q = parse_qs(u.query); refl = " ".join(v[0] for v in q.values())
            b = ("<html><body>S:" + refl + "</body></html>").encode("utf-8", "replace")
            self.send_response(200); self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        else:
            self.send_response(302); self.send_header("Location", "/reflect?" + (u.query or ""))
            self.send_header("Content-Length", "0"); self.end_headers()
    def log_message(self, *a):
        pass

def _serve(handler):
    srv = http.server.HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]

class TestCheckerSystems(unittest.TestCase):
    def test_hash_precheck(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "1", "--hash", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
        self.assertIn("HASH FOUND", out)
    def test_heuristic_probes(self):
        out = _run(["-u", _url(), "--heuristic", "--timeout", "6"])
        self.assertNotIn("Traceback", out)
        self.assertIn("Checking:", out)
    def test_discode_discards(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "3", "--discode", "S:", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
        self.assertIn("DISCARDING", out)
    def test_checkaturl_blind(self):
        _BlindHandler.store = []
        srv, port = _serve(_BlindHandler)
        base = "http://127.0.0.1:%d" % port
        try:
            out = _run(["-u", base + "/submit?q=XSS", "--checkaturl", base + "/check",
                        "--auto", "--auto-set", "3", "--timeout", "5"])
        finally:
            srv.shutdown(); srv.server_close()
        self.assertNotIn("Traceback", out)
        self.assertIn("FOUND", out)
    def test_checkmethod_and_checkatdata(self):
        _BlindHandler.store = []
        srv, port = _serve(_BlindHandler)
        base = "http://127.0.0.1:%d" % port
        try:
            out = _run(["-u", base + "/submit?q=XSS", "--checkaturl", base + "/check",
                        "--checkmethod", "GET", "--checkatdata", "q=XSS",
                        "--auto", "--auto-set", "2", "--timeout", "5"])
        finally:
            srv.shutdown(); srv.server_close()
        self.assertNotIn("Traceback", out)

class TestXST(unittest.TestCase):
    def test_xst_vulnerable(self):
        srv, port = _serve(_TraceHandler)
        try:
            out = _run(["--xst", "http://127.0.0.1:%d/" % port, "--timeout", "5"])
        finally:
            srv.shutdown(); srv.server_close()
        self.assertNotIn("Traceback", out)
        self.assertIn("vulnerable to XST", out)
    def test_xst_not_vulnerable(self):
        srv, port = _serve(_NoTraceHandler)
        try:
            out = _run(["--xst", "http://127.0.0.1:%d/" % port, "--timeout", "5"])
        finally:
            srv.shutdown(); srv.server_close()
        self.assertNotIn("Traceback", out)
        self.assertIn("NOT vulnerable", out)

class TestRequestOptions(unittest.TestCase):
    def test_head_precheck_sent(self):
        _REC.clear()
        srv, port = _serve(_RecordHandler)
        try:
            out = _run(["-u", "http://127.0.0.1:%d/?q=XSS" % port, "--head", "--auto", "--auto-set", "1", "--timeout", "5"])
        finally:
            srv.shutdown(); srv.server_close()
        self.assertNotIn("Traceback", out)
        self.assertTrue(any(r["method"] == "HEAD" for r in _REC))
    def test_no_head_by_default(self):
        _REC.clear()
        srv, port = _serve(_RecordHandler)
        try:
            _run(["-u", "http://127.0.0.1:%d/?q=XSS" % port, "--auto", "--auto-set", "1", "--timeout", "5"])
        finally:
            srv.shutdown(); srv.server_close()
        self.assertFalse(any(r["method"] == "HEAD" for r in _REC))
    def test_agent_referer_cookie_headers(self):
        _REC.clear()
        srv, port = _serve(_RecordHandler)
        try:
            out = _run(["-u", "http://127.0.0.1:%d/?q=XSS" % port, "--auto", "--auto-set", "1",
                        "--user-agent", "FOO/9", "--referer", "http://ref.example/",
                        "--cookie", "sid=abc123", "--headers", "X-Test: hello123", "--timeout", "5"])
        finally:
            srv.shutdown(); srv.server_close()
        self.assertNotIn("Traceback", out)
        self.assertTrue(any(r["ua"] == "FOO/9" for r in _REC))
        self.assertTrue(any(r["referer"] == "http://ref.example/" for r in _REC))
        self.assertTrue(any("sid=abc123" in r["cookie"] for r in _REC))
        self.assertTrue(any("hello123" in r["xtest"] for r in _REC))
    def test_xforw_xclient(self):
        _REC.clear()
        srv, port = _serve(_RecordHandler)
        try:
            out = _run(["-u", "http://127.0.0.1:%d/?q=XSS" % port, "--auto", "--auto-set", "1",
                        "--xforw", "--xclient", "--timeout", "5"])
        finally:
            srv.shutdown(); srv.server_close()
        self.assertNotIn("Traceback", out)
        self.assertTrue(any(r["xff"] for r in _REC))
        self.assertTrue(any(r["xclient"] for r in _REC))
    def test_drop_cookie(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "1", "--drop-cookie", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
    def test_timeout_retries_delay_nodelay(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "1", "--timeout", "5",
                    "--retries", "2", "--delay", "0", "--tcp-nodelay"])
        self.assertNotIn("Traceback", out)
        self.assertIn("FOUND", out)
    def test_follow_redirects(self):
        srv, port = _serve(_RedirectHandler)
        try:
            out = _run(["-u", "http://127.0.0.1:%d/start?q=XSS" % port, "--auto", "--auto-set", "2",
                        "--follow-redirects", "--follow-limit", "10", "--timeout", "5"])
        finally:
            srv.shutdown(); srv.server_close()
        self.assertNotIn("Traceback", out)
        self.assertIn("FOUND", out)
    def test_ignore_proxy(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "1", "--ignore-proxy", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
        self.assertIn("FOUND", out)
    def test_proxy_is_applied(self):
        _REC.clear()
        srv, port = _serve(_RecordHandler)
        try:
            out = _run(["-u", "http://127.0.0.1:%d/?q=XSS" % port, "--auto", "--auto-set", "1",
                        "--proxy", "http://127.0.0.1:1", "--timeout", "5"])
        finally:
            srv.shutdown(); srv.server_close()
        self.assertNotIn("Traceback", out)
        self.assertFalse(any(r["method"] == "GET" for r in _REC))

class TestAuth(unittest.TestCase):
    def test_basic_auth_gates_access(self):
        srv, port = _serve(_BasicAuthHandler)
        base = "http://127.0.0.1:%d/?q=XSS" % port
        try:
            no = _run(["-u", base, "--auto", "--auto-set", "1", "--timeout", "5"])
            yes = _run(["-u", base, "--auto", "--auto-set", "1", "--auth-type", "basic",
                        "--auth-cred", "admin:s3cr3t", "--timeout", "5"])
        finally:
            srv.shutdown(); srv.server_close()
        self.assertNotIn("Traceback", no)
        self.assertNotIn("Traceback", yes)
        self.assertNotIn("FOUND !!!", no)
        self.assertIn("FOUND !!!", yes)
    def test_auth_cert_parses(self):
        from core.options import XSSerOptions
        opts = XSSerOptions().get_options(["--auth-cert", "key.pem,cert.pem", "-u", "http://127.0.0.1"])
        self.assertEqual(opts.acert, "key.pem,cert.pem")

class TestCheckTor(unittest.TestCase):
    def test_check_tor_runs(self):
        out = _run(["--check-tor", "--timeout", "5"], timeout=70)
        self.assertNotIn("Traceback", out)
        self.assertIn("tor", out.lower())
    def test_check_tor_proxy_parses(self):
        from core.options import XSSerOptions
        opts = XSSerOptions().get_options(["--check-tor", "--proxy", "http://127.0.0.1:8118"])
        self.assertTrue(opts.checktor)
        self.assertEqual(opts.proxy, "http://127.0.0.1:8118")

class TestCemEncoders(unittest.TestCase):
    def test_cem_chain_runs(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "2", "--Cem", "Mix,Str", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
        self.assertIn("Trying:", out)
    def test_cem_parses(self):
        from core.options import XSSerOptions
        opts = XSSerOptions().get_options(["--Cem", "Mix,Une,Str,Hex", "-u", "http://127.0.0.1"])
        self.assertEqual(opts.Cem, "Mix,Une,Str,Hex")

class TestMiscellaneous(unittest.TestCase):
    def test_debug_mode(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "1", "--timeout", "5"])
        self.assertIn("Debug mode: ON", out)
    def test_silent_mode(self):
        base = "http://127.0.0.1:%d/?q=XSS" % _MOCK["port"]
        r = subprocess.run([sys.executable, "xsser", "-u", base, "--auto", "--auto-set", "1",
                            "--silent", "--timeout", "5"], cwd=ROOT, capture_output=True, text=True, timeout=60)
        out = r.stdout + r.stderr
        self.assertNotIn("Traceback", out)
    def test_alive_parses(self):
        from core.options import XSSerOptions
        opts = XSSerOptions().get_options(["--alive", "3", "-u", "http://127.0.0.1"])
        self.assertEqual(opts.isalive, 3)
    def test_update_parses(self):
        from core.options import XSSerOptions
        opts = XSSerOptions().get_options(["--update"])
        self.assertTrue(opts.update)

class TestWafBypassers(unittest.TestCase):
    def _flag(self, flag):
        return _run(["-u", _url(), "--auto", "--auto-set", "2", flag, "--timeout", "5"])
    def test_cloudflare(self):
        self.assertNotIn("Traceback", self._flag("--Cloudflare"))
    def test_akamai(self):
        self.assertNotIn("Traceback", self._flag("--Akamai"))
    def test_awswaf(self):
        self.assertNotIn("Traceback", self._flag("--Awswaf"))
    def test_wordfence(self):
        self.assertNotIn("Traceback", self._flag("--Wordfence"))
    def test_fortiweb(self):
        self.assertNotIn("Traceback", self._flag("--Fortiweb"))

class TestSpecialInjections(unittest.TestCase):
    def test_xsa(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "2", "--Xsa", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
    def test_xsr(self):
        out = _run(["-u", _url(), "--auto", "--auto-set", "2", "--Xsr", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
    def test_dcp(self):
        out = _run(["-u", _url(), "--Dcp", "--timeout", "5"])
        self.assertNotIn("Traceback", out)
    def test_induced(self):
        out = _run(["-u", _url(), "--Ind", "--timeout", "5"])
        self.assertNotIn("Traceback", out)

if __name__ == "__main__":
    unittest.main(verbosity=2)
