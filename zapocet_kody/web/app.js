(function () {
  'use strict';
  const E = window.OptEngine;
  const SEED = window.SEED_DATA || { priklady: [], vysledky: {} };
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const state = { method: 'gradient', F: null, out: null, k: 0, exId: '', exSnap: '', zlomky: true, userK: 0 };

  // =====================================================================
  //  CISLA
  // =====================================================================
  const SUPD = { '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '-': '⁻' };
  const supStr = e => String(e).split('').map(c => SUPD[c] || c).join('');
  function fmt(v, d) {
    d = d === undefined ? 6 : d;
    if (v === Infinity) return '∞';
    if (v === -Infinity) return '−∞';
    if (!isFinite(v)) return 'nedef.';
    const a = Math.abs(v);
    if (a < 1e-12) return '0';
    if (a >= 1e7 || a < 1e-6) {
      let e = Math.floor(Math.log10(a)), m = v / Math.pow(10, e);
      if (Math.abs(m) >= 9.9995) { m /= 10; e += 1; }
      return m.toFixed(3).replace(/\.?0+$/, '').replace('.', ',').replace('-', '−') + '·10' + supStr(e);
    }
    let s = v.toFixed(d);
    if (s.indexOf('.') >= 0) s = s.replace(/0+$/, '').replace(/\.$/, '');
    if (s === '-0') s = '0';
    return s.replace('.', ',').replace('-', '−');
  }
  function fracOf(v, maxDen) {
    if (!isFinite(v) || Number.isInteger(v)) return null;
    const sg = v < 0 ? -1 : 1, x = Math.abs(v);
    let h0 = 0, h1 = 1, k0 = 1, k1 = 0, b = x;
    for (let i = 0; i < 32; i++) {
      const ai = Math.floor(b);
      const h2 = ai * h1 + h0, k2 = ai * k1 + k0;
      if (k2 > maxDen) break;
      h0 = h1; h1 = h2; k0 = k1; k1 = k2;
      if (Math.abs(x - h1 / k1) <= 1e-9 * Math.max(1, x)) return k1 > 1 ? [sg * h1, k1] : null;
      const r = b - ai;
      if (r < 1e-15) break;
      b = 1 / r;
    }
    return null;
  }
  // kratke desatinne cisla (1,2; 0,25) nechavam desatinne, zlomok len pre 12/17, 1/3 ...
  const niceFrac = (v, maxDen) => (Math.abs(v * 1000 - Math.round(v * 1000)) < 1e-7 * Math.max(1, Math.abs(v)) ? null : fracOf(v, maxDen));
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const fracHTML = (p, q) => `<span class="fr"><span class="nu">${Math.abs(p)}</span><span class="de">${q}</span></span>`;

  // hodnota ako vysledok (modre pero), pri zlomku aj desatinne cislo
  function V(v) {
    const fr = state.zlomky ? niceFrac(v, 1000) : null;
    if (fr) return `<span class="nm m">${fr[0] < 0 ? '−' : ''}${fracHTML(fr[0], fr[1])}</span><span class="hint">≈ ${fmt(v)}</span>`;
    return `<span class="nm">${fmt(v)}</span>`;
  }
  function Pt(P) { return `<span class="nm nw">(${fmt(P[0])}; ${fmt(P[1])})</span>`; }
  const sb = (s, k) => `<span class="m"><i class="v">${s}</i><sub>${k}</sub></span>`;
  const mv = s => `<span class="m"><i class="v">${s}</i></span>`;
  const EQ = '<span class="o">=</span>';

  // =====================================================================
  //  MATEMATIKA -> HTML  (zlomky pod sebou, mocniny hore, odmocnina so ciarou)
  // =====================================================================
  const atom = (h, kind) => ({ h, p: 5, lead: kind, trail: kind, neg: false });
  const par = r => ({ h: `<span class="pa">(</span>${r.h}<span class="pa">)</span>`, p: 5, lead: 'paren', trail: 'paren', neg: false });
  function numR(v, o) {
    if (v < 0) { const a = numR(-v, o); return { h: '−' + a.h, p: 2, lead: 'op', trail: 'num', neg: true }; }
    const fr = (state.zlomky && !o.dec) ? niceFrac(v, 200) : null;
    if (fr) return { h: fracHTML(fr[0], fr[1]), p: 5, lead: 'num', trail: 'num', neg: false };
    return atom(fmt(v), 'num');
  }
  function R(n, o) {
    switch (n.t) {
      case 'num':
        if (n.txt !== undefined) return atom(n.txt.replace('.', ','), 'num');
        return numR(n.v, o);
      case 'const': return atom(`<i class="c">${n.n}</i>`, 'var');
      case 'var': {
        if (o.sub && o.sub[n.n] !== undefined) {
          const v = o.sub[n.n];
          const r = numR(v, o);
          return v < 0 ? Object.assign(par(r), { h: `<span class="sv">${par(r).h}</span>` }) : Object.assign(r, { h: `<span class="sv">${r.h}</span>` });
        }
        return atom(`<i class="v">${n.n === 'g' ? 'γ' : n.n}</i>`, 'var');
      }
      case 'neg': {
        let a = R(n.a, o);
        if (a.p === 1 || a.neg) a = par(a);
        return { h: '−' + a.h, p: 2, lead: 'op', trail: a.trail, neg: true };
      }
      case '+': case '-': {
        const a = R(n.a, o);
        let b = R(n.b, o);
        if (n.t === '+' && b.neg) b = par(b);
        if (n.t === '-' && (b.p === 1 || b.neg)) b = par(b);
        return { h: `${a.h}<span class="o">${n.t === '+' ? '+' : '−'}</span><wbr>${b.h}`, p: 1, lead: a.lead, trail: b.trail, neg: a.neg };
      }
      case '*': {
        let a = R(n.a, o), b = R(n.b, o);
        if (a.p === 1) a = par(a);
        if (b.p === 1 || b.neg) b = par(b);
        const jux = !o.sub && ((a.trail === 'num' && ['var', 'fn', 'paren'].includes(b.lead)) ||
          (['var', 'pow', 'paren'].includes(a.trail) && ['var', 'fn', 'paren'].includes(b.lead)));
        return { h: a.h + (jux ? '' : '<span class="o dot">·</span>') + b.h, p: 2, lead: a.lead, trail: b.trail, neg: a.neg };
      }
      case '/':
        return { h: `<span class="fr"><span class="nu">${R(n.a, o).h}</span><span class="de">${R(n.b, o).h}</span></span>`, p: 5, lead: 'frac', trail: 'frac', neg: false };
      case '^': {
        let base = R(n.a, o);
        if (base.p < 5 || base.neg || base.lead === 'frac' || (n.a.t === 'num' && n.a.v < 0)) base = par(base);
        const ex = R(n.b, Object.assign({}, o));
        return { h: `${base.h}<sup>${ex.h}</sup>`, p: 4, lead: base.lead, trail: 'pow', neg: false };
      }
      case 'fn': {
        const a = R(n.a, o);
        switch (n.n) {
          case 'sqrt': return { h: `<span class="rt"><span class="rs">√</span><span class="ra">${a.h}</span></span>`, p: 5, lead: 'fn', trail: 'paren', neg: false };
          case 'cbrt': return { h: `<span class="rt"><span class="ri">3</span><span class="rs">√</span><span class="ra">${a.h}</span></span>`, p: 5, lead: 'fn', trail: 'paren', neg: false };
          case 'exp': return { h: `<i class="c">e</i><sup>${a.h}</sup>`, p: 4, lead: 'var', trail: 'pow', neg: false };
          case 'abs': return { h: `|${a.h}|`, p: 5, lead: 'paren', trail: 'paren', neg: false };
          default: return { h: `<span>${n.n === 'sign' ? 'sgn' : n.n}</span><span class="pa">(</span>${a.h}<span class="pa">)</span>`, p: 5, lead: 'fn', trail: 'paren', neg: false };
        }
      }
    }
    return atom('?', 'var');
  }
  const MH = (n, o) => `<span class="m">${R(n, o || {}).h}</span>`;
  const N = v => ({ t: 'num', v });
  const G = { t: 'var', n: 'g' };
  // polynom v gama (koeficienty od g^0)
  function uNode(c) {
    let node = null;
    let mx = 0;
    for (let k = 0; k < c.length; k++) mx = Math.max(mx, Math.abs(c[k]));
    for (let k = c.length - 1; k >= 0; k--) {
      const v = c[k];
      if (v === 0 || Math.abs(v) < 1e-14 * mx) continue;
      const mono = k === 0 ? null : k === 1 ? G : { t: '^', a: G, b: N(k) };
      const av = Math.abs(v);
      const term = !mono ? N(av) : av === 1 ? mono : { t: '*', a: N(av), b: mono };
      if (!node) node = v < 0 ? { t: 'neg', a: term } : term;
      else node = { t: v < 0 ? '-' : '+', a: node, b: term };
    }
    return node || N(0);
  }
  // priamka p + d*gama
  function linNode(p, d) {
    return E.simp({ t: '+', a: N(p), b: { t: '*', a: N(d), b: G } });
  }

  // =====================================================================
  //  POMOCNE CASTI LISTOV
  // =====================================================================
  const step = (label, body, cls) => `<li class="st ${cls || ''}"><div class="lbl">${label}</div><div class="bd">${body}</div></li>`;
  const line = (...p) => `<div class="ln">${p.join(' ')}</div>`;
  const lineS = (...p) => `<div class="ln small">${p.join(' ')}</div>`;
  const note = (t, k) => `<div class="note ${k || ''}">${t}</div>`;
  const sqrtH = h => `<span class="rt"><span class="rs">√</span><span class="ra">${h}</span></span>`;
  const mat = (a, b, c, d) => `<span class="mat m"><span class="br">[</span><span class="cells"><span>${a}</span><span>${b}</span><span>${c}</span><span>${d}</span></span><span class="br">]</span></span>`;
  const vec = (a, b) => `<span class="vec m"><span class="br">(</span><span class="cells"><span>${a}</span><span>${b}</span></span><span class="br">)</span></span>`;
  const subXY = P => ({ sub: { x: P[0], y: P[1] } });
  function fLine(F, P, name) {
    return line(`<span class="m"><i>f</i></span>${name ? `<span class="m">(${name})</span>` : `(${fmt(P[0])}; ${fmt(P[1])})`}`, EQ, MH(F.node, subXY(P)), EQ, V(F.f(P[0], P[1])));
  }

  // hladanie po priamke, ako na papieri
  function lsHTML(F, ls, P, u, kladne, gName) {
    let h = '';
    h += line(mv('x'), EQ, MH(linNode(P[0], u[0])), '&nbsp;&nbsp;&nbsp;', mv('y'), EQ, MH(linNode(P[1], u[1])));
    if (!ls) return h;
    const fSub = MH(E.simp(substGamma(F.node, P, u)));
    if (ls.typ === 'poly') {
      h += line(`<span class="m"><i>φ</i>(<i>γ</i>)</span>`, EQ, `<span class="m"><i>f</i></span>(<span class="m"><i>x</i></span>, <span class="m"><i>y</i></span>)`, EQ, fSub);
      h += line('', EQ, MH(uNode(ls.phi)));
      const fP = F.f(P[0], P[1]);
      h += note(`Kontrola: konštantný člen ${fmt(ls.phi[0] || 0)} = f v bode, z ktorého idem (${fmt(fP)}) <span class="dec ok">✓</span>`);
      if (ls.konst) { h += note('φ(γ) je na tejto priamke konštantná, nie je kam ísť, preto γ = 0.', 'amber'); return h; }
      h += line(`<span class="m"><i>φ</i>′(<i>γ</i>)</span>`, EQ, MH(uNode(ls.dphi)), EQ, '<span class="m">0</span>');
      if (ls.dphi.length === 2) {
        h += line(mv('γ'), EQ, MH({ t: '/', a: N(-ls.dphi[0]), b: N(ls.dphi[1]) }, { dec: true }), EQ, V(ls.gama));
      } else if (ls.krit) {
        const nazov = { min: 'minimum φ', max: 'maximum φ', inflex: 'inflexný bod φ' };
        h += note('φ′(γ) = 0 má viac koreňov. Beriem len tie, kde má φ minimum' + (kladne ? ' a γ > 0' : '') + '; z nich to s najmenším φ.');
        for (const c of ls.krit) {
          const zvol = ls.vybrane && c === ls.vybrane;
          const preco = c.typ !== 'min' ? 'nie je minimum' : (kladne && c.g <= 0) ? 'γ ≤ 0, ideme v smere S' : zvol ? 'vyberám' : 'väčšie φ';
          h += lineS(mv('γ'), EQ, `<span class="${zvol ? 'nm' : ''}">${fmt(c.g)}</span>`, `<span class="note">→ ${nazov[c.typ]}, φ = ${fmt(c.phi)}</span>`, zvol ? '<span class="dec ok">✓ ' + preco + '</span>' : `<span class="dec red">✗ ${preco}</span>`);
        }
      }
    } else {
      h += line(`<span class="m"><i>φ</i>(<i>γ</i>)</span>`, EQ, fSub);
      if (ls.interval) {
        h += note(`φ nie je polynóm, rovnica φ′(γ) = 0 sa nedá vyriešiť vzorcom. Minimum φ hľadám numericky na intervale [${fmt(ls.interval[0])}; ${fmt(ls.interval[1])}] (zlatý rez, potom φ′(γ) = 0 dopresním bisekciou).`);
        h += line(mv('γ'), EQ, V(ls.gama));
      }
    }
    if (gName && ls.gama < 0) h += note('γ je záporné: minimum leží „za chrbtom“, proti smeru. Pri Powellovi je to v poriadku.', 'amber');
    return h;
  }
  function substGamma(n, P, u) {
    const go = m => {
      if (m.t === 'var') return m.n === 'x' ? linNode(P[0], u[0]) : linNode(P[1], u[1]);
      if (m.t === 'num' || m.t === 'const') return m;
      if (m.t === 'neg' || m.t === 'fn') return Object.assign({}, m, { a: go(m.a) });
      return Object.assign({}, m, { a: go(m.a), b: go(m.b) });
    };
    return go(n);
  }

  // =====================================================================
  //  LISTY PRE JEDNOTLIVE METODY
  // =====================================================================
  function gradLines(F, P, Pname) {
    const gx = F.gx(P[0], P[1]), gy = F.gy(P[0], P[1]);
    return line(`<span class="m">∂<i>f</i>/∂<i>x</i></span>`, EQ, MH(F.show.fx), EQ, MH(F.show.fx, subXY(P)), EQ, V(gx)) +
      line(`<span class="m">∂<i>f</i>/∂<i>y</i></span>`, EQ, MH(F.show.fy), EQ, MH(F.show.fy, subXY(P)), EQ, V(gy)) +
      line(`<span class="m">∇<i>f</i></span>(${Pname})`, EQ, `<span class="nm">(${fmt(gx)}; ${fmt(gy)})</span>`);
  }
  function normLines(g, norm, eps) {
    const s = g[0] * g[0] + g[1] * g[1];
    const pod = { t: 'fn', n: 'sqrt', a: { t: '+', a: { t: '^', a: N(g[0]), b: N(2) }, b: { t: '^', a: N(g[1]), b: N(2) } } };
    return line(`<span class="m">‖∇<i>f</i>‖</span>`, EQ, MH(pod), EQ, MH({ t: 'fn', n: 'sqrt', a: N(s) }), EQ, V(norm)) +
      note(`‖∇f‖ = ${fmt(norm)} ≥ ε = ${fmt(eps)} → ešte nie som v minime, pokračujem.`);
  }

  function sheetGradient(it, F, out, eps) {
    const k = it.k, Pk = sb('P', k - 1), Pn = sb('P', k);
    let s = '';
    s += step(`Gradient v bode ${Pk} = ${Pt(it.P)}`, gradLines(F, it.P, Pk));
    s += step('Dĺžka gradientu', normLines(it.grad, it.norm, eps));
    s += step(`Normovaný smer ${sb('S', k - 1)} = −∇f / ‖∇f‖`,
      line(sb('S', k - 1), EQ, `<span class="m">(</span>${MH({ t: '/', a: N(-it.grad[0]), b: N(it.norm) }, { dec: true })}<span class="m">;</span> ${MH({ t: '/', a: N(-it.grad[1]), b: N(it.norm) }, { dec: true })}<span class="m">)</span>`, EQ, `<span class="nm">(${fmt(it.S[0])}; ${fmt(it.S[1])})</span>`) +
      (k >= 2 && out.iter[k - 2] ? note(`Kontrola: ${sb('S', k - 1)} · ${sb('S', k - 2)} = ${fmt(it.S[0] * out.iter[k - 2].S[0] + it.S[1] * out.iter[k - 2].S[1])} ≈ 0, po sebe idúce smery sú na seba kolmé <span class="dec ok">✓</span>`) : ''));
    s += step(`Priamka z ${Pk} v smere ${sb('S', k - 1)}, dosadím do f a hľadám γ`, lsHTML(F, it.ls, it.P, it.S, true));
    if (it.chyba) return s + step('Chyba', note(esc(it.chyba), 'red'));
    s += step(`Nový bod ${Pn} = ${Pk} + γ·${sb('S', k - 1)}`,
      line(Pn, EQ, `<span class="m">(${fmt(it.P[0])} <span class="o">+</span> ${fmt(it.gama)}<span class="o dot">·</span>${pp(it.S[0])}; ${fmt(it.P[1])} <span class="o">+</span> ${fmt(it.gama)}<span class="o dot">·</span>${pp(it.S[1])})</span>`, EQ, Pt(it.Pn)) +
      fLine(F, it.Pn) +
      note(it.fPn < it.fP ? `f kleslo z ${fmt(it.fP)} na ${fmt(it.fPn)} <span class="dec ok">✓</span>` : `f nekleslo (${fmt(it.fP)} → ${fmt(it.fPn)}).`, it.fPn < it.fP ? '' : 'red'));
    return s;
  }

  function sheetNewton(it, F, out, eps) {
    const k = it.k, Xk = sb('X', k - 1), Xn = sb('X', k);
    let s = '';
    s += step(`Gradient v bode ${Xk} = ${Pt(it.P)}`, gradLines(F, it.P, Xk));
    s += step('Dĺžka gradientu', normLines(it.grad, it.norm, eps));
    const [a, b, c, d] = it.H;
    s += step(`Hessova matica v bode ${Xk}`,
      line(`<span class="m"><i>H</i></span>(${Xk})`, EQ, mat(MH(F.show.fxx, subXY(it.P)), MH(F.show.fxy, subXY(it.P)), MH(F.show.fxy, subXY(it.P)), MH(F.show.fyy, subXY(it.P))), EQ,
        mat(V(a), V(b), V(c), V(d))) + note('Označím si ju [[a, b], [c, d]]: a = ' + fmt(a) + ', b = ' + fmt(b) + ', c = ' + fmt(c) + ', d = ' + fmt(d) + '.'));
    s += step('Determinant',
      line('<span class="m">det <i>H</i></span>', EQ, '<span class="m"><i>a</i>·<i>d</i> − <i>b</i>·<i>c</i></span>', EQ, `<span class="m">${pp(a)}·${pp(d)} − ${pp(b)}·${pp(c)}</span>`, EQ, V(it.det)) +
      (it.singular ? note('det H = 0 → inverzná matica neexistuje, Newton sa tu nedá použiť.', 'red') : ''));
    if (it.singular) return s;
    s += step('Vymením a ↔ d, pri b a c zmením znamienko',
      line(mat(mv('d'), '−' + mv('b'), '−' + mv('c'), mv('a')), EQ, mat(V(d), V(it.mb), V(it.mc), V(a))) +
      note(`Toto je H⁻¹ ešte bez delenia determinantom (H⁻¹ = 1/det · táto matica).`));
    s += step('Vynásobím gradientom',
      line(mat(V(d), V(it.mb), V(it.mc), V(a)), '<span class="o">·</span>', vec(fmt(it.grad[0]), fmt(it.grad[1])), EQ,
        vec(`${pp(d)}·${pp(it.grad[0])} + ${pp(it.mb)}·${pp(it.grad[1])}`, `${pp(it.mc)}·${pp(it.grad[0])} + ${pp(a)}·${pp(it.grad[1])}`), EQ, vec(V(it.sx), V(it.sy))));
    s += step('A až teraz raz vydelím determinantom',
      line('<span class="m"><i>H</i><sup>−1</sup>∇<i>f</i></span>', EQ, vec(MH({ t: '/', a: N(it.sx), b: N(it.det) }, { dec: true }), MH({ t: '/', a: N(it.sy), b: N(it.det) }, { dec: true })), EQ, vec(V(it.krok[0]), V(it.krok[1]))));
    s += step(`Nový bod ${Xn} = ${Xk} − H⁻¹∇f`,
      line(Xn, EQ, `<span class="m">(${fmt(it.P[0])} − ${pp(it.krok[0])}; ${fmt(it.P[1])} − ${pp(it.krok[1])})</span>`, EQ, Pt(it.Pn)) +
      fLine(F, it.Pn) +
      note(`Posun ‖X${subTxt(k)} − X${subTxt(k - 1)}‖ = ${fmt(it.posun)} ${it.posun < eps ? '< ε → koniec' : '≥ ε → pokračujem'}.`, it.posun < eps ? 'ok' : ''));
    return s;
  }
  const pp = v => (v < 0 ? `(${fmt(v)})` : fmt(v));

  function sheetPowell(it, F, out) {
    let s = '';
    s += step('Začiatok iterácie', line(sb('P', 0), EQ, Pt(it.P0), '&nbsp;&nbsp;', `<span class="m"><i>f</i></span>(${sb('P', 0)})`, EQ, V(it.fP0)) +
      line(sb('u', 1), EQ, Pt(it.u1), '&nbsp;&nbsp;', sb('u', 2), EQ, Pt(it.u2)));
    const names = { u1: ['P', 0, 'P', 1], u2: ['P', 1, 'P', 2], d: ['P', 2, 'P', 3] };
    for (const h of it.hladania) {
      const [, a, , b] = names[h.meno];
      const smer = h.meno === 'd' ? mv('d') : sb('u', h.meno === 'u1' ? 1 : 2);
      let body = lsHTML(F, h.ls, h.z, h.smer, false, true);
      if (h.chyba) body += note(esc(h.chyba), 'red');
      else body += line(sb('P', b), EQ, `${sb('P', a)} + γ·${smer}`, EQ, Pt(h.Q), '&nbsp;&nbsp;', `<span class="m"><i>f</i></span>(${sb('P', b)})`, EQ, V(h.fQ));
      if (h.meno === 'd') {
        s += step('Nový smer d = P₂ − P₀', line(mv('d'), EQ, `<span class="m">(${fmt(it.P2[0])} − ${pp(it.P0[0])}; ${fmt(it.P2[1])} − ${pp(it.P0[1])})</span>`, EQ, Pt(it.d)));
      }
      s += step(`Hľadanie po priamke z ${sb('P', a)} v smere ${smer} = ${Pt(h.smer)} → ${sb('P', b)}`, `<div class="box ${h.meno}">${body}</div>`);
    }
    if (it.chyba) return s;
    if (it.dNula) s += step('Nový smer d = P₂ − P₀', line(mv('d'), EQ, '<span class="nm">(0; 0)</span>') + note('Bod sa po oboch smeroch nepohol, P₃ = P₂.', 'ok'));
    if (!it.dNula) {
      if (it.rovnobezne) s += step('Posunutie smerov', note('d je rovnobežný s u₂ (v prvom kroku vyšlo γ = 0). Keby som smery posunul, boli by oba rovnobežné a metóda by sa zasekla mimo minima. Preto smery NEMENÍM.', 'amber') + line(sb('u', 1), EQ, Pt(it.noveU[0]), '&nbsp;&nbsp;', sb('u', 2), EQ, Pt(it.noveU[1])));
      else s += step('Posunutie smerov: u₁ ← u₂, u₂ ← d', line(sb('u', 1), EQ, Pt(it.noveU[0]), '&nbsp;&nbsp;', sb('u', 2), EQ, Pt(it.noveU[1])));
    }
    s += step('Zastavenie', note(`‖P₃ − P₀‖ = ${fmt(it.posun)} ${it.posun < out.eps ? '< ε → koniec, výsledok je P₃' : '≥ ε → pokračujem, P₃ je nový P₀'}.`, it.posun < out.eps ? 'ok' : ''));
    return s;
  }

  function sheetNM(it, F, out) {
    const ko = out.koef;
    let s = '';
    const vals = it.pred.map(p => fLine(F, p.P)).join('');
    s += step('Hodnoty funkcie v rohoch trojuholníka', vals);
    s += step('Zoradím podľa f: B najmenšie, G stredné, W najväčšie',
      line(mv('B'), EQ, Pt(it.B.P), `<span class="note">f = ${fmt(it.B.f)}</span>`) +
      line(mv('G'), EQ, Pt(it.G.P), `<span class="note">f = ${fmt(it.G.f)}</span>`) +
      line(mv('W'), EQ, Pt(it.W.P), `<span class="note">f = ${fmt(it.W.f)}</span>`) +
      note(`d = najväčšia vzdialenosť vrcholu od B = ${fmt(it.d)} ≥ ε → pokračujem.`));
    s += step('Stred strany oproti W',
      line(mv('M'), EQ, '<span class="m">(<i>B</i> + <i>G</i>)/2</span>', EQ, `<span class="m">((${fmt(it.B.P[0])} + ${pp(it.G.P[0])})/2; (${fmt(it.B.P[1])} + ${pp(it.G.P[1])})/2)</span>`, EQ, Pt(it.M)));
    s += step(`Reflexia R = M + α(M − W), α = ${fmt(ko.al)}`,
      line(mv('R'), EQ, `<span class="m">(${fmt(it.M[0])} + ${fmt(ko.al)}·(${fmt(it.M[0])} − ${pp(it.W.P[0])}); ${fmt(it.M[1])} + ${fmt(ko.al)}·(${fmt(it.M[1])} − ${pp(it.W.P[1])}))</span>`, EQ, Pt(it.R)) +
      (ko.al === 1 ? note('Pri α = 1 je to R = 2M − W.') : '') + fLine(F, it.R, 'R'));
    let roz = '';
    if (it.pripad === 1) {
      roz += note(`f(R) = ${fmt(it.fR)} < f(B) = ${fmt(it.B.f)} → <b>prípad 1</b>: R je lepší než najlepší bod, skúsim ísť ďalej (expanzia).`);
      roz += line(mv('E'), EQ, `<span class="m"><i>M</i> + ${fmt(ko.ga)}(<i>R</i> − <i>M</i>)</span>`, EQ, `<span class="m">(${fmt(it.M[0])} + ${fmt(ko.ga)}·(${fmt(it.R[0])} − ${pp(it.M[0])}); ${fmt(it.M[1])} + ${fmt(ko.ga)}·(${fmt(it.R[1])} − ${pp(it.M[1])}))</span>`, EQ, Pt(it.E));
      roz += fLine(F, it.E, 'E');
      roz += it.novy === 'E' ? note(`f(E) = ${fmt(it.fE)} < f(R) = ${fmt(it.fR)} → <span class="dec ok">W nahradím bodom E</span>`) : note(`f(E) = ${fmt(it.fE)} ≥ f(R) = ${fmt(it.fR)} → <span class="dec ok">W nahradím bodom R</span>`);
    } else if (it.pripad === 2) {
      roz += note(`f(B) = ${fmt(it.B.f)} ≤ f(R) = ${fmt(it.fR)} < f(G) = ${fmt(it.G.f)} → <b>prípad 2</b>: <span class="dec ok">W nahradím bodom R</span>`);
    } else {
      roz += note(`f(R) = ${fmt(it.fR)} ≥ f(G) = ${fmt(it.G.f)} → <b>prípad 3</b>: reflexia nepomohla, kontrakcia.`);
      roz += line(sb('C', 1), EQ, `<span class="m"><i>M</i> + ${fmt(ko.rh)}(<i>W</i> − <i>M</i>)</span>`, EQ, Pt(it.C1), `<span class="note">f = ${fmt(it.fC1)}</span>`);
      if (it.C2) {
        roz += line(sb('C', 2), EQ, `<span class="m"><i>M</i> + ${fmt(ko.rh)}(<i>R</i> − <i>M</i>)</span>`, EQ, Pt(it.C2), `<span class="note">f = ${fmt(it.fC2)}</span>`);
        roz += note(`Lepší (menšie f) je ${it.meno === 'C2' ? 'C₂' : 'C₁'}.`);
      }
      const cn = it.meno === 'C2' ? 'C₂' : 'C₁';
      if (it.novy === 'S') {
        roz += note(`f(${cn}) = ${fmt(it.fC)} ≥ f(W) = ${fmt(it.W.f)} → ani kontrakcia nepomohla, <span class="dec red">zmrštenie k B</span>.`);
        roz += line(mv('S'), EQ, `<span class="m"><i>B</i> + ${fmt(ko.si)}(<i>W</i> − <i>B</i>)</span>`, EQ, Pt(it.S));
        roz += line(mv('M'), EQ, `<span class="m"><i>B</i> + ${fmt(ko.si)}(<i>G</i> − <i>B</i>)</span>`, EQ, Pt(it.M2));
      } else {
        roz += note(`f(${cn}) = ${fmt(it.fC)} < f(W) = ${fmt(it.W.f)} → <span class="dec ok">W nahradím bodom ${cn}</span>`);
      }
    }
    s += step('Rozhodnutie podľa f(R)', roz);
    s += step('Nový trojuholník', it.po.map(p => line(Pt(p.P), `<span class="note">f = ${fmt(p.f)}</span>`)).join(''));
    return s;
  }

  // =====================================================================
  //  VYKRESLENIE LISTOV
  // =====================================================================
  const RES = {
    gradient: it => it.Pn ? `${sb('P', it.k)} = ${Pt(it.Pn)}` : '',
    newton: it => it.Pn ? `${sb('X', it.k)} = ${Pt(it.Pn)}` : '',
    powell: it => it.P3 ? `${sb('P', 3)} = ${Pt(it.P3)}` : '',
    nm: it => `<span class="note">${it.krok}</span> · B = ${Pt(it.po ? E_best(it.po) : it.B.P)}`
  };
  function E_best(po) { return po.slice().sort((a, b) => a.f - b.f)[0].P; }

  function renderSheets() {
    const out = state.out, F = state.F, root = $('#sheets');
    if (!out) { root.innerHTML = ''; return; }
    const eps = out.eps;
    let h = '';
    if (state.method !== 'nm') h += derivSheet(F);
    if (state.method === 'powell') h += `<section class="sheet endsheet"><h3>Pravidlá Powella</h3>${note('Jedna iterácia: P₀ → P₁ po u₁, P₁ → P₂ po u₂, d = P₂ − P₀, P₂ → P₃ po d. Potom u₁ ← u₂, u₂ ← d. Smery sa nenormujú a γ môže byť aj záporné.')}</section>`;
    const fn = { gradient: sheetGradient, newton: sheetNewton, powell: sheetPowell, nm: sheetNM }[state.method];
    out.iter.forEach((it, i) => {
      const head = `<h3>Iterácia ${it.k}${it.chyba || it.singular ? ' <small>chyba</small>' : ''}</h3><div class="res">${RES[state.method](it)}</div>`;
      if (i < 3 || it.chyba || it.singular) h += `<article class="sheet" data-k="${it.k}"><div class="sh-h">${head}</div><ol class="steps">${fn(it, F, out, eps)}</ol></article>`;
      else h += `<details class="sheet" data-k="${it.k}" data-i="${i}"><summary class="sh-h">${head}</summary><ol class="steps"></ol></details>`;
    });
    h += endSheet();
    h += tableSheet();
    root.innerHTML = h;
    $$('details.sheet', root).forEach(d => d.addEventListener('toggle', () => {
      const ol = $('ol', d);
      if (d.open && !ol.childElementCount) ol.innerHTML = fn(out.iter[+d.dataset.i], F, out, eps);
      if (d.open) setK(+d.dataset.k, false);
    }));
    $$('.sheet[data-k] .sh-h', root).forEach(el => el.addEventListener('click', () => setK(+el.closest('.sheet').dataset.k, false)));
    $$('tr[data-k]', root).forEach(tr => tr.addEventListener('click', () => {
      const k = +tr.dataset.k;
      setK(k, false);
      const sh = $(`.sheet[data-k="${k}"]`, root);
      if (sh) { if (sh.tagName === 'DETAILS') sh.open = true; sh.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    }));
    observeSheets();
  }

  function derivSheet(F) {
    let h = `<section class="sheet endsheet"><h3>Derivácie (raz na začiatku)</h3>`;
    h += line(`<span class="m"><i>f</i>(<i>x</i>, <i>y</i>)</span>`, EQ, MH(F.node));
    if (state.method === 'powell') {
      h += note('Powell parciálne derivácie f nepotrebuje. Derivuje sa až φ(γ) na každej priamke.');
      return h + '</section>';
    }
    h += line(`<span class="m">∂<i>f</i>/∂<i>x</i></span>`, EQ, MH(F.show.fx));
    h += line(`<span class="m">∂<i>f</i>/∂<i>y</i></span>`, EQ, MH(F.show.fy));
    if (state.method === 'newton') {
      h += line(`<span class="m">∂²<i>f</i>/∂<i>x</i>²</span>`, EQ, MH(F.show.fxx), '&nbsp;&nbsp;', `<span class="m">∂²<i>f</i>/∂<i>x</i>∂<i>y</i></span>`, EQ, MH(F.show.fxy), '&nbsp;&nbsp;', `<span class="m">∂²<i>f</i>/∂<i>y</i>²</span>`, EQ, MH(F.show.fyy));
      h += line(`<span class="m"><i>H</i>(<i>x</i>, <i>y</i>)</span>`, EQ, mat(MH(F.show.fxx), MH(F.show.fxy), MH(F.show.fxy), MH(F.show.fyy)));
    }
    return h + '</section>';
  }

  function endSheet() {
    const out = state.out, F = state.F, m = state.method;
    let h = `<section class="sheet endsheet" id="koniec"><h3>${out.chyba ? 'Výpočet sa zastavil' : 'Koniec'}</h3>`;
    if (out.chyba) return h + note(esc(out.chyba), 'red') + '</section>';
    const st = out.stop;
    const kk = out.iteracie;
    if (st.typ === 'grad') {
      const P = out.bod;
      h += note(`Iterácia ${kk + 1} sa už nerobí: v bode ${m === 'newton' ? 'X' : 'P'}${sub(kk)} = (${fmt(P[0])}; ${fmt(P[1])}) vyšlo`);
      h += line(`<span class="m">‖∇<i>f</i>‖</span>`, EQ, V(st.hodnota), '<span class="m">&lt;</span>', `<span class="m"><i>ε</i></span>`, EQ, `<span class="m">${fmt(out.eps)}</span>`, '<span class="dec ok">→ STOP</span>');
    } else if (st.typ === 'posun') {
      h += line(m === 'powell' ? '<span class="m">‖<i>P</i><sub>3</sub> − <i>P</i><sub>0</sub>‖</span>' : `<span class="m">‖<i>X</i><sub>${kk}</sub> − <i>X</i><sub>${kk - 1}</sub>‖</span>`, EQ, V(st.hodnota), '<span class="m">&lt; <i>ε</i></span>', '<span class="dec ok">→ STOP</span>');
    } else if (st.typ === 'd') {
      h += note(`Pred iteráciou ${kk + 1}: d = najväčšia vzdialenosť vrcholu od B = ${fmt(st.hodnota)} < ε = ${fmt(out.eps)} → STOP, výsledok je B.`, 'ok');
    } else {
      h += note(`Dosiahnutý maximálny počet iterácií (${kk}). Metóda ešte nie je v minime. Zvýš „max. iterácií“.`, 'amber');
    }
    h += line('Výsledok', Pt(out.bod), '&nbsp;&nbsp;', '<span class="m"><i>f</i></span>', EQ, V(out.f));
    if (m === 'newton' && out.hess) {
      const P = out.bod, a = F.hxx(P[0], P[1]), b = F.hxy(P[0], P[1]), d = F.hyy(P[0], P[1]);
      h += `<div class="sub-h">Čo Newton našiel? (Newton hľadá ∇f = 0, to môže byť aj maximum alebo sedlo)</div>`;
      h += line(`<span class="m"><i>H</i></span>`, EQ, mat(V(a), V(b), V(b), V(d)), '&nbsp;&nbsp;', '<span class="m">det <i>H</i></span>', EQ, V(out.hess.det), '&nbsp;&nbsp;', `<span class="m">∂²<i>f</i>/∂<i>x</i>²</span>`, EQ, V(a));
      const t = out.hess.typ;
      const vys = t === 'MINIMUM' ? 'det H > 0 a ∂²f/∂x² > 0 → MINIMUM' : t === 'MAXIMUM' ? 'det H > 0 a ∂²f/∂x² < 0 → MAXIMUM, Newton nenašiel minimum!' : t === 'SEDLO' ? 'det H < 0 → SEDLO, Newton nenašiel minimum!' : 'det H = 0 → podľa H sa nedá rozhodnúť';
      h += note(vys, t === 'MINIMUM' ? 'ok' : 'red');
    }
    return h + '</section>';
  }
  const sub = k => `<sub>${k}</sub>`;

  function tableSheet() {
    const out = state.out, m = state.method;
    if (!out.iter.length) return '';
    let head, rows;
    if (m === 'gradient') { head = ['k', 'Pₖ', 'f(Pₖ)', 'γ', '‖∇f(Pₖ₋₁)‖']; rows = out.iter.filter(i => i.Pn).map(i => [i.k, pT(i.Pn), fmt(i.fPn), fmt(i.gama), fmt(i.norm)]); }
    else if (m === 'newton') { head = ['k', 'Xₖ', 'f(Xₖ)', 'det H', '‖Xₖ − Xₖ₋₁‖']; rows = out.iter.filter(i => i.Pn).map(i => [i.k, pT(i.Pn), fmt(i.fPn), fmt(i.det), fmt(i.posun)]); }
    else if (m === 'powell') { head = ['k', 'P₁', 'P₂', 'P₃', 'f(P₃)', '‖P₃ − P₀‖']; rows = out.iter.filter(i => i.P3).map(i => [i.k, pT(i.P1), pT(i.P2), pT(i.P3), fmt(i.fP3), fmt(i.posun)]); }
    else { head = ['k', 'krok', 'B', 'f(B)', 'd']; rows = out.iter.map(i => { const b = i.po.slice().sort((p, q) => p.f - q.f)[0]; return [i.k, i.krok, pT(b.P), fmt(b.f), fmt(i.d)]; }); }
    return `<section class="sheet endsheet"><h3>Zhrnutie všetkých iterácií</h3><div class="tblwrap"><table class="sumt"><thead><tr>${head.map(x => `<th>${x}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr data-k="${r[0]}">${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`;
  }
  const pT = P => `(${fmt(P[0])}; ${fmt(P[1])})`;

  // =====================================================================
  //  SUHRN
  // =====================================================================
  function renderSummary() {
    const out = state.out, el = $('#sum');
    if (!out) { el.innerHTML = '<div class="empty">Oprav zápis funkcie, výpočet sa spustí sám.</div>'; return; }
    let h = '';
    const nazov = { gradient: 'Najstrmší gradient', newton: 'Newton 2D', powell: 'Powell', nm: 'Nelder–Mead' }[state.method];
    if (out.chyba) {
      h += `<div class="sum-top"><div class="sum-res"><span class="lbl2">${nazov}</span>Výpočet sa zastavil</div></div><div class="errbox">${esc(out.chyba)}</div>`;
    } else {
      const st = out.stop;
      const stopTxt = st.typ === 'grad' ? `‖∇f‖ = ${fmt(st.hodnota)} < ε` : st.typ === 'posun' ? `${state.method === 'powell' ? '‖P₃ − P₀‖' : '‖Xₖ − Xₖ₋₁‖'} = ${fmt(st.hodnota)} < ε` : st.typ === 'd' ? `d = ${fmt(st.hodnota)} < ε` : 'max. počet iterácií';
      h += `<div class="sum-top"><div class="sum-res"><span class="lbl2">${nazov} · ${state.method === 'newton' ? 'stacionárny bod' : 'minimum'}</span><span class="m">(${fmt(out.bod[0])}; ${fmt(out.bod[1])})</span></div><div class="sum-meta">f = ${fmt(out.f)}</div></div>`;
      h += `<div class="chips"><span class="chip blue">${out.iteracie} ${iterWord(out.iteracie)}</span><span class="chip ${st.typ === 'maxit' ? 'amber' : ''}">STOP: ${stopTxt}</span>`;
      if (out.hess) h += `<span class="chip ${out.hess.typ === 'MINIMUM' ? '' : 'red'}">${out.hess.typ}</span>`;
      h += `</div>`;
    }
    // porovnanie so seedom
    if (state.exId && snapshot() === state.exSnap) {
      const x = SEED.vysledky[state.exId];
      if (x) {
        let ok, txt;
        if (x.chyba || out.chyba) { ok = !!x.chyba === !!out.chyba; txt = x.chyba ? 'Python tiež skončil chybou' : 'Python chybu nehlási'; }
        else { ok = Math.hypot(x.bod[0] - out.bod[0], x.bod[1] - out.bod[1]) < 1e-6 && x.iteracie === out.iteracie; txt = `Python: (${fmt(x.bod[0])}; ${fmt(x.bod[1])}), ${x.iteracie} ${iterWord(x.iteracie)}`; }
        h += `<div class="sum-meta">Seed ${state.exId} · ${txt} <span class="chip ${ok ? '' : 'red'}">${ok ? 'zhoda ✓' : 'nezhoda'}</span></div>`;
      }
    }
    el.innerHTML = h;
  }
  const iterWord = n => (n === 1 ? 'iterácia' : n >= 2 && n <= 4 ? 'iterácie' : 'iterácií');

  // =====================================================================
  //  GRAF
  // =====================================================================
  const plot = { cv: null, bg: null, view: null, W: 0, H: 0, dpr: 1, ml: 46, mb: 24 };
  function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  function hexRgb(h) {
    h = h.replace('#', '');
    if (h.length === 3) h = h.split('').map(c => c + c).join('');
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
  }
  function viewPoints() {
    const out = state.out;
    let pts = [];
    if (!out) return pts;
    if (state.method === 'nm') {
      (out.trojuholniky || []).forEach(t => t.forEach(p => pts.push(p)));
      out.iter.slice(0, 3).forEach(it => ['R', 'E', 'C1', 'C2'].forEach(q => { if (it[q]) pts.push(it[q]); }));
    }
    else {
      (out.body || []).forEach(p => pts.push(p));
      if (state.method === 'powell') out.iter.forEach(it => { if (it.P1) pts.push(it.P1); if (it.P2) pts.push(it.P2); });
    }
    if (!pts.length && out.start) pts.push(out.start);
    if (!pts.length && out.startBody) out.startBody.forEach(b => pts.push(b.P));
    return pts.filter(p => p && isFinite(p[0]) && isFinite(p[1]) && Math.abs(p[0]) < 1e6 && Math.abs(p[1]) < 1e6);
  }
  function setupPlot() {
    const wrap = $('#plotwrap'), cv = $('#plot');
    const W = Math.max(260, wrap.clientWidth), H = Math.round(Math.min(Math.max(W * 0.78, 260), window.innerHeight * 0.55, 560));
    const dpr = window.devicePixelRatio || 1;
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    cv.style.height = H + 'px';
    Object.assign(plot, { cv, W, H, dpr });
    const pts = viewPoints();
    if (!pts.length || !state.F) { plot.view = null; drawPlot(); return; }
    let x0 = Math.min(...pts.map(p => p[0])), x1 = Math.max(...pts.map(p => p[0]));
    let y0 = Math.min(...pts.map(p => p[1])), y1 = Math.max(...pts.map(p => p[1]));
    let w = x1 - x0, h = y1 - y0;
    const big = Math.max(w, h);
    const pad = big > 0 ? 0.18 * big : 1;
    let cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    let hw = w / 2 + pad, hh = h / 2 + pad;
    const iw = W - plot.ml, ih = H - plot.mb;
    if (hw / hh < iw / ih) hw = hh * iw / ih; else hh = hw * ih / iw;
    plot.view = { x0: cx - hw, x1: cx + hw, y0: cy - hh, y1: cy + hh };
    renderBackground();
    drawPlot();
  }
  const PX = x => plot.ml + (x - plot.view.x0) / (plot.view.x1 - plot.view.x0) * (plot.W - plot.ml);
  const PY = y => (plot.H - plot.mb) - (y - plot.view.y0) / (plot.view.y1 - plot.view.y0) * (plot.H - plot.mb);

  function renderBackground() {
    const { W, H, dpr, view } = plot, F = state.F;
    const bg = document.createElement('canvas');
    bg.width = Math.round(W * dpr); bg.height = Math.round(H * dpr);
    const c = bg.getContext('2d');
    c.scale(dpr, dpr);
    c.fillStyle = css('--sheet'); c.fillRect(0, 0, W, H);
    const iw = W - plot.ml, ih = H - plot.mb;
    const nx = 110, ny = Math.max(40, Math.round(nx * ih / iw));
    const Z = [], fin = [];
    for (let j = 0; j <= ny; j++) {
      const row = [];
      const y = view.y0 + (view.y1 - view.y0) * j / ny;
      for (let i = 0; i <= nx; i++) {
        const x = view.x0 + (view.x1 - view.x0) * i / nx;
        let v = F.f(x, y);
        if (!isFinite(v)) v = NaN; else fin.push(v);
        row.push(v);
      }
      Z.push(row);
    }
    fin.sort((a, b) => a - b);
    const L = 18, levels = [];
    for (let i = 1; i <= L; i++) {
      const v = fin[Math.min(fin.length - 1, Math.floor(fin.length * (i - 0.5) / (L + 0.5)))];
      if (v !== undefined && (!levels.length || v > levels[levels.length - 1] + 1e-12 * Math.max(1, Math.abs(v)))) levels.push(v);
    }
    // farebne pasy
    const lo = hexRgb(css('--plot-lo')), hi = hexRgb(css('--plot-hi'));
    const cw = iw / nx, ch = ih / ny;
    const band = v => { let a = 0, b = levels.length; while (a < b) { const m = (a + b) >> 1; if (levels[m] < v) a = m + 1; else b = m; } return a; };
    for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
      const v = (Z[j][i] + Z[j][i + 1] + Z[j + 1][i] + Z[j + 1][i + 1]) / 4;
      if (!isFinite(v)) continue;
      const t = Math.pow(band(v) / levels.length, 0.85);
      const col = lo.map((l, q) => Math.round(l + (hi[q] - l) * t));
      c.fillStyle = `rgb(${col[0]},${col[1]},${col[2]})`;
      c.fillRect(plot.ml + i * cw - 0.3, ih - (j + 1) * ch - 0.3, cw + 0.6, ch + 0.6);
    }
    // vrstevnice (marching squares)
    c.strokeStyle = css('--contour'); c.lineWidth = 1;
    const X = i => plot.ml + i * cw, Y = j => ih - j * ch;
    const SEG = { 1: [[3, 0]], 2: [[0, 1]], 3: [[3, 1]], 4: [[1, 2]], 5: [[0, 1], [2, 3]], 6: [[0, 2]], 7: [[3, 2]], 8: [[2, 3]], 9: [[0, 2]], 10: [[3, 0], [1, 2]], 11: [[1, 2]], 12: [[1, 3]], 13: [[0, 1]], 14: [[3, 0]] };
    c.beginPath();
    for (const lv of levels) {
      for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
        const bl = Z[j][i], br = Z[j][i + 1], tr = Z[j + 1][i + 1], tl = Z[j + 1][i];
        if (!(isFinite(bl) && isFinite(br) && isFinite(tr) && isFinite(tl))) continue;
        const idx = (tl > lv ? 8 : 0) | (tr > lv ? 4 : 0) | (br > lv ? 2 : 0) | (bl > lv ? 1 : 0);
        const segs = SEG[idx];
        if (!segs) continue;
        const ep = e => {
          if (e === 0) { const t = (lv - bl) / (br - bl); return [X(i + t), Y(j)]; }
          if (e === 1) { const t = (lv - br) / (tr - br); return [X(i + 1), Y(j + t)]; }
          if (e === 2) { const t = (lv - tl) / (tr - tl); return [X(i + t), Y(j + 1)]; }
          const t = (lv - bl) / (tl - bl); return [X(i), Y(j + t)];
        };
        for (const [e1, e2] of segs) { const p = ep(e1), q = ep(e2); c.moveTo(p[0], p[1]); c.lineTo(q[0], q[1]); }
      }
    }
    c.stroke();
    // osi
    c.fillStyle = css('--sheet'); c.fillRect(0, 0, plot.ml, H); c.fillRect(0, ih, W, plot.mb);
    c.strokeStyle = css('--line'); c.beginPath(); c.moveTo(plot.ml + .5, 0); c.lineTo(plot.ml + .5, ih + .5); c.lineTo(W, ih + .5); c.stroke();
    c.fillStyle = css('--pencil'); c.font = `11px ${css('--ff-mono')}`;
    const tick = (a, b) => { const r = (b - a) / 5, p = Math.pow(10, Math.floor(Math.log10(r))), m = r / p; return (m < 1.5 ? 1 : m < 3 ? 2 : m < 7 ? 5 : 10) * p; };
    const tx = tick(view.x0, view.x1), ty = tick(view.y0, view.y1);
    c.textAlign = 'center'; c.textBaseline = 'top';
    for (let v = Math.ceil(view.x0 / tx) * tx; v <= view.x1; v += tx) { const x = PX(v); if (x < plot.ml + 10) continue; c.fillText(fmt(+v.toPrecision(10), 4), x, ih + 5); c.fillRect(x, ih, 1, 4); }
    c.textAlign = 'right'; c.textBaseline = 'middle';
    for (let v = Math.ceil(view.y0 / ty) * ty; v <= view.y1; v += ty) { const y = PY(v); if (y > ih - 8) continue; c.fillText(fmt(+v.toPrecision(10), 4), plot.ml - 6, y); c.fillRect(plot.ml - 4, y, 4, 1); }
    // osi x = 0, y = 0
    c.strokeStyle = css('--faint'); c.setLineDash([3, 4]); c.beginPath();
    if (view.x0 < 0 && view.x1 > 0) { c.moveTo(PX(0), 0); c.lineTo(PX(0), ih); }
    if (view.y0 < 0 && view.y1 > 0) { c.moveTo(plot.ml, PY(0)); c.lineTo(W, PY(0)); }
    c.stroke(); c.setLineDash([]);
    plot.bg = bg;
  }

  function drawPlot() {
    const { cv, W, H, dpr } = plot;
    if (!cv) return;
    const c = cv.getContext('2d');
    c.setTransform(1, 0, 0, 1, 0, 0);
    c.clearRect(0, 0, cv.width, cv.height);
    if (!plot.view || !plot.bg) {
      c.scale(dpr, dpr); c.fillStyle = css('--sheet'); c.fillRect(0, 0, W, H);
      c.fillStyle = css('--pencil'); c.font = `14px ${css('--ff-ui')}`; c.textAlign = 'center';
      c.fillText('Graf sa ukáže po výpočte', W / 2, H / 2);
      return;
    }
    c.drawImage(plot.bg, 0, 0);
    c.scale(dpr, dpr);
    c.save();
    c.beginPath(); c.rect(plot.ml, 0, W - plot.ml, H - plot.mb); c.clip();
    const out = state.out, k = state.k, m = state.method;
    const pen = css('--pen'), old = css('--path-old'), red = css('--red'), amber = css('--amber'), ok = css('--ok'), sheet = css('--sheet'), ink = css('--ink');
    const dot = (P, r, fill, stroke) => { c.beginPath(); c.arc(PX(P[0]), PY(P[1]), r, 0, 2 * Math.PI); if (fill) { c.fillStyle = fill; c.fill(); } if (stroke) { c.strokeStyle = stroke; c.lineWidth = 1.5; c.stroke(); } };
    const seg = (P, Q, col, w, dash) => { c.beginPath(); c.setLineDash(dash || []); c.strokeStyle = col; c.lineWidth = w; c.moveTo(PX(P[0]), PY(P[1])); c.lineTo(PX(Q[0]), PY(Q[1])); c.stroke(); c.setLineDash([]); };
    const arrow = (P, Q, col, w) => {
      seg(P, Q, col, w);
      const x1 = PX(P[0]), y1 = PY(P[1]), x2 = PX(Q[0]), y2 = PY(Q[1]);
      const L = Math.hypot(x2 - x1, y2 - y1);
      if (L < 8) return;
      const a = Math.atan2(y2 - y1, x2 - x1), s = Math.min(10, L / 3);
      c.beginPath(); c.fillStyle = col;
      c.moveTo(x2, y2); c.lineTo(x2 - s * Math.cos(a - .4), y2 - s * Math.sin(a - .4)); c.lineTo(x2 - s * Math.cos(a + .4), y2 - s * Math.sin(a + .4)); c.closePath(); c.fill();
    };
    const label = (P, txt, col, dx, dy) => {
      c.font = `italic 13px ${css('--ff-math')}`; c.textAlign = 'left'; c.textBaseline = 'middle';
      const x = PX(P[0]) + (dx || 7), y = PY(P[1]) + (dy || -9);
      c.lineWidth = 3; c.strokeStyle = sheet; c.strokeText(txt, x, y); c.fillStyle = col; c.fillText(txt, x, y);
    };
    if (m === 'gradient' || m === 'newton') {
      const B = out.body;
      for (let i = 1; i <= Math.min(k, B.length - 1); i++) {
        if (i === k) arrow(B[i - 1], B[i], pen, 2.4); else seg(B[i - 1], B[i], old, 1.6);
      }
      for (let i = 0; i <= Math.min(k, B.length - 1); i++) dot(B[i], i === k ? 4.5 : 3, i === k ? pen : sheet, pen);
      const nm = m === 'gradient' ? 'P' : 'X';
      for (let i = Math.max(0, k - 1); i <= Math.min(k, B.length - 1); i++) label(B[i], nm + subTxt(i), i === k ? pen : old);
      if (k === 0) label(B[0], nm + '₀', pen);
    } else if (m === 'powell') {
      for (let i = 0; i < Math.min(k, out.iter.length); i++) {
        const it = out.iter[i], cur = i === k - 1, w = cur ? 2.4 : 1.3;
        if (!it.P1) continue;
        const cols = cur ? [pen, amber, red] : [old, old, old];
        const pts = [it.P0, it.P1, it.P2, it.P3];
        for (let q = 0; q < 3; q++) if (pts[q + 1]) (cur ? arrow : seg)(pts[q], pts[q + 1], cols[q], w);
        if (cur) { ['P₀', 'P₁', 'P₂', 'P₃'].forEach((t, q) => { if (pts[q]) { dot(pts[q], 3.5, sheet, cols[Math.max(0, q - 1)]); label(pts[q], t, ink, 7, q % 2 ? 11 : -9); } }); }
      }
      dot(out.start, 4, k === 0 ? pen : sheet, pen);
      if (k === 0) label(out.start, 'P₀ (štart)', pen);
    } else if (m === 'nm') {
      const T = out.trojuholniky || [];
      const kk = Math.min(k, T.length - 1);
      for (let i = 0; i < kk; i++) { const t = T[i]; c.beginPath(); c.moveTo(PX(t[0][0]), PY(t[0][1])); c.lineTo(PX(t[1][0]), PY(t[1][1])); c.lineTo(PX(t[2][0]), PY(t[2][1])); c.closePath(); c.strokeStyle = old; c.lineWidth = 1; c.stroke(); }
      if (T[kk]) {
        const t = T[kk];
        c.beginPath(); c.moveTo(PX(t[0][0]), PY(t[0][1])); c.lineTo(PX(t[1][0]), PY(t[1][1])); c.lineTo(PX(t[2][0]), PY(t[2][1])); c.closePath();
        c.fillStyle = css('--pen-soft'); c.fill(); c.strokeStyle = pen; c.lineWidth = 2.2; c.stroke();
        ['B', 'G', 'W'].forEach((n, q) => { dot(t[q], 3.5, sheet, pen); label(t[q], n, pen); });
      }
      // body z iteracie, ktora tento trojuholnik vyrobila
      const it = out.iter[kk - 1];
      if (it) {
        dot(it.M, 3, red); label(it.M, 'M', red, 6, 10);
        seg(it.W.P, it.R, red, 1.2, [4, 4]);
        dot(it.R, 3.5, sheet, red); label(it.R, 'R', red);
        if (it.E) { dot(it.E, 3.5, sheet, red); label(it.E, 'E', red); }
        if (it.C1) { dot(it.C1, 3.5, sheet, red); label(it.C1, 'C₁', red); }
        if (it.C2) { dot(it.C2, 3.5, sheet, red); label(it.C2, 'C₂', red); }
      }
    }
    if (!out.chyba && out.bod && k >= (out.iter.length || 0)) {
      const P = out.bod; c.strokeStyle = ok; c.lineWidth = 2;
      c.beginPath(); c.arc(PX(P[0]), PY(P[1]), 8, 0, 2 * Math.PI); c.stroke();
      c.beginPath(); c.moveTo(PX(P[0]) - 12, PY(P[1])); c.lineTo(PX(P[0]) + 12, PY(P[1])); c.moveTo(PX(P[0]), PY(P[1]) - 12); c.lineTo(PX(P[0]), PY(P[1]) + 12); c.stroke();
    }
    c.restore();
  }
  const subTxt = i => String(i).split('').map(d => '₀₁₂₃₄₅₆₇₈₉'[+d]).join('');

  function legend() {
    const m = state.method, el = $('#legend');
    const it = (col, t) => `<span><i style="background:${col}"></i>${t}</span>`;
    if (m === 'powell') el.innerHTML = it('var(--pen)', 'po u₁') + it('var(--amber)', 'po u₂') + it('var(--red)', 'po d') + it('var(--ok)', 'výsledok');
    else if (m === 'nm') el.innerHTML = it('var(--pen)', 'aktuálny trojuholník') + it('var(--path-old)', 'predchádzajúce') + it('var(--red)', 'M, R, E, C z poslednej iterácie') + it('var(--ok)', 'výsledok');
    else el.innerHTML = it('var(--pen)', 'aktuálny krok') + it('var(--path-old)', 'predchádzajúce kroky') + it('var(--ok)', 'výsledok');
  }

  function setK(k, fromScroll) {
    const out = state.out;
    if (!out) return;
    const max = out.iter.length;
    k = Math.max(0, Math.min(max, k));
    state.k = k;
    $('#kRange').max = max; $('#kRange').value = k;
    const nm = state.method === 'nm';
    $('#kLbl').innerHTML = k === 0 ? (nm ? 'Začiatočný trojuholník' : 'Štart') : `Po iterácii ${k} / ${max}`;
    $$('.sheet.on').forEach(s => s.classList.remove('on'));
    const sh = $(`.sheet[data-k="${k}"]`);
    if (sh) sh.classList.add('on');
    $$('tr.on').forEach(t => t.classList.remove('on'));
    const tr = $(`tr[data-k="${k}"]`);
    if (tr) tr.classList.add('on');
    if (!fromScroll) state.userK = Date.now();
    drawPlot();
  }

  let observer = null;
  function observeSheets() {
    if (observer) observer.disconnect();
    if (!('IntersectionObserver' in window)) return;
    observer = new IntersectionObserver(entries => {
      if (Date.now() - state.userK < 900) return;
      const vis = entries.filter(e => e.isIntersecting);
      if (vis.length) setK(+vis[0].target.dataset.k, true);
    }, { rootMargin: '-25% 0px -65% 0px' });
    $$('.sheet[data-k]').forEach(s => observer.observe(s));
  }

  // =====================================================================
  //  ZADANIE
  // =====================================================================
  function numIn(id) {
    const el = $('#' + id), s = el.value.trim().replace('−', '-');
    let v = NaN;
    if (/^[-+]?(\d+[.,]?\d*|[.,]\d+)(e[-+]?\d+)?$/i.test(s)) v = parseFloat(s.replace(',', '.'));
    else if (s) {
      try {
        const n = E.parse(s);
        if (!JSON.stringify(n).includes('"var"')) v = E.compile(n)(0, 0, 0);
      } catch (e) { v = NaN; }
    }
    el.classList.toggle('bad', !isFinite(v));
    return v;
  }
  function readForm() {
    const m = state.method;
    const f = { method: m, fn: $('#fn').value, eps: numIn('eps'), maxIt: Math.round(numIn('maxit')) };
    let ok = isFinite(f.eps) && f.eps > 0 && isFinite(f.maxIt) && f.maxIt >= 1;
    if (f.maxIt > 2000) f.maxIt = 2000;
    if (m !== 'nm') { f.start = [numIn('x0'), numIn('y0')]; ok = ok && f.start.every(isFinite); }
    if (m === 'powell') { f.u1 = [numIn('u1x'), numIn('u1y')]; f.u2 = [numIn('u2x'), numIn('u2y')]; ok = ok && f.u1.concat(f.u2).every(isFinite); }
    if (m === 'nm') {
      f.body = [[numIn('a1'), numIn('a2')], [numIn('b1'), numIn('b2')], [numIn('c1'), numIn('c2')]];
      f.alfa = numIn('alfa'); f.gama = numIn('gama'); f.rho = numIn('rho'); f.sigma = numIn('sigma');
      f.kontrakcia = $('#k-pr').checked ? 'prednaska' : 'cvicenie';
      ok = ok && f.body.flat().every(isFinite) && [f.alfa, f.gama, f.rho, f.sigma].every(isFinite);
    }
    f.ok = ok;
    return f;
  }
  const IDS = ['fn', 'x0', 'y0', 'u1x', 'u1y', 'u2x', 'u2y', 'a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'alfa', 'gama', 'rho', 'sigma', 'eps', 'maxit'];
  function snapshot() {
    const vals = {};
    IDS.forEach(i => { vals[i] = $('#' + i).value; });
    return JSON.stringify({ m: state.method, v: vals, pr: $('#k-pr').checked });
  }

  function updatePreview() {
    const src = $('#fn').value, pv = $('#preview'), er = $('#fnErr');
    try {
      const n = E.parse(src);
      pv.innerHTML = `<span class="m"><i>f</i>(<i>x</i>, <i>y</i>) <span class="o">=</span> ${R(n, {}).h}</span>`;
      pv.classList.remove('bad'); $('#fn').classList.remove('bad');
      er.hidden = true;
      return true;
    } catch (e) {
      if (!(e instanceof E.ParseError)) throw e;
      pv.classList.add('bad'); $('#fn').classList.add('bad');
      pv.innerHTML = '<span class="note">Zápis zatiaľ nie je úplný</span>';
      const p = Math.min(e.pos, src.length);
      er.innerHTML = `${esc(e.message)}<br><code>${esc(src.slice(0, p))}<mark>${esc(src.slice(p, p + 1) || ' ')}</mark>${esc(src.slice(p + 1))}</code>`;
      er.hidden = false;
      return false;
    }
  }

  function compute() {
    const okFn = updatePreview();
    const f = readForm();
    if (!okFn || !f.ok) { state.out = null; renderSummary(); renderSheets(); setupPlot(); return; }
    let F;
    try { F = E.prepare(f.fn); } catch (e) { state.out = null; renderSummary(); return; }
    const run = { gradient: E.runGradient, newton: E.runNewton, powell: E.runPowell, nm: E.runNM }[f.method];
    let out;
    try { out = run(F, f); } catch (e) { out = { chyba: 'Neočakávaná chyba: ' + e.message, iter: [] }; }
    out.eps = f.eps;
    state.F = F; state.out = out;
    renderSummary();
    renderSheets();
    legend();
    setupPlot();
    setK(out.chyba ? out.iter.length : out.iter.length, true);
    save();
  }
  let timer = null;
  const later = () => { clearTimeout(timer); timer = setTimeout(compute, 220); };

  function setMethod(m, silent) {
    const prev = state.method;
    state.method = m;
    $$('.tabs button').forEach(b => b.setAttribute('aria-selected', String(b.dataset.m === m)));
    $$('fieldset[data-for]').forEach(fs => { fs.hidden = !fs.dataset.for.split(' ').includes(m); });
    const mi = $('#maxit');
    if (m === 'nm' && prev !== 'nm' && mi.value.trim() === '100') mi.value = '200';
    if (m !== 'nm' && prev === 'nm' && mi.value.trim() === '200') mi.value = '100';
    if (!silent) compute();
  }

  // prikladov zo seedu
  function pyToHuman(s) {
    return s.replace(/\*\*/g, '^').replace(/(\d|\))\s*\*\s*(?=[a-z(√])/g, '$1').replace(/([xy])\s*\*\s*(?=[xy(])/g, '$1').replace(/\*/g, '·');
  }
  const numTxt = v => String(v).replace('.', ',');
  function fillExamples() {
    const sel = $('#ex');
    const nazvy = { gradient: 'Najstrmší gradient', newton: 'Newton 2D', powell: 'Powell', nm: 'Nelder–Mead' };
    let h = '<option value="">vlastný príklad</option>';
    for (const m of ['gradient', 'newton', 'powell', 'nm']) {
      h += `<optgroup label="${nazvy[m]}">`;
      for (const p of SEED.priklady.filter(p => p.metoda === m)) h += `<option value="${p.id}">${p.id}: ${esc(pyToHuman(p.funkcia))}</option>`;
      h += '</optgroup>';
    }
    sel.innerHTML = h;
  }
  function loadExample(id) {
    const p = SEED.priklady.find(q => q.id === id);
    if (!p) { state.exId = ''; $('#exdesc').textContent = ''; compute(); return; }
    $('#fn').value = pyToHuman(p.funkcia);
    if (p.start) { $('#x0').value = numTxt(p.start[0]); $('#y0').value = numTxt(p.start[1]); }
    $('#u1x').value = '1'; $('#u1y').value = '0'; $('#u2x').value = '0'; $('#u2y').value = '1';
    if (p.body) { ['a', 'b', 'c'].forEach((l, i) => { $('#' + l + '1').value = numTxt(p.body[i][0]); $('#' + l + '2').value = numTxt(p.body[i][1]); }); }
    $('#alfa').value = numTxt(p.alfa ?? 1); $('#gama').value = numTxt(p.gama ?? 2); $('#rho').value = numTxt(p.rho ?? 0.5); $('#sigma').value = numTxt(p.sigma ?? 0.5);
    if (p.kontrakcia) { $('#k-pr').checked = p.kontrakcia === 'prednaska'; $('#k-cv').checked = p.kontrakcia !== 'prednaska'; }
    $('#eps').value = numTxt(p.eps || 0.001);
    $('#maxit').value = String(p.max_it || (p.metoda === 'nm' ? 200 : 100));
    $('#exdesc').textContent = 'Pasca: ' + p.pasca;
    setMethod(p.metoda, true);
    state.exId = id;
    state.exSnap = snapshot();
    compute();
  }

  function save() {
    try { localStorage.setItem('optkrok2', JSON.stringify({ snap: snapshot(), ex: state.exId, zl: state.zlomky })); } catch (e) { /* bez ulozenia */ }
  }
  function restore() {
    try {
      const d = JSON.parse(localStorage.getItem('optkrok2') || 'null');
      if (!d || !d.snap) return false;
      const sn = JSON.parse(d.snap);
      if (!sn || !sn.v || !sn.m) return false;
      IDS.forEach(id => { if (typeof sn.v[id] === 'string') $('#' + id).value = sn.v[id]; });
      $('#k-pr').checked = !!sn.pr; $('#k-cv').checked = !sn.pr;
      state.zlomky = d.zl !== false; $('#zlomky').checked = state.zlomky;
      setMethod(sn.m, true);
      if (d.ex) { state.exId = d.ex; $('#ex').value = d.ex; const p = SEED.priklady.find(q => q.id === d.ex); $('#exdesc').textContent = p ? 'Pasca: ' + p.pasca : ''; state.exSnap = snapshot(); }
      return true;
    } catch (e) { return false; }
  }

  // ---- udalosti ----
  function init() {
    fillExamples();
    $$('.tabs button').forEach(b => b.addEventListener('click', () => setMethod(b.dataset.m)));
    $('#fn').addEventListener('input', () => { updatePreview(); later(); });
    $$('.params input').forEach(el => el.addEventListener('input', later));
    $$('input[name=kontr]').forEach(el => el.addEventListener('change', compute));
    $('#ex').addEventListener('change', e => loadExample(e.target.value));
    $('#keys').addEventListener('click', e => {
      const b = e.target.closest('button');
      if (!b) return;
      const inp = $('#fn'), ins = b.dataset.ins, c = b.dataset.c !== undefined ? +b.dataset.c : ins.length;
      const s = inp.selectionStart ?? inp.value.length, en = inp.selectionEnd ?? s;
      inp.value = inp.value.slice(0, s) + ins + inp.value.slice(en);
      inp.focus();
      inp.setSelectionRange(s + c, s + c);
      updatePreview(); later();
    });
    $('#kRange').addEventListener('input', e => setK(+e.target.value, false));
    $('#kPrev').addEventListener('click', () => setK(state.k - 1, false));
    $('#kNext').addEventListener('click', () => setK(state.k + 1, false));
    $('#zlomky').addEventListener('change', e => { state.zlomky = e.target.checked; renderSummary(); renderSheets(); setK(state.k, true); save(); });
    const cv = $('#plot');
    cv.addEventListener('mousemove', e => {
      if (!plot.view || !state.F) return;
      const r = cv.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top;
      if (px < plot.ml || py > plot.H - plot.mb) { $('#readout').textContent = ''; return; }
      const x = plot.view.x0 + (px - plot.ml) / (plot.W - plot.ml) * (plot.view.x1 - plot.view.x0);
      const y = plot.view.y0 + (plot.H - plot.mb - py) / (plot.H - plot.mb) * (plot.view.y1 - plot.view.y0);
      $('#readout').textContent = `x = ${fmt(x, 4)}   y = ${fmt(y, 4)}   f = ${fmt(state.F.f(x, y), 4)}`;
    });
    if ('ResizeObserver' in window) {
      let w = 0;
      new ResizeObserver(() => { const nw = $('#plotwrap').clientWidth; if (Math.abs(nw - w) > 2) { w = nw; setupPlot(); } }).observe($('#plotwrap'));
    }
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const re = () => { if (state.out) setupPlot(); };
    if (mq.addEventListener) mq.addEventListener('change', re);
    new MutationObserver(re).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    document.addEventListener('keydown', e => {
      if (e.target.matches('input, select, textarea')) return;
      if (e.key === 'ArrowRight') setK(state.k + 1, false);
      if (e.key === 'ArrowLeft') setK(state.k - 1, false);
    });
    if (!restore()) { loadExample('G1'); $('#ex').value = 'G1'; return; }
    compute();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
