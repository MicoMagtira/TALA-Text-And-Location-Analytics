--- key: title
LDA & topic stability

--- key: p1
LDA proposes candidate topics. **People name them, and people are responsible for them.** The model never sees a theme — it sees which words tend to occur in the same documents, and works backwards to a set of word-distributions that would explain that pattern.

--- key: p2
**The two distributions it learns.** Each *document* is modelled as a mixture of topics (a comment can be 70% one thing, 30% another), and each *topic* as a distribution over words. That double flexibility is why LDA handles comments covering several concerns at once, and also why its output is softer than it looks: nothing is assigned anywhere with certainty.

--- key: p3
**Choosing K is your call, not the model's.** There is no correct number of topics, and LDA will happily produce whatever K you ask for — five topics from noise, twenty topics from five real themes. Judge a solution by whether the top words cohere, whether the representative quotes below actually belong together, and whether the sizes are usable. A topic holding 3% of documents is rarely worth reporting; one holding 60% usually needs splitting.

--- key: p4
**Why stability matters more than plausibility.** LDA is initialised randomly, so different seeds give different topics from identical data. Human beings are extremely good at reading meaning into any list of related words — you will find a story in a topic that is pure noise. The stability check is the defence: it re-fits under three seeds and scores how much the topic word-sets overlap. High agreement means you found structure in the data. Low agreement means you found structure in the random seed, no matter how convincing the words look.

--- key: p5
**A note on speed.** The fit runs at `max_iter=10` rather than the library default of 10× more work per document. On this corpus that halves the wait while topic word-sets still agree with the slower settings at 0.79 Jaccard — a deliberate accuracy-for-latency trade, and exactly the kind of decision worth writing down when you report results.
