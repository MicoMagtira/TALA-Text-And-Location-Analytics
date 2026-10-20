--- key: title
Places: from points to regions and clusters

--- key: p1
**Why group at all.** One comment is an anecdote; a place is a sample. Chapter 2 compares what places say, so every comment needs a place label first. There are two ways to get one, and they answer different questions.

--- key: p2
**Region: use what people wrote.** Each comment takes the region of the place it names (from the gazetteer). A comment with no usable name takes the nearest region centroid to its located point. It is readable, stable and needs no parameters, but regions are administrative: they can be very unequal in size and population, and a region is drawn here as a bubble at its centroid, not as a boundary.

--- key: p3
**Cluster: let density decide.** DBSCAN grows a cluster from any point that has at least *min_samples* neighbours within *eps*, and labels points that belong to no dense region as noise. It needs no number of clusters in advance and does not force every point into a group. Both knobs matter: a small eps splinters one city into many clusters, a large one merges neighbouring cities into one blob.

--- key: p4
**Projected metres, not degrees.** DBSCAN's eps is a distance, so coordinates are first projected into UTM metres. A degree of longitude is shorter than a degree of latitude away from the equator, so running DBSCAN on raw degrees would draw ellipses, not circles.

--- key: p5
**The k-distance elbow.** For each point take the distance to its k-th nearest neighbour and sort those distances. Most points sit in dense areas and have small values; stragglers have large ones, so the curve bends sharply upward at the boundary. A good eps is near that elbow. Set k close to min_samples. The elbow is a guide, not a proof: look at the map and check that the clusters correspond to places you recognise.

--- key: p6
**Noise is a result.** Points DBSCAN leaves unassigned are not an error. Rural comments scattered between towns will often be noise, which is honest: they do not belong to a dense place. In Region mode only comments with no location at all are unassigned.
