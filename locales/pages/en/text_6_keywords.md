--- key: title
RAKE, POS tagging & co-occurrence

--- key: p1
Three tabs, three genuinely different questions — worth keeping straight, because they fail in different ways.

--- key: p2
**RAKE: which phrases stand out?** Rapid Automatic Keyword Extraction splits text at stopwords and punctuation, treats each surviving run as a candidate phrase, and scores it by word *degree* divided by word *frequency*. That ratio rewards words appearing in longer phrases rather than words appearing often — which is why RAKE surfaces specific multi-word terms that raw counting buries. The side effect: a phrase said once, if distinctive, can outrank one said five hundred times. RAKE ranks distinctiveness, never importance.

--- key: p3
**POS tagging: which words are things?** The tagger labels every token, letting us split common nouns (what people discuss) from proper nouns (where and who). The top common nouns here are `health` (975), `hospital` (736), `process` (702) and `update` (684) — note that filtering to nouns did *not* rescue us from the template wording the frequency page flagged, since `process` and `update` are perfectly good nouns. Grammar is not relevance. Proper nouns fare better, recovering the geography the coordinates also encode — `Brgy`, `Davao`, `Norte`, `Sur`, `Zamboanga` — a useful cross-check that the text and the map describe the same country.

--- key: p4
**Why proper nouns are hard.** Capitalisation is the tagger's strongest clue, and the first word of every sentence is capitalised too. Raw output ranked `Tried` and `Felt` among the top "names" in this corpus. The page filters them out by keeping only capitalised words that *also* appear mid-sentence somewhere — worth knowing, because the same trap catches anyone tagging survey text. And the tagger is trained on English newswire, so Filipino and Taglish tokens get unreliable tags.

--- key: p5
**Co-occurrence: which terms travel together?** The heatmap counts how often two terms appear in the same comment, binary per document, so one comment saying `staff` twenty times contributes once. Bright cells mark concepts discussed together. They do not mark cause: `waited` and `staff` co-occurring tells you people raised both, not that staffing caused the wait. Use all three tabs to generate questions, then answer them by reading comments.
