--- key: title
Contrastive keywords: weighted log-odds

--- key: p1
**Why not just count words?** The most frequent words in any place are the most frequent words everywhere ("staff", "hospital"). To see what makes a place *different* you compare it with a reference group and ask which words lean one way. Raw ratios fail too: a word seen twice in place A and never elsewhere has an infinite ratio.

--- key: p2
**The method (Monroe, Colaresi & Quinn 2008).** For each term w, let y_a and y_b be its counts in groups A and B, n_a and n_b the total words in each, and alpha_w a Dirichlet prior proportional to the word's count in *all* comments, scaled so the alphas sum to a0 = 500. Then delta = log((y_a + alpha_w) / (n_a + a0 - y_a - alpha_w)) - log((y_b + alpha_w) / (n_b + a0 - y_b - alpha_w)), its variance is 1/(y_a + alpha_w) + 1/(y_b + alpha_w), and z = delta / sqrt(variance). Positive z means more typical of A, negative of B. Swapping A and B flips the sign exactly.

**What the prior does.** It pulls rare words toward their overall rate, so a word seen three times cannot top the chart. A bigger prior is more cautious. Dividing by the standard deviation turns "how different" into "how sure": common words with a modest lean can outrank rare words with a large one.

--- key: p3
**Place names win unless you hide them.** For Central Luzon the top terms are *nueva*, *central*, *fernando*, *bulacan*, *zambales* (z from 21 down to 11), because people there name their own province. That is true but not news, so the page hides place names by default (words from region, province and city names, plus every place the geoparser found). What remains is much quieter: the strongest remaining terms have z around 4. In this dataset the comments follow shared templates, so places differ little in what they say. Reading "nothing much sets this place apart" is a result, not a failure.

--- key: p4
**Limits.** Terms are single words and two-word phrases after stopword removal, so phrases appear as pairs ("handled lab"). The minimum-count slider (never below 5) stops a term from describing one or two people. With 17 regions and thousands of candidate terms, a few high z values arise by chance; treat z above about 3 as interesting, and verify with aggregated counts, never by reading individual comments.
