#import "@preview/cetz:0.3.4"
#set page(paper: "a4", height: 17.5cm, margin: 10pt)
#set par(justify: true)
#set text(font: "New Computer Modern", size: 12pt, hyphenate: false)

#let fig1 = image("interventions_2025_05_16_16_12.png")
#let fig2 = image("interventions_2025_05_16_17_04.png")
#let fig3 = image("intervnetions_2025_05_23_15_45.png")
#let fig4 = image("no_interventions_2025_05_20_15_15.png")
#let fig5 = image("no_interventions_2025_05_20_16_12.png")
#let fig6 = image("no_interventions_2025_05_21_16_07.png")

#show figure.caption: caption =>{
  set text(size: 10pt)
  caption.body
}

#grid(
  columns: (1fr, 1fr),
  gutter: 0pt,
  column-gutter: 0pt,
  row-gutter: (1pt, 10pt, 10pt, 10pt),
  align: center,
  inset: 0pt,
  rows: (.5cm, 5cm, 5cm, 5cm),
  [
    Interventions
  ],
  [
    No interventions
  ],
  [
    #figure(fig1, caption: "Group 1", gap: 0pt)
  ],
  [
    #figure(fig4, caption: "Group 2", gap: 0pt)
  ],
  [
    #figure(fig2, caption: "Group 3", gap: 0pt)
  ],
  [
    #figure(fig6, caption: "Group 4", gap: 0pt)
  ],
  [
    #figure(fig3, caption: "Group 5", gap: 0pt)
  ],
  [
    #figure(fig5, caption: "Group 6", gap: 0pt)
  ],
)