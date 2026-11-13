# NEWTONOVA METODA 2D - jednoducha verzia, kroky ako na papieri
#
#   1. grad f(X) = (fx, fy)                    STOP ak ||grad|| < eps
#   2. H(X) = | fxx  fxy |  = | a  b |         Hessova matica v bode X
#             | fyx  fyy |    | c  d |
#   3. det H = a*d - b*c                       ak det = 0, Newton sa neda pouzit
#   4. sposob B:  | d  -b |  krat grad,  potom vydelim det   ->  krok = H^-1 * grad
#                 | -c  a |
#   5. X_nove = X - krok                       STOP ak ||krok|| < eps
#   Na konci: det > 0 a fxx > 0 -> MINIMUM,  det > 0 a fxx < 0 -> MAXIMUM,  det < 0 -> SEDLO
#
# Pocita sa na 50 platnych cifier, takze zaokruhlovanie vysledok nepokazi.
# DESATINNE = na kolko desatinnych miest zaokruhlim VYSLEDOK (5 a viac nahor);
# vypocet aj vsetky kroky idu stale v plnej presnosti.

from decimal import ROUND_HALF_UP, Decimal

import sympy as sp
from sympy.parsing.sympy_parser import (convert_xor, implicit_multiplication_application,
                                        parse_expr, standard_transformations)

# ============================== ZADANIE ===============================
#  Funkciu pis ako na papieri (premenne su x a y):
#    x^2   x^3   (alebo x**2)          na druhu, na tretiu
#    2x   xy   3xy^2                   krat netreba pisat
#    (x + 1)/(y - 2)                   zlomok: citatel aj menovatel do ( )
#    3/4x^2                            = (3/4)*x^2
#    sqrt(x^2 + 1)   cbrt(x)           odmocnina, tretia odmocnina
#    e^(x + y)   exp(x + y)            e na nieco
#    ln(x)   abs(x)   sin(x)   pi      logaritmus, abs. hodnota, ...
#    0.5x                              desatinna BODKA (nie ciarka)
FUNKCIA = "(x+2)**2 + (y-1)**2 + (x*y)/2"
START = (3, -2)           # zaciatocny bod X0 = (x, y)
EPS = 0.001              # STOP ked ||grad f|| < EPS alebo ||X_nove - X|| < EPS
MAX_IT = 100             # najviac tolko iteracii
DESATINNE = 5            # VYSLEDOK zaokruhlim na tolko desatinnych miest
                         # (len konecny vypis - vypocet sa tym nemeni)
# ======================================================================

CIFRY = 50
x, y = sp.symbols("x y", real=True)


def nacitaj_funkciu(text):
    """Text funkcie -> sympy vyraz (desatinne cisla sa zmenia na presne zlomky)."""
    pravidla = standard_transformations + (implicit_multiplication_application, convert_xor)
    try:
        f = parse_expr(text, local_dict={"x": x, "y": y, "e": sp.E, "ln": sp.log},
                       transformations=pravidla)
    except Exception:
        raise SystemExit(f"CHYBA: funkciu '{text}' neviem precitat - skontroluj zatvorky.")
    if f.free_symbols - {x, y}:
        raise SystemExit(f"CHYBA: vo funkcii su nezname pismena {f.free_symbols - {x, y}}.")
    return sp.nsimplify(f, rational=True)


def hodnota(vyraz, P):
    """Dosadi bod P = (x, y) do vyrazu a vrati cislo (50 cifier)."""
    v = vyraz.subs({x: P[0], y: P[1]}).evalf(CIFRY)
    if v.is_real is not True:
        raise SystemExit(f"CHYBA: v bode ({float(P[0]):g}, {float(P[1]):g}) sa to neda vypocitat.")
    return v


def zaokruhli(v):
    """Cislo zaokruhlene na DESATINNE miest (5 a viac nahor) - len na vypis vysledku."""
    d = Decimal(str(sp.Float(v, 60))).quantize(Decimal(1).scaleb(-DESATINNE), ROUND_HALF_UP)
    return format(abs(d) if d == 0 else d, "f")


def t(v):
    """Pekny vypis cisla v krokoch: najviac 6 desatinnych miest."""
    s = f"{float(v):.6f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def bod(P):
    return f"({t(P[0])}, {t(P[1])})"


def vypocitaj(funkcia=FUNKCIA, start=START, eps=EPS, max_it=MAX_IT, vypis=True):
    pis = print if vypis else (lambda *a, **k: None)
    f = nacitaj_funkciu(funkcia)
    fx, fy = sp.diff(f, x), sp.diff(f, y)
    fxx, fxy, fyx, fyy = sp.diff(fx, x), sp.diff(fx, y), sp.diff(fy, x), sp.diff(fy, y)
    pis("f(x, y) =", str(f).replace("**", "^"))
    pis("fx =", str(fx).replace("**", "^"), "    fy =", str(fy).replace("**", "^"))
    pis("fxx =", str(fxx).replace("**", "^"), "    fxy =", str(fxy).replace("**", "^"),
        "    fyy =", str(fyy).replace("**", "^"))

    X = (sp.Float(str(start[0]), CIFRY), sp.Float(str(start[1]), CIFRY))
    historia = []
    for k in range(max_it + 1):
        gx, gy = hodnota(fx, X), hodnota(fy, X)
        norma = sp.sqrt(gx ** 2 + gy ** 2)
        if norma < eps:
            stop = f"||grad f|| = {float(norma):.2e} < eps po {k} iteraciach"
            break
        if k == max_it:
            stop = f"dosiahnuty MAX_IT = {max_it} (este nie je v minime)"
            break

        pis(f"\n--- iteracia {k + 1} ---")
        pis(f"X = {bod(X)},  f(X) = {t(hodnota(f, X))}")
        pis(f"grad f(X) = {bod((gx, gy))},  ||grad|| = {t(norma)}")
        a, b, c, d = hodnota(fxx, X), hodnota(fxy, X), hodnota(fyx, X), hodnota(fyy, X)
        pis(f"H = | {t(a)}  {t(b)} |")
        pis(f"    | {t(c)}  {t(d)} |")
        det = a * d - b * c
        pis(f"det H = {t(a)}*{t(d)} - {t(b)}*{t(c)} = {t(det)}")
        if abs(det) <= 1e-30 * (a * a + b * b + c * c + d * d):
            raise SystemExit("CHYBA: det H = 0, inverzna matica neexistuje -> Newton sa neda pouzit.")

        # sposob B: vymenena matica krat gradient, az potom delim det
        v1 = d * gx - b * gy
        v2 = -c * gx + a * gy
        pis(f"| {t(d)}  {t(-b)} | * {bod((gx, gy))} = {bod((v1, v2))}")
        pis(f"| {t(-c)}  {t(a)} |")
        krok = (v1 / det, v2 / det)
        pis(f"krok = {bod((v1, v2))} / {t(det)} = {bod(krok)}")
        X = (X[0] - krok[0], X[1] - krok[1])
        posun = sp.sqrt(krok[0] ** 2 + krok[1] ** 2)
        pis(f"X_nove = X - krok = {bod(X)},  f = {t(hodnota(f, X))},  ||krok|| = {t(posun)}")
        historia.append({"grad": (gx, gy), "det": det, "krok": krok, "P": X})
        if posun < eps:
            stop = f"||X{k + 1} - X{k}|| = {float(posun):.2e} < eps po {k + 1} iteraciach"
            break

    # aky je to bod? (Hessova matica vo vysledku)
    a, b, c, d = hodnota(fxx, X), hodnota(fxy, X), hodnota(fyx, X), hodnota(fyy, X)
    det = a * d - b * c
    if det > 0 and a > 0:
        typ = "MINIMUM"
    elif det > 0 and a < 0:
        typ = "MAXIMUM"
    elif det < 0:
        typ = "SEDLO"
    else:
        typ = "NEDA SA URCIT (det H = 0)"

    pis(f"\nSTOP: {stop}")
    pis(f"VYSLEDOK: {typ} v bode ({zaokruhli(X[0])}, {zaokruhli(X[1])}),  f = {zaokruhli(hodnota(f, X))}")
    pis(f"  (det H = {t(det)}, fxx = {t(a)})")
    return {"bod": X, "f": hodnota(f, X), "iteracie": len(historia), "stop": stop, "typ": typ,
            "historia": historia}


if __name__ == "__main__":
    vypocitaj()
