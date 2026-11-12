# Metoda najstrmsieho zostupu (steepest descent)
#   - smer je NORMOVANY:        S = -grad f / ||grad f||
#   - krok gama hladame presne:  phi(gama) = f(P + gama*S),  phi'(gama) = 0
#   - novy bod:                  P_nove = P + gama*S
#
# STOP: ||grad f|| < eps  (gradient je takmer nulovy -> sme v minime)
#   (podmienka ||P_nove - P|| < eps tu NESTACI: v uzkom udoli su kroky male
#    aj daleko od minima a metoda by zastala predcasne)
#
# Spustenie (vsetko ma predvolene hodnoty, staci python gradient.py):
#   python gradient.py --f "x**2 + 2*y**2" --start 3 1 --eps 1e-3 --max_it 100
import argparse
import math
import sympy as sp

x, y, gama = sp.symbols("x y gama")


def nacitaj_parametre():
    p = argparse.ArgumentParser(description="Najstrmsi zostup s normovanym smerom")
    p.add_argument("--f", default="x**2 + 2*y**2", help='funkcia, napr. "x**2 + 2*y**2"')
    p.add_argument("--start", nargs=2, type=float, default=[3, 1], help="startovaci bod x y")
    p.add_argument("--eps", type=float, default=1e-3, help="presnost na zastavenie")
    p.add_argument("--max_it", type=int, default=100, help="maximalny pocet iteracii")
    return p.parse_args()


def najdi_gamu(f, P, S):
    """Dosadi priamku do f, zderivuje podla gama, polozi = 0 a vyberie najlepsie gama."""
    # 1. dosadenie priamky: x = Px + gama*Sx,  y = Py + gama*Sy
    phi = sp.expand(f.subs({x: P[0] + gama * S[0], y: P[1] + gama * S[1]}, simultaneous=True))
    # 2. derivacia phi podla gama
    dphi = sp.diff(phi, gama)
    # 3. dphi = 0 -> korene (berieme len realne a kladne, ideme v smere S)
    korene = [float(sp.re(r)) for r in sp.Poly(dphi, gama).nroots() if abs(sp.im(r)) < 1e-9]
    kandidati = [r for r in korene if r > 0]
    # 4. ak je korenov viac (napr. pri x**4), vyberiem to gama, kde je phi najmensie
    najlepsie = min(kandidati, key=lambda r: float(phi.subs(gama, r)))
    return najlepsie, phi


def main():
    arg = nacitaj_parametre()
    f = sp.sympify(arg.f)                       # text -> sympy vyraz
    fx, fy = sp.diff(f, x), sp.diff(f, y)       # parcialne derivacie
    print(f"f = {f}")
    print(f"grad f = ({fx}, {fy})\n")

    P = (arg.start[0], arg.start[1])
    print(f"P0 = ({P[0]:.6f}, {P[1]:.6f}),  f(P0) = {float(f.subs({x: P[0], y: P[1]})):.6f}")

    for k in range(arg.max_it):
        # gradient v bode P
        gx = float(fx.subs({x: P[0], y: P[1]}))
        gy = float(fy.subs({x: P[0], y: P[1]}))
        dlzka = math.sqrt(gx**2 + gy**2)
        if dlzka < arg.eps:                     # gradient je skoro 0 -> sme v minime
            print(f"\nSTOP: ||grad f|| = {dlzka:.2e} < eps")
            break

        # normovany smer
        S = (-gx / dlzka, -gy / dlzka)

        # presne hladanie po priamke
        g, phi = najdi_gamu(f, P, S)

        # novy bod
        P_nove = (P[0] + g * S[0], P[1] + g * S[1])

        print(f"\n--- iteracia {k + 1} ---")
        print(f"grad f(P{k}) = ({gx:.6f}, {gy:.6f}),  ||grad|| = {dlzka:.6f}")
        print(f"S{k} = ({S[0]:.6f}, {S[1]:.6f})")
        print(f"phi(gama) = {sp.N(phi, 6)}")
        print(f"gama = {g:.6f}")
        print(f"P{k + 1} = ({P_nove[0]:.6f}, {P_nove[1]:.6f}),  "
              f"f(P{k + 1}) = {float(f.subs({x: P_nove[0], y: P_nove[1]})):.6f}")

        P = P_nove
    else:
        print(f"\nSTOP: dosiahnuty max_it = {arg.max_it}")

    print(f"\nVYSLEDOK: minimum v ({P[0]:.6f}, {P[1]:.6f}),  f = {float(f.subs({x: P[0], y: P[1]})):.6f}")


if __name__ == "__main__":
    main()
