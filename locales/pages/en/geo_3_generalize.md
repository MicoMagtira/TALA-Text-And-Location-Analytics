--- key: title
Generalization: grid vs centroids (Lab 3)

--- key: p1
Generalization is the step where you *deliberately destroy precision*. That sounds like damage, and it is — chosen on purpose, because a map of exact coordinates attached to medical complaints is both harder to read and unsafe to publish. The question is not whether to lose detail but which detail you can afford to lose.

--- key: p2
**Grid aggregation** lays equal metre-based squares over the projected points and counts what falls in each. Every location becomes "somewhere in this cell". The number of populated cells, the largest count, and the median count should change as you adjust the cell size; compare those values to see the resolution–privacy trade-off rather than relying on one default.

--- key: p3
**Cluster centroids** replace each DBSCAN cluster with one representative point carrying the member count, giving **29 markers** instead of 11,715. Far cleaner, but it inherits every parameter choice from the previous page — change `eps` and your centroids move.

--- key: p4
**Choosing between them.** Grids answer "where is activity concentrated?" and cover everywhere, including sparse areas. Centroids answer "where are the dense groups we identified?" and are silent about everything DBSCAN called noise. Grids impose an arbitrary lattice that can split one real hotspot across four cells; centroids place a marker at a mean position where possibly nobody was — a centroid can land in the sea.

--- key: p5
**Cell size is a privacy control, not just a visual one.** Shrink the cells and counts drop until a cell contains one person at a known address. A common rule is to suppress or merge any cell below a minimum count (often 5). Use the slider and watch the median count fall — that is your privacy budget being spent.

--- key: p6
**The question to carry forward:** what does this representation hide, and is that the detail I intended to remove?
