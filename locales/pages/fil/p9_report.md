--- key: title src: 931679624d
Generalization, privacy at mga report card

--- key: p1 src: 3a6975005f
**Bakit kailangang mag-generalize.** Puwedeng makilala ang isang tao mula sa isang point sa mapa kahit wala ang mga salita niya, lalo na sa mga lugar na kaunti ang tao. Pinapalitan ng generalization ang mga point ng mga aggregate: mga parisukat na grid cell, o isang centroid kada lugar. Itinatago ng slider ang kahit anong cell o lugar na mas kaunti sa k ang komento, sa diwa ng k-anonymity: walang marker na kumakatawan sa mas kaunti sa k na tao. Simpleng suppression rule ito, hindi garantiya; ang pagsasama-sama ng ilang release, o maliit na k kasama ng data mula sa labas, ay puwede pa ring maglabas ng impormasyon, kaya piliin ang k kasama ng may-ari ng data mo.

--- key: p2 src: ecbfb4d967
**Grid vs centroids.** Ang mga cell na may nakapirming laki (kinukuwenta sa UTM na metro) ay nagpapanatili ng spatial na detalye at ang mga cell lang na may laman ang ipinapakita; ang centroids naman ay ginagawang isang bilog ang bawat lugar sa gitna nito sa gazetteer (para sa mga rehiyon) o sa mean ng mga miyembro nito (para sa mga cluster). Mas malalaking cell at mas malaking k, mas maraming privacy at mas kaunting detalye.

--- key: p3 src: 8f321a7e8f
**Mga report card.** Pinagsasama ng bawat card ang mga resulta ng Chapter 2 para sa isang lugar: natatanging salita (log-odds laban sa lahat ng ibang lugar, nakatago ang mga pangalan ng lugar, hindi bababa sa 10 banggit), % negatibo kasama ang Wilson interval nito, ang pinakainirereklamong aspect (hindi bababa sa 15 pangungusap), ang pangunahing tema (k = 4) at isang hotspot flag. Naka-flag ang isang lugar kapag hindi bababa sa 30% ng mga komento nito ang nasa mga cell na hot sa 95% o 99% ayon sa settings mo sa hakbang 8 (default kung nilaktawan mo ito). Gabay lang ang flag, hindi pormal na test.

--- key: p4 src: 77c64a582a
**Mga export.** Ang GeoJSON ay naglalaman lang ng mga generalized na feature (bilang at % negatibo), ang CSV ay may isang row kada lugar, at itinatala ng metadata.json kung paano ginawa ang lahat: generalization, DBSCAN settings, place unit, pagkukunan ng lokasyon, text-vs-GPS threshold, minimum na laki ng grupo, sentiment method, at settings ng hotspot at tema. Sadyang naka-English ang mga pangalan ng field anuman ang wika ng interface, para manatiling compatible ang mga pinagsasaluhang worksheet. Hindi kailanman ine-export ang text ng kahit anong komento.
