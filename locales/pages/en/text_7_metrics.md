--- key: title
Readability formulas & lexical diversity

--- key: p1
Every number on this page is a *proxy*. Readability formulas do not read; they count syllables, words and sentences, then run the totals through a regression fitted decades ago on English schoolbook prose. Knowing what each one actually measures is the difference between using them and being used by them.

--- key: p2
**The readability family.** Flesch Reading Ease scores 0–100, higher = easier; this corpus lands at 54.0, which the scale calls "fairly difficult" — plausible for clinical vocabulary in casual sentences. Flesch-Kincaid (8.2), Gunning Fog (10.6) and SMOG (10.8) all convert to US school grades and *disagree by more than two grades on identical text.* That spread is the most useful thing here: it shows the formulas are opinions, not measurements. Report the direction of a difference between subsets, never the absolute grade.

--- key: p3
**Why two diversity measures.** Type-Token Ratio is unique words ÷ total words. On this corpus that is 1,687 ÷ 292,674 = **0.0058**, a number that looks alarming and means nothing — TTR falls mechanically as text lengthens, because vocabulary saturates while token count keeps climbing. Any long corpus scores near zero. **Herdan's C** takes the ratio in log space (log types ÷ log tokens) and lands at **0.59**, stable enough to compare corpora of different sizes. When someone reports a bare TTR across unequal samples, that is the error to catch.

--- key: p4
**Where this breaks on this data.** Syllable counters are English pronunciation rules, so Filipino and Taglish words get miscounted and every derived grade drifts. Sentence-splitting depends on punctuation these comments use loosely. And short survey replies sit far outside the prose these formulas were fitted on.

--- key: p5
**One firm boundary.** These are properties of *text*, never of people. A low readability score describes writing that is dense, not a writer who is limited — and applying them to individuals rather than corpora is the standard misuse.
