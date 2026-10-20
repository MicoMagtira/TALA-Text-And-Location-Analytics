--- key: title
Sentiment per place with honest intervals

--- key: p1
**VADER.** A rule-based lexicon scorer: each word has a valence, rules handle negation, intensifiers and punctuation, and the sum is squashed into a compound score between -1 and 1. A comment is negative when compound <= -0.05 (VADER's own cut-off). It was built for English social media, so Filipino and Taglish text is only partly understood; read results as *relative* between places, not as absolute truth. TALA scores every comment once per dataset and reuses it on steps 5, 6, 8 and 9.

--- key: p2
**Why intervals.** A place's % negative is a proportion k/n, and small n makes it noisy. The Wilson score interval at z = 1.96 is centre = (p + z^2/2n) / (1 + z^2/n), half-width = z * sqrt(p(1-p)/n + z^2/4n^2) / (1 + z^2/n). Unlike the textbook p +/- z*sqrt(p(1-p)/n), it never leaves [0, 1] and behaves for small n or p near 0 or 1.

--- key: p3
**What the bundled data says.** Overall 36% of the 12,000 comments score negative. By region it runs from 31% (Ilocos Region, n = 575) to 39% (Western Visayas, n = 895, 95% interval 35.6 to 42.0). Those intervals overlap heavily: the data do not support ranking most regions against each other. The National Capital Region has only 157 comments, so its interval is wide (26.8 to 41.5). That is why places under the minimum n are greyed out instead of ranked.

**Overlap is a rough guide, not a test.** Overlapping intervals do not prove there is no difference, and non-overlapping ones do not prove there is. For a formal comparison use a two-proportion test, and remember that many comparisons at once inflate false alarms.
