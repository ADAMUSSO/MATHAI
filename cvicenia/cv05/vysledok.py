# Spolocna "obalka" na vysledok kazdej metody, aby sa dali lahko porovnat.
import math


class Vysledok:
    def __init__(self, metoda, fn, x, iteracie, konvergoval, historia, poznamka=""):
        self.metoda = metoda
        self.fn = fn
        self.x = x                      # konecny bod (x, y)
        self.iteracie = iteracie        # pocet iteracii
        self.konvergoval = konvergoval  # True / False
        self.historia = historia        # zoznam bodov x_0, x_1, ..., x_k (na graf v ulohe 5)
        self.poznamka = poznamka        # preco nekonvergoval
        self.pocet_f = fn.pocet_f
        self.pocet_grad = fn.pocet_grad
        self.pocet_hess = fn.pocet_hess
        self.minimum = fn.najblizsie_minimum(*x) if all(map(math.isfinite, x)) else None

    def do_tabulky(self):
        """Text do bunky tabulky: pocet iteracii alebo X."""
        if not self.konvergoval:
            return "X"
        return str(self.iteracie)

    def __str__(self):
        stav = "OK" if self.konvergoval else f"X ({self.poznamka})"
        return (f"{self.metoda:<12} {self.fn.nazov:<20} it = {self.iteracie:<6} "
                f"f-eval = {self.pocet_f:<6} grad = {self.pocet_grad:<6} hess = {self.pocet_hess:<5} "
                f"x = ({self.x[0]:.6f}, {self.x[1]:.6f})  {stav}")


def rozbehnuty(a, b):
    """Kontrola divergencie: NaN, nekonecno alebo obrovske cisla."""
    return not (math.isfinite(a) and math.isfinite(b)) or abs(a) > 1e10 or abs(b) > 1e10
