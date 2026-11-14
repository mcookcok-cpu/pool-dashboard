import json, os, shutil, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
M = "100.106.213.94"
NAMA = {"100.111.72.114":"vm-1-20","100.74.242.111":"vm-2-185","100.116.45.82":"vm-3-52","100.66.103.43":"vm-3-57","100.104.192.89":"vm-33-69","100.117.164.54":"vm-38-23","100.111.26.19":"vm-39-219","100.80.57.51":"vm-69-54"}
def get(u):
    try: return json.load(urllib.request.urlopen(u, timeout=5))
    except Exception: return None
def up(u):
    try: urllib.request.urlopen(u, timeout=5); return True
    except Exception: return False
def status():
    d = get(f"http://{M}:62030/dir/status"); nodes = []
    if d:
        for dc in d["Topology"]["DataCenters"]:
            for r in dc["Racks"]:
                for n in r["DataNodes"]:
                    ip = n["Url"].split(":")[0]
                    nodes.append({"nama": NAMA.get(ip, ip), "ip": ip, "vol": n.get("Volumes", 0), "max": n.get("Max", 0)})
    try: u = shutil.disk_usage("/mnt/pool"); disk = {"total": u.total, "used": u.used}
    except Exception: disk = None
    return {"master": d is not None, "filer": up(f"http://{M}:62028/"), "mount": os.path.ismount("/mnt/pool"), "t": time.strftime("%H:%M:%S"), "nodes": nodes, "disk": disk}
HTML = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"), "rb").read()
class H(BaseHTTPRequestHandler):
    def do_GET(s):
        if s.path.startswith("/api/status"): b, c = json.dumps(status()).encode(), "application/json"
        else: b, c = HTML, "text/html; charset=utf-8"
        s.send_response(200); s.send_header("Content-Type", c); s.send_header("Cache-Control", "no-store"); s.end_headers(); s.wfile.write(b)
    def log_message(s, *a): pass
ThreadingHTTPServer(("0.0.0.0", 62021), H).serve_forever()
