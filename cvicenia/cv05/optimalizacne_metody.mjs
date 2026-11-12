/**
 * Jednoduché 2D implementácie metód z uloga1_metody.html.
 *
 * AKO ČÍTAŤ VÝSLEDKY
 * Pri rovnakej funkcii, počiatočnom bode, parametroch a implementácii je beh
 * týchto metód deterministický: mali by vyjsť rovnaké výsledky (prípadne s
 * nepatrnou odchýlkou zaokrúhlenia). Ak trom ľuďom vyjdú rôzne hodnoty, zvyčajne
 * nepoužili úplne rovnaký algoritmus alebo rovnaké nastavenia. Skontrolujte najmä:
 *   - α pri gradientovej metóde,
 *   - veľkosť počiatočného simplexu pri Nelderovej–Meadovej metóde,
 *   - toleranciu a spôsob hľadania minima na priamke pri Powellovej metóde,
 *   - toleranciu zastavenia, definíciu chyby a maximálny počet iterácií,
 *   - či sa počíta počet iterácií, vyhodnotení funkcie alebo obe veličiny.
 * Rôzne metódy môžu zo spoločného štartu skončiť v rôznych minimách, najmä ak
 * má funkcia viac lokálnych miním. To je očakávané; rozdiel medzi ľuďmi pri tej
 * istej metóde znamená, že sa líši aspoň jedna z uvedených vecí.
 *
 * ČO ROBÍ KAŽDÁ METÓDA
 * 1. Gradientová: x_(k+1) = x_k − α∇f(x_k). α určuje dĺžku kroku.
 * 2. Newtonova:   x_(k+1) = x_k − H(x_k)^(-1)∇f(x_k). Používa gradient aj
 *                  Hessián; krok môže byť veľký a nemusí vždy smerovať k minimu.
 * 3. Nelder–Mead: porovnáva tri vrcholy trojuholníka (simplexu) a skúša
 *                  odraz, rozšírenie, kontrakciu alebo zmenšenie simplexu.
 *                  Nepotrebuje derivácie.
 * 4. Powellova:   postupne minimalizuje funkciu pozdĺž smerov. Tu používa dva
 *                  súradnicové smery a potom smer posunu za celý cyklus; minimum
 *                  na priamke hľadá zátvorkovaním a zlatým rezom. Nepotrebuje
 *                  derivácie.
 *
 * Poznámka k tomuto výukovému programu: zastavenie sa kontroluje vzdialenosťou
 * od známych zadaných miním, nie normou gradientu ani zmenou hodnoty f. Preto
 * sa pri porovnaní s iným programom musí zhodovať aj stopovacie kritérium.
 * Niektoré uvedené súradnice miním (napr. pri Himmelblauovej funkcii) sú len
 * zaokrúhlené, čo môže ovplyvniť okamih zastavenia pri veľmi malom TOL.
 *
 * Spustenie: node output/optimalizacne_metody.mjs
 * Použitie v inom ES module: import { runAll, functions } from './optimalizacne_metody.mjs';
 */
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const DEFAULTS = {
  tol: 1e-3,
  alpha: 0.01,
  simplexSide: 0.1,
  lineTol: 1e-5,
  maxIterations: 20_000,
};

export const functions = {
  sphere: {
    name: 'Sféra', start: [3, 2], minima: [[0, 0]],
    f: ([x, y]) => x * x + y * y,
    gradient: ([x, y]) => [2 * x, 2 * y],
    hessian: () => [[2, 0], [0, 2]],
  },
  stretched: {
    name: 'Pretiahnutá kvadratická', start: [3, 1], minima: [[0, 0]],
    f: ([x, y]) => x * x + 25 * y * y,
    gradient: ([x, y]) => [2 * x, 50 * y],
    hessian: () => [[2, 0], [0, 50]],
  },
  booth: {
    name: 'Booth', start: [0, 0], minima: [[1, 3]],
    f: ([x, y]) => (x + 2 * y - 7) ** 2 + (2 * x + y - 5) ** 2,
    gradient: ([x, y]) => {
      const a = x + 2 * y - 7, b = 2 * x + y - 5;
      return [2 * a + 4 * b, 4 * a + 2 * b];
    },
    hessian: () => [[10, 8], [8, 10]],
  },
  matyas: {
    name: 'Matyas', start: [5, -3], minima: [[0, 0]],
    f: ([x, y]) => 0.26 * (x * x + y * y) - 0.48 * x * y,
    gradient: ([x, y]) => [0.52 * x - 0.48 * y, 0.52 * y - 0.48 * x],
    hessian: () => [[0.52, -0.48], [-0.48, 0.52]],
  },
  rosenbrock: {
    name: 'Rosenbrock', start: [-1.2, 1], minima: [[1, 1]],
    f: ([x, y]) => (1 - x) ** 2 + 100 * (y - x * x) ** 2,
    gradient: ([x, y]) => {
      const r = y - x * x;
      return [2 * (x - 1) - 400 * x * r, 200 * r];
    },
    hessian: ([x, y]) => [[2 - 400 * (y - x * x) + 800 * x * x, -400 * x], [-400 * x, 200]],
  },
  himmelblau: {
    name: 'Himmelblau', start: [0, 0],
    minima: [[3, 2], [-2.805, 3.131], [-3.779, -3.283], [3.584, -1.848]],
    f: ([x, y]) => (x * x + y - 11) ** 2 + (x + y * y - 7) ** 2,
    gradient: ([x, y]) => {
      const a = x * x + y - 11, b = x + y * y - 7;
      return [4 * x * a + 2 * b, 2 * a + 4 * y * b];
    },
    hessian: ([x, y]) => {
      const a = x * x + y - 11, b = x + y * y - 7;
      return [[4 * a + 8 * x * x + 2, 4 * x + 4 * y], [4 * x + 4 * y, 2 + 4 * b + 8 * y * y]];
    },
  },
  beale: {
    name: 'Beale', start: [1, 1], minima: [[3, 0.5]],
    f: ([x, y]) => [1.5, 2.25, 2.625].reduce((sum, c, i) => sum + (c - x + x * y ** (i + 1)) ** 2, 0),
    gradient: ([x, y]) => {
      const c = [1.5, 2.25, 2.625]; let gx = 0, gy = 0;
      for (let i = 1; i <= 3; i++) {
        const r = c[i - 1] - x + x * y ** i;
        gx += 2 * r * (y ** i - 1);
        gy += 2 * r * x * i * y ** (i - 1);
      }
      return [gx, gy];
    },
    hessian: ([x, y]) => {
      const c = [1.5, 2.25, 2.625]; let xx = 0, xy = 0, yy = 0;
      for (let i = 1; i <= 3; i++) {
        const r = c[i - 1] - x + x * y ** i;
        const rx = y ** i - 1, ry = x * i * y ** (i - 1);
        const rxy = i * y ** (i - 1), ryy = i > 1 ? x * i * (i - 1) * y ** (i - 2) : 0;
        xx += 2 * rx * rx;
        xy += 2 * (rx * ry + r * rxy);
        yy += 2 * (ry * ry + r * ryy);
      }
      return [[xx, xy], [xy, yy]];
    },
  },
  custom: {
    name: 'Vlastná kvartická funkcia', start: [0.5, -0.5],
    minima: [[-1, -1], [-1, 1], [1, -1], [1, 1]],
    f: ([x, y]) => (x * x - 1) ** 2 + (y * y - 1) ** 2,
    gradient: ([x, y]) => [4 * x * (x * x - 1), 4 * y * (y * y - 1)],
    hessian: ([x, y]) => [[12 * x * x - 4, 0], [0, 12 * y * y - 4]],
  },
};

const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
const mul = (a, s) => [a[0] * s, a[1] * s];
const norm = (a) => Math.hypot(a[0], a[1]);
const nearestDistance = (x, minima) => Math.min(...minima.map((m) => norm(sub(x, m))));

function countedFunction(f) {
  let evaluations = 0;
  return {
    evaluate(x) {
      evaluations++;
      const value = f(x);
      return Number.isFinite(value) ? value : Infinity;
    },
    get evaluations() { return evaluations; },
  };
}

function makeResult(state, iterations, F, x, trace, reason = '') {
  return { state, iterations, evaluations: F.evaluations, point: x, trace, reason };
}

// Gradientový zostup: v každom kroku ideme proti gradientu. Funkcia sa
// vyhodnotí na štarte a potom raz v každom novom bode.
function gradientDescent(f, options) {
  const F = countedFunction(f.f), x = f.start.slice(), trace = [x.slice()];
  F.evaluate(x);
  if (nearestDistance(x, f.minima) < options.tol) return makeResult('ok', 0, F, x, trace);
  for (let k = 1; k <= options.maxIterations; k++) {
    const g = f.gradient(x), next = sub(x, mul(g, options.alpha));
    if (!next.every(Number.isFinite) || norm(next) > 1e100)
      return makeResult('fail', k, F, x, trace, 'Divergencia; krok α môže byť príliš veľký.');
    F.evaluate(next);
    x.splice(0, 2, ...next);
    trace.push(x.slice());
    if (nearestDistance(x, f.minima) < options.tol) return makeResult('ok', k, F, x.slice(), trace);
  }
  return makeResult('limit', options.maxIterations, F, x.slice(), trace, 'Dosiahnutý limit iterácií.');
}

// Newtonova metóda pre 2D: vyriešime H * krok = -gradient pomocou vzorca pre
// inverziu matice 2×2. Ak je determinant H takmer nula, krok sa nedá spoľahlivo
// vypočítať. Každá iterácia vyhodnotí f v novom bode.
function newton(f, options) {
  const F = countedFunction(f.f), x = f.start.slice(), trace = [x.slice()];
  F.evaluate(x);
  if (nearestDistance(x, f.minima) < options.tol) return makeResult('ok', 0, F, x, trace);
  for (let k = 1; k <= options.maxIterations; k++) {
    const g = f.gradient(x), H = f.hessian(x);
    const det = H[0][0] * H[1][1] - H[0][1] * H[1][0];
    if (!Number.isFinite(det) || Math.abs(det) < 1e-14)
      return makeResult('fail', k - 1, F, x.slice(), trace, 'Hesián je singulárny.');
    const step = [(-H[1][1] * g[0] + H[0][1] * g[1]) / det,
      (H[1][0] * g[0] - H[0][0] * g[1]) / det];
    const next = add(x, step);
    if (!next.every(Number.isFinite) || norm(next) > 1e100)
      return makeResult('fail', k - 1, F, x.slice(), trace, 'Newtonov krok diverguje.');
    F.evaluate(next);
    x.splice(0, 2, ...next);
    trace.push(x.slice());
    if (nearestDistance(x, f.minima) < options.tol) return makeResult('ok', k, F, x.slice(), trace);
  }
  return makeResult('limit', options.maxIterations, F, x.slice(), trace, 'Dosiahnutý limit iterácií.');
}

// Nelder–Mead v 2D používa simplex s tromi vrcholmi. Jeden cyklus môže
// vyhodnotiť f viackrát (napr. odraz aj rozšírenie), preto počet vyhodnotení f
// nie je totožný s počtom iterácií.
function nelderMead(f, options) {
  const F = countedFunction(f.f), start = f.start.slice();
  const simplex = [{ x: start, value: F.evaluate(start) }];
  for (let j = 0; j < 2; j++) {
    const point = start.slice();
    point[j] += options.simplexSide * Math.max(1, Math.abs(point[j]));
    simplex.push({ x: point, value: F.evaluate(point) });
  }
  const trace = [start.slice()];
  for (let k = 1; k <= options.maxIterations; k++) {
    simplex.sort((a, b) => a.value - b.value);
    let [best, good, worst] = simplex;
    if (nearestDistance(best.x, f.minima) < options.tol)
      return makeResult('ok', k - 1, F, best.x.slice(), trace.concat([best.x.slice()]));
    const center = mul(add(best.x, good.x), 0.5);
    const reflected = add(center, sub(center, worst.x));
    const reflectedValue = F.evaluate(reflected);

    if (reflectedValue < best.value) {
      const expanded = add(center, mul(sub(reflected, center), 2));
      const expandedValue = F.evaluate(expanded);
      simplex[2] = expandedValue < reflectedValue
        ? { x: expanded, value: expandedValue }
        : { x: reflected, value: reflectedValue };
    } else if (reflectedValue < good.value) {
      simplex[2] = { x: reflected, value: reflectedValue };
    } else {
      const outside = reflectedValue < worst.value;
      const contracted = outside
        ? add(center, mul(sub(reflected, center), 0.5))
        : add(center, mul(sub(worst.x, center), 0.5));
      const contractedValue = F.evaluate(contracted);
      if (contractedValue < (outside ? reflectedValue : worst.value)) {
        simplex[2] = { x: contracted, value: contractedValue };
      } else {
        for (let i = 1; i < 3; i++) {
          const point = add(best.x, mul(sub(simplex[i].x, best.x), 0.5));
          simplex[i] = { x: point, value: F.evaluate(point) };
        }
      }
    }
    simplex.sort((a, b) => a.value - b.value);
    trace.push(simplex[0].x.slice());
    if (nearestDistance(simplex[0].x, f.minima) < options.tol)
      return makeResult('ok', k, F, simplex[0].x.slice(), trace);
  }
  simplex.sort((a, b) => a.value - b.value);
  return makeResult('limit', options.maxIterations, F, simplex[0].x.slice(), trace, 'Dosiahnutý limit iterácií.');
}

// Pomocná metóda pre Powellovu metódu: najprv nájde interval obsahujúci minimum
// pozdĺž daného smeru, potom ho zužuje zlatým rezom. Jedno také hľadanie potrebuje
// viac vyhodnotení f, čo vysvetľuje vysoký počet vyhodnotení pri Powellovi.
function goldenSection(F, x, direction, lineTol) {
  const step = 1 / Math.max(norm(direction), 1e-12);
  const at = (t) => F.evaluate(add(x, mul(direction, t)));
  const centerValue = at(0), plusValue = at(step), minusValue = at(-step);
  let sign = 1, a, b;
  if (plusValue < centerValue || minusValue < centerValue) {
    sign = plusValue <= minusValue ? 1 : -1;
    let previous = sign === 1 ? plusValue : minusValue, t = step;
    a = 0; b = 2 * t;
    for (let i = 0; i < 80; i++) {
      const nextT = 2 * t, nextValue = at(sign * nextT);
      if (nextValue >= previous) { b = nextT; break; }
      t = nextT; previous = nextValue; b = i === 79 ? t : 2 * t;
    }
  } else {
    a = -step; b = step;
  }
  const ratio = (Math.sqrt(5) - 1) / 2;
  let c = b - ratio * (b - a), d = a + ratio * (b - a);
  let fc = at(sign * c), fd = at(sign * d);
  for (let i = 0; i < 240 && Math.abs(b - a) > lineTol * (1 + Math.abs(a) + Math.abs(b)); i++) {
    if (fc < fd) {
      b = d; d = c; fd = fc; c = b - ratio * (b - a); fc = at(sign * c);
    } else {
      a = c; c = d; fc = fd; d = a + ratio * (b - a); fd = at(sign * d);
    }
  }
  const point = add(x, mul(direction, sign * (a + b) / 2));
  return { point, value: F.evaluate(point) };
}

// Jeden Powellov cyklus: minimalizácia v smere x, potom v smere y a napokon
// v smere celkového posunu cyklu. Počet iterácií tu znamená počet takých cyklov;
// vyhodnotení f je oveľa viac, lebo každé hľadanie na priamke ich potrebuje veľa.
function powell(f, options) {
  const F = countedFunction(f.f);
  let x = f.start.slice();
  const directions = [[1, 0], [0, 1]];
  F.evaluate(x);
  const trace = [x.slice()];
  if (nearestDistance(x, f.minima) < options.tol) return makeResult('ok', 0, F, x, trace);
  for (let k = 1; k <= options.maxIterations; k++) {
    const start = x.slice();
    for (const direction of directions) x = goldenSection(F, x, direction, options.lineTol).point;
    const newDirection = sub(x, start);
    if (norm(newDirection) > 1e-12) {
      x = goldenSection(F, x, newDirection, options.lineTol).point;
    }
    trace.push(x.slice());
    if (nearestDistance(x, f.minima) < options.tol) return makeResult('ok', k, F, x.slice(), trace);
  }
  return makeResult('limit', options.maxIterations, F, x.slice(), trace, 'Dosiahnutý limit iterácií.');
}

/** Spustí všetky štyri metódy. Možnosti: tol, alpha, simplexSide, lineTol, maxIterations. */
export function runAll(func = functions.custom, overrides = {}) {
  const options = { ...DEFAULTS, ...overrides };
  return {
    'Gradientová': gradientDescent(func, options),
    'Newtonova': newton(func, options),
    'Nelder–Mead': nelderMead(func, options),
    'Powellova': powell(func, options),
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const results = runAll(functions.custom);
  console.log(`Funkcia: f(x,y) = (x² − 1)² + (y² − 1)²; štart: (${functions.custom.start.join(', ')})`);
  console.table(Object.entries(results).map(([method, r]) => ({
    metoda: method,
    stav: r.state,
    iteracie: r.iterations,
    vyhodnotenia_f: r.evaluations,
    x: Number(r.point[0].toFixed(8)),
    y: Number(r.point[1].toFixed(8)),
    f: Number(functions.custom.f(r.point).toExponential(4)),
  })));
}
