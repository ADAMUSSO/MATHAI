# Uloha 5 - graf konvergencie pre Rosenbrockovu funkciu
#
# Pre kazdu metodu vypocita vzdialenost od minima ||x_k - x*|| v kazdej iteracii
# a nakresli ich do jedneho grafu s logaritmickou osou y.
import math
import matplotlib.pyplot as plt

from funkcie import FUNKCIE
from gradientna import gradientna
from newton import newton
from nelder_mead import nelder_mead
from powell import powell

TOL = 1e-3
fn = FUNKCIE["rosenbrock"]          # start (-1.2, 1), minimum (1, 1)

vysledky = [
    ("Gradientná (α = 0,001)", gradientna(fn, alfa=0.001, tol=TOL, max_it=20000)),
    ("Newtonova", newton(fn, tol=TOL)),
    ("Nelder–Mead", nelder_mead(fn, tol=TOL)),
    ("Powell", powell(fn, tol=TOL)),
]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

for nazov, r in vysledky:
    # historia = zoznam bodov x_0, x_1, ..., x_k  ->  vzdialenost kazdeho od minima (1, 1)
    vzdialenosti = [math.dist(bod, (1, 1)) for bod in r.historia]
    print(f"{nazov:<24} iteracie = {r.iteracie}")

    ax1.plot(vzdialenosti, label=nazov)                      # cely priebeh
    ax2.plot(vzdialenosti[:151], marker=".", label=nazov)    # prvych 150 iteracii

for ax, titulok in ((ax1, "Celý priebeh"), (ax2, "Prvých 150 iterácií")):
    ax.set_yscale("log")                                     # logaritmicka os y
    ax.axhline(TOL, color="gray", linestyle="--", label=f"TOL = {TOL:g}")
    ax.set_title(titulok)
    ax.set_xlabel("iterácia k")
    ax.set_ylabel("‖xₖ − x*‖")
    ax.grid(True, alpha=0.3)
    ax.legend()

ax2.set_xlim(0, 150)
fig.suptitle("Rosenbrock, štart (−1,2; 1): vzdialenosť od minima")
fig.tight_layout()
fig.savefig("uloha5_graf.png", dpi=150)   # ulozi obrazok vedla skriptu
plt.show()                                # otvori okno s grafom
