/* Vypoctove jadro: parser, derivacie, polynomy, 4 metody.
   Algoritmy su presne podla Python skriptov v zapocet_kody (gradient.py, newton.py,
   powell.py, nelder_mead.py), aby vysledky sedeli so seedom. Ziadne externe kniznice. */
(function (root) {
  'use strict';

  // ======================================================================
  //  1. TOKENIZER + PARSER  (x^2, x², 2xy, √x, |x|, e^x, ln, 0,5 ...)
  // ======================================================================
  function ParseError(message, pos) { this.message = message; this.pos = pos; }

  const SUP = { '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁻': '-' };
  const NAMES = ['sqrt', 'cbrt', 'exp', 'sin', 'cos', 'tan', 'abs', 'ln', 'log', 'pi', 'e', 'x', 'y'];
  const FUNCS = new Set(['sqrt', 'cbrt', 'exp', 'sin', 'cos', 'tan', 'abs', 'ln', 'log']);

  function tokenize(s) {
    const t = [];
    let i = 0;
    while (i < s.length) {
      const ch = s[i];
      if (/\s/.test(ch)) { i++; continue; }
      if (SUP[ch] !== undefined) {
        let j = i, txt = '';
        while (j < s.length && SUP[s[j]] !== undefined) { txt += SUP[s[j]]; j++; }
        if (!/^-?\d+$/.test(txt)) throw new ParseError('Nesprávny exponent', i);
        t.push({ k: 'op', v: '^', pos: i }, { k: '(', pos: i });
        if (txt[0] === '-') t.push({ k: 'op', v: '-', pos: i });
        const d = txt.replace('-', '');
        t.push({ k: 'num', v: parseInt(d, 10), txt: d, pos: i }, { k: ')', pos: i });
        i = j; continue;
      }
      if (/[0-9.,]/.test(ch)) {
        let j = i;
        while (j < s.length && /[0-9.,]/.test(s[j])) j++;
        const raw = s.slice(i, j), norm = raw.replace(/,/g, '.');
        if ((norm.match(/\./g) || []).length > 1 || norm === '.')
          throw new ParseError('Nesprávne číslo „' + raw + '“', i);
        t.push({ k: 'num', v: parseFloat(norm), txt: norm, pos: i });
        i = j; continue;
      }
      if (/[a-zA-Z]/.test(ch)) {
        let j = i;
        while (j < s.length && /[a-zA-Z]/.test(s[j])) j++;
        const word = s.slice(i, j).toLowerCase();
        let p = 0;
        while (p < word.length) {
          const name = NAMES.find(n => word.startsWith(n, p));
          if (!name) throw new ParseError('Neznáme písmeno „' + word[p] + '“. Funkcia môže obsahovať len x a y.', i + p);
          t.push({ k: FUNCS.has(name) ? 'fn' : 'id', v: name, pos: i + p });
          p += name.length;
        }
        i = j; continue;
      }
      if ('+-−–'.includes(ch)) { t.push({ k: 'op', v: ch === '+' ? '+' : '-', pos: i }); i++; continue; }
      if ('*·×⋅∙'.includes(ch)) { t.push({ k: 'op', v: '*', pos: i }); i++; continue; }
      if ('/÷:'.includes(ch)) { t.push({ k: 'op', v: '/', pos: i }); i++; continue; }
      if (ch === '^') { t.push({ k: 'op', v: '^', pos: i }); i++; continue; }
      if ('([{'.includes(ch)) { t.push({ k: '(', pos: i }); i++; continue; }
      if (')]}'.includes(ch)) { t.push({ k: ')', pos: i }); i++; continue; }
      if (ch === '|') { t.push({ k: '|', pos: i }); i++; continue; }
      if (ch === '√') { t.push({ k: 'fn', v: 'sqrt', pos: i }); i++; continue; }
      if (ch === '∛') { t.push({ k: 'fn', v: 'cbrt', pos: i }); i++; continue; }
      if (ch === 'π') { t.push({ k: 'id', v: 'pi', pos: i }); i++; continue; }
      throw new ParseError('Neznámy znak „' + ch + '“', i);
    }
    return t;
  }

  function parse(src) {
    const toks = tokenize(src);
    if (!toks.length) throw new ParseError('Zadaj funkciu', 0);
    let i = 0, absDepth = 0;
    const peek = () => toks[i];
    const isOp = (tk, v) => tk && tk.k === 'op' && tk.v === v;
    const startsFactor = tk => tk && (tk.k === 'num' || tk.k === 'id' || tk.k === 'fn' || tk.k === '(' || (tk.k === '|' && absDepth === 0));
    const endPos = () => (toks[i] ? toks[i].pos : src.length);

    function expr() {
      let a = term();
      while (isOp(peek(), '+') || isOp(peek(), '-')) {
        const o = toks[i++].v;
        a = { t: o, a, b: term() };
      }
      return a;
    }
    function term() {
      let a = unary();
      for (;;) {
        const tk = peek();
        if (isOp(tk, '*') || isOp(tk, '/')) { i++; a = { t: tk.v, a, b: unary() }; }
        else if (startsFactor(tk)) { a = { t: '*', a, b: power() }; }
        else break;
      }
      return a;
    }
    function unary() {
      const tk = peek();
      if (isOp(tk, '-')) { i++; return { t: 'neg', a: unary() }; }
      if (isOp(tk, '+')) { i++; return unary(); }
      return power();
    }
    function power() {
      const base = primary();
      if (isOp(peek(), '^')) { i++; return { t: '^', a: base, b: unary() }; }
      return base;
    }
    function primary() {
      const tk = toks[i++];
      if (!tk) throw new ParseError('Výraz je neúplný, na konci niečo chýba', src.length);
      if (tk.k === 'num') return { t: 'num', v: tk.v, txt: tk.txt };
      if (tk.k === 'id') {
        if (tk.v === 'x' || tk.v === 'y') return { t: 'var', n: tk.v };
        if (tk.v === 'e') return { t: 'const', n: 'e', v: Math.E };
        return { t: 'const', n: 'π', v: Math.PI };
      }
      if (tk.k === 'fn') {
        let arg;
        if (peek() && peek().k === '(') {
          i++; arg = expr();
          if (!peek() || peek().k !== ')') throw new ParseError('Chýba zatváracia zátvorka )', endPos());
          i++;
        } else {
          if (!peek() || !(startsFactor(peek()) || peek().k === '|')) throw new ParseError('Za „' + tk.v + '“ chýba, z čoho sa počíta', tk.pos);
          arg = power();
        }
        return { t: 'fn', n: tk.v, a: arg };
      }
      if (tk.k === '(') {
        const e = expr();
        if (!peek() || peek().k !== ')') throw new ParseError('Chýba zatváracia zátvorka )', endPos());
        i++;
        return e;
      }
      if (tk.k === '|') {
        absDepth++;
        const e = expr();
        if (!peek() || peek().k !== '|') throw new ParseError('Chýba zatváracia čiara | pri absolútnej hodnote', endPos());
        i++; absDepth--;
        return { t: 'fn', n: 'abs', a: e };
      }
      if (tk.k === ')') throw new ParseError('Zátvorka ) navyše alebo chýba niečo pred ňou', tk.pos);
      throw new ParseError('Tu chýba číslo alebo premenná', tk.pos);
    }
    const node = expr();
    if (i < toks.length) {
      const tk = toks[i];
      throw new ParseError(tk.k === ')' ? 'Zátvorka ) navyše' : 'Nečakaný znak', tk.pos);
    }
    return node;
  }

  // ======================================================================
  //  2. VYHODNOTENIE  (premenne x, y, g = gama)
  // ======================================================================
  function fnValue(n, v) {
    switch (n) {
      case 'sqrt': return v < 0 ? NaN : Math.sqrt(v);
      case 'cbrt': return Math.cbrt(v);
      case 'exp': return Math.exp(v);
      case 'ln': return v <= 0 ? NaN : Math.log(v);
      case 'log': return v <= 0 ? NaN : Math.log10(v);
      case 'sin': return Math.sin(v);
      case 'cos': return Math.cos(v);
      case 'tan': return Math.tan(v);
      case 'abs': return Math.abs(v);
      case 'sign': return v > 0 ? 1 : v < 0 ? -1 : 0;
    }
    return NaN;
  }

  function compile(n) {
    switch (n.t) {
      case 'num': case 'const': { const v = n.v; return () => v; }
      case 'var': return n.n === 'x' ? (x) => x : n.n === 'y' ? (x, y) => y : (x, y, g) => g;
      case 'neg': { const a = compile(n.a); return (x, y, g) => -a(x, y, g); }
      case '+': { const a = compile(n.a), b = compile(n.b); return (x, y, g) => a(x, y, g) + b(x, y, g); }
      case '-': { const a = compile(n.a), b = compile(n.b); return (x, y, g) => a(x, y, g) - b(x, y, g); }
      case '*': { const a = compile(n.a), b = compile(n.b); return (x, y, g) => a(x, y, g) * b(x, y, g); }
      case '/': { const a = compile(n.a), b = compile(n.b); return (x, y, g) => { const d = b(x, y, g); return d === 0 ? NaN : a(x, y, g) / d; }; }
      case '^': {
        const a = compile(n.a), b = compile(n.b);
        return (x, y, g) => {
          const base = a(x, y, g), ex = b(x, y, g);
          if (base === 0 && ex < 0) return NaN;
          return Math.pow(base, ex);
        };
      }
      case 'fn': { const a = compile(n.a), name = n.n; return (x, y, g) => fnValue(name, a(x, y, g)); }
    }
    throw new Error('compile: ' + n.t);
  }

  function hasVar(n, v) {
    switch (n.t) {
      case 'var': return n.n === v;
      case 'num': case 'const': return false;
      case 'neg': case 'fn': return hasVar(n.a, v);
      default: return hasVar(n.a, v) || hasVar(n.b, v);
    }
  }
  const isConstNode = n => !hasVar(n, 'x') && !hasVar(n, 'y') && !hasVar(n, 'g');

  // ======================================================================
  //  3. POLYNOMY v x, y  (mapa "i,j" -> koeficient)
  // ======================================================================
  function pAdd(p, q, s) {
    const r = Object.assign({}, p);
    for (const k in q) r[k] = (r[k] || 0) + s * q[k];
    return r;
  }
  function pMul(p, q) {
    const r = {};
    for (const a in p) for (const b in q) {
      const [i1, j1] = a.split(',').map(Number), [i2, j2] = b.split(',').map(Number);
      const k = (i1 + i2) + ',' + (j1 + j2);
      r[k] = (r[k] || 0) + p[a] * q[b];
    }
    return r;
  }
  function pScale(p, c) { const r = {}; for (const k in p) r[k] = p[k] * c; return r; }
  const pConst = c => ({ '0,0': c });
  function pIsConst(p) { for (const k in p) if (k !== '0,0' && p[k] !== 0) return false; return true; }
  const pConstVal = p => p['0,0'] || 0;

  function toPoly(n) {
    if (isConstNode(n)) {
      const v = compile(n)(0, 0, 0);
      return isFinite(v) ? pConst(v) : null;
    }
    switch (n.t) {
      case 'var': return n.n === 'x' ? { '1,0': 1 } : n.n === 'y' ? { '0,1': 1 } : null;
      case 'neg': { const a = toPoly(n.a); return a && pScale(a, -1); }
      case '+': case '-': {
        const a = toPoly(n.a), b = toPoly(n.b);
        return a && b && pAdd(a, b, n.t === '+' ? 1 : -1);
      }
      case '*': { const a = toPoly(n.a), b = toPoly(n.b); return a && b && pMul(a, b); }
      case '/': {
        const a = toPoly(n.a), b = toPoly(n.b);
        if (!a || !b || !pIsConst(b) || pConstVal(b) === 0) return null;
        return pScale(a, 1 / pConstVal(b));
      }
      case '^': {
        const a = toPoly(n.a);
        if (!a || !isConstNode(n.b)) return null;
        const e = compile(n.b)(0, 0, 0);
        if (!Number.isInteger(e) || e < 0 || e > 40) return null;
        let r = pConst(1);
        for (let k = 0; k < e; k++) r = pMul(r, a);
        return r;
      }
    }
    return null;
  }
  function pClean(p) {
    const r = {};
    for (const k in p) if (p[k] !== 0) r[k] = p[k];
    return r;
  }
  function pDeriv(p, v) {
    const r = {};
    for (const k in p) {
      const [i, j] = k.split(',').map(Number);
      if (v === 'x' && i > 0) r[(i - 1) + ',' + j] = (r[(i - 1) + ',' + j] || 0) + p[k] * i;
      if (v === 'y' && j > 0) r[i + ',' + (j - 1)] = (r[i + ',' + (j - 1)] || 0) + p[k] * j;
    }
    return pClean(r);
  }
  function pEval(p, x, y) {
    let s = 0;
    for (const k in p) { const [i, j] = k.split(',').map(Number); s += p[k] * Math.pow(x, i) * Math.pow(y, j); }
    return s;
  }
  // dosadenie priamky x = a + b*g, y = c + d*g  ->  koeficienty polynomu v g (od g^0)
  function uMul(p, q) {
    const r = new Array(p.length + q.length - 1).fill(0);
    for (let i = 0; i < p.length; i++) for (let j = 0; j < q.length; j++) r[i + j] += p[i] * q[j];
    return r;
  }
  function pSubstLine(p, a, b, c, d) {
    let res = [0];
    const pw = (base, e) => { let r = [1]; for (let k = 0; k < e; k++) r = uMul(r, base); return r; };
    for (const k in p) {
      const [i, j] = k.split(',').map(Number);
      const t = uMul(pw([a, b], i), pw([c, d], j)).map(v => v * p[k]);
      if (t.length > res.length) res = res.concat(new Array(t.length - res.length).fill(0));
      for (let m = 0; m < t.length; m++) res[m] += t[m];
    }
    return res;
  }

  // ---- polynom jednej premennej (koeficienty od g^0) ----
  function uTrim(c) { const r = c.slice(); while (r.length > 1 && r[r.length - 1] === 0) r.pop(); return r; }
  const uDeg = c => uTrim(c).length - 1;
  function uEval(c, g) { let s = 0; for (let k = c.length - 1; k >= 0; k--) s = s * g + c[k]; return s; }
  function uDeriv(c) { const r = []; for (let k = 1; k < c.length; k++) r.push(c[k] * k); return r.length ? r : [0]; }
  // ako ocisti_polynom v Pythone: koeficienty ~1e-17 su len zaokruhlovacie smeti
  function uChop(c) {
    let mx = 0;
    for (let k = 1; k < c.length; k++) mx = Math.max(mx, Math.abs(c[k]));
    const lim = mx ? 1e-12 * mx : 0;
    return uTrim(c.map((v, k) => (k === 0 || Math.abs(v) > lim ? v : 0)));
  }

  // komplexne korene (Durand-Kerner + Newton), ako sympy nroots
  function uRoots(cIn) {
    const c = uTrim(cIn), n = c.length - 1;
    if (n < 1) return [];
    const a = c.map(v => v / c[n]);
    if (n === 1) return [{ re: -a[0], im: 0 }];
    let R = 0;
    for (let k = 0; k < n; k++) R = Math.max(R, Math.pow(Math.abs(a[k]), 1 / (n - k)));
    R = Math.max(R, 1e-3);
    const zr = [], zi = [];
    for (let k = 0; k < n; k++) { const th = 2 * Math.PI * k / n + 0.4; zr.push(R * Math.cos(th)); zi.push(R * Math.sin(th)); }
    const pv = (re, im) => {
      let sr = 1, si = 0;               // monicky polynom, Horner
      for (let k = n - 1; k >= 0; k--) { const tr = sr * re - si * im + a[k], ti = sr * im + si * re; sr = tr; si = ti; }
      return [sr, si];
    };
    for (let it = 0; it < 5000; it++) {
      let mx = 0;
      for (let k = 0; k < n; k++) {
        let [nr, ni] = pv(zr[k], zi[k]);
        let dr = 1, di = 0;
        for (let j = 0; j < n; j++) if (j !== k) {
          const er = zr[k] - zr[j], ei = zi[k] - zi[j];
          const tr = dr * er - di * ei, ti = dr * ei + di * er; dr = tr; di = ti;
        }
        const den = dr * dr + di * di;
        if (den === 0) { zr[k] += 1e-8 * R; continue; }
        const qr = (nr * dr + ni * di) / den, qi = (ni * dr - nr * di) / den;
        zr[k] -= qr; zi[k] -= qi;
        mx = Math.max(mx, Math.hypot(qr, qi) / (1 + Math.hypot(zr[k], zi[k])));
      }
      if (mx < 1e-15) break;
    }
    // dopresnenie Newtonom (komplexne), pre jednoduche korene az na strojovu presnost
    const da = [];
    for (let k = 1; k <= n; k++) da.push(k === n ? n : a[k] * k);
    const dv = (re, im) => {
      let sr = 0, si = 0;
      for (let k = da.length - 1; k >= 0; k--) { const tr = sr * re - si * im + da[k], ti = sr * im + si * re; sr = tr; si = ti; }
      return [sr, si];
    };
    for (let k = 0; k < n; k++) {
      for (let it = 0; it < 8; it++) {
        const [nr, ni] = pv(zr[k], zi[k]), [dr, di] = dv(zr[k], zi[k]);
        const den = dr * dr + di * di;
        if (!den) break;
        const qr = (nr * dr + ni * di) / den, qi = (ni * dr - nr * di) / den;
        const before = Math.hypot(nr, ni);
        const [mr, mi] = pv(zr[k] - qr, zi[k] - qi);
        if (Math.hypot(mr, mi) >= before) break;
        zr[k] -= qr; zi[k] -= qi;
      }
    }
    return zr.map((re, k) => ({ re, im: zi[k] }));
  }

  // kriticke body phi: korene phi' (viacnasobne spojene), typ min/max/inflex
  function uCritical(phi) {
    const dphi = uDeriv(phi);
    if (uDeg(dphi) < 1) return [];
    const real = uRoots(dphi).filter(r => Math.abs(r.im) < 1e-4 * (1 + Math.abs(r.re))).map(r => r.re).sort((p, q) => p - q);
    const groups = [];
    for (const r of real) {
      const g = groups[groups.length - 1];
      if (g && Math.abs(r - g[g.length - 1]) < 1e-4 * (1 + Math.abs(r))) g.push(r); else groups.push([r]);
    }
    return groups.map(g => {
      const r = g.reduce((s, v) => s + v, 0) / g.length;
      const h = 1e-3 * (1 + Math.abs(r));
      const v = uEval(phi, r), vl = uEval(phi, r - h), vr = uEval(phi, r + h);
      const typ = (vl >= v && vr >= v) ? 'min' : (vl <= v && vr <= v) ? 'max' : 'inflex';
      return { g: r, phi: v, typ, nasobnost: g.length };
    });
  }
  const round12 = v => Math.round(v * 1e12) / 1e12;

  // ======================================================================
  //  4. SYMBOLICKE DERIVACIE + ZJEDNODUSENIE
  // ======================================================================
  const N = v => ({ t: 'num', v });
  const isN = (n, v) => n.t === 'num' && (v === undefined || n.v === v);

  function deriv(n, v) {
    switch (n.t) {
      case 'num': case 'const': return N(0);
      case 'var': return N(n.n === v ? 1 : 0);
      case 'neg': return { t: 'neg', a: deriv(n.a, v) };
      case '+': case '-': return { t: n.t, a: deriv(n.a, v), b: deriv(n.b, v) };
      case '*': return { t: '+', a: { t: '*', a: deriv(n.a, v), b: n.b }, b: { t: '*', a: n.a, b: deriv(n.b, v) } };
      case '/': return { t: '/', a: { t: '-', a: { t: '*', a: deriv(n.a, v), b: n.b }, b: { t: '*', a: n.a, b: deriv(n.b, v) } }, b: { t: '^', a: n.b, b: N(2) } };
      case '^': {
        const ab = hasVar(n.a, v), eb = hasVar(n.b, v);
        if (!eb) return { t: '*', a: { t: '*', a: n.b, b: { t: '^', a: n.a, b: { t: '-', a: n.b, b: N(1) } } }, b: deriv(n.a, v) };
        if (!ab && n.a.t === 'const' && n.a.n === 'e') return { t: '*', a: n, b: deriv(n.b, v) };
        if (!ab) return { t: '*', a: { t: '*', a: n, b: { t: 'fn', n: 'ln', a: n.a } }, b: deriv(n.b, v) };
        return { t: '*', a: n, b: { t: '+', a: { t: '*', a: deriv(n.b, v), b: { t: 'fn', n: 'ln', a: n.a } }, b: { t: '/', a: { t: '*', a: n.b, b: deriv(n.a, v) }, b: n.a } } };
      }
      case 'fn': {
        const da = deriv(n.a, v), a = n.a;
        let outer;
        switch (n.n) {
          case 'sqrt': return { t: '/', a: da, b: { t: '*', a: N(2), b: n } };
          case 'cbrt': return { t: '/', a: da, b: { t: '*', a: N(3), b: { t: '^', a: n, b: N(2) } } };
          case 'exp': outer = n; break;
          case 'ln': return { t: '/', a: da, b: a };
          case 'log': return { t: '/', a: da, b: { t: '*', a, b: { t: 'fn', n: 'ln', a: N(10) } } };
          case 'sin': outer = { t: 'fn', n: 'cos', a }; break;
          case 'cos': outer = { t: 'neg', a: { t: 'fn', n: 'sin', a } }; break;
          case 'tan': return { t: '/', a: da, b: { t: '^', a: { t: 'fn', n: 'cos', a }, b: N(2) } };
          case 'abs': outer = { t: 'fn', n: 'sign', a }; break;
          case 'sign': return N(0);
        }
        return { t: '*', a: outer, b: da };
      }
    }
    throw new Error('deriv ' + n.t);
  }

  function simp(n) {
    switch (n.t) {
      case 'num': case 'var': case 'const': return n;
      case 'neg': {
        const a = simp(n.a);
        if (a.t === 'num') return N(-a.v);
        if (a.t === 'neg') return a.a;
        return { t: 'neg', a };
      }
      case '+': {
        const a = simp(n.a), b = simp(n.b);
        if (isN(a, 0)) return b;
        if (isN(b, 0)) return a;
        if (a.t === 'num' && b.t === 'num') return N(a.v + b.v);
        if (b.t === 'neg') return { t: '-', a, b: b.a };
        if (b.t === 'num' && b.v < 0) return { t: '-', a, b: N(-b.v) };
        if (a.t === 'neg') return simp({ t: '-', a: b, b: a.a });
        return { t: '+', a, b };
      }
      case '-': {
        const a = simp(n.a), b = simp(n.b);
        if (isN(b, 0)) return a;
        if (isN(a, 0)) return simp({ t: 'neg', a: b });
        if (a.t === 'num' && b.t === 'num') return N(a.v - b.v);
        if (b.t === 'neg') return { t: '+', a, b: b.a };
        if (b.t === 'num' && b.v < 0) return { t: '+', a, b: N(-b.v) };
        return { t: '-', a, b };
      }
      case '*': {
        let a = simp(n.a), b = simp(n.b);
        if (isN(a, 0) || isN(b, 0)) return N(0);
        if (isN(a, 1)) return b;
        if (isN(b, 1)) return a;
        if (a.t === 'num' && b.t === 'num') return N(a.v * b.v);
        if (b.t === 'num') { const t = a; a = b; b = t; }
        if (a.t === 'neg') return simp({ t: 'neg', a: { t: '*', a: a.a, b } });
        if (b.t === 'neg') return simp({ t: 'neg', a: { t: '*', a, b: b.a } });
        if (a.t === 'num' && b.t === '*' && b.a.t === 'num') return simp({ t: '*', a: N(a.v * b.a.v), b: b.b });
        if (a.t === 'num' && a.v < 0) return { t: 'neg', a: simp({ t: '*', a: N(-a.v), b }) };
        if (a.t === 'num' && b.t === '/' && b.a.t === 'num') return simp({ t: '/', a: N(a.v * b.a.v), b: b.b });
        return { t: '*', a, b };
      }
      case '/': {
        const a = simp(n.a), b = simp(n.b);
        if (isN(b, 1)) return a;
        if (isN(a, 0)) return N(0);
        if (a.t === 'num' && b.t === 'num' && b.v !== 0) return N(a.v / b.v);
        if (a.t === 'neg') return simp({ t: 'neg', a: { t: '/', a: a.a, b } });
        // (k*A)/(k*B) -> A/B
        const ka = a.t === '*' && a.a.t === 'num' ? a.a.v : a.t === 'num' ? a.v : null;
        const kb = b.t === '*' && b.a.t === 'num' ? b.a.v : b.t === 'num' ? b.v : null;
        if (ka !== null && kb !== null && ka !== 0 && kb !== 0 && ka === kb) {
          const A = a.t === '*' ? a.b : N(1), B = b.t === '*' ? b.b : N(1);
          return simp({ t: '/', a: A, b: B });
        }
        return { t: '/', a, b };
      }
      case '^': {
        const a = simp(n.a), b = simp(n.b);
        if (isN(b, 1)) return a;
        if (isN(b, 0)) return N(1);
        if (a.t === 'num' && b.t === 'num') { const v = Math.pow(a.v, b.v); if (isFinite(v)) return N(v); }
        return { t: '^', a, b };
      }
      case 'fn': {
        const a = simp(n.a);
        if (n.n === 'ln' && a.t === 'const' && a.n === 'e') return N(1);
        if (a.t === 'num') { const v = fnValue(n.n, a.v); if (isFinite(v) && Number.isInteger(v)) return N(v); }
        return { t: 'fn', n: n.n, a };
      }
    }
    throw new Error('simp ' + n.t);
  }

  // polynom -> pekny strom (x pred y, vyssie mocniny skor)
  function polyToNode(p) {
    const keys = Object.keys(p).filter(k => p[k] !== 0 && Math.abs(p[k]) > 1e-14 * maxAbs(p));
    if (!keys.length) return N(0);
    keys.sort((k1, k2) => {
      const [i1, j1] = k1.split(',').map(Number), [i2, j2] = k2.split(',').map(Number);
      return (i2 + j2) - (i1 + j1) || i2 - i1;
    });
    let node = null;
    for (const k of keys) {
      const [i, j] = k.split(',').map(Number);
      const c = p[k];
      let mono = null;
      const mul = (m, f) => (m ? { t: '*', a: m, b: f } : f);
      if (i) mono = mul(mono, i === 1 ? { t: 'var', n: 'x' } : { t: '^', a: { t: 'var', n: 'x' }, b: N(i) });
      if (j) mono = mul(mono, j === 1 ? { t: 'var', n: 'y' } : { t: '^', a: { t: 'var', n: 'y' }, b: N(j) });
      const ac = Math.abs(c);
      const term = !mono ? N(ac) : ac === 1 ? mono : { t: '*', a: N(ac), b: mono };
      if (!node) node = c < 0 ? { t: 'neg', a: term } : term;
      else node = { t: c < 0 ? '-' : '+', a: node, b: term };
    }
    return node;
  }
  function maxAbs(p) { let m = 0; for (const k in p) m = Math.max(m, Math.abs(p[k])); return m; }

  // pekny tvar: polynom kanonicky, inak zjednodusene a polynomialne casti kanonicky
  function pretty(n) {
    const s = simp(n);
    if (s.t === 'num' || s.t === 'var' || s.t === 'const') return s;
    const p = toPoly(s);
    if (p) return polyToNode(pClean(p));
    const rec = m => {
      if (m.t === 'num' || m.t === 'var' || m.t === 'const') return m;
      const q = (m.t === '+' || m.t === '-' || m.t === '*') ? toPoly(m) : null;
      if (q && Object.keys(pClean(q)).length > 1) return polyToNode(pClean(q));
      if (m.t === 'neg' || m.t === 'fn') return Object.assign({}, m, { a: rec(m.a) });
      return Object.assign({}, m, { a: rec(m.a), b: rec(m.b) });
    };
    return simp(rec(s));
  }

  // ======================================================================
  //  5. PRIPRAVA FUNKCIE
  // ======================================================================
  function prepare(src) {
    const node = parse(src);
    const poly = toPoly(node);
    const fx = simp(deriv(node, 'x')), fy = simp(deriv(node, 'y'));
    const fxx = simp(deriv(fx, 'x')), fxy = simp(deriv(fx, 'y')), fyy = simp(deriv(fy, 'y'));
    const F = { src, node, poly: poly ? pClean(poly) : null };
    F.nodes = { fx, fy, fxx, fxy, fyy };
    F.show = { f: node, fx: pretty(fx), fy: pretty(fy), fxx: pretty(fxx), fxy: pretty(fxy), fyy: pretty(fyy) };
    if (F.poly) {
      const px = pDeriv(F.poly, 'x'), py = pDeriv(F.poly, 'y');
      const pxx = pDeriv(px, 'x'), pxy = pDeriv(px, 'y'), pyy = pDeriv(py, 'y');
      F.show = { f: node, fx: polyToNode(px), fy: polyToNode(py), fxx: polyToNode(pxx), fxy: polyToNode(pxy), fyy: polyToNode(pyy) };
    }
    const cf = compile(node), cx = compile(fx), cy = compile(fy), cxx = compile(fxx), cxy = compile(fxy), cyy = compile(fyy);
    F.f = (x, y) => cf(x, y, 0);
    F.gx = (x, y) => cx(x, y, 0);
    F.gy = (x, y) => cy(x, y, 0);
    F.hxx = (x, y) => cxx(x, y, 0);
    F.hxy = (x, y) => cxy(x, y, 0);
    F.hyy = (x, y) => cyy(x, y, 0);
    return F;
  }

  function MethodError(msg) { this.message = msg; }
  const bodTxt = P => '(' + P[0].toFixed(4) + '; ' + P[1].toFixed(4) + ')';
  function val(v, P, co) {
    if (!isFinite(v)) throw new MethodError('V bode ' + bodTxt(P) + ' ' + (co || 'funkcia') + ' nie je definovaná (delenie nulou alebo odmocnina zo záporného čísla). Skús iný štart.');
    return v;
  }

  // ======================================================================
  //  6. HLADANIE PO PRIAMKE  (ako najdi_gamu / po_priamke v Pythone)
  // ======================================================================
  function zlatyRez(phi, a, b, presnost) {
    presnost = presnost || 1e-12;
    const k = (Math.sqrt(5) - 1) / 2;
    while (b - a > presnost * Math.max(1, Math.abs(a) + Math.abs(b))) {
      const t1 = b - k * (b - a), t2 = a + k * (b - a);
      if (phi(t1) < phi(t2)) b = t2; else a = t1;
    }
    return (a + b) / 2;
  }
  function presneMinimum(phi, dphi, a, b) {
    const g = zlatyRez(phi, a, b);
    const h = 1e-6 * (1 + Math.abs(g));
    let lo = g - h, hi = g + h;
    if (dphi(lo) < 0 && 0 < dphi(hi)) {
      for (let it = 0; it < 200; it++) {
        const s = (lo + hi) / 2;
        if (dphi(s) < 0) lo = s; else hi = s;
        if (hi - lo < 1e-15 * (1 + Math.abs(s))) break;
      }
      return (lo + hi) / 2;
    }
    return g;
  }

  // kladne = true: len gama > 0 (gradient); false: aj zaporne (Powell)
  function lineSearch(F, P, u, kladne) {
    const res = { P, u };
    if (F.poly) {
      const raw = pSubstLine(F.poly, P[0], u[0], P[1], u[1]);
      const phi = uChop(raw);
      res.typ = 'poly';
      res.phi = phi;
      res.dphi = uDeriv(phi);
      if (!kladne && uDeg(phi) < 1) { res.konst = true; res.gama = 0; return res; }
      res.krit = uCritical(phi);
      let kand = res.krit.filter(c => c.typ === 'min' && (!kladne || c.g > 0));
      if (!kand.length) {
        const err = new MethodError('φ(γ) nemá minimum: funkcia ' + (kladne ? 'v smere S' : 'na tejto priamke') + ' klesá do −∞ (funkcia nemá minimum).');
        err.res = res;
        throw err;
      }
      kand.sort((p, q) => (round12(p.phi) - round12(q.phi)) || (kladne ? p.g - q.g : (Math.abs(p.g) - Math.abs(q.g)) || (q.g - p.g)));
      res.vybrane = kand[0];
      res.gama = kand[0].g;
      return res;
    }
    // nie je polynom: zlaty rez + bisekcia phi'(gama) = 0
    res.typ = 'num';
    const phi = g => { const v = F.f(P[0] + g * u[0], P[1] + g * u[1]); return isFinite(v) ? v : Infinity; };
    const dphi = g => {
      const x = P[0] + g * u[0], y = P[1] + g * u[1];
      const v = F.gx(x, y) * u[0] + F.gy(x, y) * u[1];
      return isFinite(v) ? v : NaN;
    };
    let h = 1e-3;
    if (!kladne && phi(-h) < phi(h)) h = -h;
    while (phi(2 * h) < phi(h)) {
      h *= 2;
      if (Math.abs(h) > 1e8) {
        const err = new MethodError('φ(γ) stále klesá: funkcia ' + (kladne ? 'v smere S' : 'na priamke') + ' nemá minimum.');
        res.phiNode = substLineNode(F.node, P, u);
        err.res = res;
        throw err;
      }
    }
    const a = kladne ? 0 : Math.min(-Math.abs(h), 2 * h), b = kladne ? 2 * h : Math.max(Math.abs(h), 2 * h);
    res.interval = [a, b];
    res.gama = presneMinimum(phi, dphi, a, b);
    res.phiNode = substLineNode(F.node, P, u);
    return res;
  }
  // f(P + gama*u) ako strom (na zobrazenie)
  function substLineNode(n, P, u) {
    const lin = (p, d) => (d === 0 ? N(p) : p === 0 ? (d === 1 ? { t: 'var', n: 'g' } : { t: '*', a: N(d), b: { t: 'var', n: 'g' } })
      : { t: d < 0 ? '-' : '+', a: N(p), b: Math.abs(d) === 1 ? { t: 'var', n: 'g' } : { t: '*', a: N(Math.abs(d)), b: { t: 'var', n: 'g' } } });
    const go = m => {
      if (m.t === 'var') return m.n === 'x' ? lin(P[0], u[0]) : lin(P[1], u[1]);
      if (m.t === 'num' || m.t === 'const') return m;
      if (m.t === 'neg' || m.t === 'fn') return Object.assign({}, m, { a: go(m.a) });
      return Object.assign({}, m, { a: go(m.a), b: go(m.b) });
    };
    return go(n);
  }

  // ======================================================================
  //  7. METODY
  // ======================================================================
  function runGradient(F, o) {
    const eps = o.eps, maxIt = o.maxIt;
    let P = [Number(o.start[0]), Number(o.start[1])];
    const out = { metoda: 'gradient', start: P.slice(), fStart: val(F.f(P[0], P[1]), P), iter: [], body: [P.slice()] };
    try {
      let k;
      for (k = 0; k < maxIt; k++) {
        const gx = val(F.gx(P[0], P[1]), P, 'derivácia'), gy = val(F.gy(P[0], P[1]), P, 'derivácia');
        const dlzka = Math.sqrt(gx ** 2 + gy ** 2);
        if (dlzka < eps) { out.stop = { typ: 'grad', hodnota: dlzka, k }; break; }
        const S = [-gx / dlzka, -gy / dlzka];
        let ls;
        try { ls = lineSearch(F, P, S, true); }
        catch (e) {
          if (e instanceof MethodError) out.iter.push({ k: k + 1, P: P.slice(), fP: F.f(P[0], P[1]), grad: [gx, gy], norm: dlzka, S, ls: e.res, chyba: e.message });
          throw e;
        }
        const g = ls.gama;
        const Pn = [P[0] + g * S[0], P[1] + g * S[1]];
        const it = { k: k + 1, P: P.slice(), fP: F.f(P[0], P[1]), grad: [gx, gy], norm: dlzka, S, ls, gama: g, Pn, fPn: val(F.f(Pn[0], Pn[1]), Pn) };
        out.iter.push(it);
        out.body.push(Pn.slice());
        P = Pn;
      }
      if (!out.stop) out.stop = { typ: 'maxit', k: maxIt };
      out.iteracie = out.stop.k;
      out.bod = P; out.f = F.f(P[0], P[1]);
      if (out.stop.typ === 'maxit') {
        const gx = F.gx(P[0], P[1]), gy = F.gy(P[0], P[1]);
        out.stop.hodnota = Math.sqrt(gx * gx + gy * gy);
      }
    } catch (e) { if (e instanceof MethodError) out.chyba = e.message; else throw e; }
    return out;
  }

  function hessType(F, P) {
    const a = F.hxx(P[0], P[1]), b = F.hxy(P[0], P[1]), d = F.hyy(P[0], P[1]);
    const det = a * d - b * b;
    if (det > 0 && a > 0) return { typ: 'MINIMUM', det, a };
    if (det > 0 && a < 0) return { typ: 'MAXIMUM', det, a };
    if (det < 0) return { typ: 'SEDLO', det, a };
    return { typ: 'NEDÁ SA ROZHODNÚŤ', det, a };
  }

  function runNewton(F, o) {
    const eps = o.eps, maxIt = o.maxIt;
    let P = [Number(o.start[0]), Number(o.start[1])];
    const out = { metoda: 'newton', start: P.slice(), fStart: val(F.f(P[0], P[1]), P), iter: [], body: [P.slice()] };
    try {
      for (let k = 0; k < maxIt; k++) {
        const gx = val(F.gx(P[0], P[1]), P, 'derivácia'), gy = val(F.gy(P[0], P[1]), P, 'derivácia');
        const dlzka = Math.sqrt(gx ** 2 + gy ** 2);
        if (dlzka < eps) { out.stop = { typ: 'grad', hodnota: dlzka, k }; break; }
        const a = val(F.hxx(P[0], P[1]), P, 'druhá derivácia'), b = val(F.hxy(P[0], P[1]), P, 'druhá derivácia');
        const c = b, d = val(F.hyy(P[0], P[1]), P, 'druhá derivácia');
        const det = a * d - b * c;
        if (Math.abs(det) <= 1e-14 * (a * a + b * b + c * c + d * d)) {
          out.iter.push({ k: k + 1, P: P.slice(), fP: F.f(P[0], P[1]), grad: [gx, gy], norm: dlzka, H: [a, b, c, d], det, singular: true });
          throw new MethodError('det H = 0 v bode ' + bodTxt(P) + ': inverzná matica neexistuje, Newton sa tu nedá použiť.');
        }
        const mb = -b + 0, mc = -c + 0;
        const sx = d * gx + mb * gy, sy = mc * gx + a * gy;
        const krok = [sx / det, sy / det];
        const Pn = [P[0] - krok[0], P[1] - krok[1]];
        const posun = Math.hypot(P[0] - Pn[0], P[1] - Pn[1]);
        out.iter.push({ k: k + 1, P: P.slice(), fP: F.f(P[0], P[1]), grad: [gx, gy], norm: dlzka, H: [a, b, c, d], det, mb, mc, sx, sy, krok, Pn, fPn: val(F.f(Pn[0], Pn[1]), Pn), posun });
        out.body.push(Pn.slice());
        P = Pn;
        if (posun < eps) { out.stop = { typ: 'posun', hodnota: posun, k: k + 1 }; break; }
      }
      if (!out.stop) out.stop = { typ: 'maxit', k: maxIt };
      out.iteracie = out.stop.k;
      out.bod = P; out.f = F.f(P[0], P[1]);
      out.hess = hessType(F, P);
    } catch (e) { if (e instanceof MethodError) out.chyba = e.message; else throw e; }
    return out;
  }

  function runPowell(F, o) {
    const eps = o.eps, maxIt = o.maxIt;
    let P0 = [Number(o.start[0]), Number(o.start[1])];
    let u1 = (o.u1 || [1, 0]).map(Number), u2 = (o.u2 || [0, 1]).map(Number);
    const out = { metoda: 'powell', start: P0.slice(), fStart: val(F.f(P0[0], P0[1]), P0), iter: [], body: [P0.slice()], u0: [u1.slice(), u2.slice()] };
    try {
      if (Math.hypot(...u1) === 0 || Math.hypot(...u2) === 0) throw new MethodError('Smer nesmie byť (0, 0).');
      if (Math.abs(u1[0] * u2[1] - u1[1] * u2[0]) <= 1e-12 * Math.hypot(...u1) * Math.hypot(...u2))
        throw new MethodError('Začiatočné smery u1 a u2 sú rovnobežné (determinant = 0). Metóda by sa hýbala len po jednej priamke.');
      for (let k = 0; k < maxIt; k++) {
        const it = { k: k + 1, P0: P0.slice(), fP0: F.f(P0[0], P0[1]), u1: u1.slice(), u2: u2.slice(), hladania: [] };
        const krok = (P, u, meno, kam) => {
          let ls;
          try { ls = lineSearch(F, P, u, false); }
          catch (e) {
            if (e instanceof MethodError) { it.hladania.push({ meno, z: P.slice(), smer: u.slice(), ls: e.res, kam, chyba: e.message }); it.chyba = e.message; out.iter.push(it); }
            throw e;
          }
          const Q = [P[0] + ls.gama * u[0], P[1] + ls.gama * u[1]];
          it.hladania.push({ meno, z: P.slice(), smer: u.slice(), ls, gama: ls.gama, kam, Q, fQ: val(F.f(Q[0], Q[1]), Q) });
          return Q;
        };
        const P1 = krok(P0, u1, 'u1', 'P1');
        const P2 = krok(P1, u2, 'u2', 'P2');
        const d = [P2[0] - P0[0], P2[1] - P0[1]];
        it.d = d;
        let P3;
        if (Math.hypot(d[0], d[1]) < 1e-14) { P3 = P2; it.dNula = true; }
        else {
          P3 = krok(P2, d, 'd', 'P3');
          if (Math.abs(u2[0] * d[1] - u2[1] * d[0]) <= 1e-12 * Math.hypot(...u2) * Math.hypot(...d)) it.rovnobezne = true;
          else { u1 = u2; u2 = d; }
        }
        it.P1 = P1; it.P2 = P2; it.P3 = P3; it.fP3 = F.f(P3[0], P3[1]);
        it.noveU = [u1.slice(), u2.slice()];
        const posun = Math.hypot(P3[0] - P0[0], P3[1] - P0[1]);
        it.posun = posun;
        out.iter.push(it);
        out.body.push(P3.slice());
        P0 = P3;
        if (posun < eps) { out.stop = { typ: 'posun', hodnota: posun, k: k + 1 }; break; }
      }
      if (!out.stop) out.stop = { typ: 'maxit', k: maxIt };
      out.iteracie = out.stop.k;
      out.bod = P0; out.f = F.f(P0[0], P0[1]);
    } catch (e) { if (e instanceof MethodError) out.chyba = e.message; else throw e; }
    return out;
  }

  function mensie(a, b) { return a < b - 1e-12 * Math.max(1, Math.abs(a), Math.abs(b)); }
  function zorad(body) {
    const r = [];
    for (const p of body) {
      let i = r.length;
      while (i > 0 && mensie(p.f, r[i - 1].f)) i--;
      r.splice(i, 0, p);
    }
    return r;
  }

  function runNM(F, o) {
    const eps = o.eps, maxIt = o.maxIt;
    const al = Number(o.alfa), ga = Number(o.gama), rh = Number(o.rho), si = Number(o.sigma);
    const rozdiel = (P, Q) => [P[0] - Q[0], P[1] - Q[1]];
    const posun = (P, k, s) => [P[0] + k * s[0], P[1] + k * s[1]];
    const fv = P => ({ P, f: val(F.f(P[0], P[1]), P) });
    const out = { metoda: 'nm', iter: [], trojuholniky: [], kontrakcia: o.kontrakcia, koef: { al, ga, rh, si } };
    try {
      let body = o.body.map(p => fv([Number(p[0]), Number(p[1])]));
      out.startBody = body.map(b => ({ P: b.P.slice(), f: b.f }));
      let k;
      for (k = 0; k < maxIt; k++) {
        const pred = body.map(b => ({ P: b.P.slice(), f: b.f }));
        body = zorad(body);
        const [B, G, W] = body;
        out.trojuholniky.push([B.P, G.P, W.P]);
        const d = Math.max(Math.hypot(B.P[0] - G.P[0], B.P[1] - G.P[1]), Math.hypot(B.P[0] - W.P[0], B.P[1] - W.P[1]));
        if (d < eps) { out.stop = { typ: 'd', hodnota: d, k }; break; }
        const it = { k: k + 1, pred, B, G, W, d };
        const M = [(B.P[0] + G.P[0]) / 2, (B.P[1] + G.P[1]) / 2];
        const R = posun(M, al, rozdiel(M, W.P));
        const fR = val(F.f(R[0], R[1]), R);
        Object.assign(it, { M, R, fR });
        if (mensie(fR, B.f)) {
          it.pripad = 1;
          const E = posun(M, ga, rozdiel(R, M));
          const fE = val(F.f(E[0], E[1]), E);
          Object.assign(it, { E, fE });
          if (mensie(fE, fR)) { body[2] = { P: E, f: fE }; it.krok = 'expanzia E'; it.novy = 'E'; }
          else { body[2] = { P: R, f: fR }; it.krok = 'reflexia R (E nepomohol)'; it.novy = 'R'; }
        } else if (mensie(fR, G.f)) {
          it.pripad = 2;
          body[2] = { P: R, f: fR }; it.krok = 'reflexia R'; it.novy = 'R';
        } else {
          it.pripad = 3;
          const C1 = posun(M, rh, rozdiel(W.P, M));
          const fC1 = val(F.f(C1[0], C1[1]), C1);
          Object.assign(it, { C1, fC1 });
          let C = C1, fC = fC1, meno = 'C1';
          if (o.kontrakcia === 'prednaska') {
            const C2 = posun(M, rh, rozdiel(R, M));
            const fC2 = val(F.f(C2[0], C2[1]), C2);
            Object.assign(it, { C2, fC2 });
            if (mensie(fC2, fC1)) { C = C2; fC = fC2; meno = 'C2'; }
          }
          it.C = C; it.fC = fC; it.meno = meno;
          if (mensie(fC, W.f)) { body[2] = { P: C, f: fC }; it.krok = 'kontrakcia ' + meno; it.novy = meno; }
          else {
            const S = posun(B.P, si, rozdiel(W.P, B.P));
            const M2 = posun(B.P, si, rozdiel(G.P, B.P));
            body = [B, fv(M2), fv(S)];
            Object.assign(it, { S, M2, fS: body[2].f, fM2: body[1].f });
            it.krok = 'zmrštenie'; it.novy = 'S';
          }
        }
        it.po = body.map(b => ({ P: b.P.slice(), f: b.f }));
        out.iter.push(it);
      }
      if (!out.stop) { body = zorad(body); out.stop = { typ: 'maxit', k: maxIt }; out.trojuholniky.push(body.map(b => b.P)); }
      out.iteracie = out.stop.k;
      out.bod = body[0].P; out.f = body[0].f;
      out.body = out.trojuholniky.map(t => t[0]);
    } catch (e) { if (e instanceof MethodError) out.chyba = e.message; else throw e; }
    return out;
  }

  const api = {
    ParseError, MethodError, tokenize, parse, compile, toPoly, polyToNode, pretty, simp, deriv,
    prepare, runGradient, runNewton, runPowell, runNM, uEval, uRoots, uCritical, hessType, pClean
  };
  root.OptEngine = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
