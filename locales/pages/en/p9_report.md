--- key: title
Generalization, privacy and report cards

--- key: p1
**Why generalize.** A point on a map can identify a person even without their words, particularly in sparse areas. Generalizing replaces points with aggregates: either square grid cells or one centroid per place. The slider hides any cell or place with fewer comments than k, in the spirit of k-anonymity: no marker stands for fewer than k people. It is a simple suppression rule, not a guarantee; combining several releases, or a small k with outside data, can still leak information, so choose k with your data owner.

--- key: p2
**Grid vs centroids.** Cells of a fixed size (computed in UTM metres) keep spatial detail and show only occupied cells; centroids reduce each place to one disc at its gazetteer centre (regions) or the mean of its members (clusters). Larger cells and larger k give more privacy and less detail.

--- key: p3
**Report cards.** Each card combines Chapter 2 results for one place: distinctive words (log-odds against all other places, place names hidden, at least 10 mentions), % negative with its Wilson interval, the most faulted aspect (at least 15 sentences), the main theme (k = 4) and a hotspot flag. A place is flagged when at least 30% of its comments sit in cells that are hot at 95% or 99% under your step-8 settings (defaults if you skipped it). The flag is a rule of thumb, not a test.

--- key: p4
**Exports.** GeoJSON holds only the generalized features (counts and % negative), the CSV has one row per place, and metadata.json records how everything was made: generalization, DBSCAN settings, place unit, location source, text-vs-GPS threshold, minimum group size, sentiment method, hotspot and theme settings. Field names are deliberately in English whatever the interface language, so shared worksheets stay compatible. No comment text is ever exported.
