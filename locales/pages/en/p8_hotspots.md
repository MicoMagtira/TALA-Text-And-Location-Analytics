--- key: title
Getis-Ord Gi* hotspots

--- key: p1
**The question.** Some clusters of negative comments are just chance. Gi* asks whether a cell and its neighbours together are more (hot) or less (cold) negative than random shuffling of the same values would give. TALA bins comments into square cells, sets each cell's value x to its share of negative comments (cells with fewer comments than the minimum are dropped), and computes Gi* on those cells.

--- key: p2
**The formula.** With n cells, mean X-bar and standard deviation S of x, and binary weights w_ij = 1 when cell j is within the radius of cell i (i included): Gi*_i = (sum_j w_ij x_j - X-bar * W_i) / (S * sqrt((n * sum_j w_ij^2 - W_i^2) / (n - 1))), where W_i = sum_j w_ij. The result is already a z-score: values at or above 1.645, 1.960 and 2.576 are hot at 90%, 95% and 99% confidence (the negatives are cold). Neighbours come from a BallTree on metric (UTM) coordinates.

--- key: p3
**Multiple testing.** One test at 95% is wrong 5% of the time, but here every cell is tested, so some cells look "significant" by luck even with no pattern. That is why the 99% class is the safest reading and 90% cells deserve scepticism. On the bundled data with the defaults (20 km cells, 50 km radius, at least 10 comments) 309 cells are tested; 4 are hot (none at 99%) and 7 cold. The strongest hot cell (z = 2.4, 50% negative in 10 comments) lies near Apayao. Only about 3.6% of cells are significant in either direction, fewer than the 10% chance alone would give at the 90% level, so this dataset shows no convincing complaint clusters overall. That is a legitimate finding.

--- key: p4
**Choices matter.** The radius should span at least two cells or each cell is hardly compared with neighbours. Larger cells are steadier but blur local detail (the modifiable areal unit problem). Choosing "waiting" restricts the map to comments mentioning waiting and counts a comment as negative when its matching sentences read negative. Binary weights treat all neighbours equally; inverse-distance weights are a common alternative.
