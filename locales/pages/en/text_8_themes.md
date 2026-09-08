--- key: title
TF-IDF + K-Means themes (from NLP.ipynb)

--- key: p1
This page runs the notebook's clustering workflow end to end, and the result contains a mistake worth more than the method itself. Look at the themes before reading on.

--- key: p2
**How the two pieces fit.** TF-IDF weights each term by how often it appears in a comment (TF) against how rare it is across all comments (IDF), so words everywhere get crushed and words that distinguish a comment get amplified. K-Means then groups comments that are near each other in that weighted space. TF-IDF decides what "similar" means; K-Means only obeys it.

--- key: p3
**What K=4 finds here.** Themes of 2,719 / 1,131 / 1,316 / 6,834 comments. Three are recognisable service concerns — waiting times, staff conduct, general experience. One is not. Its top terms are `del`, `del norte`, `del sur`, `norte`, `sur`, `surigao`.

--- key: p4
**That cluster is geography, not a theme.** Nothing malfunctioned. Province names are rare across the corpus, so IDF scored them as highly distinctive, and K-Means faithfully grouped every comment mentioning a `del`-province together. The algorithm did exactly what it was asked. The question it answered was simply not the question anyone wanted asked. This is the most common failure in applied clustering and it never raises an error — a cluster is always returned, and it always looks like a finding.

--- key: p5
**What to do about it.** Add place names to the sidebar's custom stopwords and re-run: the geographic cluster dissolves and a real theme usually takes its place. Then note that you did it. "We excluded toponyms because they clustered on location rather than content" is a legitimate, reportable analytical decision.

--- key: p6
**Reading the scatter.** The map is a 2-D projection of a 1,200-dimension space, so most of the separation is not on your screen. Points that look adjacent may be far apart. Use it to spot a cluster that is obviously smeared or split — never as evidence that themes are cleanly separated. And name every theme from the sample comments, not the keyword list, precisely because the keyword list is what fooled us above.
