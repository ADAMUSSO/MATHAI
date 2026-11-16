# Metoda najstrmsieho zostupu (steepest descent)
#   - smer BEZ normovania:      S = -grad f
#     (NORMOVAT = True ->       S = -grad f / ||grad f||)
#   - krok gama hladame presne:  phi(gama) = f(P + gama*S),  phi'(gama) = 0
#   - novy bod:                  P_nove = P + gama*S
#
# STOP: ||grad f|| < eps  (gradient je takmer nulovy -> sme v minime)
#   (podmienka ||P_nove - P|| < eps tu NESTACI: v uzkom udoli su kroky male
#    aj daleko od minima a metoda by zastala predcasne)
#
# Spustenie:  python gradient.py   (priklad sa meni v sekcii NASTAVENIA nizsie)
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
FUNKCIA = "3*(x+2)**2+0.2*(y-1)**2+0.5*(x+2)*(y-1)+(x+2)**2*(y-1)**2"   # funkcia v uvodzovkach
START = (0,3)              # startovaci bod (x0, y0), napr. (-1.2, 1)
EPS = 10e-8                  # presnost: 1e-3 = 0.001,  1e-4 = 0.0001
MAX_IT = 20000                # najviac tolko iteracii
NORMOVAT = False              # False: S = -grad,   True: S = -grad/||grad||
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


def najdi_gamu(f, P, S):
    """Najde gama > 0, kde je phi(gama) = f(P + gama*S) najmensie.
    Ked S nie je normovany (S = -grad), je pri minime velmi kratky a phi ma
    drobne koeficienty (1e-24...) -> korene by sa nenasli. Preto gama hladam
    v smere dlzky 1 a prepocitam: gama = gama_jednotkove / ||S||  (ten isty bod)."""
    d = math.hypot(S[0], S[1])
    g, phi = najdi_gamu_jednotkovy(f, P, (S[0] / d, S[1] / d))
    if d != 1:
        phi = sp.expand(f.subs({x: P[0] + gama * S[0], y: P[1] + gama * S[1]}, simultaneous=True))
    return g / d, phi


def najdi_gamu_jednotkovy(f, P, S):
    """Dosadi priamku do f a najde gama > 0, kde je phi(gama) najmensie."""
    # 1. dosadenie priamky: x = Px + gama*Sx,  y = Py + gama*Sy
    phi = sp.expand(f.subs({x: P[0] + gama * S[0], y: P[1] + gama * S[1]}, simultaneous=True))

    if phi.is_polynomial(gama):
        # 2. polynom (ako na papieri): phi'(gama) = 0, korene, necham len minima phi
        phi = ocisti_polynom(phi)
        kandidati = [r for r in minima_polynomu(phi) if r > 0]   # ideme v smere S -> gama > 0
        if not kandidati:
            raise SystemExit("CHYBA: phi(gama) nema minimum - funkcia v smere S klesa "
                             "do -nekonecna (funkcia nema minimum).")
        # ak je minim viac (napr. pri x**4), vyberiem to s najmensim phi (pri rovnosti blizsie)
        return min(kandidati, key=lambda r: (round(float(phi.subs(gama, r)), 12), r)), phi

    # 3. nie je polynom (sqrt, exp, zlomok...) -> phi'(gama) = 0 sa neda vyriesit
    #    vzorcom, tak minimum najdem numericky zlatym rezom
    phi_n = cislo_funkcia(phi)
    dphi_n = cislo_funkcia(sp.diff(phi, gama))

    h = 1e-3
    while phi_n(2 * h) < phi_n(h):              # zvacsujem krok, kym phi klesa
        h *= 2
        if h > 1e8:
            raise SystemExit("CHYBA: phi(gama) stale klesa - funkcia v smere S nema minimum.")
    return presne_minimum(phi_n, dphi_n, 0, 2 * h), phi


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


def main():
    f = nacitaj_funkciu(FUNKCIA)
    fx, fy = sp.diff(f, x), sp.diff(f, y)       # parcialne derivacie
    print("f(x, y) =")
    print(sp.pretty(f))                         # skontroluj, ci to sedi so zadanim!
    print(f"\ndf/dx = {fx}")
    print(f"df/dy = {fy}\n")

    P = (float(START[0]), float(START[1]))
    print(f"P0 = ({P[0]:.6f}, {P[1]:.6f}),  f(P0) = {hodnota(f, P):.6f}")
    historia = []                               # vysledky iteracii (na porovnanie)

    for k in range(MAX_IT):
        # gradient v bode P
        gx, gy = hodnota(fx, P), hodnota(fy, P)
        dlzka = math.sqrt(gx**2 + gy**2)
        if dlzka < EPS:                         # gradient je skoro 0 -> sme v minime
            stop = f"||grad f|| = {dlzka:.2e} < eps po {k} iteraciach"
            break

        # smer najvacsieho klesania (normovany len ak NORMOVAT = True)
        S = (-gx / dlzka, -gy / dlzka) if NORMOVAT else (-gx, -gy)

        # presne hladanie po priamke
        g, phi = najdi_gamu(f, P, S)

        # novy bod
        P_nove = (P[0] + g * S[0], P[1] + g * S[1])

        print(f"\n--- iteracia {k + 1} ---")
        print(f"grad f(P{k}) = ({gx:.6f}, {gy:.6f}),  ||grad|| = {dlzka:.6f}")
        print(f"S{k} = ({S[0]:.6f}, {S[1]:.6f})")
        print(f"phi(gama) = {sp.N(phi, 6)}")
        print(f"gama = {g:.6f}")
        print(f"P{k + 1} = ({P_nove[0]:.6f}, {P_nove[1]:.6f}),  f(P{k + 1}) = {hodnota(f, P_nove):.6f}")
        historia.append({"grad": (gx, gy), "S": S, "gama": g, "P": P_nove})

        P = P_nove
    else:
        k = MAX_IT
        stop = f"dosiahnuty MAX_IT = {MAX_IT} (este nie je v minime)"

    print(f"\nSTOP: {stop}")
    print(f"\nVYSLEDOK: minimum v ({P[0]:.6f}, {P[1]:.6f}),  f = {hodnota(f, P):.6f}")
    return {"bod": P, "f": hodnota(f, P), "iteracie": k, "stop": stop, "historia": historia}


if __name__ == "__main__":
    main()
