--- key: title
NLP per cluster — where text meets place (Lab 5)

--- key: p1
This is the page the whole app exists for. Everything before it ran one track or the other; here the text becomes an *attribute of place*. For each of the 29 non-noise clusters you get TF-IDF keywords, a sentiment breakdown, and a rule-based tag — a profile of what people are saying **in that specific area**.

--- key: p2
**Why this is more than either half.** The text pages found that 1,448 comments mention waiting hours; the geo pages found a cluster of 1,750 points. Neither could connect them. Grouping by `cluster_id` before running TF-IDF answers the question that matters operationally: not *what is discussed* or *where is dense*, but **which concern belongs to which place** — the difference between "waiting times are a problem" and "waiting times are the problem in these four areas."

--- key: p3
**TF-IDF is doing something specific here.** It is not ranking each cluster's commonest words — that would return `health` and `hospital` for all 29. It weights each cluster's terms against the *other clusters*, surfacing what makes this area's comments distinctive. A term appearing everywhere scores near zero even if it appears constantly.

--- key: p4
**Read size first, always.** A cluster of 1,750 comments supports a claim; a cluster of 12 does not, yet both produce a confident-looking row of keywords and a sentiment percentage. Small clusters yield unstable terms that change completely if you nudge `eps`. Sort by `n_points` and treat the tail with suspicion. The auto-assigned `tag` is a keyword-matching convenience for navigation, not a classification — read the terms and decide yourself.

--- key: p5
**The privacy boundary is structural.** This table exports counts, aggregated percentages and term lists — never a comment, never a coordinate. That is deliberate: location-linked personal accounts of medical visits are among the most re-identifying combinations you can hold. Aggregate here is not a formatting choice; it is the control that makes the output shareable.
