--- key: title
DBSCAN & the k-distance elbow (Lab 2)

--- key: p1
The important difference from k-means: **DBSCAN is never told how many clusters to find.** You describe what "dense" means and it reports however many dense regions exist — possibly zero. It is also the only method here allowed to say *this point belongs to nothing*, labelling it noise (`cluster_id = -1`). For scattered real-world events that honesty is the whole appeal.

--- key: p2
**Two parameters, one definition.** `eps` is a radius in metres and `min_samples` a count. Together they define density: a point is a core point if at least `min_samples` neighbours fall within `eps`. Clusters grow by chaining core points together. Because `eps` is a real distance, this only works on the projected metre-based layer from Lab 1 — run it on raw degrees and `eps=15000` means 15,000 degrees, which is nonsense the code will happily compute.

--- key: p3
**Reading the k-distance curve above.** Each point's distance to its k-th nearest neighbour, sorted ascending. The flat stretch is points sitting in dense company; the upward sweep at the right is increasingly isolated points. The knee between them is where "nearby" stops meaning much — a defensible starting `eps`. On this data the 10th-neighbour distance is 7.8 km at the median but 60.1 km at the 90th percentile, and that steep tail is exactly the knee you are looking for.

--- key: p4
**How sensitive this is.** Holding `min_samples=10` and moving only `eps`:

--- key: p5
- `eps = 5 km` → **109 clusters, 7,241 noise** (fragmented; most data discarded)
- `eps = 15 km` → **29 clusters, 2,199 noise** (the lab default)
- `eps = 40 km` → **17 clusters, 1,290 noise** (merging distinct cities)

--- key: p6
Same data, same algorithm, three different stories. Nothing in the output says which is right — that judgement is yours, and it is what you must defend.

--- key: p7
**What a cluster is not.** It is a region that met *your* density threshold. It is not a community, a catchment, or an outbreak. And noise is not error: an isolated point may be the most important case in the dataset.
