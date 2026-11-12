# Cvicenie 5 - Newtonova metoda v 2D
#
#   H(x_k) * d_k = -grad f(x_k)       (sustava 2x2, riesime Cramerovym pravidlom)
#   x_{k+1} = x_k + d_k
#
# POZOR: Newton hlada bod, kde grad f = 0 - to moze byt aj sedlo alebo maximum!
#
# STOP: ||x_k - x*|| < TOL  (x* = najblizsie minimum)
from funkcie import FUNKCIE
from vysledok import Vysledok, rozbehnuty

MAX_IT = 20000


def newton(fn, start=None, tol=1e-3, max_it=MAX_IT, vypis=False):
    fn.vynuluj()
    a, b = start if start is not None else fn.start
    historia = [(a, b)]

    for k in range(1, max_it + 1):
        gx, gy = fn.grad(a, b)
        (hxx, hxy), (_, hyy) = fn.hess(a, b)

        # H * d = -g  ->  Cramerovo pravidlo
        det = hxx * hyy - hxy * hxy
        if det == 0:
            return Vysledok("Newton", fn, (a, b), k, False, historia, "singularna H")
        dx = (-gx * hyy + gy * hxy) / det
        dy = (-gy * hxx + gx * hxy) / det

        a, b = a + dx, b + dy
        historia.append((a, b))

        if vypis:
            print(f"  {k}: d = ({dx:.6f}, {dy:.6f}) -> ({a:.6f}, {b:.6f}), "
                  f"||x - x*|| = {fn.vzdialenost(a, b):.2e}")

        if rozbehnuty(a, b):
            return Vysledok("Newton", fn, (a, b), k, False, historia, "diverguje")
        if fn.vzdialenost(a, b) < tol:
            return Vysledok("Newton", fn, (a, b), k, True, historia)
        if abs(dx) + abs(dy) < 1e-14:   # grad = 0, ale nie minimum (sedlo / maximum)
            return Vysledok("Newton", fn, (a, b), k, False, historia, "zasekol sa v sedle/maxime")

    return Vysledok("Newton", fn, (a, b), max_it, False, historia, f"> {max_it} it")


if __name__ == "__main__":
    print("Newtonova metoda - Rosenbrock, start (-1.2, 1)")
    r = newton(FUNKCIE["rosenbrock"], vypis=True)
    print(r)
