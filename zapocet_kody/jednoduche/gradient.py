# NAJSTRMSI GRADIENT (normovany smer) - jednoducha verzia, kroky ako na papieri
#
#   1. grad f(P) = (fx, fy)            dosadim bod P do derivacii
#   2. ||grad|| = odmocnina(fx^2 + fy^2)        STOP ak ||grad|| < eps
#   3. S = -grad / ||grad||            smer najvacsieho klesania (dlzka 1)
#   4. phi(gama) = f(P + gama*S)       dosadim priamku do f
#   5. phi'(gama) = 0  ->  gama > 0    (ak vyjde viac miním, beriem to s najmensim phi)
#   6. P = P + gama*S                  a ideme znova od 1.
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
FUNKCIA = "x^2 + 2y^2"
START = (2, 2)           # zaciatocny bod P0 = (x, y)
EPS = 0.001              # STOP ked ||grad f|| < EPS
MAX_IT = 100             # najviac tolko iteracii
DESATINNE = 4            # VYSLEDOK zaokruhlim na tolko desatinnych miest
                         # (len konecny vypis - vypocet sa tym nemeni)
# ======================================================================

CIFRY = 50
x, y = sp.symbols("x y", real=True)
gama = sp.Symbol("gama", real=True)


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


def je_minimum(phi_v, r):
    """Je v gama = r minimum? (kusok vlavo aj vpravo je phi vyssie)"""
    h = sp.Float(1e-6, CIFRY) * (1 + abs(r))
    return phi_v(r - h) >= phi_v(r) and phi_v(r + h) >= phi_v(r)


def minimum_numericky(phi_v):
    """Ked phi nie je polynom: najdem minimum pre gama > 0 zlatym rezom."""
    h = sp.Float(1e-3, CIFRY)
    a = sp.Float(0, CIFRY)
    while phi_v(2 * h) < phi_v(h):        # idem dalej, kym phi klesa (krok zdvojnasobujem)
        a, h = h, 2 * h
        if h > 1e8:
            raise SystemExit("CHYBA: phi(gama) stale klesa - funkcia nema minimum.")
    b = 2 * h                             # minimum je medzi a a b
    k = (sp.sqrt(5) - 1).evalf(CIFRY) / 2
    for _ in range(130):                  # zlaty rez: usek sa zmensi asi 10^27-krat
        c, d = b - k * (b - a), a + k * (b - a)
        if phi_v(c) < phi_v(d):
            b = d
        else:
            a = c
    return (a + b) / 2


def najdi_gamu(phi):
    """phi'(gama) = 0, gama > 0, minimum phi. Vrati (gama, phi'(gama) na vypis)."""
    phi_v = lambda r: phi.subs(gama, r).evalf(CIFRY)
    if not phi.is_polynomial(gama):
        return minimum_numericky(phi_v), sp.diff(phi, gama)

    p = sp.Poly(phi, gama)
    najvacsi = max(abs(c) for c in p.coeffs())
    # koeficienty mensie nez 10^-30 su len smeti zo zaokruhlenia -> nula
    p = sp.Poly([c if abs(c) > 1e-30 * najvacsi else 0 for c in p.all_coeffs()], gama)
    dp = p.diff(gama)                                       # phi'(gama)
    presne = sp.Poly([sp.Rational(c) for c in dp.all_coeffs()], gama)
    korene = [r.evalf(CIFRY) for r in presne.real_roots()]  # vsetky realne korene phi' = 0
    minima = [r for r in korene if r > 0 and je_minimum(phi_v, r)]
    if not minima:
        raise SystemExit("CHYBA: phi(gama) nema minimum pre gama > 0 - funkcia v smere S "
                         "klesa do -nekonecna (funkcia nema minimum).")
    return min(minima, key=lambda r: (round(float(phi_v(r)), 12), r)), dp.as_expr()


def vypocitaj(funkcia=FUNKCIA, start=START, eps=EPS, max_it=MAX_IT, vypis=True):
    pis = print if vypis else (lambda *a, **k: None)
    f = nacitaj_funkciu(funkcia)
    fx, fy = sp.diff(f, x), sp.diff(f, y)
    pis("f(x, y) =", str(f).replace("**", "^"))
    pis("fx =", str(fx).replace("**", "^"))
    pis("fy =", str(fy).replace("**", "^"))

    P = (sp.Float(str(start[0]), CIFRY), sp.Float(str(start[1]), CIFRY))
    historia = []
    for k in range(max_it + 1):
        gx, gy = hodnota(fx, P), hodnota(fy, P)
        norma = sp.sqrt(gx ** 2 + gy ** 2)
        if norma < eps:
            stop = f"||grad f|| = {float(norma):.2e} < eps po {k} iteraciach"
            break
        if k == max_it:
            stop = f"dosiahnuty MAX_IT = {max_it} (este nie je v minime)"
            break

        pis(f"\n--- iteracia {k + 1} ---")
        pis(f"P = {bod(P)},  f(P) = {t(hodnota(f, P))}")
        pis(f"grad f(P) = {bod((gx, gy))},  ||grad|| = {t(norma)}")
        S = (-gx / norma, -gy / norma)
        pis(f"S = -grad/||grad|| = {bod(S)}")
        phi = sp.expand(f.subs({x: P[0] + gama * S[0], y: P[1] + gama * S[1]}, simultaneous=True))
        pis(f"phi(gama) = f(P + gama*S) = {str(sp.N(phi, 7)).replace('**', '^')}")
        g, dphi = najdi_gamu(phi)
        pis(f"phi'(gama) = {str(sp.N(dphi, 7)).replace('**', '^')} = 0  ->  gama = {t(g)}")
        P = (P[0] + g * S[0], P[1] + g * S[1])
        pis(f"P_nove = P + gama*S = {bod(P)},  f = {t(hodnota(f, P))}")
        historia.append({"grad": (gx, gy), "S": S, "gama": g, "P": P})

    pis(f"\nSTOP: {stop}")
    pis(f"VYSLEDOK: minimum v bode ({zaokruhli(P[0])}, {zaokruhli(P[1])}),  f = {zaokruhli(hodnota(f, P))}")
    return {"bod": P, "f": hodnota(f, P), "iteracie": len(historia), "stop": stop,
            "historia": historia}


if __name__ == "__main__":
    vypocitaj()
