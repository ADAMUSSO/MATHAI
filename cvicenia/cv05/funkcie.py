# Cvicenie 5 - testovacie funkcie
#
# Kazda funkcia je zadana LEN ako vzorec v sympy. Gradient a Hessovu maticu
# si sympy zderivuje sama (ako v Cvic_4/newton.py), takze ich netreba pocitat rucne.
#
# Pouzitie:
#   from funkcie import FUNKCIE
#   fn = FUNKCIE["rosenbrock"]
#   fn.f(1, 2)        -> hodnota funkcie
#   fn.grad(1, 2)     -> (df/dx, df/dy)
#   fn.hess(1, 2)     -> ((fxx, fxy), (fyx, fyy))
#   fn.start          -> startovaci bod zo zadania
#   fn.minima         -> zoznam vsetkych minim (Himmelblau ma 4)
import math
import sympy as sp

x, y = sp.symbols('x y')


class Funkcia:
    def __init__(self, nazov, vyraz, start, minima):
        self.nazov = nazov
        self.vyraz = vyraz
        self.start = start
        self.minima = minima

        # derivacie cez sympy
        gx = sp.diff(vyraz, x)
        gy = sp.diff(vyraz, y)
        hxx = sp.diff(gx, x)
        hxy = sp.diff(gx, y)
        hyy = sp.diff(gy, y)

        # lambdify = zo sympy vyrazu spravi obycajnu pythonovsku funkciu (rychle)
        self._f = sp.lambdify((x, y), vyraz, "math")
        self._g = sp.lambdify((x, y), (gx, gy), "math")
        self._h = sp.lambdify((x, y), ((hxx, hxy), (hxy, hyy)), "math")

        # pocitadla vyhodnoteni (nulujeme pred kazdym spustenim metody)
        self.vynuluj()

    def vynuluj(self):
        self.pocet_f = 0
        self.pocet_grad = 0
        self.pocet_hess = 0

    def f(self, a, b):
        self.pocet_f += 1
        try:
            return self._f(a, b)
        except OverflowError:
            return math.inf

    def grad(self, a, b):
        self.pocet_grad += 1
        return self._g(a, b)

    def hess(self, a, b):
        self.pocet_hess += 1
        return self._h(a, b)

    def najblizsie_minimum(self, a, b):
        """Vrati minimum x*, ktore je najblizsie k bodu (a, b)."""
        return min(self.minima, key=lambda m: math.dist((a, b), m))

    def vzdialenost(self, a, b):
        """||x_k - x*|| k najblizsiemu minimu - toto je STOP kriterium zo zadania."""
        return math.dist((a, b), self.najblizsie_minimum(a, b))


FUNKCIE = {
    "sfera": Funkcia(
        "Sfera", x**2 + y**2,
        start=(3.0, 2.0), minima=[(0.0, 0.0)]),

    "pretiahnuta": Funkcia(
        "Pretiahnuta kvadr.", x**2 + 25 * y**2,
        start=(3.0, 1.0), minima=[(0.0, 0.0)]),

    "booth": Funkcia(
        "Booth", (x + 2 * y - 7)**2 + (2 * x + y - 5)**2,
        start=(0.0, 0.0), minima=[(1.0, 3.0)]),

    "matyas": Funkcia(
        "Matyas", sp.Rational(26, 100) * (x**2 + y**2) - sp.Rational(48, 100) * x * y,
        start=(5.0, -3.0), minima=[(0.0, 0.0)]),

    "rosenbrock": Funkcia(
        "Rosenbrock", (1 - x)**2 + 100 * (y - x**2)**2,
        start=(-1.2, 1.0), minima=[(1.0, 1.0)]),

    "himmelblau": Funkcia(
        "Himmelblau", (x**2 + y - 11)**2 + (x + y**2 - 7)**2,
        start=(0.0, 0.0),
        minima=[(3.0, 2.0), (-2.805118, 3.131312),
                (-3.779310, -3.283186), (3.584428, -1.848126)]),

    "beale": Funkcia(
        "Beale",
        (sp.Rational(3, 2) - x + x * y)**2
        + (sp.Rational(9, 4) - x + x * y**2)**2
        + (sp.Rational(21, 8) - x + x * y**3)**2,
        start=(1.0, 1.0), minima=[(3.0, 0.5)]),
}


if __name__ == "__main__":
    # rychla kontrola: vypise vzorce, derivacie a hodnotu v minime (ma byt ~0)
    for fn in FUNKCIE.values():
        print(f"{fn.nazov}")
        print(f"  f      = {fn.vyraz}")
        print(f"  grad   = ({sp.diff(fn.vyraz, x)},  {sp.diff(fn.vyraz, y)})")
        m = fn.minima[0]
        print(f"  f(x*)  = {fn.f(*m):.6g},  grad(x*) = {fn.grad(*m)}\n")
