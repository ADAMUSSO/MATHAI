# Cvicenie 5 - Powellova metoda (bez derivacii)
#
# Jedna iteracia:
#   1. z bodu x0 hladam minimum po priamke v smere u1, potom v smere u2  -> x_n
#   2. novy smer d = x_n - x0, hladam minimum aj po nom
#   3. smery posuniem: u1 <- u2, u2 <- d
#
# Hladanie po priamke: min_t f(x + t*u) - najprv najdem interval, kde je minimum
# (zvacsujem krok), potom ho zuzim metodou zlateho rezu (ako v 1D cviceniach).
#
# STOP: ||x_k - x*|| < TOL  (x* = najblizsie minimum)
import math
from funkcie import FUNKCIE
from vysledok import Vysledok, rozbehnuty

MAX_IT = 20000
ZLATY = (math.sqrt(5) - 1) / 2  # 0.618...


def po_priamke(fn, p, u, presnost=1e-10):
    """Najde t, ktore minimalizuje g(t) = f(p + t*u). Vrati novy bod."""
    def g(t):
        return fn.f(p[0] + t * u[0], p[1] + t * u[1])

    # 1. ohranicenie minima: hladam a < b < c, kde g(b) < g(a) a g(b) < g(c)
    a, b = 0.0, 1.0
    ga, gb = g(a), g(b)
    if gb > ga:                     # ideme opacnym smerom
        a, b, ga, gb = b, a, gb, ga
    c = b + 2 * (b - a)
    gc = g(c)
    while gc < gb:
        a, b, ga, gb = b, c, gb, gc
        c = b + 2 * (b - a)
        gc = g(c)
        if abs(c) > 1e10:
            break
    lo, hi = min(a, c), max(a, c)

    # 2. zlaty rez na intervale [lo, hi]
    t1 = hi - ZLATY * (hi - lo)
    t2 = lo + ZLATY * (hi - lo)
    g1, g2 = g(t1), g(t2)
    while hi - lo > presnost:
        if g1 < g2:
            hi, t2, g2 = t2, t1, g1
            t1 = hi - ZLATY * (hi - lo)
            g1 = g(t1)
        else:
            lo, t1, g1 = t1, t2, g2
            t2 = lo + ZLATY * (hi - lo)
            g2 = g(t2)
    t = (lo + hi) / 2
    return (p[0] + t * u[0], p[1] + t * u[1])


def powell(fn, start=None, tol=1e-3, max_it=MAX_IT, vypis=False):
    fn.vynuluj()
    a, b = start if start is not None else fn.start
    x0 = (a, b)
    u1, u2 = (1.0, 0.0), (0.0, 1.0)     # zaciname smermi suradnicovych osi
    historia = [x0]

    for k in range(1, max_it + 1):
        p = po_priamke(fn, x0, u1)
        p = po_priamke(fn, p, u2)
        d = (p[0] - x0[0], p[1] - x0[1])

        if math.hypot(*d) > 0:          # novy smer d = x_n - x_0
            p = po_priamke(fn, p, d)
            u1, u2 = u2, d

        x0 = p
        historia.append(x0)

        if vypis:
            print(f"  {k}: x = ({x0[0]:.6f}, {x0[1]:.6f}), d = ({d[0]:.4f}, {d[1]:.4f}), "
                  f"||x - x*|| = {fn.vzdialenost(*x0):.2e}")

        if rozbehnuty(*x0):
            return Vysledok("Powell", fn, x0, k, False, historia, "diverguje")
        if fn.vzdialenost(*x0) < tol:
            return Vysledok("Powell", fn, x0, k, True, historia)
        if math.hypot(*d) < 1e-14:      # uz sa nehybe, ale nie je v minime
            return Vysledok("Powell", fn, x0, k, False, historia, "zasekol sa")

    return Vysledok("Powell", fn, x0, max_it, False, historia, f"> {max_it} it")


if __name__ == "__main__":
    print("Powell - Rosenbrock, start (-1.2, 1)")
    r = powell(FUNKCIE["rosenbrock"], vypis=True)
    print(r)
