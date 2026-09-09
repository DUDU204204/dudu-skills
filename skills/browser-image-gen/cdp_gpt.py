#!/usr/bin/env python3
"""cdp_gpt.py — CDP helper for driving chatgpt.com in the server Chrome (:9222).
Plumbing copied from ypay.py (hand-rolled websocket, no deps)."""
import base64, json, os, socket, struct, sys, time, urllib.request

DBG = "http://127.0.0.1:9222"


def _ws(u):
    hp, p = u[5:].split("/", 1); h, po = hp.split(":")
    s = socket.create_connection((h, int(po)), timeout=30)
    k = base64.b64encode(os.urandom(16)).decode()
    s.send(("GET /%s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
            "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n" % (p, hp, k)).encode())
    b = b""
    while b"\r\n\r\n" not in b: b += s.recv(4096)
    return s


def _snd(s, o):
    d = json.dumps(o).encode(); hdr = bytearray([0x81]); n = len(d); m = os.urandom(4)
    if n < 126: hdr.append(0x80 | n)
    elif n < 65536: hdr.append(0x80 | 126); hdr += struct.pack(">H", n)
    else: hdr.append(0x80 | 127); hdr += struct.pack(">Q", n)
    hdr += m; s.send(bytes(hdr) + bytes(x ^ m[i % 4] for i, x in enumerate(d)))


def _rcv(s):
    def rd(n):
        b = b""
        while len(b) < n:
            c = s.recv(n - len(b))
            if not c: raise IOError("closed")
            b += c
        return b
    o = b""
    while True:
        b0, b1 = rd(2); ln = b1 & 0x7F
        if ln == 126: ln = struct.unpack(">H", rd(2))[0]
        elif ln == 127: ln = struct.unpack(">Q", rd(8))[0]
        o += rd(ln)
        if b0 & 0x80: return json.loads(o.decode())


def targets():
    return json.load(urllib.request.urlopen(DBG + "/json", timeout=10))


def open_tab(url):
    req = urllib.request.Request(DBG + "/json/new?" + urllib.parse.urlencode({"url": url}), method="PUT")
    return json.load(urllib.request.urlopen(req, timeout=10))


def find_tab(substr):
    for t in targets():
        if t.get("type") == "page" and substr in t.get("url", ""):
            return t
    return None


class CDP:
    def __init__(self, target):
        self.s = _ws(target["webSocketDebuggerUrl"]); self.i = 0
        self.cmd("Page.enable"); self.cmd("Runtime.enable")

    def cmd(self, m, p=None, timeout_iters=2000):
        self.i += 1; _snd(self.s, {"id": self.i, "method": m, "params": p or {}})
        while True:
            r = _rcv(self.s)
            if r.get("id") == self.i: return r.get("result", {})

    def js(self, expr, wait=True):
        r = self.cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": wait})
        if "exceptionDetails" in r:
            return {"__jserror__": str(r["exceptionDetails"].get("exception", {}).get("description", r["exceptionDetails"]))}
        return r.get("result", {}).get("value")

    def front(self):
        self.cmd("Page.bringToFront")

    def shot(self, path):
        r = self.cmd("Page.captureScreenshot", {"format": "png"})
        open(path, "wb").write(base64.b64decode(r["data"]))

    def upload(self, selector, path):
        doc = self.cmd("DOM.getDocument")
        node = self.cmd("DOM.querySelector", {"nodeId": doc["root"]["nodeId"], "selector": selector})
        if not node.get("nodeId"):
            return "no-input"
        self.cmd("DOM.setFileInputFiles", {"files": [path], "nodeId": node["nodeId"]})
        return "ok"


import urllib.parse  # noqa: E402  (used in open_tab)
