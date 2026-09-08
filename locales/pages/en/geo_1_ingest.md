--- key: title
CRS validation & reprojection (Lab 1)

--- key: p1
Two numbers in a spreadsheet are not yet a location. This lab turns `lon`/`lat` columns into geometry a computer can measure with, and every later page depends on getting it right here.

--- key: p2
**The validation gate.** 12,000 input rows lose 29 to missing coordinates and 256 to values outside the valid ranges (longitude ±180, latitude ±90), leaving 11,715 points. Note what that gate does *not* catch: a comment about Cebu carrying London's coordinates is perfectly valid as a number and survives untouched. Bounds checking proves a coordinate is well-formed, never that it is correct.

--- key: p3
**`set_crs` versus `to_crs` — the classic error.** `set_crs` *declares* what your numbers already mean; `to_crs` *converts* them to a different system. Calling `set_crs` when you meant `to_crs` silently relabels your data instead of moving it, and nothing errors — the points simply land in the wrong place on every subsequent map. If a layer looks shifted, suspect this first.

--- key: p4
**Why the reprojection is not optional.** EPSG:4326 measures in degrees, and a degree of longitude is ~111 km at the equator but shrinks toward the poles, so degree distances are not comparable across a map. DBSCAN's `eps` on the next page is a *distance*, so the data must first move to a metre-based CRS — here **EPSG:32651** (UTM zone 51N), chosen automatically from the median longitude.

--- key: p5
**Read the nearest-neighbour check as a diagnostic.** Median 2.3 km is sensible for health facilities. The two extremes are the interesting part: **minimum 0 m** means at least two points share identical coordinates — duplicates, or several comments rounded to the same facility — which will inflate density for DBSCAN. **Maximum 175 km** is the far-flung junk announcing itself before any map is drawn.

--- key: p6
**On privacy.** From this point you hold precise locations attached to personal accounts of medical visits. That combination is re-identifying. Everything you share from here should be aggregated — which is what Labs 3 and 5 build.
