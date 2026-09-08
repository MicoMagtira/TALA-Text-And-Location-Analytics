--- key: title
Land clipping & the output contract (Lab 4)

--- key: p1
Here is the number that should stop you: clipping removes **3,467 of 11,715 points**. Nearly a third of this dataset was never in the Philippines, and it survived every previous page. Lab 1's bounds check passed them because London and California are valid coordinates. DBSCAN clustered them. The maps you have already looked at all included them.

--- key: p2
**Nothing warned you.** That is the lesson of this page, and the reason the dirty coordinates were left in this long on purpose. Bad spatial data does not announce itself; it produces confident, attractive, wrong output at every intermediate step.

--- key: p3
**Polygon, not bounding box.** A rectangle around the Philippines would also catch chunks of Malaysia, Taiwan and open sea. Clipping to the actual land geometry is a *principled* filter — a point is kept because it falls on the country, not because it falls in a convenient rectangle. The polygon is buffered ~15 km so a coarse coastline does not discard legitimate seaside facilities; without that buffer you silently lose real coastal data, which is its own quiet failure.

--- key: p4
**The output contract.** Exports pair the GeoJSON with a `metadata.json` recording CRS, the clipping decision and counts, DBSCAN parameters and the generalization method. This is what makes the work reproducible: someone receiving your layer should never have to guess whether coordinates are lon/lat or projected, or whether 3,467 records were dropped. A layer without that metadata is not a finished deliverable.

--- key: p5
**Before you publish.** Prefer the aggregated layers from Lab 3 over raw points. A map is a rhetorical object — readers grant it more authority than a table, so state your filtering choices *on the map itself*, and never let a point pattern imply a cause it cannot support.
