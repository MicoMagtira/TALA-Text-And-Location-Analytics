--- key: title
Aspect sentiment with a lexicon

--- key: p1
**The idea.** Overall sentiment hides what people are unhappy about. Aspect sentiment splits each comment into sentences, keeps the sentences that mention an aspect (waiting, staff, cost, medicine, facilities, access) and scores only those with VADER. One sentence can count for several aspects. The percentage in each cell is the share of those sentences scoring negative; n is the number of sentences, not comments.

--- key: p2
**The lexicon.** Terms live in data/aspects.json, English and Filipino. English words match whole words with simple endings (wait, waited, waiting); Filipino roots also match after a short affix (hintay inside naghintay). It is transparent, fast and easy to extend, which is why it suits teaching.

--- key: p3
**What it finds.** Across the bundled data waiting is by far the most faulted aspect: about 48% of waiting sentences are negative, against about 24% for staff and facilities, 28% for medicine, 29% for access and 32% for cost. The most negative cell is Mimaropa on waiting (58%, n = 213). Cost has few sentences per place (often under 60), so its cells are noisy and the minimum-sentences slider hides the thinnest ones.

--- key: p4
**Limits.** A lexicon matches words, not meaning: "line" also matches "the line moved fast", and it misses paraphrase ("two hours of my day") and sarcasm. A sentence that mentions two aspects gives both the same score. A supervised or zero-shot model would do better on meaning but is harder to inspect. To validate, read a sample of matched sentences and count how many are right (precision), then look for sentences that should have matched but did not (recall).
