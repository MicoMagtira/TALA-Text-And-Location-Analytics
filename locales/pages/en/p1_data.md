--- key: title
Data and cleaning

--- key: p1
**What the pipeline needs.** TALA wants one text column and, for the place steps, a longitude and a latitude column. Everything later in the journey reads those three columns by name, which is why you map them here once and never again. The mapping is stored as column names in your session, never as a copy of the data.

--- key: p2
**Cleaning is a small, fixed pipeline.** Lower-case, strip links, @mentions and #hashtags, drop punctuation and digits, collapse whitespace, then split on spaces. Tokens shorter than three characters and tokens in the stopword set are discarded. Use the slider to watch one comment go through each stage. The point is that every step is a visible rule, not a black box.

--- key: p3
**Stopwords are an analytical choice.** Words like "the", "ang" or "sa" carry grammar, not content, so they would dominate any word count. The default set is English plus a Filipino list. Add your own: if you later find that place names or the word "hospital" swamp the results, put them in the extra-words box and say so in your write-up. Excluding a word is a decision you should be able to defend.

--- key: p4
**Why cleaning comes before place-reading.** Geoparsing in the next step uses the *original* text, because place names depend on capital letters ("Baguio" the city, not "baguio" the word). The cleaned tokens are used later, in Chapter 2, when we compare what each place says.
