# SEED - sada zaludnych prikladov na porovnanie kodov (gradient, Newton, Powell, Nelder-Mead)
#
# Spustenie (z priecinka zapocet_kody):   python seed/spusti_seed.py
#   - spusti vsetky 4 skripty na vsetkych prikladoch nizsie
#   - zapise:  seed/seed_priklady.json   (len zadania - na spustenie vo vlastnom kode)
#              seed/seed_vysledky.json   (ocakavane vysledky, vsetky iteracie)
#              seed/seed_vysledky.md     (citatelna tabulka: 1. a 2. iteracia + vysledok)
#              seed/seed_vystup.txt      (kompletny vypis vsetkych skriptov)
#
# PRAVIDLA, ktore musi mat aj tvoj kod, aby sa vysledky zhodovali:
#   gradient : S = -grad/||grad||, presne gama > 0 (minimum phi), STOP ||grad|| < eps
#   Newton   : X - H^-1 grad, STOP ||grad|| < eps (pred krokom) alebo ||X_nove - X|| < eps
#   Powell   : u1=(1,0), u2=(0,1); P0->P1 (u1), P1->P2 (u2), d = P2-P0, P2->P3 (d);
#              u1 <- u2, u2 <- d (ALE ak je d rovnobezny s u2, smery nemenim);
#              gama moze byt zaporne; STOP ||P3 - P0|| < eps
#   hladanie po priamke (gradient aj Powell): zo vsetkych lokalnych minim phi(gama)
#              beriem to s NAJMENSIM phi (pri rovnosti to blizsie k 0)
#   NM       : B,G,W; M=(B+G)/2; R=M+a(M-W); 1) f(R)<f(B): E=M+g(R-M), E ak f(E)<f(R) inak R
#              2) f(R)<f(G): R   3) inak C1=M+r(W-M) [prednaska: aj C2=M+r(R-M), lepsi]
#              C ak f(C)<f(W), inak zmrstenie k B (S=B+s(W-B), M=B+s(G-B))
#              STOP d = max vzdialenost od B < eps (kontroluje sa pred iteraciou)
#              rovnost f: plati vetva s nesplnenym '<'; pri zoradeni s rovnakym f
#              zostava poradie zo zadania, novy bod je pri rovnosti horsi nez stary
import contextlib
import io
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(TU))         # priecinok zapocet_kody so skriptmi
os.environ.setdefault("MPLBACKEND", "Agg")

import gradient
import newton
import powell
import nelder_mead

ROSEN = "(1 - x)**2 + 100*(y - x**2)**2"
HIMMEL = "(x**2 + y - 11)**2 + (x + y**2 - 7)**2"

PRIKLADY = [
    # ---------------- NAJSTRMSI GRADIENT (normovany smer, presne gama) ----------------
    dict(id="G1", metoda="gradient", funkcia="x**2 + 2*y**2", start=(3, 1),
         pasca="zakladny priklad z hodiny (gradient (6, 4), ||grad|| = odmocnina z 52)"),
    dict(id="G2", metoda="gradient", funkcia="x**2 - 4*x + y**2 - y - x*y", start=(0, 0),
         pasca="clen -x*y (obe derivacie zavisia od x aj y)"),
    dict(id="G3", metoda="gradient", funkcia="(x - 1)**2 + 10*(y + 2)**2", start=(-2.5, 0.5),
         pasca="desatinny a zaporny start, uzke udolie -> cik-cak, vela iteracii"),
    dict(id="G4", metoda="gradient", funkcia="x**4/4 + x**2/2 + y**2/2", start=(1, 1),
         pasca="phi(gama) je polynom 4. stupna, phi' je kubicka rovnica"),
    dict(id="G5", metoda="gradient", funkcia="x**3 + y**3 - 3*x*y", start=(2, 1.5),
         pasca="kubicka funkcia: phi' ma 2 korene, jeden je MAXIMUM phi -> treba vybrat minimum"),
    dict(id="G6", metoda="gradient", funkcia="x**4 + y**4", start=(1, 2),
         pasca="plocha funkcia, viacnasobny koren phi' (nroots/zaokruhlenie)"),
    dict(id="G7", metoda="gradient", funkcia=HIMMEL, start=(0, 0),
         pasca="Himmelblau: 4 minima, phi ma viac lokalnych minim -> ktore?"),
    dict(id="G8", metoda="gradient", funkcia="sqrt(x**2 + 1) + (y - 2)**2", start=(3, 0),
         pasca="nie je polynom -> phi' = 0 sa neda vyriesit vzorcom (numericky)"),
    dict(id="G9", metoda="gradient", funkcia="exp(x**2 + y**2) - 2*x", start=(1, 1),
         pasca="exponenciala, nie je polynom"),
    dict(id="G10", metoda="gradient", funkcia="x**2 + y**2", start=(0, 0),
         pasca="start uz je v minime -> 0 iteracii (ziadne delenie nulou!)"),
    dict(id="G11", metoda="gradient", funkcia="x**3 + y**2", start=(1, 1),
         pasca="funkcia NEMA minimum -> kod ma zahlasit chybu, nie vypisat nezmysel"),
    dict(id="G12", metoda="gradient", funkcia=ROSEN, start=(-1.2, 1), max_it=100,
         pasca="Rosenbrock: steepest je extremne pomaly -> po 100 iteraciach este nie je v (1, 1)"),

    # ---------------- NEWTON 2D ----------------
    dict(id="N1", metoda="newton", funkcia="x**2 + 2*y**2", start=(2, 2),
         pasca="kvadraticka funkcia -> minimum za 1 krok"),
    dict(id="N2", metoda="newton", funkcia="x**2 - 4*x + y**2 - y - x*y", start=(0, 0),
         pasca="H ma nenulove b = c = -1 (vymenit a<->d, zmenit znamienka b, c)"),
    dict(id="N3", metoda="newton", funkcia="x**4/4 + x**2/2 + y**2/2", start=(1, 1),
         pasca="priklad z cvicenia 4"),
    dict(id="N4", metoda="newton", funkcia=ROSEN, start=(-1.2, 1),
         pasca="Rosenbrock (znamy X1 = (-1.1753, 1.3807))"),
    dict(id="N5", metoda="newton", funkcia=HIMMEL, start=(0, 0),
         pasca="Newton skonci v MAXIME (-0.2708, -0.9230), nie v minime!"),
    dict(id="N6", metoda="newton", funkcia="x**2 - y**2", start=(1, 1),
         pasca="Newton skonci v SEDLE (0, 0)"),
    dict(id="N7", metoda="newton", funkcia="x**3 + y**3 - 3*x*y", start=(2, 2),
         pasca="kubicka funkcia, minimum (1, 1)"),
    dict(id="N8", metoda="newton", funkcia="exp(x**2 + y**2) - 2*x", start=(1, 1),
         pasca="exponenciala"),
    dict(id="N9", metoda="newton", funkcia="x**4 + y**2", start=(0, 1),
         pasca="det H = 0 v starte -> H^-1 neexistuje, kod ma zahlasit chybu"),
    dict(id="N10", metoda="newton", funkcia="x**4 + y**4", start=(1, 1),
         pasca="det H -> 0 pri minime, Newton je tu len linearny (x -> 2x/3)"),

    # ---------------- POWELL ----------------
    dict(id="P1", metoda="powell", funkcia="x**2 - 4*x + y**2 - y - x*y", start=(0, 0),
         pasca="kvadraticka -> presne minimum (3, 2) po 2 iteraciach"),
    dict(id="P2", metoda="powell", funkcia="x**2 + 2*y**2", start=(3, 1),
         pasca="minimum najde uz P2, smer d da gama = 0"),
    dict(id="P3", metoda="powell", funkcia="(x - 1)**2 + (y - 2)**2 + x*y", start=(5, 5),
         pasca="ZAPORNE gama (minimum je 'za chrbtom')"),
    dict(id="P4", metoda="powell", funkcia="x**4/4 + x**2/2 + y**2/2", start=(1, 1),
         pasca="phi je polynom 4. stupna"),
    dict(id="P5", metoda="powell", funkcia=ROSEN, start=(-1.2, 1),
         pasca="na priamke y = 1 su 2 lokalne minima phi -> berie sa to s mensim phi (x = 1)"),
    dict(id="P6", metoda="powell", funkcia=HIMMEL, start=(0, 0),
         pasca="Himmelblau: ktore zo 4 minim (zavisi od vyberu minima na priamke)"),
    dict(id="P7", metoda="powell", funkcia="sqrt(x**2 + 1) + (y - 2)**2", start=(3, 0),
         pasca="nie je polynom (numericke hladanie po priamke)"),
    dict(id="P8", metoda="powell", funkcia="x**3 + y**3 - 3*x*y", start=(2, 2),
         pasca="kubicka: phi' ma koren s maximom aj minimom, minimum je pri zapornom gama"),
    dict(id="P9", metoda="powell", funkcia="x**2 + y**2", start=(0, 0),
         pasca="start v minime -> d = (0, 0), ziadne delenie nulou"),
    dict(id="P10", metoda="powell", funkcia="x**2 + y**2 + x*y - 3*y", start=(0, 0),
         pasca="v starte je df/dx = 0 -> gama1 = 0, d je rovnobezny s u2; ked sa smery "
               "posunu, metoda sa ZASEKNE v (0, 1.5) namiesto minima (-1, 2) -> smery nemenit"),
    dict(id="P11", metoda="powell", funkcia="x**2 - 4*x + y**2 - y - x*y", start=(2, 0),
         pasca="ta ista pasca ako P10 (df/dx(2, 0) = 0), zasekol by sa v (2, 1.5) namiesto (3, 2)"),

    # ---------------- NELDER-MEAD ----------------
    dict(id="M1", metoda="nm", funkcia="x**2 + y**2 + x - 2*y - x*y + 2",
         body=[(1.2, 0), (0, 0.8), (0, 0)], kontrakcia="cvicenie",
         pasca="slajd 27 z cvicenia (vzor zapoctu), kontrakcia len C1"),
    dict(id="M2", metoda="nm", funkcia="x**2 - 4*x + y**2 - y - x*y",
         body=[(0, 0), (1.2, 0), (0, 0.8)], kontrakcia="prednaska",
         pasca="vzorovy priklad z prednasky 4 (C1 aj C2)"),
    dict(id="M3", metoda="nm", funkcia="x**2 - 4*x + y**2 - y - x*y",
         body=[(0, 0), (1.2, 0), (0, 0.8)], kontrakcia="cvicenie",
         pasca="ten isty priklad, verzia z cvicenia -> porovnaj s M2, kde sa rozidu"),
    dict(id="M4", metoda="nm", funkcia="x**2 - 4*x + y**2 - y - x*y",
         body=[(0, 1), (1, 1), (0, 1.5)], kontrakcia="cvicenie",
         pasca="priklad z fotky cvicenia 4"),
    dict(id="M5", metoda="nm", funkcia="x**2 + 2*y**2",
         body=[(2, 2), (2, 1), (1, 2)], kontrakcia="cvicenie",
         pasca="priklad z cvicenia 4 (A, B, C)"),
    dict(id="M6", metoda="nm", funkcia="x**2 + y**2",
         body=[(-1, 3), (0, 4), (1, 2)], kontrakcia="prednaska",
         pasca="v 2. iteracii je lepsi C2 nez C1"),
    dict(id="M7", metoda="nm", funkcia="x**2 + y**2",
         body=[(-1, 3), (0, 4), (1, 2)], kontrakcia="cvicenie",
         pasca="ten isty, len C1 -> ina cesta nez M6"),
    dict(id="M8", metoda="nm", funkcia="x**4 - 3*x**2 + y**2",
         body=[(-1.3, 0.2), (0.8, 0.7), (-0.5, -0.2)], kontrakcia="cvicenie",
         pasca="ZMRSTENIE hned v 1. iteracii"),
    dict(id="M9", metoda="nm", funkcia="x**2 + y**2",
         body=[(1, 0), (0, 1), (-1, 0)], kontrakcia="cvicenie",
         pasca="ROVNOST: vsetky 3 body maju f = 1 -> poradie podla zadania"),
    dict(id="M10", metoda="nm", funkcia="x**2 + y**2",
         body=[(1.1, -0.7), (-0.4, 0.7), (2.0, -0.1)], kontrakcia="cvicenie",
         pasca="ZAOKRUHLENIE: presne f(R) = f(G) = 1.7, ale v pocitaci f(R) = 1.6999999999999995 "
               "a f(G) = 1.7000000000000002 -> naivny kod (<) spravi reflexiu namiesto kontrakcie"),
    dict(id="M11", metoda="nm", funkcia="x**2 + y**2",
         body=[(0.4, 1.2), (1.1, 0.2), (0.5, 1.9)], kontrakcia="cvicenie",
         pasca="ZAOKRUHLENIE: presne f(R) = f(B) = 1.25, ale v pocitaci f(R) = 1.25 a "
               "f(B) = 1.2500000000000002 -> naivny kod (<) skusi expanziu namiesto reflexie"),
    dict(id="M12", metoda="nm", funkcia="x**2 - 4*x + y**2 - y - x*y",
         body=[(0, 0), (1.2, 0), (0, 0.8)], kontrakcia="cvicenie",
         alfa=1, gama=3, rho=0.25, sigma=0.5,
         pasca="ine koeficienty (gama = 3, rho = 0.25) -> vseobecne vzorce M + k*(smer)"),
    dict(id="M13", metoda="nm", funkcia=ROSEN,
         body=[(-1.2, 1), (-0.7, 1), (-1.2, 1.5)], kontrakcia="cvicenie",
         pasca="Rosenbrock, dlhy beh (vela kontrakcii aj expanzii)"),
]

MODUL = {"gradient": gradient, "newton": newton, "powell": powell, "nm": nelder_mead}


def spusti(p):
    """Spusti jeden priklad. Vrati (vysledok alebo {'chyba': ...}, cely vypis)."""
    m = MODUL[p["metoda"]]
    m.FUNKCIA = p["funkcia"]
    m.EPS = p.get("eps", 1e-3)
    m.MAX_IT = p.get("max_it", 200 if p["metoda"] == "nm" else 100)
    if p["metoda"] == "nm":
        m.BODY = p["body"]
        m.ALFA, m.GAMA = p.get("alfa", 1), p.get("gama", 2)
        m.RHO, m.SIGMA = p.get("rho", 0.5), p.get("sigma", 0.5)
        m.KONTRAKCIA, m.KRESLIT = p["kontrakcia"], 0
    else:
        m.START = p["start"]
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            r = m.main()
    except SystemExit as e:
        r = {"chyba": str(e)}
        out.write(f"\n{e}\n")
    return r, out.getvalue()


def bod(P):
    return f"({P[0]:.6f}, {P[1]:.6f})"


def zadanie(p):
    if p["metoda"] == "nm":
        z = f"`{p['funkcia']}`, body {p['body']}, kontrakcia: {p['kontrakcia']}"
        if any(k in p for k in ("alfa", "gama", "rho", "sigma")):
            z += f", alfa={p.get('alfa', 1)}, gama={p.get('gama', 2)}, rho={p.get('rho', 0.5)}, sigma={p.get('sigma', 0.5)}"
    else:
        z = f"`{p['funkcia']}`, start {tuple(p['start'])}"
    return z + f", eps = {p.get('eps', 1e-3)}"


def riadky_md(p, r):
    h = r.get("historia", [])
    L = []
    for i, it in enumerate(h[:2] if p["metoda"] != "nm" else h[:3], 1):
        if p["metoda"] == "gradient":
            L.append(f"  - it. {i}: S = {bod(it['S'])}, gama = {it['gama']:.6f}, P{i} = {bod(it['P'])}")
        elif p["metoda"] == "newton":
            L.append(f"  - it. {i}: X{i} = {bod(it['P'])}")
        elif p["metoda"] == "powell":
            L.append(f"  - it. {i}: P1 = {bod(it['P1'])}, P2 = {bod(it['P2'])}, d = {bod(it['d'])}, "
                     f"P3 = {bod(it['P3'])}")
        else:
            t = it["trojuholnik"]
            L.append(f"  - it. {i}: B = {bod(it['B'])}, G = {bod(it['G'])}, W = {bod(it['W'])}, "
                     f"f(R) = {it['fR']:.6f} -> **{it['krok']}** -> {bod(t[0])}, {bod(t[1])}, {bod(t[2])}")
    if "chyba" in r:
        L.append(f"  - **CHYBA (ocakavana):** {r['chyba']}")
    else:
        extra = f", typ: **{r['typ']}**" if "typ" in r else ""
        L.append(f"  - **vysledok: {bod(r['bod'])}, f = {r['f']:.6f}, iteracie = {r['iteracie']}**{extra}")
        L.append(f"  - stop: {r['stop']}")
    return L


def na_json(v):
    if isinstance(v, dict):
        return {k: na_json(w) for k, w in v.items()}
    if isinstance(v, (list, tuple)):
        return [na_json(w) for w in v]
    if isinstance(v, float):
        return round(v, 10)
    return v


def main():
    nazvy = {"gradient": "Najstrmsi gradient (normovany smer, presne gama)", "newton": "Newton 2D",
             "powell": "Powell", "nm": "Nelder-Mead"}
    md = ["# Seed: zaludne priklady na porovnanie kodov", "",
          "## Ako porovnat", "",
          "1. Kazdy priklad spusti vo svojom kode s presne tymito vstupmi (aj eps).",
          "2. Porovnaj 1. a 2. iteraciu (tie sa pocitaju aj rucne) a konecny bod.",
          "   Pri 6 desatinnych miestach sa smie lisit najviac posledna cifra.",
          "3. Pocet iteracii sedi len vtedy, ked mas rovnake STOP pravidlo (nizsie).",
          "4. Priklady s CHYBOU (G11, N9) maju v tvojom kode skoncit hlaskou, nie nezmyslom.", "",
          "## Pravidla (musia byt rovnake, inak sa vysledky rozidu)", "",
          "- **gradient:** S = -grad/||grad||, gama > 0 z phi'(gama) = 0, STOP ||grad|| < eps (pred krokom)",
          "- **Newton:** X - H^-1 grad, STOP ||grad|| < eps (pred krokom) alebo ||X_nove - X|| < eps",
          "- **Powell:** u1 = (1, 0), u2 = (0, 1); P0->P1 po u1, P1->P2 po u2, d = P2 - P0, P2->P3 po d;"
          " potom u1 <- u2, u2 <- d; gama moze byt zaporne; STOP ||P3 - P0|| < eps."
          " VYNIMKA: ak je d rovnobezny s u2 (stane sa, ked v 1. kroku vyjde gama = 0), smery sa"
          " nemenia - inak by boli oba smery rovnobezne a metoda by sa zasekla mimo minima (P10, P11)",
          "- **hladanie po priamke:** ak ma phi(gama) viac lokalnych minim, berie sa to s najmensim phi",
          "- **Nelder-Mead:** M = (B+G)/2, R = M + a(M-W); f(R) < f(B) -> E = M + g(R-M), E ak f(E) < f(R)"
          " inak R; f(R) < f(G) -> R; inak C1 = M + r(W-M) (prednaska aj C2 = M + r(R-M), lepsi z nich),"
          " C ak f(C) < f(W), inak zmrstenie k B. STOP d = max vzdialenost od B < eps (pred iteraciou)",
          "- **rovnost v NM:** pri rovnakom f plati vetva s nesplnenym '<'; pri zoradeni bodov s rovnakym f"
          " zostava poradie zo zadania, novy bod je pri rovnosti horsi nez stary. Cisla, ktore sa lisia"
          " len zaokruhlenim (1e-12), su rovnake (M10, M11).", ""]
    vystup, vysledky = [], {}
    metoda = None
    for p in PRIKLADY:
        r, text = spusti(p)
        vysledky[p["id"]] = na_json(r)
        vystup.append(f"{'=' * 78}\n{p['id']}: {zadanie(p)}\npasca: {p['pasca']}\n{'=' * 78}\n{text}")
        if p["metoda"] != metoda:
            metoda = p["metoda"]
            md += ["", f"## {nazvy[metoda]}", ""]
        md += [f"**{p['id']}** - {zadanie(p)}", f"  - pasca: {p['pasca']}"] + riadky_md(p, r) + [""]
        stav = r["chyba"] if "chyba" in r else f"{bod(r['bod'])} it={r['iteracie']}"
        print(f"{p['id']:4} {stav}")

    with open(os.path.join(TU, "seed_priklady.json"), "w") as f:
        json.dump(PRIKLADY, f, indent=1, ensure_ascii=False)
    with open(os.path.join(TU, "seed_vysledky.json"), "w") as f:
        json.dump(vysledky, f, indent=1, ensure_ascii=False)
    with open(os.path.join(TU, "seed_vysledky.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(TU, "seed_vystup.txt"), "w") as f:
        f.write("\n".join(vystup))
    print("\nzapisane: seed_priklady.json, seed_vysledky.json, seed_vysledky.md, seed_vystup.txt")


if __name__ == "__main__":
    main()
