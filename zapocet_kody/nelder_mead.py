# Nelder-Mead (bez derivacii, len dosadzanie do f)
#   B = najlepsi bod (najmensie f), G = dobry (stredne f), W = najhorsi (najvacsie f)
#   (na cviceni: A = najlepsi, B = dobry, C = najhorsi, x0 = M - vzorce su rovnake)
#
#   M  = (B + G) / 2                stred strany oproti W
#   R  = M + alfa*(M - W)           reflexia     (alfa = 1   ->  R = 2M - W)
#   E  = M + gama*(R - M)           expanzia     (gama = 2   ->  E = 2R - M)
#   C1 = M + rho*(W - M)            kontrakcia   (rho = 0.5  ->  C1 = (W + M)/2)
#   C2 = M + rho*(R - M)            (len prednaska)            C2 = (M + R)/2
#   zmrstenie k B: kazdy bod P -> B + sigma*(P - B)   (sigma = 0.5 -> S = (W+B)/2, M)
#
#   Pripad 1: f(R) < f(B)          -> skusim E: ak f(E) < f(R) beriem E, inak R
#   Pripad 2: f(B) <= f(R) < f(G)  -> beriem R
#   Pripad 3: f(R) >= f(G)         -> kontrakcia C: ak f(C) < f(W) beriem C, inak zmrstenie
#
# STOP: d = najvacsia vzdialenost vrcholu od B < eps  -> vysledok je B
#
# ROVNOST: pri rovnakom f (aj f(R) = f(G) a pod.) plati vzdy ta vetva, kde je '<'
#   nesplnene; pri zoradovani bodov s rovnakym f zostava poradie zo zadania
#   a novy bod je pri rovnosti horsi nez stary.
#
# Spustenie:  python nelder_mead.py   (priklad sa meni v sekcii NASTAVENIA nizsie)
import math
import sympy as sp


# =============================================================================
#  NASTAVENIA - TU ZADAJ PRIKLAD
# =============================================================================
#
#  AKO NAPISAT FUNKCIU (premenne su len x a y):
#
#    co chcem               ako napisem               poznamka
#    ---------------------  ------------------------  ---------------------------
#    x na druhu             x**2                      (ide aj x^2)
#    x na tretiu            x**3
#    x na minus prvu        x**(-1)                   = 1/x
#    krat                   2*x,  x*y,  3*x*y         2x NEJDE, vzdy pis *
#    deleno                 x/2,  1/x
#    zlomok (cislo)         3/4*x,  (1/2)*x**2        zlomok ostane presny (3/4)
#    zlomok (vyraz)         (x + 1)/(y - 2)           CITATEL aj MENOVATEL do ( )
#    zlomok na druhu        ((x + 1)/(y - 2))**2      cely zlomok este raz do ( )
#    zlozeny zlomok         (1/(x + 1))/(1 + 1/y)     kazde poschodie do ( )
#    odmocnina              sqrt(x)                   alebo x**(1/2)
#    tretia odmocnina       cbrt(x)                   alebo x**(1/3), root(x, 3)
#    n-ta odmocnina z x^m   x**(m/n)                  napr. x**(2/3)
#    3. odmocnina zo zap.   real_root(x, 3)           cbrt(-8) by NEdalo -2
#    odmocnina z vyrazu     sqrt(x**2 + y**2)
#    e na x                 exp(x)                    alebo E**x (VELKE E!)
#                                                     e**x NEJDE (male e = premenna)
#    e na vyraz             exp(x**2 + y)
#    2 na x                 2**x
#    prirodzeny logaritmus  log(x)                    alebo ln(x)
#    logaritmus so zakl. 10 log(x, 10)
#    absolutna hodnota      abs(x)
#    sinus, kosinus         sin(x), cos(x), tan(x)    v radianoch
#    pi                     pi
#    desatinne cislo        0.5*x                     BODKA, nie ciarka (0,5 NEJDE)
#    zatvorky               len okruhle ( )           [ ] a { } NEJDU
#
#  PRIKLADY CELYCH FUNKCII:
#    "x**2 + 2*y**2"
#    "x**2 - 4*x + y**2 - y - x*y"
#    "x**4/4 + x**2/2 + y**2/2"
#    "(1 - x)**2 + 100*(y - x**2)**2"          (Rosenbrock)
#    "(x**2 + y - 11)**2 + (x + y**2 - 7)**2"  (Himmelblau)
#    "sqrt(x**2 + 1) + (y - 2)**2"
#    "exp(x**2 + y**2) - 2*x"
#
FUNKCIA = "x**2 + y**2 + x - 2*y - x*y + 2"     # funkcia v uvodzovkach
BODY = [(1.2, 0), (0, 0.8), (0, 0)]   # 3 startovacie body trojuholnika (poradie je jedno)
ALFA = 1                    # reflexia
GAMA = 2                    # expanzia
RHO = 0.5                   # kontrakcia
SIGMA = 0.5                 # zmrstenie
KONTRAKCIA = "prednaska"    # "prednaska" = C1 aj C2, beriem ten s mensim f
                            # "cvicenie"  = len C1 = M + rho*(W - M)
EPS = 1e-3                  # presnost: 1e-3 = 0.001,  1e-4 = 0.0001
MAX_IT = 200                # najviac tolko iteracii
KRESLIT = 200                 # nakresli trojuholniky prvych KRESLIT iteracii (0 = nekreslit)
# =============================================================================


x, y = sp.symbols("x y", real=True)      # real=True: aby abs(x) a odmocniny fungovali


def nacitaj_funkciu(text):
    """Prelozi text na sympy vyraz a skontroluje, ze obsahuje len x a y."""
    try:
        f = sp.sympify(text, locals={"x": x, "y": y})
    except sp.SympifyError:
        raise SystemExit(f"CHYBA: funkciu '{text}' sa neda precitat. Chyba * (2*x) alebo zatvorka?")
    ine = f.free_symbols - {x, y}
    if ine:
        raise SystemExit(f"CHYBA: vo funkcii su nezname premenne {ine}. "
                         f"(e na x sa pise exp(x), nie e**x)")
    return f


def hodnota(vyraz, P):
    """Dosadi bod P = (x, y) do vyrazu a vrati cislo."""
    try:
        v = complex(vyraz.subs({x: P[0], y: P[1]}).evalf(30))
    except TypeError:           # napr. 1/0 -> nekonecno
        raise SystemExit(f"CHYBA: v bode ({P[0]:.4f}, {P[1]:.4f}) sa deli nulou "
                         f"(funkcia tam nie je definovana).")
    if abs(v.imag) > 1e-12:     # napr. sqrt(-1) alebo x**(1/3) pre zaporne x
        raise SystemExit(f"CHYBA: v bode ({P[0]:.4f}, {P[1]:.4f}) funkcia nema realnu hodnotu "
                         f"(odmocnina zo zaporneho cisla?). Skus ine BODY.")
    return v.real


# --- pocitanie s bodmi po suradniciach (x zvlast, y zvlast) -------------------
def rozdiel(P, Q):
    """P - Q  (sipka od Q k P)"""
    return (P[0] - Q[0], P[1] - Q[1])


def posun(P, k, smer):
    """P + k*smer  (zacnem v P a prejdem k-krat sipku smer)"""
    return (P[0] + k * smer[0], P[1] + k * smer[1])


def txt(P):
    return f"({P[0]:.6f}, {P[1]:.6f})"


def mensie(a, b):
    """a < b, ale cisla, ktore sa lisia len zaokruhlenim (napr. 1.0000000000000002 a 1),
    berie ako ROVNAKE. Inak by 0.1 + 0.2 != 0.3 zmenilo pripad oproti papieru."""
    return a < b - 1e-12 * max(1.0, abs(a), abs(b))


def zorad(body):
    """Zoradi body podla f (B, G, W). Pri ROVNAKOM f zostava povodne poradie:
    na zaciatku poradie zo zadania, novy bod je pri rovnosti horsi nez stary."""
    vysledok = []
    for p in body:
        i = len(vysledok)
        while i > 0 and mensie(p[1], vysledok[i - 1][1]):
            i -= 1
        vysledok.insert(i, p)
    return vysledok


def main():
    f = nacitaj_funkciu(FUNKCIA)
    print("f(x, y) =")
    print(sp.pretty(f))                         # skontroluj, ci to sedi so zadanim!
    print(f"\nalfa = {ALFA}, gama = {GAMA}, rho = {RHO}, sigma = {SIGMA}, kontrakcia: {KONTRAKCIA}")
    if KONTRAKCIA not in ("cvicenie", "prednaska"):
        raise SystemExit('CHYBA: KONTRAKCIA musi byt "cvicenie" alebo "prednaska".')

    # body ukladam spolu s hodnotou f:  [(bod, f(bod)), ...]
    body = [((float(P[0]), float(P[1])), hodnota(f, P)) for P in BODY]
    trojuholniky = []                           # na kreslenie
    historia = []                               # vysledky iteracii (na porovnanie)

    for k in range(MAX_IT):
        # 1. zoradenie podla f: B (najlepsi), G (dobry), W (najhorsi)
        body = zorad(body)
        (B, fB), (G, fG), (W, fW) = body
        trojuholniky.append((B, G, W))

        # STOP: najvacsia vzdialenost vrcholu od B
        d = max(math.dist(B, G), math.dist(B, W))
        if d < EPS:
            stop = f"d = {d:.2e} < eps po {k} iteraciach"
            break

        print(f"\n--- iteracia {k + 1} ---")
        print(f"  B = {txt(B)},  f(B) = {fB:.6f}")
        print(f"  G = {txt(G)},  f(G) = {fG:.6f}")
        print(f"  W = {txt(W)},  f(W) = {fW:.6f}")
        print(f"  d = {d:.6f}  (>= eps -> pokracujem)")

        # 2. stred a reflexia
        M = ((B[0] + G[0]) / 2, (B[1] + G[1]) / 2)
        R = posun(M, ALFA, rozdiel(M, W))       # R = M + alfa*(M - W)
        fR = hodnota(f, R)
        print(f"  M = {txt(M)}")
        print(f"  R = {txt(R)},  f(R) = {fR:.6f}")

        # 3. rozhodnutie podla f(R)
        if mensie(fR, fB):
            # Pripad 1: R je lepsi nez najlepsi -> skusim ist este dalej
            E = posun(M, GAMA, rozdiel(R, M))   # E = M + gama*(R - M)
            fE = hodnota(f, E)
            print(f"  pripad 1: f(R) < f(B) -> expanzia E = {txt(E)},  f(E) = {fE:.6f}")
            if mensie(fE, fR):
                body[2], krok = (E, fE), "expanzia E"
                print("  f(E) < f(R) -> W nahradim bodom E")
            else:
                body[2], krok = (R, fR), "reflexia R (E nepomohol)"
                print("  f(E) >= f(R) -> W nahradim bodom R")

        elif mensie(fR, fG):
            # Pripad 2: R je slusny -> beriem R
            body[2], krok = (R, fR), "reflexia R"
            print("  pripad 2: f(B) <= f(R) < f(G) -> W nahradim bodom R")

        else:
            # Pripad 3: R nepomohol -> kontrakcia
            C1 = posun(M, RHO, rozdiel(W, M))   # C1 = M + rho*(W - M)
            fC1 = hodnota(f, C1)
            print(f"  pripad 3: f(R) >= f(G) -> kontrakcia")
            print(f"  C1 = {txt(C1)},  f(C1) = {fC1:.6f}")
            C, fC, meno = C1, fC1, "C1"
            if KONTRAKCIA == "prednaska":
                C2 = posun(M, RHO, rozdiel(R, M))   # C2 = M + rho*(R - M)
                fC2 = hodnota(f, C2)
                print(f"  C2 = {txt(C2)},  f(C2) = {fC2:.6f}")
                if mensie(fC2, fC1):            # pri rovnosti necham C1
                    C, fC, meno = C2, fC2, "C2"
                print(f"  lepsi je {meno}")

            if mensie(fC, fW):
                body[2], krok = (C, fC), f"kontrakcia {meno}"
                print(f"  f({meno}) < f(W) -> W nahradim bodom {meno}")
            else:
                # zmrstenie: G a W sa posunu do polovice k B
                S = posun(B, SIGMA, rozdiel(W, B))       # S = B + sigma*(W - B)
                M2 = posun(B, SIGMA, rozdiel(G, B))      # pri sigma = 0.5 je to M
                body = [(B, fB), (M2, hodnota(f, M2)), (S, hodnota(f, S))]
                krok = "zmrstenie"
                print(f"  f({meno}) >= f(W) -> zmrstenie k B: S = {txt(S)}, M = {txt(M2)}")

        print(f"  novy trojuholnik: {txt(body[0][0])}, {txt(body[1][0])}, {txt(body[2][0])}")
        historia.append({"B": B, "G": G, "W": W, "M": M, "R": R, "fR": fR, "krok": krok,
                         "trojuholnik": [p[0] for p in body]})
    else:
        body = zorad(body)
        k = MAX_IT
        stop = f"dosiahnuty MAX_IT = {MAX_IT} (este nie je v minime)"

    B, fB = body[0]
    print(f"\nSTOP: {stop}")
    print(f"\nVYSLEDOK: minimum v {txt(B)},  f = {fB:.6f}")

    if KRESLIT > 0:
        nakresli(f, trojuholniky[:KRESLIT + 1], B)
    return {"bod": B, "f": fB, "iteracie": k, "stop": stop, "historia": historia}


def nakresli(f, trojuholniky, B):
    """Vrstevnice funkcie a trojuholniky prvych iteracii (ako na papieri)."""
    import numpy as np
    import matplotlib.pyplot as plt

    vsetky = [P for t in trojuholniky for P in t] + [B]
    xs, ys = [P[0] for P in vsetky], [P[1] for P in vsetky]
    okraj = 0.3 * max(max(xs) - min(xs), max(ys) - min(ys), 1)
    X, Y = np.meshgrid(np.linspace(min(xs) - okraj, max(xs) + okraj, 200),
                       np.linspace(min(ys) - okraj, max(ys) + okraj, 200))
    Z = sp.lambdify((x, y), f, "numpy")(X, Y) * np.ones_like(X)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.contour(X, Y, Z, levels=25, cmap="viridis", linewidths=0.6)
    for i, (P1, P2, P3) in enumerate(trojuholniky):
        tx, ty = [P1[0], P2[0], P3[0], P1[0]], [P1[1], P2[1], P3[1], P1[1]]
        ax.plot(tx, ty, "-o", label=f"po iteracii {i}" if i else "start")
    ax.plot(*B, "r*", markersize=14, label="vysledok")
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    ax.set_title("Nelder-Mead: trojuholniky")
    fig.savefig("nelder_mead_trojuholniky.png", dpi=130)
    print("obrazok ulozeny: nelder_mead_trojuholniky.png")
    plt.show()


if __name__ == "__main__":
    main()
