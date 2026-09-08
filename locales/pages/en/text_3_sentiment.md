--- key: title
How VADER scores sentiment

--- key: p1
Sentiment analysis asks what emotional weather a text seems to carry. Some comments are sunny, some stormy, most are cloudy — and weather reports are least reliable in unfamiliar places. This corpus is an unfamiliar place for VADER.

--- key: p2
**How the score is produced.** VADER is a rule-and-lexicon model, not a trained classifier. Each word carries a hand-assigned valence, then rules adjust the total: `ALL CAPS` intensifies, `!!!` intensifies, `very` boosts, `not` flips. The result is a compound score from -1 to +1, cut into labels at ±0.05 by default. Because those rules read punctuation and capitalization, **VADER runs on the raw comment, not the cleaned tokens** — this is the one page where preprocessing does not apply.

--- key: p3
**Read the distribution, not just the headline.** This corpus scores 47% positive, 36% negative, 17% neutral. But the mean compound is +0.115 while the *median is exactly 0.000* — more than a sixth of comments land on precisely zero, meaning VADER found no lexicon words it recognised at all. A flat zero is not neutrality; it is silence. Move the threshold slider and watch how much of the neutral band is genuinely mixed versus simply unscored.

--- key: p4
**Where it will be wrong here, specifically.** Sarcasm inverts cleanly and VADER cannot see it — "Great, I waited three hours again" scores positive on `Great`. Clinical vocabulary collides with emotional vocabulary: a `positive` test result is bad news, `critical` is a severity not a complaint, and `discharged` is usually relief. Taglish is largely invisible to an English lexicon, so a fluent Filipino complaint may score 0.000 and land in your neutral bucket. And politeness softens dissatisfaction, which biases the whole distribution upward.

--- key: p5
**So treat this as triage, never as a label.** The right workflow is: read the distribution, sort to the extremes, open the actual comments, and decide whether the tool is behaving sensibly *on your data*. Report the percentage only alongside what you found when you checked.
