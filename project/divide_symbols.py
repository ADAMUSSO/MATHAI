import os
import numpy as np
from PIL import Image

ZNAKY = ["R", "S", "C", "E", "H", "X", "9", "K", "7", "2"]


def useky(maska, max_medzera):
    idx = np.where(maska)[0]          # pozície, kde je atrament
    vysledok = []
    zac = pred = idx[0]
    for i in idx[1:]:
        if i - pred > max_medzera:    # veľká medzera → koniec úseku
            vysledok.append((zac, pred))
            zac = i
        pred = i
    vysledok.append((zac, pred))
    return vysledok




def na_28x28(vyrez):
    # 1) orež tesne okolo písma
    ink = vyrez < 128
    r = np.where(ink.any(axis=1))[0]
    s = np.where(ink.any(axis=0))[0]
    vyrez = vyrez[r[0]:r[-1]+1, s[0]:s[-1]+1]

    # 2) doplň na štvorec, písmeno do stredu
    h, w = vyrez.shape
    strana = max(h, w)
    stvorec = np.full((strana, strana), 255, dtype=np.uint8)   # biely štvorec
    y0 = (strana - h) // 2
    x0 = (strana - w) // 2
    stvorec[y0:y0+h, x0:x0+w] = vyrez

    # 3) zmenši na 20×20 a 4) vlož do stredu 28×28
    maly = Image.fromarray(stvorec).resize((20, 20), Image.LANCZOS)
    platno = Image.new("L", (28, 28), 255)
    platno.paste(maly, (4, 4))
    return platno


a = np.array(Image.open("data/raw/symbols.jpg").convert("L"))
ink = a < 128

# riadky
riadky = useky(ink.any(axis=1), max_medzera=2)
assert len(riadky) == 10, f"Našiel som {len(riadky)} riadkov namiesto 10"

for ci, (r0, r1) in enumerate(riadky):
    znak = ZNAKY[ci]
    pas = a[r0:r1+1]                        # vodorovný pás s jedným riadkom písmen

    # písmená v riadku
    pismena = useky((pas < 128).any(axis=0), max_medzera=10)
    assert len(pismena) == 10, f"Riadok {znak}: {len(pismena)} písmen namiesto 10"

    os.makedirs(f"data/processed/{znak}", exist_ok=True)
    for k, (s0, s1) in enumerate(pismena):
        img = na_28x28(pas[:, s0:s1+1])
        img.save(f"data/processed/{znak}/{znak}_{k+1:02d}.png")
