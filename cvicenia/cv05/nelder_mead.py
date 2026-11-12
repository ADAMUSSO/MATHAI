# Cvicenie 5 - Nelder-Mead (simplex z 3 bodov, bez derivacii)
#
# Kazda iteracia:
#   1. zoradim body: A (najlepsi), B (dobry), C (najhorsi)
#   2. M = tazisko A, B
#   3. reflexia   R = M + (M - C)
#   4. ak R je najlepsi -> skusim expanziu E = M + 2(M - C)
#   5. ak R je horsi ako B -> kontrakcia K = (M + C) / 2
#   6. ak ani K nepomohol -> zmrstenie vsetkeho k A
#
# Pociatocny simplex: x0, x0 + (h, 0), x0 + (0, h)
# STOP: ||A - x*|| < TOL  (najlepsi vrchol je dost blizko minima)
from funkcie import FUNKCIE
from vysledok import Vysledok, rozbehnuty

MAX_IT = 20000


def nelder_mead(fn, start=None, h=0.5, tol=1e-3, max_it=MAX_IT, vypis=False):
    fn.vynuluj()
    a, b = start if start is not None else fn.start

    # body si ukladam spolu s hodnotou f, aby som f nepocital zbytocne viackrat
    body = [((a, b), fn.f(a, b)),
            ((a + h, b), fn.f(a + h, b)),
            ((a, b + h), fn.f(a, b + h))]
    body.sort(key=lambda p: p[1])
    historia = [body[0][0]]

    for k in range(1, max_it + 1):
        (A, fA), (B, fB), (C, fC) = body

        M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
        R = (2 * M[0] - C[0], 2 * M[1] - C[1])
        fR = fn.f(*R)

        if fA <= fR < fB:                       # reflexia
            body[2] = (R, fR)
            krok = "reflexia"
        elif fR < fA:                           # expanzia
            E = (M[0] + 2 * (R[0] - M[0]), M[1] + 2 * (R[1] - M[1]))
            fE = fn.f(*E)
            body[2] = (E, fE) if fE < fR else (R, fR)
            krok = "expanzia" if fE < fR else "reflexia"
        else:                                   # kontrakcia
            K = ((M[0] + C[0]) / 2, (M[1] + C[1]) / 2)
            fK = fn.f(*K)
            if fK < fC:
                body[2] = (K, fK)
                krok = "kontrakcia"
            else:                               # zmrstenie k A
                B2 = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
                C2 = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)
                body = [(A, fA), (B2, fn.f(*B2)), (C2, fn.f(*C2))]
                krok = "zmrstenie"

        body.sort(key=lambda p: p[1])
        najlepsi = body[0][0]
        historia.append(najlepsi)

        if vypis:
            print(f"  {k}: {krok:<10} best = ({najlepsi[0]:.6f}, {najlepsi[1]:.6f}), "
                  f"f = {body[0][1]:.6f}, ||x - x*|| = {fn.vzdialenost(*najlepsi):.2e}")

        if rozbehnuty(*najlepsi):
            return Vysledok("Nelder-Mead", fn, najlepsi, k, False, historia, "diverguje")
        if fn.vzdialenost(*najlepsi) < tol:
            return Vysledok("Nelder-Mead", fn, najlepsi, k, True, historia)

        # simplex sa zmrstil na bod, ale nie v minime -> zasekol sa
        if max(abs(p[0][0] - najlepsi[0]) + abs(p[0][1] - najlepsi[1]) for p in body) < 1e-15:
            return Vysledok("Nelder-Mead", fn, najlepsi, k, False, historia, "zasekol sa")

    return Vysledok("Nelder-Mead", fn, najlepsi, max_it, False, historia, f"> {max_it} it")


if __name__ == "__main__":
    print("Nelder-Mead - Booth, start (0, 0)")
    r = nelder_mead(FUNKCIE["booth"], vypis=True)
    print(r)
