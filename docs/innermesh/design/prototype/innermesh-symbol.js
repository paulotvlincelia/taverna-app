(function () {
  // Geometria do símbolo InnerMesh, grade 64, centro (32,32), raio 22.
  var DEF = {
    a: { n: 6, chords: { L: [[1, 3], [4, 0]], M: [[1, 3]], S: [] }, out: 1 },
    b: { n: 7, gap: [6, 0], chords: { L: [[1, 3]], M: [[1, 3]], S: [] }, out: 0 },
    c: { n: 5, angles: [-90, -18, 50, 130, 200], ringCircle: true, chords: { L: [[0, 2]], M: [], S: [] }, out: 1 }
  };
  function tier(px) { return px >= 56 ? 'L' : px >= 24 ? 'M' : 'S'; }
  function IMSymbol(o) {
    var R = React.createElement, d = DEF[o.opt || 'a'], t = o.tier || tier(o.size), st = o.state || 'completo';
    var sw = { L: 2.5, M: 3.2, S: 4.8 }[t], nr = { L: 3.5, M: 4, S: 5 }[t], cr = { L: 3, M: 3.5, S: 4.5 }[t];
    var ang = d.angles || Array.from({ length: d.n }, function (_, k) { return -90 + k * 360 / d.n; });
    var P = ang.map(function (a) { var r = a * Math.PI / 180; return [32 + 22 * Math.cos(r), 32 + 22 * Math.sin(r)]; });
    var anim = st === 'anim', p = anim ? Math.max(0, Math.min(1, o.p || 0)) : 0;
    var clamp = function (v) { return Math.max(0, Math.min(1, v)); };
    var e1 = 1 - Math.pow(1 - clamp(p * 600 / 360), 3), e2 = clamp((p * 600 - 240) / 280), e3 = clamp((p * 600 - 520) / 80);
    var outside = st !== 'completo' && !anim ? d.out : -1;
    var mover = anim ? d.out : -1;
    var ink = st === 'fora' ? o.muted : o.ink;
    var els = [];
    if (d.ringCircle) {
      els.push(R('circle', { key: 'ring', cx: 32, cy: 32, r: 22, fill: 'none', stroke: ink, strokeWidth: sw * 0.75 }));
    } else {
      for (var k = 0; k < d.n; k++) {
        var j = (k + 1) % d.n;
        if (d.gap && d.gap[0] === k && d.gap[1] === j) continue;
        if (k === outside || j === outside) continue;
        if (k === mover || j === mover) continue;
        els.push(R('line', { key: 'r' + k, x1: P[k][0], y1: P[k][1], x2: P[j][0], y2: P[j][1], stroke: ink, strokeWidth: sw, strokeLinecap: 'round' }));
      }
    }
    (d.chords[t] || []).forEach(function (c, i) {
      if (c[0] === outside || c[1] === outside) return;
      if (c[0] === mover || c[1] === mover) return;
      els.push(R('line', { key: 'c' + i, x1: P[c[0]][0], y1: P[c[0]][1], x2: P[c[1]][0], y2: P[c[1]][1], stroke: ink, strokeWidth: sw * 0.8, strokeLinecap: 'round' }));
    });
    if (mover >= 0) {
      var ma = (ang[mover] + 28 * (1 - e1)) * Math.PI / 180, mr = 35 - 13 * e1;
      var m = [32 + mr * Math.cos(ma), 32 + mr * Math.sin(ma)];
      var nb = [];
      if (!d.ringCircle) {
        var prev = (mover - 1 + d.n) % d.n, next = (mover + 1) % d.n;
        if (!(d.gap && d.gap[0] === prev && d.gap[1] === mover)) nb.push([prev, sw]);
        if (!(d.gap && d.gap[0] === mover && d.gap[1] === next)) nb.push([next, sw]);
      }
      (d.chords[t] || []).forEach(function (c) { if (c[0] === mover) nb.push([c[1], sw * 0.8]); if (c[1] === mover) nb.push([c[0], sw * 0.8]); });
      if (e2 > 0) nb.forEach(function (n, i) { var q = P[n[0]]; els.push(R('line', { key: 'm' + i, x1: m[0], y1: m[1], x2: m[0] + (q[0] - m[0]) * e2, y2: m[1] + (q[1] - m[1]) * e2, stroke: ink, strokeWidth: n[1], strokeLinecap: 'round' })); });
      els.push(e1 < 1
        ? R('circle', { key: 'mv', cx: m[0], cy: m[1], r: nr, fill: 'none', stroke: o.accent, strokeWidth: 1.8 })
        : R('circle', { key: 'mv', cx: m[0], cy: m[1], r: nr, fill: ink }));
    }
    P.forEach(function (p, k) { if (k !== outside && k !== mover) els.push(R('circle', { key: 'n' + k, cx: p[0], cy: p[1], r: nr, fill: ink })); });
    if (outside >= 0) {
      var a = ang[outside] * Math.PI / 180, q = [32 + 35 * Math.cos(a), 32 + 35 * Math.sin(a)];
      els.push(st === 'fora'
        ? R('circle', { key: 'o', cx: q[0], cy: q[1], r: nr, fill: o.muted })
        : R('circle', { key: 'o', cx: q[0], cy: q[1], r: nr, fill: 'none', stroke: o.accent, strokeWidth: 1.8 }));
    }
    if (st !== 'fora') els.push(R('circle', { key: 'ctr', cx: 32, cy: 32, r: cr, fill: o.mono ? ink : o.accent, opacity: anim ? 0.85 + 0.15 * e3 : 1 }));
    return R('svg', {
      width: o.size, height: o.size, viewBox: outside >= 0 || anim || o.pad ? '-10 -10 84 84' : '0 0 64 64', role: 'img', 'aria-label': o.title || 'InnerMesh',
      style: { display: 'block', flex: 'none', transform: o.rotate ? 'rotate(' + o.rotate + 'deg)' : undefined }
    }, els);
  }
  IMSymbol.defs = DEF;
  window.IMSymbol = IMSymbol;
})();
