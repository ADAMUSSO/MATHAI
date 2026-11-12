# Cvicenie 5 - webove rozhranie k metodam
#
# Spustenie:  python server.py      potom otvor  http://localhost:8000
#
# Server len vola existujuce subory (funkcie.py, gradientna.py, newton.py,
# nelder_mead.py, powell.py) a vysledky posiela do web/index.html ako JSON.
import base64
import json
import math
import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

import sympy as sp

from funkcie import FUNKCIE, Funkcia
from gradientna import gradientna
from newton import newton
from nelder_mead import nelder_mead
from powell import powell

PORT = 8000
WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

METODY = {
    "gradientna": lambda fn, p: gradientna(fn, start=p["start"], alfa=p["alfa"], tol=p["tol"], max_it=p["max_it"]),
    "newton": lambda fn, p: newton(fn, start=p["start"], tol=p["tol"], max_it=p["max_it"]),
    "nelder_mead": lambda fn, p: nelder_mead(fn, start=p["start"], h=p["h"], tol=p["tol"], max_it=p["max_it"]),
    "powell": lambda fn, p: powell(fn, start=p["start"], tol=p["tol"], max_it=p["max_it"]),
}

# realne symboly - vlastna funkcia moze obsahovat napr. Abs(x)
xr, yr = sp.symbols("x y", real=True)


class VlastnaFunkcia(Funkcia):
    """Funkcia zadana textom z webu (uloha 6). Sprava sa rovnako ako Funkcia z funkcie.py."""

    def __init__(self, vyraz_text, start, minima):
        self.nazov = "Vlastna"
        self.vyraz = sp.sympify(vyraz_text, locals={"x": xr, "y": yr, "abs": sp.Abs})
        self.start = start
        self.minima = minima
        gx, gy = sp.diff(self.vyraz, xr), sp.diff(self.vyraz, yr)
        hxx, hxy, hyy = sp.diff(gx, xr), sp.diff(gx, yr), sp.diff(gy, yr)
        # druha derivacia |x| je DiracDelta - mimo nuly je to 0
        bez_delta = lambda e: e.replace(sp.DiracDelta, lambda *a: 0)
        self._f = sp.lambdify((xr, yr), self.vyraz, "math")
        self._g = sp.lambdify((xr, yr), (gx, gy), "math")
        self._h = sp.lambdify((xr, yr), ((bez_delta(hxx), bez_delta(hxy)),
                                         (bez_delta(hxy), bez_delta(hyy))), "math")
        self.vynuluj()


def cislo(v):
    """JSON nevie inf/nan -> None."""
    v = float(v)
    return v if math.isfinite(v) else None


def bod(p):
    return [cislo(p[0]), cislo(p[1])]


def hodnota_f(fn, a, b):
    try:
        return cislo(fn._f(a, b))
    except (OverflowError, ValueError, ZeroDivisionError):
        return None


def vysledok_json(r):
    fn = r.fn
    hist = r.historia
    vzd = [cislo(math.dist(p, fn.najblizsie_minimum(*p))) if all(map(math.isfinite, p)) else None
           for p in hist]

    # cesta na graf vrstevnic - max ~1500 bodov
    krok = max(1, len(hist) // 1500)
    cesta = [bod(p) for p in hist[::krok]]
    if (len(hist) - 1) % krok:
        cesta.append(bod(hist[-1]))

    # vypis iteracii: prvych 300 + poslednych 20
    idx = list(range(min(len(hist), 300)))
    if len(hist) > 300:
        idx += list(range(max(300, len(hist) - 20), len(hist)))
    log = [[k, cislo(hist[k][0]), cislo(hist[k][1]), hodnota_f(fn, *hist[k]), vzd[k]] for k in idx]

    # kmitanie: kolko krat sa zmenil smer pohybu (pre ulohu 3)
    zmeny = 0
    for k in range(2, len(hist)):
        d1 = (hist[k - 1][0] - hist[k - 2][0], hist[k - 1][1] - hist[k - 2][1])
        d2 = (hist[k][0] - hist[k - 1][0], hist[k][1] - hist[k - 1][1])
        if d1[0] * d2[0] + d1[1] * d2[1] < 0:
            zmeny += 1

    return {
        "metoda": r.metoda,
        "iteracie": r.iteracie,
        "konvergoval": r.konvergoval,
        "poznamka": r.poznamka,
        "do_tabulky": r.do_tabulky(),
        "pocet_f": r.pocet_f,
        "pocet_grad": r.pocet_grad,
        "pocet_hess": r.pocet_hess,
        "x": bod(r.x),
        "f_x": hodnota_f(fn, *r.x) if all(map(math.isfinite, r.x)) else None,
        "minimum": list(r.minimum) if r.minimum else None,
        "kmitanie": zmeny / max(1, len(hist) - 2),
        "vzdialenosti": vzd,
        "cesta": cesta,
        "log": log,
        "log_skrateny": len(hist) > 300,
    }


def mriezka(fn, vysledky, n=110):
    """Hodnoty f na mriezke okolo startu, minim a ciest - na graf vrstevnic."""
    body = [fn.start] + list(fn.minima)
    # vyrez podla metod, ktore skonvergovali (divergujuca cesta by graf prilis oddialila)
    for r in [r for r in vysledky if r["konvergoval"]] or vysledky:
        body += [p for p in r["cesta"] if p[0] is not None and p[1] is not None
                 and abs(p[0]) < 50 and abs(p[1]) < 50]
    xs, ys = [p[0] for p in body], [p[1] for p in body]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    sx, sy = max(x1 - x0, 1.0), max(y1 - y0, 1.0)
    x0, x1, y0, y1 = x0 - 0.15 * sx, x1 + 0.15 * sx, y0 - 0.15 * sy, y1 + 0.15 * sy
    z = [[hodnota_f(fn, x0 + (x1 - x0) * i / (n - 1), y0 + (y1 - y0) * j / (n - 1))
          for i in range(n)] for j in range(n)]
    return {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "n": n, "z": z}


def info_funkcie(kluc, fn):
    return {"kluc": kluc, "nazov": fn.nazov, "vyraz": str(fn.vyraz),
            "start": list(fn.start), "minima": [list(m) for m in fn.minima]}


def spusti(p):
    if p.get("funkcia") == "vlastna":
        minima = [tuple(map(float, m)) for m in p["minima"]]
        fn = VlastnaFunkcia(p["vyraz"], tuple(p["start"]), minima)
    else:
        fn = FUNKCIE[p["funkcia"]]
    nast = {
        "start": tuple(map(float, p.get("start") or fn.start)),
        "tol": float(p.get("tol", 1e-3)),
        "alfa": float(p.get("alfa", 0.01)),
        "h": float(p.get("h", 0.5)),
        "max_it": int(p.get("max_it", 20000)),
    }
    vysledky = [vysledok_json(METODY[m](fn, nast)) for m in p.get("metody", list(METODY))]
    out = {"funkcia": info_funkcie(p.get("funkcia"), fn), "start": list(nast["start"]),
           "vysledky": vysledky}
    if p.get("mriezka"):
        out["mriezka"] = mriezka(fn, vysledky)
    if p.get("bez_detailov"):
        for r in vysledky:
            del r["log"], r["cesta"]
    return out


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=WEB, **kw)

    def posli_json(self, data, kod=200):
        telo = json.dumps(data).encode()
        self.send_response(kod)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(telo)))
        self.end_headers()
        self.wfile.write(telo)

    def do_GET(self):
        if self.path == "/api/funkcie":
            return self.posli_json([info_funkcie(k, fn) for k, fn in FUNKCIE.items()])
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/ulozit":   # ulozi PNG graf do cvicenia/cv05/grafy/
            p = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            nazov = "".join(c for c in p["nazov"] if c.isalnum() or c in "_-") + ".png"
            priecinok = os.path.join(os.path.dirname(WEB), "grafy")
            os.makedirs(priecinok, exist_ok=True)
            with open(os.path.join(priecinok, nazov), "wb") as f:
                f.write(base64.b64decode(p["data"].split(",", 1)[1]))
            return self.posli_json({"subor": f"grafy/{nazov}"})
        if self.path != "/api/run":
            return self.send_error(404)
        try:
            p = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.posli_json(spusti(p))
        except Exception as e:
            self.posli_json({"chyba": f"{type(e).__name__}: {e}"}, 400)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"Server bezi na http://localhost:{PORT}  (Ctrl+C = koniec)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
