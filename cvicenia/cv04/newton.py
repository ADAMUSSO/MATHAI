# Cvicenie 4 - Newtonova metoda (1D a 2D)
import math
import sympy as sp

eps = 10e-3 #zadanie 10e-3 (good to know)

#############################################
# PRIKLAD 1 - Newtonova metoda 2D:
# f(x, y) = x^4/4 + x^2/2 + y^2/2,  A0 = (1, 1)
#############################################
print("PRIKLAD 1 - Newton 2D")
x = 1.0 
y = 1.0

for k in range(1, 51):
    grad = (x**3 + x, y)
    H = (3 * x**2 + 1, 1)          # diagonala Hessovej matice (mimo diagonaly su 0)
    dx = -grad[0] / H[0]
    dy = -grad[1] / H[1]
    x, y = x + dx, y + dy
    print(f"  {k}: grad = ({grad[0]:.4f}, {grad[1]:.4f}), d = ({dx:.4f}, {dy:.4f}) -> ({x:.6f}, {y:.6f})")
    if math.hypot(dx, dy) < eps:
        break

print(f"  Vysledok: ({x:.6f}, {y:.6f})\n")


#############################################
# PRIKLAD 3 - Newtonova metoda 1D:
# f(x) = x^4 - 3x^3 + 2
#############################################
print("PRIKLAD 3 - Newton 1D")
x = 3.0                         # pociatocny bod (zmen podla zadania)
krok = 1.0                      # aby cyklus zbehol aspon raz
k = 0

while krok > eps:
    d1 = 4 * x**3 - 9 * x**2    # f'(x)
    d2 = 12 * x**2 - 18 * x     # f''(x)
    x_novy = x - d1 / d2
    k += 1
    print(f"  {k}: x = {x:.6f}, f' = {d1:.6f}, f'' = {d2:.6f} -> {x_novy:.6f}")
    krok = abs(x_novy - x)
    x = x_novy

print(f"  Vysledok: x = {x:.6f}, f(x) = {x**4 - 3 * x**3 + 2:.6f}\n")


#############################################
# PRIKLAD 3 - Newton 1D so sympy
#############################################
print("PRIKLAD 3 - Newton 1D WITH SYMPY")
xd = sp.symbols('x')           
f = xd**4 - 3 * xd**3 + 2
f1 = sp.diff(f, xd)
f2 = sp.diff(f1, xd)
print(f"  f'(x) = {f1},  f''(x) = {f2}")

x = 3.0                        
krok = 1.0                     
k = 0

while krok > eps:
    d1 = float(f1.subs(xd, x))
    d2 = float(f2.subs(xd, x))
    x_novy = x - d1 / d2
    k += 1
    print(f"  {k}: x = {x:.6f}, f' = {d1:.6f}, f'' = {d2:.6f} -> {x_novy:.6f}")
    krok = abs(x_novy - x)
    x = x_novy

print(f"  Vysledok: x = {x:.6f}, f(x) = {float(f.subs(xd, x)):.6f}")