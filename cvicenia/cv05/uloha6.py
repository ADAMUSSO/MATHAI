# Uloha 6 - vlastna funkcia
#
#   f(x, y) = x^4 + y^4 - 4xy + 1
#
# Dve globalne minima (1, 1) a (-1, -1) s f = -1 a SEDLO v (0, 0) s f = 1.
# Startujeme blizko sedla, v bode (0.3, -0.2), a porovname vsetky 4 metody.
#
# Skript:
#   1. sympy najde stacionarne body (grad f = 0) a podla Hessovej matice
#      urci, ci je to minimum alebo sedlo
#   2. spusti 4 metody a vypise tabulku
#   3. nakresli vrstevnice s cestami metod + graf konvergencie
import math
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from funkcie import Funkcia, x, y
from gradientna import gradientna
from newton import newton
from nelder_mead import nelder_mead
from powell import powell

TOL = 1e-3
ALFA = 0.01                          # rovnaky krok ako v ulohe 1
START = (0.3, -0.2)
VYRAZ = x**4 + y**4 - 4 * x * y + 1

# --- 1. stacionarne body a ich typ -------------------------------------------
gx, gy = sp.diff(VYRAZ, x), sp.diff(VYRAZ, y)
H = sp.hessian(VYRAZ, (x, y))
print(f"f      = {VYRAZ}")
print(f"grad f = ({gx}, {gy})")
print(f"H      = {H.tolist()}\n")

minima = []
for riesenie in sp.solve([gx, gy], [x, y], dict=True):
    a, b = riesenie[x], riesenie[y]
    if not (a.is_real and b.is_real):
        continue                     # komplexne korene nas nezaujimaju
    Hb = H.subs({x: a, y: b})
    vl = sorted(Hb.eigenvals().keys())
    if all(v > 0 for v in vl):
        typ = "MINIMUM"
        minima.append((float(a), float(b)))
    elif all(v < 0 for v in vl):
        typ = "maximum"
    else:
        typ = "SEDLO"
    print(f"  ({a}, {b}):  f = {VYRAZ.subs({x: a, y: b})},  "
          f"H = {Hb.tolist()},  vlastne cisla = {vl}  ->  {typ}")
print()

# --- 2. spustenie metod -------------------------------------------------------
fn = Funkcia("x^4 + y^4 - 4xy + 1", VYRAZ, start=START, minima=minima)

vysledky = [
    (f"Gradientná (α = {ALFA:g})", gradientna(fn, alfa=ALFA, tol=TOL)),
    ("Newtonova", newton(fn, tol=TOL)),
    ("Nelder–Mead", nelder_mead(fn, tol=TOL)),
    ("Powell", powell(fn, tol=TOL)),
]

print(f"Start {START}, TOL = {TOL:g}")
print(f"{'metoda':<22} {'iteracie':>8} {'f-eval':>7} {'grad':>5} {'hess':>5}   koniec")
for nazov, r in vysledky:
    koniec = f"({r.x[0]:.4f}, {r.x[1]:.4f})"
    if r.konvergoval:
        koniec += f"  -> minimum {r.minimum}"
    else:
        koniec += f"  X ({r.poznamka})"
    print(f"{nazov:<22} {r.do_tabulky():>8} {r.pocet_f:>7} {r.pocet_grad:>5} {r.pocet_hess:>5}   {koniec}")

# --- 3. grafy -----------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

# vrstevnice
f_np = sp.lambdify((x, y), VYRAZ, "numpy")
X, Y = np.meshgrid(np.linspace(-1.7, 1.7, 400), np.linspace(-1.7, 1.7, 400))
urovne = [-0.9, -0.6, -0.2, 0.2, 0.6, 1.0, 1.5, 2.2, 3.2, 4.5, 6.5, 9]
cs = ax1.contour(X, Y, f_np(X, Y), levels=urovne, cmap="viridis", linewidths=0.8)
ax1.clabel(cs, fontsize=7, fmt="%g")

for nazov, r in vysledky:
    cesta = np.array(r.historia)
    ax1.plot(cesta[:, 0], cesta[:, 1], marker=".", markersize=4, linewidth=1.2, label=nazov)
    vzdialenosti = [fn.vzdialenost(*bod) for bod in r.historia]
    ax2.plot(vzdialenosti, marker=".", markersize=3, label=nazov)

ax1.plot(*zip(*minima), "r*", markersize=14, label="minimá (±1; ±1)")
ax1.plot(0, 0, "kX", markersize=10, label="sedlo (0; 0)")
ax1.plot(*START, "ko", markersize=6, label=f"štart {START}")
ax1.set_title("Vrstevnice a cesty metód")
ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.set_aspect("equal")
ax1.legend(fontsize=8, loc="upper left")

ax2.set_yscale("log")
ax2.axhline(TOL, color="gray", linestyle="--", label=f"TOL = {TOL:g}")
ax2.set_title("Vzdialenosť od najbližšieho minima")
ax2.set_xlabel("iterácia k")
ax2.set_ylabel("‖xₖ − x*‖")
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=8)

fig.suptitle("Úloha 6: f(x, y) = x⁴ + y⁴ − 4xy + 1, štart (0,3; −0,2)")
fig.tight_layout()
fig.savefig("uloha6_graf.png", dpi=150)   # ulozi obrazok vedla skriptu
plt.show()                                # otvori okno s grafom
