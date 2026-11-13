# POWELLOVA METODA - jednoducha verzia, kroky ako na papieri
#
#   smery na zaciatku: u1 = (1, 0), u2 = (0, 1)
#   1. z P0 hladam minimum po priamke v smere u1     -> P1
#   2. z P1 hladam minimum po priamke v smere u2     -> P2
#   3. d = P2 - P0, z P2 hladam minimum v smere d    -> P3
#      (z P0 by to vyslo rovnako - je to ta ista priamka, len gama je o 1 vacsie)
#   4. u1 <- u2,  u2 <- d,  P3 je novy P0
#      (vynimka: ak je d rovnobezny s u2, smery nemenim - inak by sa metoda zasekla)
#   STOP: ||P3 - P0|| < eps
#
#   hladanie po priamke: phi(gama) = f(P + gama*u), phi'(gama) = 0,
#   gama moze byt aj ZAPORNE; ak vyjde viac minim, beriem to s najmensim phi
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
FUNKCIA = "x^2 - 4x + 2*y^2 - 6y + 2*xy"
START = (0, 0)           # zaciatocny bod P0 = (x, y)
EPS = 0.001              # STOP ked ||P3 - P0|| < EPS
MAX_IT = 100             # najviac tolko iteracii
DESATINNE = 5            # VYSLEDOK zaokruhlim na tolko desatinnych miest
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


def dlzka(v):
    return sp.sqrt(v[0] ** 2 + v[1] ** 2)


def je_minimum(phi_v, r):
    """Je v gama = r minimum? (kusok vlavo aj vpravo je phi vyssie)"""
    h = sp.Float(1e-6, CIFRY) * (1 + abs(r))
    return phi_v(r - h) >= phi_v(r) and phi_v(r + h) >= phi_v(r)


def minimum_numericky(phi_v):
    """Ked phi nie je polynom: najdem minimum (gama moze byt aj zaporne) zlatym rezom."""
    h = sp.Float(1e-3, CIFRY)
    if phi_v(-h) < phi_v(h):              # phi klesa dozadu -> idem zapornym smerom
        h = -h
    a = -h
    while phi_v(2 * h) < phi_v(h):        # idem dalej, kym phi klesa (krok zdvojnasobujem)
        a, h = h, 2 * h
        if abs(h) > 1e8:
            raise SystemExit("CHYBA: phi(gama) stale klesa - funkcia nema minimum.")
    a, b = min(a, 2 * h), max(a, 2 * h)   # minimum je medzi a a b
    k = (sp.sqrt(5) - 1).evalf(CIFRY) / 2
    for _ in range(130):                  # zlaty rez: usek sa zmensi asi 10^27-krat
        c, d = b - k * (b - a), a + k * (b - a)
        if phi_v(c) < phi_v(d):
            b = d
        else:
            a = c
    return (a + b) / 2


def najdi_gamu(phi):
    """phi'(gama) = 0 a minimum phi (gama moze byt aj zaporne). Vrati gama."""
    phi_v = lambda r: phi.subs(gama, r).evalf(CIFRY)
    if not phi.is_polynomial(gama):
        return minimum_numericky(phi_v)

    p = sp.Poly(phi, gama)
    najvacsi = max(abs(c) for c in p.coeffs())
    # koeficienty mensie nez 10^-30 su len smeti zo zaokruhlenia -> nula
    p = sp.Poly([c if abs(c) > 1e-30 * najvacsi else 0 for c in p.all_coeffs()], gama)
    dp = p.diff(gama)                                       # phi'(gama)
    if dp.is_zero:                                          # phi je na priamke konstantna
        return sp.Float(0, CIFRY)
    presne = sp.Poly([sp.Rational(c) for c in dp.all_coeffs()], gama)
    korene = [r.evalf(CIFRY) for r in presne.real_roots()]  # vsetky realne korene phi' = 0
    minima = [r for r in korene if je_minimum(phi_v, r)]
    if not minima:
        raise SystemExit("CHYBA: phi(gama) nema minimum - funkcia na priamke klesa "
                         "do -nekonecna (funkcia nema minimum).")
    # najmensie phi; pri rovnosti to blizsie k 0 (a radsej kladne)
    return min(minima, key=lambda r: (round(float(phi_v(r)), 12), abs(r), -r))


def po_priamke(f, P, u, pis, odkial, smer, kam):
    """Z bodu P po priamke v smere u: phi(gama) = f(P + gama*u). Vrati (novy bod, gama)."""
    phi = sp.expand(f.subs({x: P[0] + gama * u[0], y: P[1] + gama * u[1]}, simultaneous=True))
    g = najdi_gamu(phi)
    Q = (P[0] + g * u[0], P[1] + g * u[1])
    pis(f"  {odkial} -> {kam} v smere {smer} = {bod(u)}")
    pis(f"     phi(gama) = {str(sp.N(phi, 7)).replace('**', '^')}")
    pis(f"     phi'(gama) = 0  ->  gama = {t(g)}")
    pis(f"     {kam} = {odkial} + gama*{smer} = {bod(Q)}")
    return Q, g


def vypocitaj(funkcia=FUNKCIA, start=START, eps=EPS, max_it=MAX_IT, vypis=True):
    pis = print if vypis else (lambda *a, **k: None)
    f = nacitaj_funkciu(funkcia)
    pis("f(x, y) =", str(f).replace("**", "^"))

    P0 = (sp.Float(str(start[0]), CIFRY), sp.Float(str(start[1]), CIFRY))
    u1, u2 = (sp.Integer(1), sp.Integer(0)), (sp.Integer(0), sp.Integer(1))
    historia = []
    stop = f"dosiahnuty MAX_IT = {max_it} (este nie je v minime)"
    for k in range(max_it):
        pis(f"\n--- iteracia {k + 1} ---")
        pis(f"P0 = {bod(P0)},  f(P0) = {t(hodnota(f, P0))}")
        P1, g1 = po_priamke(f, P0, u1, pis, "P0", "u1", "P1")
        P2, g2 = po_priamke(f, P1, u2, pis, "P1", "u2", "P2")
        d = (P2[0] - P0[0], P2[1] - P0[1])
        pis(f"  d = P2 - P0 = {bod(d)}")
        if dlzka(d) < 1e-25:                       # P2 = P0, nie je kam ist
            P3 = P2
            pis("  d = 0 -> P3 = P2")
        else:
            P3, g3 = po_priamke(f, P2, d, pis, "P2", "d", "P3")
            if abs(u2[0] * d[1] - u2[1] * d[0]) <= 1e-30 * dlzka(u2) * dlzka(d):
                pis("  d je rovnobezny s u2 -> smery NEMENIM (inak by sa metoda zasekla)")
            else:
                u1, u2 = u2, d
        pis(f"  P3 = {bod(P3)},  f(P3) = {t(hodnota(f, P3))}")
        pis(f"  nove smery: u1 = {bod(u1)}, u2 = {bod(u2)}")
        historia.append({"P1": P1, "P2": P2, "d": d, "P3": P3})
        posun = dlzka((P3[0] - P0[0], P3[1] - P0[1]))
        P0 = P3
        if posun < eps:
            stop = f"||P3 - P0|| = {float(posun):.2e} < eps po {k + 1} iteraciach"
            break

    pis(f"\nSTOP: {stop}")
    pis(f"VYSLEDOK: minimum v bode ({zaokruhli(P0[0])}, {zaokruhli(P0[1])}),  f = {zaokruhli(hodnota(f, P0))}")
    return {"bod": P0, "f": hodnota(f, P0), "iteracie": len(historia), "stop": stop,
            "historia": historia}


if __name__ == "__main__":
    vypocitaj()
