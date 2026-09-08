--- key: title
N-grams & co-occurrence

--- key: p1
You know how you and a close friend finish each other's sentences? That happens because you have heard enough examples to know which words tend to arrive together. N-grams do the same thing to a dataset: they ask which words keep arriving together. A unigram is `test`; a bigram is `lab test`; a trigram is `rapid antigen test`. Each step adds context that the single word could not carry.

--- key: p2
**What the phrases recover here.** The trigrams surface real Philippine health infrastructure that unigrams shredded into pieces: `barangay health center` (1,037), `rural health unit` (1,023), `blood pressure monitoring` (928). As separate words, `barangay`, `health` and `center` are nearly meaningless — as a phrase they name a specific tier of the health system. This is the clearest argument for looking past word counts.

--- key: p3
**Now look at what else is up there.** `staff felt` (1,327), `took forever` (1,327), `forever staff` (1,327). Three different phrases with *identical* counts is not a coincidence — it is the signature of a template. One sentence pattern ("…took forever. Staff felt…") is being counted three times as it slides across the window. The n-gram is measuring the survey's phrasing, not the respondents' experience.

--- key: p4
**Learn to spot that.** Identical counts across overlapping phrases, or a trigram whose count equals its parent bigram's, almost always means boilerplate. The fix is not statistical — open the comments, confirm the pattern, and either add the filler to your custom stopwords or report the phrase as an artefact.

--- key: p5
**On the network.** Edges are co-occurrence, so a line between two words means "these appeared adjacently, often." It is a map of repeated associations. It is not causal, not directional, and a thick edge between `waited` and `hours` tells you people wrote that phrase — not that waiting caused anything. Start at bigrams with a low `min_df`, and raise the threshold only after you have confirmed the rare phrases are genuinely noise rather than a small but real subgroup.
