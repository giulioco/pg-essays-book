// Full wraparound cover: back | spine | front, with bleed.
//
// The idea: one exponential curve runs around the whole book. Across the back
// cover it is nearly flat, the long quiet stretch where compounding hasn't
// shown up yet. It crosses the spine and then, on the front, it takes off and
// leaves through the top edge. Growth, superlinear returns, the shape of
// a startup, the shape of a body of work: the curve is the thing these essays
// keep coming back to. Everything else stays out of its way.

#import "style.typ": *

#let meta = json("build/meta.json")
#let spine = float(sys.inputs.at("spine", default: "1.1")) * 1in
// Print area beyond the 6x9 trim on each edge: 0.125in bleed for paperback;
// larger for hardcover casewrap (the part that wraps around the boards).
#let edge = float(sys.inputs.at("edge", default: "0.125")) * 1in
#let front-only = sys.inputs.at("front", default: "0") == "1"

#let trim-w = 6in
#let trim-h = 9in
#let bleed = edge
#let W = 2 * trim-w + spine + 2 * bleed
#let H = trim-h + 2 * bleed
#let back-x = bleed                    // left edge of back trim
#let spine-x = bleed + trim-w          // left edge of spine
#let front-x = bleed + trim-w + spine  // left edge of front trim
#let m = if edge > 0.2in { 0.8in } else { 0.62in }  // type margin inside trim (casewrap needs more)

#set text(font: serif, fill: ink, number-type: "old-style")
#set par(justify: false, first-line-indent: 0pt)

// ---------------------------------------------------------------- the curve
#let baseline = H - bleed - 1.25in     // where the flat part sits (from top)
#let exit-x = front-x + trim-w * 0.80  // where it leaves through the top edge
#let k = 8.5
#let curve-y(x) = {
  let u = x / exit-x
  baseline - (baseline + 0.2in) * (calc.exp(k * u) - 1) / (calc.exp(k) - 1)
}
#let growth = {
  let n = 600
  let pts = range(n + 1).map(i => {
    let x = exit-x * i / n
    (x, curve-y(x))
  })
  curve(stroke: (paint: accent, thickness: 1.15pt, cap: "round", join: "round"),
    curve.move(pts.first()),
    ..pts.slice(1).map(p => curve.line(p)))
}

// ---------------------------------------------------------------- panels
#let and-list(xs) = if xs.len() < 2 { xs.join() } else { xs.slice(0, -1).join(", ") + " and " + xs.last() }
#let subjects = and-list(meta.parts.filter(p => p.num != "").map(p => lower(p.title)))

#let front = {
  // author
  place(top + left, dx: front-x + m, dy: bleed + 0.78in,
    tracked(size: 10.5pt, tracking: 0.32em)[PAUL GRAHAM])
  // title
  place(top + left, dx: front-x + m - 0.04in, dy: bleed + 1.02in,
    text(size: 84pt, style: "italic", tracking: -0.01em)[#meta.title])
  // what's inside, set small and quiet under the title
  place(top + left, dx: front-x + m, dy: bleed + 2.66in,
    block(width: 2.7in, text(size: 10pt, fill: ink-soft, style: "italic")[
      #num-word(meta.count) essays on #subjects
    ]))
  // the curve's last data point: a year, annotated like a chart, just
  // before the line leaves the page
  let target = bleed + 0.7in
  let yr-x = range(400).map(i => exit-x * i / 400).find(x => curve-y(x) < target)
  place(top + left, dx: yr-x - 0.5in, dy: target - 0.06in,
    text(size: 8pt, fill: accent, number-type: "lining", str(meta.last)))
}

#let spine-panel = place(top + left, dx: spine-x, dy: bleed,
  box(width: spine, height: trim-h,
    align(center + horizon, rotate(90deg, reflow: true,
      box(width: trim-h, inset: (x: 0.6in), {
        tracked(size: 9.5pt, tracking: 0.3em)[PAUL GRAHAM]
        h(1fr)
        text(size: 17pt, style: "italic", baseline: -0.5pt, meta.title)
        h(1.85in)
      })))))

#let back = {
  let x = back-x + 0.75in
  let col = trim-w - 1.5in
  place(top + left, dx: x, dy: bleed + 0.85in, block(width: col, {
    set par(leading: 0.55em, justify: false)
    for p in meta.parts {
      block(below: 5pt, {
        if p.num != "" { text(size: 9pt, fill: accent, style: "italic", p.num); h(0.6em) }
        tracked(size: 7.6pt, tracking: 0.26em, upper(p.title))
      })
      block(below: 13pt, text(size: 8.8pt, fill: ink-soft,
        p.essays.join([ #text(fill: rule-col)[·] ])))
    }
  }))
  // where the curve starts
  place(top + left, dx: back-x + 0.75in, dy: baseline - 0.2in,
    text(size: 8pt, fill: accent, number-type: "lining", str(meta.first)))
}

#let cover = {
  place(top + left, rect(width: W, height: H, fill: paper, stroke: none))
  place(top + left, growth)
  back
  spine-panel
  front
}

#if front-only {
  set page(width: trim-w, height: trim-h, margin: 0pt)
  place(top + left, dx: -front-x, dy: -bleed, box(width: W, height: H, cover))
} else {
  set page(width: W, height: H, margin: 0pt)
  cover
}
