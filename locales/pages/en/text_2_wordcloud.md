--- key: title
Frequencies & word clouds

--- key: p1
Counting words is the simplest thing you can do to a corpus, which makes it the easiest place to fool yourself. This page gives you the same counts twice, on purpose.

--- key: p2
**Read the bar chart, look at the cloud.** A word cloud encodes frequency as area, and human eyes are unreliable at comparing areas — a word twice as frequent does not look twice as big, and long words look more important than short ones simply because they occupy more pixels. `hospital` will always out-loom `staff` at equal counts. Use the cloud to notice *what is present*; use the bar chart whenever you need to say *how much*.

--- key: p3
**What the top of this corpus looks like.** `staff` (3,467), `felt` (2,765), `health` (2,612), `hospital` (2,586), `update` (2,493). Two of those five should make you suspicious. `update` and `felt` are not health-service concepts — they are artefacts of how these comments were phrased ("Manila visit update:…", "Felt smooth…"). Frequency found the template, not the topic.

--- key: p4
**That is the real lesson.** A word can be common because many people independently said it, or because one survey prompt put it in their mouths. Frequency cannot tell those apart. Only reading examples can, which is why the sample comments sit next to the chart. If a term is boilerplate, add it to the sidebar's custom stopwords and recount — a legitimate, documentable analytical move.

--- key: p5
**On the emotion clouds.** The positive/negative split uses the NRC lexicon, an English word-emotion dictionary. It matches word-by-word with no notion of context or negation, so "not kind" contributes `kind` to the positive cloud. Filipino terms are largely invisible to it. Treat the split as a rough sorting of English vocabulary, not as a measurement of how people felt — the Sentiment page handles that question with better tools, and still imperfectly.
