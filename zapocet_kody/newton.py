# Newtonova metoda v 2D
#   X_nove = X - H^-1 * grad f
#     grad f = (df/dx, df/dy)                  prve derivacie
#     H      = [[fxx, fxy], [fyx, fyy]]        druhe derivacie (Hessova matica)
#     H^-1   = 1/det * [[d, -b], [-c, a]]      pre H = [[a, b], [c, d]], det = ad - bc
#
# STOP: ||grad f|| < eps  alebo  ||X_nove - X|| < eps
# Na konci skontroluje, ci nasiel minimum (Newton moze skoncit aj v sedle/maxime).
#
# Spustenie:  python newton.py   (priklad sa meni v sekcii NASTAVENIA nizsie)
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
FUNKCIA = "x**4/4 + x**2/2 + y**2/2"   # funkcia v uvodzovkach
START = (1, 1)              # startovaci bod (x0, y0), napr. (-1.2, 1)
EPS = 1e-3                  # presnost: 1e-3 = 0.001,  1e-4 = 0.0001
MAX_IT = 100                # najviac tolko iteracii
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
    except TypeError:           # napr. 1/0 -> nekonecno (derivacia x**(2/3) v nule)
        raise SystemExit(f"CHYBA: v bode ({P[0]:.4f}, {P[1]:.4f}) sa deli nulou "
                         f"(funkcia alebo jej derivacia tam nie je definovana).")
    if abs(v.imag) > 1e-12:     # napr. sqrt(-1) alebo x**(1/3) pre zaporne x
        raise SystemExit(f"CHYBA: v bode ({P[0]:.4f}, {P[1]:.4f}) funkcia nema realnu hodnotu "
                         f"(odmocnina zo zaporneho cisla?). Skus iny START.")
    return v.real


def main():
    f = nacitaj_funkciu(FUNKCIA)

    # prve derivacie (gradient)
    fx, fy = sp.diff(f, x), sp.diff(f, y)
    # druhe derivacie (Hessova matica H = [[fxx, fxy], [fyx, fyy]])
    fxx, fxy, fyy = sp.diff(fx, x), sp.diff(fx, y), sp.diff(fy, y)

    print("f(x, y) =")
    print(sp.pretty(f))                         # skontroluj, ci to sedi so zadanim!
    print(f"\ndf/dx = {fx}")
    print(f"df/dy = {fy}")
    print(f"H = [[{fxx}, {fxy}],")
    print(f"     [{fxy}, {fyy}]]\n")

    P = (float(START[0]), float(START[1]))
    print(f"X0 = ({P[0]:.6f}, {P[1]:.6f}),  f(X0) = {hodnota(f, P):.6f}")
    historia = []                               # vysledky iteracii (na porovnanie)

    for k in range(MAX_IT):
        # 1. gradient v bode P
        gx, gy = hodnota(fx, P), hodnota(fy, P)
        dlzka = math.sqrt(gx**2 + gy**2)
        if dlzka < EPS:                         # gradient je skoro 0 -> stacionarny bod
            stop = f"||grad f|| = {dlzka:.2e} < eps po {k} iteraciach"
            break

        # 2. Hessova matica v bode P:  H = [[a, b], [c, d]]
        a, b = hodnota(fxx, P), hodnota(fxy, P)
        c, d = b, hodnota(fyy, P)               # c = b, matica je symetricka

        # 3. determinant
        det = a * d - b * c
        if abs(det) <= 1e-14 * (a * a + b * b + c * c + d * d):   # det = 0 (aj so zaokruhlenim)
            raise SystemExit("CHYBA: det H = 0, inverzna matica neexistuje -> Newton sa neda pouzit.")

        # 4. inverzna matica (sposob B z hodin):
        #    vymenim a<->d, zmenim znamienka b a c  ->  [[d, -b], [-c, a]]
        #    vynasobim gradientom a az potom raz vydelim det
        mb, mc = -b + 0.0, -c + 0.0             # -b a -c  (+ 0.0 len aby sa nevypisovalo -0.0)
        sx = d * gx + mb * gy                   # prvy riadok [d, -b] krat (gx, gy)
        sy = mc * gx + a * gy                   # druhy riadok [-c, a] krat (gx, gy)
        krok = (sx / det, sy / det)             # = H^-1 * grad f

        # 5. novy bod:  X_nove = X - H^-1 * grad f
        P_nove = (P[0] - krok[0], P[1] - krok[1])

        print(f"\n--- iteracia {k + 1} ---")
        print(f"grad f(X{k}) = ({gx:.6f}, {gy:.6f})")
        print(f"H(X{k}) = [[{a:.6f}, {b:.6f}], [{c:.6f}, {d:.6f}]]")
        print(f"det H = {det:.6f}")
        print(f"vymenena matica [[d, -b], [-c, a]] = [[{d:.6f}, {mb:.6f}], [{mc:.6f}, {a:.6f}]]")
        print(f"[[d, -b], [-c, a]] * grad = ({sx:.6f}, {sy:.6f})")
        print(f"H^-1 * grad = ({sx:.6f}, {sy:.6f}) / {det:.6f} = ({krok[0]:.6f}, {krok[1]:.6f})")
        print(f"X{k + 1} = X{k} - H^-1*grad = ({P_nove[0]:.6f}, {P_nove[1]:.6f}),  "
              f"f(X{k + 1}) = {hodnota(f, P_nove):.6f}")

        historia.append({"grad": (gx, gy), "det": det, "krok": krok, "P": P_nove})
        posun = math.dist(P, P_nove)
        P = P_nove
        if posun < EPS:                         # bod sa uz takmer nehybe
            stop = f"||X{k + 1} - X{k}|| = {posun:.2e} < eps po {k + 1} iteraciach"
            k += 1
            break
    else:
        k = MAX_IT
        stop = f"dosiahnuty MAX_IT = {MAX_IT} (este nie je v minime)"
    print(f"\nSTOP: {stop}")

    # Newton hlada bod, kde grad f = 0 -> moze to byt aj maximum alebo sedlo!
    a, b, d = hodnota(fxx, P), hodnota(fxy, P), hodnota(fyy, P)
    det = a * d - b * b
    if det > 0 and a > 0:
        typ = "MINIMUM (det H > 0, fxx > 0)"
    elif det > 0 and a < 0:
        typ = "MAXIMUM (det H > 0, fxx < 0)  -> Newton nasiel maximum, nie minimum!"
    elif det < 0:
        typ = "SEDLO (det H < 0)  -> Newton nasiel sedlo, nie minimum!"
    else:
        typ = "neda sa rozhodnut (det H = 0)"

    print(f"\nVYSLEDOK: bod ({P[0]:.6f}, {P[1]:.6f}),  f = {hodnota(f, P):.6f}")
    print(f"typ bodu: {typ}")
    return {"bod": P, "f": hodnota(f, P), "iteracie": k, "stop": stop, "typ": typ.split(" (")[0],
            "historia": historia}


if __name__ == "__main__":
    main()
