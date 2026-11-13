# Powellova metoda (bez derivacii funkcie f)
#   Jedna iteracia:
#     1. z bodu P0 hladam minimum po priamke v smere u1  -> P1
#     2. z bodu P1 hladam minimum po priamke v smere u2  -> P2
#     3. novy smer d = P2 - P0, z P2 hladam minimum po d  -> P3
#     4. posuniem smery: u1 <- u2,  u2 <- d;  P3 je novy P0
#        (vynimka: ak je d rovnobezny s u2 - stane sa pri gama = 0 v kroku 1 -
#         smery nemenim, inak by boli oba rovnobezne a metoda by sa zasekla)
#   Na zaciatku u1 = (1, 0), u2 = (0, 1).
#
#   Hladanie po priamke (ako na papieri):
#     x = Px + gama*ux,  y = Py + gama*uy  ->  phi(gama),  phi'(gama) = 0
#     smery NIE su normovane a gama MOZE byt aj zaporne
#
# STOP: ||P3 - P0|| < eps  (za celu iteraciu sa bod takmer nepohol)
# Na kvadratickej funkcii najde presne minimum po 2 iteraciach.
#
# Spustenie:  python powell.py   (priklad sa meni v sekcii NASTAVENIA nizsie)
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
FUNKCIA = "x**2 - 4*x + y**2 - y - x*y"   # funkcia v uvodzovkach
START = (0, 0)              # startovaci bod (x0, y0), napr. (-1.2, 1)
EPS = 1e-3                  # presnost: 1e-3 = 0.001,  1e-4 = 0.0001
MAX_IT = 100                # najviac tolko iteracii
# =============================================================================


x, y = sp.symbols("x y", real=True)      # real=True: aby abs(x) a odmocniny fungovali
gama = sp.symbols("gama")


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
    except TypeError:           # napr. 1/0 -> nekonecno (derivacia x**(2/3) v nule)
        raise SystemExit(f"CHYBA: v bode ({P[0]:.4f}, {P[1]:.4f}) sa deli nulou "
                         f"(funkcia alebo jej derivacia tam nie je definovana).")
    if abs(v.imag) > 1e-12:     # napr. sqrt(-1) alebo x**(1/3) pre zaporne x
        raise SystemExit(f"CHYBA: v bode ({P[0]:.4f}, {P[1]:.4f}) funkcia nema realnu hodnotu "
                         f"(odmocnina zo zaporneho cisla?). Skus iny START.")
    return v.real


def zlaty_rez(phi, a, b, presnost=1e-12):
    """Najde minimum funkcie phi na intervale [a, b] (pre nepolynomialne funkcie)."""
    k = (math.sqrt(5) - 1) / 2                  # 0.618...
    while b - a > presnost * max(1.0, abs(a) + abs(b)):
        t1, t2 = b - k * (b - a), a + k * (b - a)
        if phi(t1) < phi(t2):
            b = t2
        else:
            a = t1
    return (a + b) / 2


def presne_minimum(phi_n, dphi_n, a, b):
    """Minimum phi na [a, b]: zlatym rezom ho najdem priblizne (na ~1e-8),
    potom rovnicu phi'(gama) = 0 dopresnim bisekciou (na ~1e-15)."""
    g = zlaty_rez(phi_n, a, b)
    h = 1e-6 * (1 + abs(g))
    lo, hi = g - h, g + h
    if dphi_n(lo) < 0 < dphi_n(hi):             # phi' meni znamienko z - na + -> minimum
        for _ in range(200):
            s = (lo + hi) / 2
            if dphi_n(s) < 0:
                lo = s
            else:
                hi = s
            if hi - lo < 1e-15 * (1 + abs(s)):
                break
        return (lo + hi) / 2
    return g


def cislo_funkcia(vyraz):
    """Zo sympy vyrazu v premennej gama spravi obycajnu funkciu (mimo def. oboru = inf)."""
    fn = sp.lambdify(gama, vyraz, "math")

    def hodnota_v(t):
        try:
            v = fn(t)
            return float(v) if not isinstance(v, complex) else math.inf
        except (ValueError, TypeError, ZeroDivisionError, OverflowError):
            return math.inf                     # mimo def. oboru (napr. sqrt zo zaporneho)
    return hodnota_v


def ocisti_polynom(phi):
    """Zmaze koeficienty, ktore su len zaokruhlovacie smeti (napr. 1e-17*gama**3)."""
    poly = sp.Poly(phi, gama)
    velke = [abs(c) for (st,), c in poly.terms() if st > 0]
    hranica = 1e-12 * max(velke) if velke else 0
    return sum((c * gama**st for (st,), c in poly.terms() if st == 0 or abs(c) > hranica), sp.S(0))


def minima_polynomu(phi):
    """Vrati vsetky gama, kde ma polynom phi(gama) lokalne minimum (ako na papieri:
    phi' = 0, a z korenov nechame len tie, kde je okolo phi vyssie)."""
    dphi = sp.diff(phi, gama)
    if sp.degree(dphi, gama) < 1:               # phi je konstanta alebo priamka
        return []
    korene = sp.Poly(dphi, gama).nroots(n=30, maxsteps=500)
    realne = sorted(float(sp.re(r)) for r in korene if abs(sp.im(r)) < 1e-4 * (1 + abs(sp.re(r))))
    # viacnasobny koren (napr. (gama - 1)**3 pri x**4) sa pri zaokruhlovani rozpadne
    # na niekolko blizkych korenov -> spojim ich do jedneho (priemer)
    zhluky = []
    for r in realne:
        if zhluky and abs(r - zhluky[-1][-1]) < 1e-4 * (1 + abs(r)):
            zhluky[-1].append(r)
        else:
            zhluky.append([r])
    phi_n = sp.lambdify(gama, phi, "math")
    minima = []
    for z in zhluky:
        r = sum(z) / len(z)
        h = 1e-3 * (1 + abs(r))
        if phi_n(r - h) >= phi_n(r) and phi_n(r + h) >= phi_n(r):   # okolo je vyssie -> minimum
            minima.append(r)
    return minima


def po_priamke(f, P, u):
    """Hladanie po priamke z bodu P v smere u. Vrati gama, phi a novy bod."""
    # 1. dosadenie priamky: x = Px + gama*ux,  y = Py + gama*uy
    phi = sp.expand(f.subs({x: P[0] + gama * u[0], y: P[1] + gama * u[1]}, simultaneous=True))

    if phi.is_polynomial(gama):
        # 2. polynom (ako na papieri): phi'(gama) = 0, korene, necham len minima phi
        phi = ocisti_polynom(phi)
        if sp.degree(phi, gama) < 1:            # phi je na tejto priamke konstantna
            return 0.0, phi, P
        kandidati = minima_polynomu(phi)        # gama moze byt kladne aj ZAPORNE
        if not kandidati:
            raise SystemExit("CHYBA: phi(gama) nema minimum - funkcia na priamke klesa "
                             "do -nekonecna (funkcia nema minimum).")
        # ak je minim viac, vyberiem to s najmensim phi (pri rovnosti to blizsie k 0)
        g = min(kandidati, key=lambda r: (round(float(phi.subs(gama, r)), 12), abs(r), -r))
    else:
        # 3. nie je polynom (sqrt, exp, zlomok...) -> minimum najdem numericky
        phi_n = cislo_funkcia(phi)
        dphi_n = cislo_funkcia(sp.diff(phi, gama))

        h = 1e-3
        if phi_n(-h) < phi_n(h):                # funkcia klesa dozadu -> idem zapornym smerom
            h = -h
        while phi_n(2 * h) < phi_n(h):          # zvacsujem krok, kym phi klesa
            h *= 2
            if abs(h) > 1e8:
                raise SystemExit("CHYBA: phi(gama) stale klesa - funkcia na priamke nema minimum.")
        g = presne_minimum(phi_n, dphi_n, min(-abs(h), 2 * h), max(abs(h), 2 * h))

    return g, phi, (P[0] + g * u[0], P[1] + g * u[1])


def vypis_hladanie(nazov, start, smer, g, phi, ciel):
    print(f"  {start} -> {ciel} v smere {nazov} = ({smer[0]:.6f}, {smer[1]:.6f})")
    print(f"     phi(gama) = {sp.N(phi, 6)}")
    print(f"     gama = {g:.6f}")


def main():
    f = nacitaj_funkciu(FUNKCIA)
    print("f(x, y) =")
    print(sp.pretty(f))                         # skontroluj, ci to sedi so zadanim!
    print()

    P0 = (float(START[0]), float(START[1]))
    u1, u2 = (1.0, 0.0), (0.0, 1.0)             # zaciatocne smery = osi x a y
    print(f"start P0 = ({P0[0]:.6f}, {P0[1]:.6f}),  f = {hodnota(f, P0):.6f}")
    historia = []                               # vysledky iteracii (na porovnanie)

    for k in range(MAX_IT):
        print(f"\n--- iteracia {k + 1} ---")

        # 1. P0 -> P1 v smere u1
        g, phi, P1 = po_priamke(f, P0, u1)
        vypis_hladanie("u1", "P0", u1, g, phi, "P1")
        print(f"     P1 = ({P1[0]:.6f}, {P1[1]:.6f}),  f(P1) = {hodnota(f, P1):.6f}")

        # 2. P1 -> P2 v smere u2
        g, phi, P2 = po_priamke(f, P1, u2)
        vypis_hladanie("u2", "P1", u2, g, phi, "P2")
        print(f"     P2 = ({P2[0]:.6f}, {P2[1]:.6f}),  f(P2) = {hodnota(f, P2):.6f}")

        # 3. novy smer d = P2 - P0 a P2 -> P3 v smere d
        d = (P2[0] - P0[0], P2[1] - P0[1])
        if math.hypot(*d) < 1e-14:              # P2 = P0, nie je kam ist
            P3 = P2
            print("  d = (0, 0) -> bod sa nepohol")
        else:
            g, phi, P3 = po_priamke(f, P2, d)
            print(f"  d = P2 - P0 = ({d[0]:.6f}, {d[1]:.6f})")
            vypis_hladanie("d", "P2", d, g, phi, "P3")
            print(f"     P3 = ({P3[0]:.6f}, {P3[1]:.6f}),  f(P3) = {hodnota(f, P3):.6f}")

            # 4. posunutie smerov: u1 <- u2, u2 <- d
            #    POZOR: ak v kroku 1 vyslo gama = 0 (P1 = P0), je d rovnobezny s u2.
            #    Potom by u1 a u2 boli rovnobezne, metoda by chodila stale po jednej
            #    priamke a zasekla by sa MIMO minima -> v takom pripade smery nemenim.
            if abs(u2[0] * d[1] - u2[1] * d[0]) <= 1e-12 * math.hypot(*u2) * math.hypot(*d):
                print("  d je rovnobezny s u2 -> smery NEMENIM (inak by sa metoda zasekla)")
            else:
                u1, u2 = u2, d
                print(f"  nove smery: u1 = ({u1[0]:.6f}, {u1[1]:.6f}),  u2 = ({u2[0]:.6f}, {u2[1]:.6f})")

        historia.append({"P1": P1, "P2": P2, "d": d, "P3": P3})
        posun = math.dist(P0, P3)
        P0 = P3                                 # P3 je startom dalsej iteracie
        if posun < EPS:
            stop = f"||P3 - P0|| = {posun:.2e} < eps po {k + 1} iteraciach"
            k += 1
            break
    else:
        k = MAX_IT
        stop = f"dosiahnuty MAX_IT = {MAX_IT} (este nie je v minime)"

    print(f"\nSTOP: {stop}")
    print(f"\nVYSLEDOK: minimum v ({P0[0]:.6f}, {P0[1]:.6f}),  f = {hodnota(f, P0):.6f}")
    return {"bod": P0, "f": hodnota(f, P0), "iteracie": k, "stop": stop, "historia": historia}


if __name__ == "__main__":
    main()
