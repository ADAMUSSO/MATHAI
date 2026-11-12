# Cvicenie 4 - Nelder-Mead
import math

eps = 1e-3 # zadanie 10e-3 (good to know)


#############################################
# PRIKLAD 2 - Nelder-Mead
# f(x, y) = x^2 - 4x + y^2 - y - xy
# V1 = (0, 1), V2 = (1, 1), V3 = (0, 1.5)
#############################################
print("PRIKLAD 2 - Nelder-Mead")


def f(p):
    x, y = p
    return x**2 - 4 * x + y**2 - y - x * y


body = [(0.0, 1.0), (1.0, 1.0), (0.0, 1.5)]

for k in range(1, 201):
    #zoradenie bodov podla hodnoty funkcie (best, good, worst)
    A, B, C = sorted(body, key=f)  
    # tazisko                        
    M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)   
    # reflexia 
    R = (2 * M[0] - C[0], 2 * M[1] - C[1]) 
    # kontrola podmienok
    if f(A) <= f(R) < f(B):
        C = R
    elif f(R) < f(A):
        # expanzia (gama = 2)
        E = (M[0] + 2 * (R[0] - M[0]), M[1] + 2 * (R[1] - M[1]))   
        C = E if f(E) < f(R) else R
    else:
        # kontrakcia (rho = 0.5)
        K = ((M[0] + C[0]) / 2, (M[1] + C[1]) / 2)                  
        if f(K) < f(C):
            C = K
        else:
            # zmrstenie k A                                                       
            B = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
            C = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)

    body = sorted([A, B, C], key=f)
    best = body[0]
    d = max(math.dist(best, p) for p in body)
    print(f"  {k}: best = ({best[0]:.6f}, {best[1]:.6f}), f = {f(best):.6f}, d = {d:.6f}")
    if d < eps:
        break

print(f"  Vysledok: ({best[0]:.6f}, {best[1]:.6f}), f = {f(best):.6f}")
