// Interior of the book. Content is generated into build/ by build.py.
#import "style.typ": *

#let meta = json("build/meta.json")
#show: setup

#set document(title: meta.title, author: meta.author)
// Lulu wants interior pages at trim size plus 0.125in bleed on every side:
// 6x9in trim -> 6.25x9.25in pages. Margins below include that bleed.
#let bleed = 0.125in
#set page(
  width: 6in + 2 * bleed, height: 9in + 2 * bleed,
  binding: left,
  margin: (inside: 0.9in + bleed, outside: 0.68in + bleed, top: 0.82in + bleed, bottom: 0.9in + bleed),
  header-ascent: 0.3in,
  footer-descent: 0.36in,
  header: context running-head(),
  footer: context folio(),
)
#set text(font: serif, size: 10pt, lang: "en", hyphenate: true, number-type: "old-style",
  costs: (widow: 200%, orphan: 200%, hyphenation: 90%))
#set par(justify: true, leading: 0.66em, spacing: 0.66em,
  first-line-indent: (amount: 1.15em, all: false))
#show raw: set text(font: mono, size: 0.82em)
#show link: it => it.body

// ---------------------------------------------------------------- front matter
#frontmatter-page(first: true)[
  #v(2.4in)
  #align(center, text(size: 15pt, style: "italic", meta.title))
]
#frontmatter-page[]

#frontmatter-page[
  #v(1.5in)
  #align(center)[
    #tracked(size: 10pt, upper(meta.author))
    #v(22pt)
    #text(size: 44pt, style: "italic", meta.title)
    #v(18pt)
    #box(width: 7pt, height: 7pt, fill: accent)
    #v(18pt)
    #text(size: 9.5pt, fill: ink-soft, style: "italic")[
      #num-word(meta.count) essays, #str(meta.first)–#str(meta.last)
    ]
  ]
]

#frontmatter-page[
  #v(1fr)
  #set text(size: 8pt, fill: ink-soft)
  #set par(first-line-indent: 0pt, spacing: 1em, justify: false)
  The essays in this volume were written by Paul Graham and published
  at #emph[paulgraham.com] between #str(meta.first) and #str(meta.last).
  The text follows the online versions; Paul Graham's notes appear at the
  end of each essay.

  This edition was assembled privately for personal reading.
  It is not for sale or distribution.

  Set in Iowan Old Style.
  #v(0.2in)
]

#frontmatter-page[
  #v(0.6in)
  #tracked(size: 9pt)[CONTENTS]
  #v(26pt)
  #context {
    set par(first-line-indent: 0pt, justify: false, spacing: 0pt, leading: 0.5em)
    for hd in query(heading) {
      let pg = counter(page).at(hd.location()).first()
      if hd.level == 1 {
        v(13pt)
        grid(columns: (2.2em, 1fr),
          text(fill: accent, size: 8.5pt, style: "italic", if hd.supplement.has("text") { hd.supplement.text } else { "" }),
          tracked(size: 8.5pt, upper(hd.body)))
        v(5pt)
      } else {
        grid(columns: (2.2em, 1fr, auto), [],
          box(width: 100%, inset: (y: 2.6pt))[#text(size: 9.6pt, hd.body) #box(width: 1fr, repeat(text(fill: rule-col, size: 7pt)[#h(3.5pt).]))],
          box(inset: (y: 2.6pt), text(size: 9.6pt, str(pg))))
      }
    }
  }
]

// ---------------------------------------------------------------- body
#include "build/content.typ"

// ---------------------------------------------------------------- colophon
#blank-to-odd()
#frontmatter-page(first: true)[
  #v(2.6in)
  #align(center)[
    #box(width: 5pt, height: 5pt, fill: accent)
    #v(14pt)
    #set par(justify: false, first-line-indent: 0pt)
    #text(size: 8.5pt, fill: ink-soft, style: "italic")[
      This book was typeset with Typst from the essays \
      at paulgraham.com, in Iowan Old Style, \
      designed by John Downer.
    ]
  ]
]

#context [#metadata(here().page()) <total-pages>]
