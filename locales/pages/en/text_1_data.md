--- key: title
The preprocessing pipeline (from NLP.ipynb)

--- key: p1
Preprocessing is where you decide what the computer is allowed to notice. Raw text carries punctuation, capitalization, filler words, emoji, numbers, typos and mixed languages. Some of that is signal and some is noise, and *which is which depends entirely on your research question.* Preprocessing is not a cleansing ritual — it is a research decision you have to be able to defend.

--- key: p2
**What this pipeline does, in order.** Lowercase → strip URLs → strip `@mentions` and `#hashtags` → strip punctuation (Unicode-aware, so it handles curly quotes) → strip digits → collapse whitespace → split on spaces → drop tokens shorter than 3 characters → drop stopwords.

--- key: p3
**What it costs on this corpus.** 292,674 raw words become 174,562 tokens — you are discarding 40% of the text. The surviving vocabulary is 551 distinct words. That is a big reduction, and it is the whole point: what remains should be the part worth counting.

--- key: p4
**The stopword decision.** 318 English stopwords come from scikit-learn's standard list; 147 Filipino stopwords (`ang`, `sa`, `mga`, `naman`) are bundled separately and toggled in the sidebar. Turn the Filipino list off and re-run any later page — Tagalog function words flood the top of every frequency chart, which is exactly what happens when you apply English-only tooling to Taglish data.

--- key: p5
**Where the defaults will hurt you.** The digit-stripping rule deletes `24/7`, `3 hours` and `P500`. The punctuation rule deletes the `!` in "three hours again!" — if you are studying anger, you just removed the anger. The 3-character minimum deletes `ER`, `OB` and `IV`. None of this is wrong in general and all of it might be wrong for you.

--- key: p6
**Do this before moving on.** Read the raw-vs-cleaned pairs below. If a comment you understand becomes a comment you do not, add the lost words to the sidebar's custom stopword box in reverse — that is, reconsider the rule, not the example.
