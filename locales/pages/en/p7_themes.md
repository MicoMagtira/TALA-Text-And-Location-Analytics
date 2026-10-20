--- key: title
TF-IDF + K-Means themes, compared across places

--- key: p1
**How the pieces fit.** TF-IDF weights each term by how often it appears in a comment against how rare it is across all comments, so words found everywhere are crushed and distinguishing words are amplified. K-Means then groups comments that are near each other in that weighted space. TF-IDF decides what "similar" means; K-Means only obeys it. TALA uses unigrams and bigrams, max_df 0.9, min_df 3 and 1,200 features.

--- key: p2
**Choosing k with the silhouette.** For each comment, a is its mean cosine distance to its own theme and b its mean distance to the nearest other theme; s = (b - a) / max(a, b). The average runs from -1 to 1. Near 1 means well separated; near 0 means themes overlap. On this data the scores are low (about 0.05 at k = 4 and 0.08 at k = 8) because comments are short and share vocabulary. A higher score for larger k is not automatically better: ask whether the cards read as distinct, nameable themes.

--- key: p3
**The province-name trap (still true).** With place names left in, k = 4 produces a theme of 1,131 comments whose top terms are *del*, *del norte*, *del sur*, *norte*, *sur*, *surigao*. That is geography, not a theme: province names are rare, so IDF scored them as distinctive. TALA therefore hides place names by default, and the geographic theme dissolves into content themes (waiting, staff, rural health units, general experience). Untick the box to see the trap yourself, and say in your write-up that you excluded place names.

--- key: p4
**Theme share per place.** The stacked bar shows, within each place, what percentage of comments fall in each theme (rows sum to 100%). Because themes are shared vocabulary, shares are similar across places here. Auto-labels come from rank-weighted matches between the top terms and the aspect lexicon; always check them against the term list.
