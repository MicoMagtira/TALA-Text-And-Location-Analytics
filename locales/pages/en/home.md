--- key: title
How the two tracks connect

--- key: p1
Most analytics tools answer either *what are people saying* or *where is this happening*. TALA is built to show why those two questions are weaker apart than together. One dataset of 12,000 health-service comments carries both a `text` column and a `lon`/`lat` pair, and every page is a different way of reading the same 12,000 rows.

--- key: p2
**Why the pairing matters.** Text alone tells you that 1,448 comments mention waiting hours, but not whether that is one overwhelmed facility or a nationwide pattern. Location alone shows you a dense cluster of 1,750 points, but not that the people inside it are talking about staff conduct rather than medicine supply. The final geospatial page joins the two: keywords and sentiment computed *per cluster*, which is a claim neither track could make by itself.

--- key: p3
**Two different shapes of work.** The eight text pages are independent lenses — open them in any order. The five geospatial pages are a *pipeline*, where each step consumes the last:

--- key: p4
`Ingest → DBSCAN → Generalization → NLP per cluster → Map & exports`

--- key: p5
That ordering is not a UI convenience. Distances cannot be measured until coordinates are validated and projected; clusters cannot be found without distances; per-cluster text needs clusters to group by. Skipping ahead produces a number, just not a defensible one.

--- key: p6
**A deliberate trap.** The bundled coordinates are dirty on purpose — some land in London and California. Nothing removes them until the land-clip on the last page, which drops 3,467 of 11,715 points. Roughly a third of this dataset is wrong in a way no error message will announce, and every intermediate map still looks plausible. Noticing that is the point.

--- key: p7
**Sidebar controls apply everywhere.** Palettes, the Filipino-stopword toggle and your custom stopwords are global, so a change on one page silently changes results on the others. Set them deliberately before comparing outputs.
