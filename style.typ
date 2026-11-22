// Shared design tokens and layout functions for book.typ and cover.typ.

#let serif = ("Iowan Old Style", "Libertinus Serif")
#let mono = ("Menlo", "DejaVu Sans Mono")
#let ink = rgb("#1d1b18")
#let ink-soft = rgb("#6b665d")
#let rule-col = rgb("#b9b2a5")
#let accent = rgb("#d4501e")   // vermilion: a quieter cousin of YC orange
#let paper = rgb("#f2ede2")

#let tracked(size: 8pt, fill: ink, tracking: 0.16em, body) = text(
  size: size, fill: fill, tracking: tracking, number-type: "lining",
  smallcaps(all: true, body))

#let num-word(n) = {
  let ones = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
  let tens = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
  let w = if n < 20 { ones.at(n) } else if calc.rem(n, 10) == 0 { tens.at(calc.quo(n, 10)) } else {
    tens.at(calc.quo(n, 10)) + "-" + ones.at(calc.rem(n, 10))
  }
  upper(w.first()) + w.slice(1)
}

// ---------------------------------------------------------------- page furniture
#let on-this-page(sel) = query(sel).any(m => m.location().page() == here().page())
#let in-body() = {
  let s = query(<body-start>)
  s.len() > 0 and here().page() >= s.first().location().page()
}
// A page is blank if it was inserted by pagebreak(to: "odd") between the end of
// one section and the opening page of the next, or was marked explicitly.
#let is-blank() = {
  let p = here().page()
  on-this-page(<blank>) or (
    query(<content-end>).any(e => e.location().page() == p - 1)
      and (query(<partpage>) + query(<fm>)).any(s => s.location().page() == p + 1))
}
#let quiet-page() = on-this-page(<fm>) or on-this-page(<partpage>) or is-blank()

#let running-head() = {
  if not in-body() or quiet-page() or on-this-page(heading.where(level: 2)) { return }
  if calc.even(here().page()) {
    align(center, tracked(size: 7.4pt, fill: ink-soft, tracking: 0.22em)[PAUL GRAHAM])
  } else {
    let prev = query(selector(heading.where(level: 2)).before(here()))
    if prev.len() > 0 {
      align(center, text(size: 8.6pt, style: "italic", fill: ink-soft, prev.last().body))
    }
  }
}

#let folio() = {
  if not in-body() or quiet-page() { return }
  align(center, text(size: 8.4pt, fill: ink-soft, counter(page).display()))
}

#let frontmatter-page(first: false, body) = {
  if not first { pagebreak() }
  [#metadata("fm")<fm>]
  body
}

// Continue on the next right-hand page, marking any blank left-hand page.
#let blank-to-odd() = {
  [#metadata("end")<content-end>]
  pagebreak(to: "odd")
}

// ---------------------------------------------------------------- structure
#let part(num, title, first: false) = {
  blank-to-odd()
  if first {
    counter(page).update(1)
    [#metadata("start")<body-start>]
  }
  [#metadata("part")<partpage>]
  heading(level: 1, supplement: [#num], title)
  pagebreak()
  [#metadata("blank")<blank>]
  pagebreak()
}

#let essay(title: "", date: "", slug: "", body) = {
  pagebreak(weak: true)
  v(1.0in)
  if date != "" {
    tracked(size: 7.6pt, fill: ink-soft, tracking: 0.2em, upper(date))
    v(10pt, weak: false)
  }
  heading(level: 2, title)
  context [#metadata((slug: slug, page: here().page()))<essay-at>]
  v(13pt)
  line(length: 20pt, stroke: 0.8pt + accent)
  v(24pt)
  body
}

#let subhead(body) = block(above: 1.5em, below: 0.8em, sticky: true,
  text(style: "italic", body))

#let leadin(body) = text(tracking: 0.03em, smallcaps(body))
#let nref(n) = text(fill: accent, super(str(n)))

#let endnotes(..items) = {
  v(26pt)
  line(length: 20pt, stroke: 0.5pt + rule-col)
  v(10pt)
  tracked(size: 7.2pt, fill: ink-soft, tracking: 0.2em)[NOTES]
  v(6pt)
  set text(size: 8.3pt)
  set par(first-line-indent: 0pt, spacing: 0.7em, leading: 0.58em)
  for (n, body) in items.pos() {
    block(above: 0.95em, below: 0pt, grid(columns: (1.7em, 1fr),
      text(fill: accent, n), body))
  }
}

#let thanks(body) = {
  v(18pt)
  set par(first-line-indent: 0pt, justify: false)
  text(size: 8.3pt, style: "italic", fill: ink-soft, body)
}

#let blockquote(body) = block(above: 1.1em, below: 1.1em, pad(left: 1.5em, right: 1.2em, {
  set text(size: 9.3pt)
  set par(first-line-indent: 0pt, leading: 0.6em)
  body
}))

#let codeblock(src) = block(above: 1.1em, below: 1.1em, pad(left: 1.5em, {
  set text(font: mono, size: 6.9pt)
  set par(justify: false, leading: 0.5em)
  raw(src, block: true)
}))

// ---------------------------------------------------------------- show rules
#let setup(doc) = {
  set list(marker: text(fill: accent)[–], indent: 0.4em, body-indent: 0.7em, spacing: 0.7em)
  set enum(indent: 0.4em, spacing: 0.7em)
  show list: set block(above: 1em, below: 1em)
  show enum: set block(above: 1em, below: 1em)

  show heading.where(level: 2): it => block(width: 100%, above: 0pt, below: 0pt, {
    set par(justify: false, first-line-indent: 0pt, leading: 0.3em)
    text(size: 19.5pt, weight: "regular", hyphenate: false, it.body)
  })

  show heading.where(level: 1): it => {
    v(2.3in)
    align(center, {
      let num = if it.supplement.has("text") { it.supplement.text } else { "" }
      if num != "" {
        text(size: 26pt, fill: accent, style: "italic", num)
        v(18pt)
      } else {
        box(width: 6pt, height: 6pt, fill: accent)
        v(18pt)
      }
      tracked(size: 11pt, tracking: 0.3em, upper(it.body))
    })
  }
  doc
}
