# NELDER-MEAD - jednoducha verzia, kroky ako na papieri
#
#   zoradim body podla f:  B = najlepsi (najmensie f), G = dobry, W = najhorsi
#   STOP: d = najvacsia vzdialenost bodu od B < eps   (vysledok je B)
#
#   M = (B + G)/2                 tazisko (stred strany oproti W)
#   R = M + alfa*(M - W)          reflexia
#   1) f(R) < f(B):         E = M + gama*(R - M)   expanzia
#                           ak f(E) < f(R) W <- E,  inak W <- R
#   2) f(B) <= f(R) < f(G): W <- R
#   3) f(R) >= f(G):        kontrakcia
#        cvicenie:  C = M + rho*(W - M)
#        prednaska: C1 = M + rho*(W - M), C2 = M + rho*(R - M), C = ten s mensim f
#        ak f(C) < f(W) W <- C,  inak zmrstenie k B:
#        G <- B + sigma*(G - B),  W <- B + sigma*(W - B)
#
# Body sa pocitaju v PRESNYCH ZLOMKOCH (1.2 = 6/5), takze pri porovnani f(R) a f(G)
# nehrozi chyba zo zaokruhlenia. Pri rovnakom f je novy bod horsi nez stary.
# DESATINNE = na kolko desatinnych miest zaokruhlim VYSLEDOK (5 a viac nahor);
# vypocet aj vsetky kroky idu stale v plnej presnosti.

import math
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
FUNKCIA = "x^2 - 4*x +y**2 -y -x*y"
BODY = [(0, 0), (6.5, 0), (0, 4.5)]   # 3 vrcholy trojuholnika
ALFA = 1                 # reflexia
GAMA = 2                 # expanzia
RHO = 0.5                # kontrakcia
SIGMA = 0.5              # zmrstenie
KONTRAKCIA = "prednaska" # "prednaska" = C1 aj C2, beriem ten s mensim f
                         # "cvicenie"  = len C = M + rho*(W - M)
EPS = 0.000001              # STOP ked d < EPS
MAX_IT = 200             # najviac tolko iteracii
DESATINNE = 10            # VYSLEDOK zaokruhlim na tolko desatinnych miest
                         # (len konecny vypis - vypocet sa tym nemeni)
# ======================================================================

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


def presne(v):
    """Cislo -> presny zlomok (1.2 -> 6/5)."""
    return sp.Rational(str(v))


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


def plus(P, k, Q):
    """P + k*Q (po zlozkach)."""
    return (P[0] + k * Q[0], P[1] + k * Q[1])


def minus(P, Q):
    return (P[0] - Q[0], P[1] - Q[1])


def vypocitaj(funkcia=FUNKCIA, body=BODY, alfa=ALFA, gama=GAMA, rho=RHO, sigma=SIGMA,
              kontrakcia=KONTRAKCIA, eps=EPS, max_it=MAX_IT, vypis=True):
    pis = print if vypis else (lambda *a, **k: None)
    if kontrakcia not in ("cvicenie", "prednaska"):
        raise SystemExit('CHYBA: KONTRAKCIA musi byt "cvicenie" alebo "prednaska".')
    f = nacitaj_funkciu(funkcia)
    pis("f(x, y) =", str(f).replace("**", "^"))

    def F(P):
        """f v bode P - presne (zlomok), ak sa da; inak na 50 cifier."""
        v = f.subs({x: P[0], y: P[1]})
        if not v.is_Rational:
            v = v.evalf(50)
        if v.is_real is not True:
            raise SystemExit(f"CHYBA: v bode {bod(P)} sa f neda vypocitat.")
        return v

    alfa, gama, rho, sigma = presne(alfa), presne(gama), presne(rho), presne(sigma)
    body = [(presne(p[0]), presne(p[1])) for p in body]
    historia = []
    stop = f"dosiahnuty MAX_IT = {max_it} (este nie je v minime)"
    for k in range(max_it + 1):
        body = sorted(body, key=F)                # stabilne: pri rovnosti ostava poradie
        B, G, W = body
        d = max(math.dist(map(float, B), map(float, G)), math.dist(map(float, B), map(float, W)))
        if d < eps:
            stop = f"d = {d:.2e} < eps po {k} iteraciach"
            break
        if k == max_it:
            break

        pis(f"\n--- iteracia {k + 1} ---")
        pis(f"B = {bod(B)} f = {t(F(B))}  |  G = {bod(G)} f = {t(F(G))}  |  "
            f"W = {bod(W)} f = {t(F(W))}")
        pis(f"d = {t(d)}")
        M = plus(B, sp.Rational(1, 2), minus(G, B))        # M = (B + G)/2
        R = plus(M, alfa, minus(M, W))                      # R = M + alfa*(M - W)
        pis(f"M = (B + G)/2 = {bod(M)}")
        pis(f"R = M + {t(alfa)}*(M - W) = {bod(R)},  f(R) = {t(F(R))}")

        if F(R) < F(B):
            E = plus(M, gama, minus(R, M))                  # E = M + gama*(R - M)
            pis(f"1) f(R) < f(B) -> expanzia E = M + {t(gama)}*(R - M) = {bod(E)},  f(E) = {t(F(E))}")
            if F(E) < F(R):
                novy, krok = E, "expanzia E"
                pis("   f(E) < f(R) -> W <- E")
            else:
                novy, krok = R, "reflexia R"
                pis("   f(E) >= f(R) -> W <- R")
        elif F(R) < F(G):
            novy, krok = R, "reflexia R"
            pis("2) f(B) <= f(R) < f(G) -> W <- R")
        else:
            pis("3) f(R) >= f(G) -> kontrakcia")
            C, meno = plus(M, rho, minus(W, M)), "C1"      # C1 = M + rho*(W - M)
            pis(f"   C1 = M + {t(rho)}*(W - M) = {bod(C)},  f(C1) = {t(F(C))}")
            if kontrakcia == "prednaska":
                C2 = plus(M, rho, minus(R, M))              # C2 = M + rho*(R - M)
                pis(f"   C2 = M + {t(rho)}*(R - M) = {bod(C2)},  f(C2) = {t(F(C2))}")
                if F(C2) < F(C):
                    C, meno = C2, "C2"
                pis(f"   mensie f ma {meno}")
            if F(C) < F(W):
                novy, krok = C, f"kontrakcia {meno}"
                pis(f"   f({meno}) < f(W) -> W <- {meno}")
            else:
                novy = None
                krok = "zmrstenie"
                G2 = plus(B, sigma, minus(G, B))            # G <- B + sigma*(G - B)
                W2 = plus(B, sigma, minus(W, B))            # W <- B + sigma*(W - B)
                pis(f"   f({meno}) >= f(W) -> zmrstenie k B: G <- {bod(G2)}, W <- {bod(W2)}")
                body = [B, G2, W2]
        if novy is not None:
            body = [B, G, novy]
        pis(f"novy trojuholnik: {bod(body[0])}, {bod(body[1])}, {bod(body[2])}")
        historia.append({"B": B, "G": G, "W": W, "M": M, "R": R, "krok": krok,
                         "trojuholnik": list(body)})

    B = body[0]
    pis(f"\nSTOP: {stop}")
    pis(f"VYSLEDOK: minimum v bode ({zaokruhli(B[0])}, {zaokruhli(B[1])}),  f = {zaokruhli(F(B))}")
    return {"bod": B, "f": F(B), "iteracie": len(historia), "stop": stop, "historia": historia}


if __name__ == "__main__":
    vypocitaj()
