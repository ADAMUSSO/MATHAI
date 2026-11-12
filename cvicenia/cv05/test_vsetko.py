# Spusti vsetky 4 metody na vsetkych 7 funkciach (start a TOL zo zadania)
# a vypise iteracie aj pocty vyhodnoteni. Zaklad pre ULOHU 1.
from funkcie import FUNKCIE
from gradientna import gradientna
from newton import newton
from nelder_mead import nelder_mead
from powell import powell

TOL = 1e-3
ALFA = 0.01    # krok gradientnej metody - skus menit (uloha 3)

for kluc, fn in FUNKCIE.items():
    print(f"=== {fn.nazov}, start {fn.start} ===")
    print(gradientna(fn, alfa=ALFA, tol=TOL))
    print(newton(fn, tol=TOL))
    print(nelder_mead(fn, tol=TOL))
    print(powell(fn, tol=TOL))
    print()
