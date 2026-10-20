--- key: title
Text vs GPS: reading the place, checking the coordinates

--- key: p1
**Two witnesses for one location.** Each comment carries a GPS point and, usually, a place name in its own words. Neither is trustworthy alone: GPS can be missing, swapped or default to a device's last fix, and people can mistype a town. This step compares them. When they agree we are confident; when they disagree one of them is wrong, and the pattern of disagreement tells us which.

--- key: p2
**Geoparsing by rules, not by a model.** The parser scans each comment for the longest run of up to four tokens that matches a name or alias in a bundled gazetteer of regions, provinces, cities and municipalities (GeoNames, CC BY 4.0). Because the vocabulary is closed and the comments are consistently capitalised, a rule-based matcher is deterministic, fast and explainable in one paragraph, which a statistical named-entity model is not. Longest match matters: "Cagayan de Oro" must win over "Cagayan", and "Davao de Oro" over "Davao". Words after *Brgy*, *Purok* or *Sitio* are skipped, because those name a barangay, not a municipality.

--- key: p3
**Ambiguity and how it is resolved.** "San Fernando" names several places. The parser first looks for a co-mentioned province or region in the same comment ("San Fernando, Pampanga"). Failing that it lets a clearly dominant name win by population (Bacolod the city is at least 1.5 times bigger than any namesake), except for saint names, which are never settled that way. What is still undecided is marked *ambiguous* and kept out of the comparison rather than guessed.

--- key: p4
**Distance, and why the threshold matters.** GPS and the named place are compared with the haversine great-circle distance on a sphere of radius 6371 km. A comment *agrees* when that distance is within the threshold. A place is a point (its gazetteer centroid), but a province can be 100 km across, so a tight threshold flags comments that were fine and a loose one forgives real errors. Move the slider and watch the disagree count change: the number is a property of your threshold, not of the data alone.

--- key: p5
**The trap in this dataset.** About 31% of the bundled coordinates are invalid: they fall outside the Philippines entirely (the first row names Cagayan de Oro but sits near London). Another 8% are valid points far from the place named. Together that is roughly four coordinates in ten. A map drawn straight from the GPS column would look plausible and be badly wrong. Status order is deliberate: an invalid GPS is reported as invalid even if text is also present, because it needs repair whatever the text says.

--- key: p6
**Choosing what the next steps use.** *Repair from the text* keeps the GPS when it is valid and agrees (or no place is named) and otherwise substitutes the named place's coordinates. *GPS only* keeps only valid points on Philippine land. *Only where both agree* is the strictest and smallest sample. Repair gains coverage at the price of snapping a comment to a place centroid, which is why a repaired point is a place, not a street address.
