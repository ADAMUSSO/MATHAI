# Seed: zaludne priklady na porovnanie kodov

## Ako porovnat

1. Kazdy priklad spusti vo svojom kode s presne tymito vstupmi (aj eps).
2. Porovnaj 1. a 2. iteraciu (tie sa pocitaju aj rucne) a konecny bod.
   Pri 6 desatinnych miestach sa smie lisit najviac posledna cifra.
3. Pocet iteracii sedi len vtedy, ked mas rovnake STOP pravidlo (nizsie).
4. Priklady s CHYBOU (G11, N9) maju v tvojom kode skoncit hlaskou, nie nezmyslom.

## Pravidla (musia byt rovnake, inak sa vysledky rozidu)

- **gradient:** S = -grad/||grad||, gama > 0 z phi'(gama) = 0, STOP ||grad|| < eps (pred krokom)
- **Newton:** X - H^-1 grad, STOP ||grad|| < eps (pred krokom) alebo ||X_nove - X|| < eps
- **Powell:** u1 = (1, 0), u2 = (0, 1); P0->P1 po u1, P1->P2 po u2, d = P2 - P0, P2->P3 po d; potom u1 <- u2, u2 <- d; gama moze byt zaporne; STOP ||P3 - P0|| < eps. VYNIMKA: ak je d rovnobezny s u2 (stane sa, ked v 1. kroku vyjde gama = 0), smery sa nemenia - inak by boli oba smery rovnobezne a metoda by sa zasekla mimo minima (P10, P11)
- **hladanie po priamke:** ak ma phi(gama) viac lokalnych minim, berie sa to s najmensim phi
- **Nelder-Mead:** M = (B+G)/2, R = M + a(M-W); f(R) < f(B) -> E = M + g(R-M), E ak f(E) < f(R) inak R; f(R) < f(G) -> R; inak C1 = M + r(W-M) (prednaska aj C2 = M + r(R-M), lepsi z nich), C ak f(C) < f(W), inak zmrstenie k B. STOP d = max vzdialenost od B < eps (pred iteraciou)
- **rovnost v NM:** pri rovnakom f plati vetva s nesplnenym '<'; pri zoradeni bodov s rovnakym f zostava poradie zo zadania, novy bod je pri rovnosti horsi nez stary. Cisla, ktore sa lisia len zaokruhlenim (1e-12), su rovnake (M10, M11).


## Najstrmsi gradient (normovany smer, presne gama)

**G1** - `x**2 + 2*y**2`, start (3, 1), eps = 0.001
  - pasca: zakladny priklad z hodiny (gradient (6, 4), ||grad|| = odmocnina z 52)
  - it. 1: S = (-0.832050, -0.554700), gama = 2.757186, P1 = (0.705882, -0.529412)
  - it. 2: S = (-0.554700, 0.832050), gama = 0.751960, P2 = (0.288770, 0.096257)
  - **vysledok: (0.000258, 0.000086), f = 0.000000, iteracie = 8**
  - stop: ||grad f|| = 6.19e-04 < eps po 8 iteraciach

**G2** - `x**2 - 4*x + y**2 - y - x*y`, start (0, 0), eps = 0.001
  - pasca: clen -x*y (obe derivacie zavisia od x aj y)
  - it. 1: S = (0.970143, 0.242536), gama = 2.695877, P1 = (2.615385, 0.653846)
  - it. 2: S = (-0.242536, 0.970143), gama = 0.962813, P2 = (2.381868, 1.587912)
  - **vysledok: (2.999857, 1.999500), f = -7.000000, iteracie = 11**
  - stop: ||grad f|| = 8.83e-04 < eps po 11 iteraciach

**G3** - `(x - 1)**2 + 10*(y + 2)**2`, start (-2.5, 0.5), eps = 0.001
  - pasca: desatinny a zaporny start, uzke udolie -> cik-cak, vela iteracii
  - it. 1: S = (0.138648, -0.990342), gama = 2.568824, P1 = (-2.143838, -2.044014)
  - it. 2: S = (0.990342, 0.138648), gama = 2.706286, P2 = (0.536310, -1.668793)
  - **vysledok: (0.999872, -2.000002), f = 0.000000, iteracie = 11**
  - stop: ||grad f|| = 2.59e-04 < eps po 11 iteraciach

**G4** - `x**4/4 + x**2/2 + y**2/2`, start (1, 1), eps = 0.001
  - pasca: phi(gama) je polynom 4. stupna, phi' je kubicka rovnica
  - it. 1: S = (-0.894427, -0.447214), gama = 1.335096, P1 = (-0.194146, 0.402927)
  - it. 2: S = (0.447214, -0.894427), gama = 0.447214, P2 = (0.005854, 0.002927)
  - **vysledok: (-0.000000, 0.000000), f = 0.000000, iteracie = 3**
  - stop: ||grad f|| = 8.97e-08 < eps po 3 iteraciach

**G5** - `x**3 + y**3 - 3*x*y`, start (2, 1.5), eps = 0.001
  - pasca: kubicka funkcia: phi' ma 2 korene, jeden je MAXIMUM phi -> treba vybrat minimum
  - it. 1: S = (-0.995037, -0.099504), gama = 0.850808, P1 = (1.153414, 1.415341)
  - it. 2: S = (0.099504, -0.995037), gama = 0.314694, P2 = (1.184727, 1.102209)
  - **vysledok: (1.000143, 1.000082), f = -1.000000, iteracie = 12**
  - stop: ||grad f|| = 6.14e-04 < eps po 12 iteraciach

**G6** - `x**4 + y**4`, start (1, 2), eps = 0.001
  - pasca: plocha funkcia, viacnasobny koren phi' (nroots/zaokruhlenie)
  - it. 1: S = (-0.124035, -0.992278), gama = 2.371252, P1 = (0.705882, -0.352941)
  - it. 2: S = (-0.992278, 0.124035), gama = 0.836913, P2 = (-0.124567, -0.249135)
  - **vysledok: (0.015517, 0.031034), f = 0.000001, iteracie = 4**
  - stop: ||grad f|| = 1.20e-04 < eps po 4 iteraciach

**G7** - `(x**2 + y - 11)**2 + (x + y**2 - 7)**2`, start (0, 0), eps = 0.001
  - pasca: Himmelblau: 4 minima, phi ma viac lokalnych minim -> ktore?
  - it. 1: S = (0.536875, 0.843661), gama = 3.320508, P1 = (1.782700, 2.801385)
  - it. 2: S = (0.843661, -0.536875), gama = 1.443883, P2 = (3.000848, 2.026200)
  - **vysledok: (2.999992, 2.000011), f = 0.000000, iteracie = 13**
  - stop: ||grad f|| = 4.29e-04 < eps po 13 iteraciach

**G8** - `sqrt(x**2 + 1) + (y - 2)**2`, start (3, 0), eps = 0.001
  - pasca: nie je polynom -> phi' = 0 sa neda vyriesit vzorcom (numericky)
  - it. 1: S = (-0.230769, 0.973009), gama = 2.168636, P1 = (2.499546, 2.110101)
  - it. 2: S = (-0.973009, -0.230769), gama = 2.353223, P2 = (0.209839, 1.567049)
  - **vysledok: (0.000130, 1.999725), f = 1.000000, iteracie = 6**
  - stop: ||grad f|| = 5.65e-04 < eps po 6 iteraciach

**G9** - `exp(x**2 + y**2) - 2*x`, start (1, 1), eps = 0.001
  - pasca: exponenciala, nie je polynom
  - it. 1: S = (-0.654065, -0.756438), gama = 0.907795, P1 = (0.406243, 0.313310)
  - it. 2: S = (0.756438, -0.654065), gama = 0.368368, P2 = (0.684891, 0.072373)
  - **vysledok: (0.652821, 0.000156), f = 0.225747, iteracie = 7**
  - stop: ||grad f|| = 7.29e-04 < eps po 7 iteraciach

**G10** - `x**2 + y**2`, start (0, 0), eps = 0.001
  - pasca: start uz je v minime -> 0 iteracii (ziadne delenie nulou!)
  - **vysledok: (0.000000, 0.000000), f = 0.000000, iteracie = 0**
  - stop: ||grad f|| = 0.00e+00 < eps po 0 iteraciach

**G11** - `x**3 + y**2`, start (1, 1), eps = 0.001
  - pasca: funkcia NEMA minimum -> kod ma zahlasit chybu, nie vypisat nezmysel
  - **CHYBA (ocakavana):** CHYBA: phi(gama) nema minimum - funkcia v smere S klesa do -nekonecna (funkcia nema minimum).

**G12** - `(1 - x)**2 + 100*(y - x**2)**2`, start (-1.2, 1), eps = 0.001
  - pasca: Rosenbrock: steepest je extremne pomaly -> po 100 iteraciach este nie je v (1, 1)
  - it. 1: S = (0.925848, 0.377897), gama = 2.852388, P1 = (1.440877, 2.077909)
  - it. 2: S = (0.377897, -0.925848), gama = 0.000474, P2 = (1.441056, 2.077470)
  - **vysledok: (1.430918, 2.048337), f = 0.185756, iteracie = 100**
  - stop: dosiahnuty MAX_IT = 100 (este nie je v minime)


## Newton 2D

**N1** - `x**2 + 2*y**2`, start (2, 2), eps = 0.001
  - pasca: kvadraticka funkcia -> minimum za 1 krok
  - it. 1: X1 = (0.000000, 0.000000)
  - **vysledok: (0.000000, 0.000000), f = 0.000000, iteracie = 1**, typ: **MINIMUM**
  - stop: ||grad f|| = 0.00e+00 < eps po 1 iteraciach

**N2** - `x**2 - 4*x + y**2 - y - x*y`, start (0, 0), eps = 0.001
  - pasca: H ma nenulove b = c = -1 (vymenit a<->d, zmenit znamienka b, c)
  - it. 1: X1 = (3.000000, 2.000000)
  - **vysledok: (3.000000, 2.000000), f = -7.000000, iteracie = 1**, typ: **MINIMUM**
  - stop: ||grad f|| = 0.00e+00 < eps po 1 iteraciach

**N3** - `x**4/4 + x**2/2 + y**2/2`, start (1, 1), eps = 0.001
  - pasca: priklad z cvicenia 4
  - it. 1: X1 = (0.500000, 0.000000)
  - it. 2: X2 = (0.142857, 0.000000)
  - **vysledok: (0.000000, 0.000000), f = 0.000000, iteracie = 4**, typ: **MINIMUM**
  - stop: ||grad f|| = 3.32e-07 < eps po 4 iteraciach

**N4** - `(1 - x)**2 + 100*(y - x**2)**2`, start (-1.2, 1), eps = 0.001
  - pasca: Rosenbrock (znamy X1 = (-1.1753, 1.3807))
  - it. 1: X1 = (-1.175281, 1.380674)
  - it. 2: X2 = (0.763115, -3.175034)
  - **vysledok: (0.999996, 0.999991), f = 0.000000, iteracie = 5**, typ: **MINIMUM**
  - stop: ||grad f|| = 8.61e-06 < eps po 5 iteraciach

**N5** - `(x**2 + y - 11)**2 + (x + y**2 - 7)**2`, start (0, 0), eps = 0.001
  - pasca: Newton skonci v MAXIME (-0.2708, -0.9230), nie v minime!
  - it. 1: X1 = (-0.333333, -0.846154)
  - it. 2: X2 = (-0.270761, -0.919151)
  - **vysledok: (-0.270846, -0.923028), f = 181.616522, iteracie = 3**, typ: **MAXIMUM**
  - stop: ||grad f|| = 1.68e-04 < eps po 3 iteraciach

**N6** - `x**2 - y**2`, start (1, 1), eps = 0.001
  - pasca: Newton skonci v SEDLE (0, 0)
  - it. 1: X1 = (0.000000, 0.000000)
  - **vysledok: (0.000000, 0.000000), f = 0.000000, iteracie = 1**, typ: **SEDLO**
  - stop: ||grad f|| = 0.00e+00 < eps po 1 iteraciach

**N7** - `x**3 + y**3 - 3*x*y`, start (2, 2), eps = 0.001
  - pasca: kubicka funkcia, minimum (1, 1)
  - it. 1: X1 = (1.333333, 1.333333)
  - it. 2: X2 = (1.066667, 1.066667)
  - **vysledok: (1.000015, 1.000015), f = -1.000000, iteracie = 4**, typ: **MINIMUM**
  - stop: ||grad f|| = 6.47e-05 < eps po 4 iteraciach

**N8** - `exp(x**2 + y**2) - 2*x`, start (1, 1), eps = 0.001
  - pasca: exponenciala
  - it. 1: X1 = (0.881201, 0.745866)
  - it. 2: X2 = (0.792803, 0.447818)
  - **vysledok: (0.652919, 0.000000), f = 0.225747, iteracie = 6**, typ: **MINIMUM**
  - stop: ||X6 - X5|| = 6.48e-04 < eps po 6 iteraciach

**N9** - `x**4 + y**2`, start (0, 1), eps = 0.001
  - pasca: det H = 0 v starte -> H^-1 neexistuje, kod ma zahlasit chybu
  - **CHYBA (ocakavana):** CHYBA: det H = 0, inverzna matica neexistuje -> Newton sa neda pouzit.

**N10** - `x**4 + y**4`, start (1, 1), eps = 0.001
  - pasca: det H -> 0 pri minime, Newton je tu len linearny (x -> 2x/3)
  - it. 1: X1 = (0.666667, 0.666667)
  - it. 2: X2 = (0.444444, 0.444444)
  - **vysledok: (0.039018, 0.039018), f = 0.000005, iteracie = 8**, typ: **MINIMUM**
  - stop: ||grad f|| = 3.36e-04 < eps po 8 iteraciach


## Powell

**P1** - `x**2 - 4*x + y**2 - y - x*y`, start (0, 0), eps = 0.001
  - pasca: kvadraticka -> presne minimum (3, 2) po 2 iteraciach
  - it. 1: P1 = (2.000000, 0.000000), P2 = (2.000000, 1.500000), d = (2.000000, 1.500000), P3 = (2.923077, 2.192308)
  - it. 2: P1 = (2.923077, 1.961538), P2 = (2.994083, 2.014793), d = (0.071006, -0.177515), P3 = (3.000000, 2.000000)
  - **vysledok: (3.000000, 2.000000), f = -7.000000, iteracie = 3**
  - stop: ||P3 - P0|| = 0.00e+00 < eps po 3 iteraciach

**P2** - `x**2 + 2*y**2`, start (3, 1), eps = 0.001
  - pasca: minimum najde uz P2, smer d da gama = 0
  - it. 1: P1 = (0.000000, 1.000000), P2 = (0.000000, 0.000000), d = (-3.000000, -1.000000), P3 = (0.000000, 0.000000)
  - it. 2: P1 = (0.000000, 0.000000), P2 = (0.000000, 0.000000), d = (0.000000, 0.000000), P3 = (0.000000, 0.000000)
  - **vysledok: (0.000000, 0.000000), f = 0.000000, iteracie = 2**
  - stop: ||P3 - P0|| = 0.00e+00 < eps po 2 iteraciach

**P3** - `(x - 1)**2 + (y - 2)**2 + x*y`, start (5, 5), eps = 0.001
  - pasca: ZAPORNE gama (minimum je 'za chrbtom')
  - it. 1: P1 = (-1.500000, 5.000000), P2 = (-1.500000, 2.750000), d = (-6.500000, -2.250000), P3 = (-0.732593, 3.015641)
  - it. 2: P1 = (-0.732593, 2.366297), P2 = (-0.357795, 2.496034), d = (0.374798, -0.519606), P3 = (0.000000, 2.000000)
  - **vysledok: (0.000000, 2.000000), f = 1.000000, iteracie = 3**
  - stop: ||P3 - P0|| = 0.00e+00 < eps po 3 iteraciach

**P4** - `x**4/4 + x**2/2 + y**2/2`, start (1, 1), eps = 0.001
  - pasca: phi je polynom 4. stupna
  - it. 1: P1 = (0.000000, 1.000000), P2 = (0.000000, 0.000000), d = (-1.000000, -1.000000), P3 = (0.000000, 0.000000)
  - it. 2: P1 = (0.000000, 0.000000), P2 = (0.000000, 0.000000), d = (0.000000, 0.000000), P3 = (0.000000, 0.000000)
  - **vysledok: (0.000000, 0.000000), f = 0.000000, iteracie = 2**
  - stop: ||P3 - P0|| = 0.00e+00 < eps po 2 iteraciach

**P5** - `(1 - x)**2 + 100*(y - x**2)**2`, start (-1.2, 1), eps = 0.001
  - pasca: na priamke y = 1 su 2 lokalne minima phi -> berie sa to s mensim phi (x = 1)
  - it. 1: P1 = (1.000000, 1.000000), P2 = (1.000000, 1.000000), d = (2.200000, 0.000000), P3 = (1.000000, 1.000000)
  - it. 2: P1 = (1.000000, 1.000000), P2 = (1.000000, 1.000000), d = (0.000000, 0.000000), P3 = (1.000000, 1.000000)
  - **vysledok: (1.000000, 1.000000), f = 0.000000, iteracie = 2**
  - stop: ||P3 - P0|| = 0.00e+00 < eps po 2 iteraciach

**P6** - `(x**2 + y - 11)**2 + (x + y**2 - 7)**2`, start (0, 0), eps = 0.001
  - pasca: Himmelblau: ktore zo 4 minim (zavisi od vyberu minima na priamke)
  - it. 1: P1 = (3.395691, 0.000000), P2 = (3.395691, -1.803183), d = (3.395691, -1.803183), P3 = (3.579537, -1.900809)
  - it. 2: P1 = (3.579537, -1.846968), P2 = (3.584311, -1.849503), d = (0.004774, 0.051306), P3 = (3.584438, -1.848132)
  - **vysledok: (3.584428, -1.848127), f = 0.000000, iteracie = 3**
  - stop: ||P3 - P0|| = 1.13e-05 < eps po 3 iteraciach

**P7** - `sqrt(x**2 + 1) + (y - 2)**2`, start (3, 0), eps = 0.001
  - pasca: nie je polynom (numericke hladanie po priamke)
  - it. 1: P1 = (0.000000, 0.000000), P2 = (0.000000, 2.000000), d = (-3.000000, 2.000000), P3 = (-0.000000, 2.000000)
  - it. 2: P1 = (-0.000000, 2.000000), P2 = (0.000000, 2.000000), d = (0.000000, -0.000000), P3 = (0.000000, 2.000000)
  - **vysledok: (0.000000, 2.000000), f = 1.000000, iteracie = 2**
  - stop: ||P3 - P0|| = 2.01e-15 < eps po 2 iteraciach

**P8** - `x**3 + y**3 - 3*x*y`, start (2, 2), eps = 0.001
  - pasca: kubicka: phi' ma koren s maximom aj minimom, minimum je pri zapornom gama
  - it. 1: P1 = (1.414214, 2.000000), P2 = (1.414214, 1.189207), d = (-0.585786, -0.810793), P3 = (1.203458, 0.897498)
  - it. 2: P1 = (1.203458, 1.097022), P2 = (1.102297, 0.957004), d = (-0.101162, 0.059505), P3 = (1.009660, 1.011495)
  - **vysledok: (1.000000, 1.000000), f = -1.000000, iteracie = 4**
  - stop: ||P3 - P0|| = 7.05e-08 < eps po 4 iteraciach

**P9** - `x**2 + y**2`, start (0, 0), eps = 0.001
  - pasca: start v minime -> d = (0, 0), ziadne delenie nulou
  - it. 1: P1 = (0.000000, 0.000000), P2 = (0.000000, 0.000000), d = (0.000000, 0.000000), P3 = (0.000000, 0.000000)
  - **vysledok: (0.000000, 0.000000), f = 0.000000, iteracie = 1**
  - stop: ||P3 - P0|| = 0.00e+00 < eps po 1 iteraciach

**P10** - `x**2 + y**2 + x*y - 3*y`, start (0, 0), eps = 0.001
  - pasca: v starte je df/dx = 0 -> gama1 = 0, d je rovnobezny s u2; ked sa smery posunu, metoda sa ZASEKNE v (0, 1.5) namiesto minima (-1, 2) -> smery nemenit
  - it. 1: P1 = (0.000000, 0.000000), P2 = (0.000000, 1.500000), d = (0.000000, 1.500000), P3 = (0.000000, 1.500000)
  - it. 2: P1 = (-0.750000, 1.500000), P2 = (-0.750000, 1.875000), d = (-0.750000, 0.375000), P3 = (-1.000000, 2.000000)
  - **vysledok: (-1.000000, 2.000000), f = -3.000000, iteracie = 3**
  - stop: ||P3 - P0|| = 0.00e+00 < eps po 3 iteraciach

**P11** - `x**2 - 4*x + y**2 - y - x*y`, start (2, 0), eps = 0.001
  - pasca: ta ista pasca ako P10 (df/dx(2, 0) = 0), zasekol by sa v (2, 1.5) namiesto (3, 2)
  - it. 1: P1 = (2.000000, 0.000000), P2 = (2.000000, 1.500000), d = (0.000000, 1.500000), P3 = (2.000000, 1.500000)
  - it. 2: P1 = (2.750000, 1.500000), P2 = (2.750000, 1.875000), d = (0.750000, 0.375000), P3 = (3.000000, 2.000000)
  - **vysledok: (3.000000, 2.000000), f = -7.000000, iteracie = 3**
  - stop: ||P3 - P0|| = 0.00e+00 < eps po 3 iteraciach


## Nelder-Mead

**M1** - `x**2 + y**2 + x - 2*y - x*y + 2`, body [(1.2, 0), (0, 0.8), (0, 0)], kontrakcia: cvicenie, eps = 0.001
  - pasca: slajd 27 z cvicenia (vzor zapoctu), kontrakcia len C1
  - it. 1: B = (0.000000, 0.800000), G = (0.000000, 0.000000), W = (1.200000, 0.000000), f(R) = 2.240000 -> **kontrakcia C1** -> (0.000000, 0.800000), (0.000000, 0.000000), (0.600000, 0.200000)
  - it. 2: B = (0.000000, 0.800000), G = (0.000000, 0.000000), W = (0.600000, 0.200000), f(R) = 1.280000 -> **reflexia R** -> (0.000000, 0.800000), (0.000000, 0.000000), (-0.600000, 0.600000)
  - it. 3: B = (0.000000, 0.800000), G = (-0.600000, 0.600000), W = (0.000000, 0.000000), f(R) = 1.760000 -> **kontrakcia C1** -> (0.000000, 0.800000), (-0.600000, 0.600000), (-0.150000, 0.350000)
  - **vysledok: (0.000188, 1.000444), f = 1.000000, iteracie = 26**
  - stop: d = 9.83e-04 < eps po 26 iteraciach

**M2** - `x**2 - 4*x + y**2 - y - x*y`, body [(0, 0), (1.2, 0), (0, 0.8)], kontrakcia: prednaska, eps = 0.001
  - pasca: vzorovy priklad z prednasky 4 (C1 aj C2)
  - it. 1: B = (1.200000, 0.000000), G = (0.000000, 0.800000), W = (0.000000, 0.000000), f(R) = -4.480000 -> **expanzia E** -> (1.200000, 0.000000), (0.000000, 0.800000), (1.800000, 1.200000)
  - it. 2: B = (1.800000, 1.200000), G = (1.200000, 0.000000), W = (0.000000, 0.800000), f(R) = -4.440000 -> **reflexia R** -> (1.800000, 1.200000), (1.200000, 0.000000), (3.000000, 0.400000)
  - it. 3: B = (1.800000, 1.200000), G = (3.000000, 0.400000), W = (1.200000, 0.000000), f(R) = -6.240000 -> **reflexia R (E nepomohol)** -> (1.800000, 1.200000), (3.000000, 0.400000), (3.600000, 1.600000)
  - **vysledok: (2.999853, 1.999805), f = -7.000000, iteracie = 31**
  - stop: d = 7.15e-04 < eps po 31 iteraciach

**M3** - `x**2 - 4*x + y**2 - y - x*y`, body [(0, 0), (1.2, 0), (0, 0.8)], kontrakcia: cvicenie, eps = 0.001
  - pasca: ten isty priklad, verzia z cvicenia -> porovnaj s M2, kde sa rozidu
  - it. 1: B = (1.200000, 0.000000), G = (0.000000, 0.800000), W = (0.000000, 0.000000), f(R) = -4.480000 -> **expanzia E** -> (1.200000, 0.000000), (0.000000, 0.800000), (1.800000, 1.200000)
  - it. 2: B = (1.800000, 1.200000), G = (1.200000, 0.000000), W = (0.000000, 0.800000), f(R) = -4.440000 -> **reflexia R** -> (1.800000, 1.200000), (1.200000, 0.000000), (3.000000, 0.400000)
  - it. 3: B = (1.800000, 1.200000), G = (3.000000, 0.400000), W = (1.200000, 0.000000), f(R) = -6.240000 -> **reflexia R (E nepomohol)** -> (1.800000, 1.200000), (3.000000, 0.400000), (3.600000, 1.600000)
  - **vysledok: (3.000259, 2.000420), f = -7.000000, iteracie = 31**
  - stop: d = 8.56e-04 < eps po 31 iteraciach

**M4** - `x**2 - 4*x + y**2 - y - x*y`, body [(0, 1), (1, 1), (0, 1.5)], kontrakcia: cvicenie, eps = 0.001
  - pasca: priklad z fotky cvicenia 4
  - it. 1: B = (1.000000, 1.000000), G = (0.000000, 1.000000), W = (0.000000, 1.500000), f(R) = -3.750000 -> **reflexia R** -> (1.000000, 1.000000), (0.000000, 1.000000), (1.000000, 0.500000)
  - it. 2: B = (1.000000, 1.000000), G = (1.000000, 0.500000), W = (0.000000, 1.000000), f(R) = -5.250000 -> **reflexia R (E nepomohol)** -> (1.000000, 1.000000), (1.000000, 0.500000), (2.000000, 0.500000)
  - it. 3: B = (2.000000, 0.500000), G = (1.000000, 1.000000), W = (1.000000, 0.500000), f(R) = -6.000000 -> **expanzia E** -> (2.000000, 0.500000), (1.000000, 1.000000), (2.500000, 1.250000)
  - **vysledok: (3.000000, 2.000000), f = -7.000000, iteracie = 37**
  - stop: d = 5.47e-04 < eps po 37 iteraciach

**M5** - `x**2 + 2*y**2`, body [(2, 2), (2, 1), (1, 2)], kontrakcia: cvicenie, eps = 0.001
  - pasca: priklad z cvicenia 4 (A, B, C)
  - it. 1: B = (2.000000, 1.000000), G = (1.000000, 2.000000), W = (2.000000, 2.000000), f(R) = 3.000000 -> **expanzia E** -> (2.000000, 1.000000), (1.000000, 2.000000), (0.500000, 0.500000)
  - it. 2: B = (0.500000, 0.500000), G = (2.000000, 1.000000), W = (1.000000, 2.000000), f(R) = 2.750000 -> **reflexia R** -> (0.500000, 0.500000), (2.000000, 1.000000), (1.500000, -0.500000)
  - it. 3: B = (0.500000, 0.500000), G = (1.500000, -0.500000), W = (2.000000, 1.000000), f(R) = 2.000000 -> **reflexia R** -> (0.500000, 0.500000), (1.500000, -0.500000), (0.000000, -1.000000)
  - **vysledok: (-0.000426, -0.000004), f = 0.000000, iteracie = 28**
  - stop: d = 8.23e-04 < eps po 28 iteraciach

**M6** - `x**2 + y**2`, body [(-1, 3), (0, 4), (1, 2)], kontrakcia: prednaska, eps = 0.001
  - pasca: v 2. iteracii je lepsi C2 nez C1
  - it. 1: B = (1.000000, 2.000000), G = (-1.000000, 3.000000), W = (0.000000, 4.000000), f(R) = 1.000000 -> **expanzia E** -> (1.000000, 2.000000), (-1.000000, 3.000000), (0.000000, -0.500000)
  - it. 2: B = (0.000000, -0.500000), G = (1.000000, 2.000000), W = (-1.000000, 3.000000), f(R) = 6.250000 -> **kontrakcia C2** -> (0.000000, -0.500000), (1.000000, 2.000000), (1.250000, -0.375000)
  - it. 3: B = (0.000000, -0.500000), G = (1.250000, -0.375000), W = (1.000000, 2.000000), f(R) = 8.328125 -> **kontrakcia C1** -> (0.000000, -0.500000), (1.250000, -0.375000), (0.812500, 0.781250)
  - **vysledok: (-0.000227, 0.000231), f = 0.000000, iteracie = 28**
  - stop: d = 9.29e-04 < eps po 28 iteraciach

**M7** - `x**2 + y**2`, body [(-1, 3), (0, 4), (1, 2)], kontrakcia: cvicenie, eps = 0.001
  - pasca: ten isty, len C1 -> ina cesta nez M6
  - it. 1: B = (1.000000, 2.000000), G = (-1.000000, 3.000000), W = (0.000000, 4.000000), f(R) = 1.000000 -> **expanzia E** -> (1.000000, 2.000000), (-1.000000, 3.000000), (0.000000, -0.500000)
  - it. 2: B = (0.000000, -0.500000), G = (1.000000, 2.000000), W = (-1.000000, 3.000000), f(R) = 6.250000 -> **kontrakcia C1** -> (0.000000, -0.500000), (1.000000, 2.000000), (-0.250000, 1.875000)
  - it. 3: B = (0.000000, -0.500000), G = (-0.250000, 1.875000), W = (1.000000, 2.000000), f(R) = 1.953125 -> **reflexia R** -> (0.000000, -0.500000), (-0.250000, 1.875000), (-1.250000, -0.625000)
  - **vysledok: (0.000203, 0.000229), f = 0.000000, iteracie = 31**
  - stop: d = 7.25e-04 < eps po 31 iteraciach

**M8** - `x**4 - 3*x**2 + y**2`, body [(-1.3, 0.2), (0.8, 0.7), (-0.5, -0.2)], kontrakcia: cvicenie, eps = 0.001
  - pasca: ZMRSTENIE hned v 1. iteracii
  - it. 1: B = (-1.300000, 0.200000), G = (0.800000, 0.700000), W = (-0.500000, -0.200000), f(R) = 1.210000 -> **zmrstenie** -> (-1.300000, 0.200000), (-0.250000, 0.450000), (-0.900000, 0.000000)
  - it. 2: B = (-1.300000, 0.200000), G = (-0.900000, 0.000000), W = (-0.250000, 0.450000), f(R) = 3.114006 -> **kontrakcia C1** -> (-1.300000, 0.200000), (-0.900000, 0.000000), (-0.675000, 0.275000)
  - it. 3: B = (-1.300000, 0.200000), G = (-0.900000, 0.000000), W = (-0.675000, 0.275000), f(R) = -1.562718 -> **kontrakcia C1** -> (-1.300000, 0.200000), (-0.900000, 0.000000), (-0.887500, 0.187500)
  - **vysledok: (-1.224850, -0.000057), f = -2.250000, iteracie = 25**
  - stop: d = 6.68e-04 < eps po 25 iteraciach

**M9** - `x**2 + y**2`, body [(1, 0), (0, 1), (-1, 0)], kontrakcia: cvicenie, eps = 0.001
  - pasca: ROVNOST: vsetky 3 body maju f = 1 -> poradie podla zadania
  - it. 1: B = (1.000000, 0.000000), G = (0.000000, 1.000000), W = (-1.000000, 0.000000), f(R) = 5.000000 -> **kontrakcia C1** -> (1.000000, 0.000000), (0.000000, 1.000000), (-0.250000, 0.250000)
  - it. 2: B = (-0.250000, 0.250000), G = (1.000000, 0.000000), W = (0.000000, 1.000000), f(R) = 1.125000 -> **kontrakcia C1** -> (-0.250000, 0.250000), (1.000000, 0.000000), (0.187500, 0.562500)
  - it. 3: B = (-0.250000, 0.250000), G = (0.187500, 0.562500), W = (1.000000, 0.000000), f(R) = 1.789062 -> **kontrakcia C1** -> (-0.250000, 0.250000), (0.187500, 0.562500), (0.484375, 0.203125)
  - **vysledok: (-0.000065, -0.000121), f = 0.000000, iteracie = 27**
  - stop: d = 6.00e-04 < eps po 27 iteraciach

**M10** - `x**2 + y**2`, body [(1.1, -0.7), (-0.4, 0.7), (2.0, -0.1)], kontrakcia: cvicenie, eps = 0.001
  - pasca: ZAOKRUHLENIE: presne f(R) = f(G) = 1.7, ale v pocitaci f(R) = 1.6999999999999995 a f(G) = 1.7000000000000002 -> naivny kod (<) spravi reflexiu namiesto kontrakcie
  - it. 1: B = (-0.400000, 0.700000), G = (1.100000, -0.700000), W = (2.000000, -0.100000), f(R) = 1.700000 -> **kontrakcia C1** -> (-0.400000, 0.700000), (1.100000, -0.700000), (1.175000, -0.050000)
  - it. 2: B = (-0.400000, 0.700000), G = (1.175000, -0.050000), W = (1.100000, -0.700000), f(R) = 1.928125 -> **kontrakcia C1** -> (-0.400000, 0.700000), (1.175000, -0.050000), (0.743750, -0.187500)
  - it. 3: B = (0.743750, -0.187500), G = (-0.400000, 0.700000), W = (1.175000, -0.050000), f(R) = 1.007383 -> **kontrakcia C1** -> (0.743750, -0.187500), (-0.400000, 0.700000), (0.673438, 0.103125)
  - **vysledok: (0.000266, 0.000050), f = 0.000000, iteracie = 33**
  - stop: d = 8.16e-04 < eps po 33 iteraciach

**M11** - `x**2 + y**2`, body [(0.4, 1.2), (1.1, 0.2), (0.5, 1.9)], kontrakcia: cvicenie, eps = 0.001
  - pasca: ZAOKRUHLENIE: presne f(R) = f(B) = 1.25, ale v pocitaci f(R) = 1.25 a f(B) = 1.2500000000000002 -> naivny kod (<) skusi expanziu namiesto reflexie
  - it. 1: B = (1.100000, 0.200000), G = (0.400000, 1.200000), W = (0.500000, 1.900000), f(R) = 1.250000 -> **reflexia R** -> (1.100000, 0.200000), (0.400000, 1.200000), (1.000000, -0.500000)
  - it. 2: B = (1.100000, 0.200000), G = (1.000000, -0.500000), W = (0.400000, 1.200000), f(R) = 5.140000 -> **kontrakcia C1** -> (1.100000, 0.200000), (1.000000, -0.500000), (0.725000, 0.525000)
  - it. 3: B = (0.725000, 0.525000), G = (1.100000, 0.200000), W = (1.000000, -0.500000), f(R) = 2.181250 -> **kontrakcia C1** -> (0.725000, 0.525000), (1.100000, 0.200000), (0.956250, -0.068750)
  - **vysledok: (-0.000269, 0.000152), f = 0.000000, iteracie = 31**
  - stop: d = 9.75e-04 < eps po 31 iteraciach

**M12** - `x**2 - 4*x + y**2 - y - x*y`, body [(0, 0), (1.2, 0), (0, 0.8)], kontrakcia: cvicenie, alfa=1, gama=3, rho=0.25, sigma=0.5, eps = 0.001
  - pasca: ine koeficienty (gama = 3, rho = 0.25) -> vseobecne vzorce M + k*(smer)
  - it. 1: B = (1.200000, 0.000000), G = (0.000000, 0.800000), W = (0.000000, 0.000000), f(R) = -4.480000 -> **expanzia E** -> (1.200000, 0.000000), (0.000000, 0.800000), (2.400000, 1.600000)
  - it. 2: B = (2.400000, 1.600000), G = (1.200000, 0.000000), W = (0.000000, 0.800000), f(R) = -4.480000 -> **reflexia R** -> (2.400000, 1.600000), (1.200000, 0.000000), (3.600000, 0.800000)
  - it. 3: B = (2.400000, 1.600000), G = (3.600000, 0.800000), W = (1.200000, 0.000000), f(R) = -4.320000 -> **kontrakcia C1** -> (2.400000, 1.600000), (3.600000, 0.800000), (2.550000, 0.900000)
  - **vysledok: (3.000318, 1.998552), f = -6.999997, iteracie = 22**
  - stop: d = 6.59e-04 < eps po 22 iteraciach

**M13** - `(1 - x)**2 + 100*(y - x**2)**2`, body [(-1.2, 1), (-0.7, 1), (-1.2, 1.5)], kontrakcia: cvicenie, eps = 0.001
  - pasca: Rosenbrock, dlhy beh (vela kontrakcii aj expanzii)
  - it. 1: B = (-1.200000, 1.500000), G = (-1.200000, 1.000000), W = (-0.700000, 1.000000), f(R) = 200.500000 -> **kontrakcia C1** -> (-1.200000, 1.500000), (-1.200000, 1.000000), (-0.950000, 1.125000)
  - it. 2: B = (-1.200000, 1.500000), G = (-0.950000, 1.125000), W = (-1.200000, 1.000000), f(R) = 56.003125 -> **kontrakcia C1** -> (-1.200000, 1.500000), (-0.950000, 1.125000), (-1.137500, 1.156250)
  - it. 3: B = (-1.200000, 1.500000), G = (-1.137500, 1.156250), W = (-0.950000, 1.125000), f(R) = 21.216370 -> **kontrakcia C1** -> (-1.200000, 1.500000), (-1.137500, 1.156250), (-1.059375, 1.226562)
  - **vysledok: (1.000184, 1.000381), f = 0.000000, iteracie = 79**
  - stop: d = 9.48e-04 < eps po 79 iteraciach

