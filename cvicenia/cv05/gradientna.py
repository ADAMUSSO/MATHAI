# Cvicenie 5 - Gradientna metoda (najstrmsi zostup s PEVNYM krokom alfa)
#
#   x_{k+1} = x_k - alfa * grad f(x_k)
#
# STOP: ||x_k - x*|| < TOL  (x* = najblizsie minimum)
# Nekonverguje: po MAX_IT iteraciach alebo ked cisla "vybuchnu" -> X
from funkcie import FUNKCIE
from vysledok import Vysledok, rozbehnuty

MAX_IT = 20000


def gradientna(fn, start=None, alfa=0.01, tol=1e-3, max_it=MAX_IT, vypis=False):
    fn.vynuluj()
    a, b = start if start is not None else fn.start
    historia = [(a, b)]

    for k in range(1, max_it + 1):
        gx, gy = fn.grad(a, b)
        a, b = a - alfa * gx, b - alfa * gy
        historia.append((a, b))

        if vypis:
            print(f"  {k}: grad = ({gx:.4f}, {gy:.4f}) -> ({a:.6f}, {b:.6f}), "
                  f"||x - x*|| = {fn.vzdialenost(a, b):.2e}")

        if rozbehnuty(a, b):
            return Vysledok("Gradientna", fn, (a, b), k, False, historia, "diverguje")
        if fn.vzdialenost(a, b) < tol:
            return Vysledok("Gradientna", fn, (a, b), k, True, historia)

    return Vysledok("Gradientna", fn, (a, b), max_it, False, historia, f"> {max_it} it")


if __name__ == "__main__":
    # ukazka: sfera so startom (3, 2), alfa = 0.1 - kazdu iteraciu vypise
    print("Gradientna metoda - Sfera, alfa = 0.1")
    r = gradientna(FUNKCIE["sfera"], alfa=0.1, vypis=True)
    print(r)
