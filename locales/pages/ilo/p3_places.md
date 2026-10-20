--- key: title src: c443695e58
Dagiti lugar: manipud iti points agingga kadagiti rehion ken cluster

--- key: p1 src: 9e04298220
**Apay a masapul ti panagbunggoy.** Ti maysa a komento ket anekdota; ti lugar ket sample. Idilig ti Kapitulo 2 no ania ti ibagbaga dagiti lugar, isu a masapul nga umuna nga addaan label ti lugar ti tunggal komento. Adda dua a wagas tapno makaala iti daytoy, ken nagduma a saludsod ti sungbatan da.

--- key: p2 src: f1707fe2eb
**Rehion: usaren ti insurat dagiti tattao.** Ti tunggal komento ket maikabil iti rehion ti lugar a nadakamat iti daytoy (manipud iti gazetteer). Ti komento nga awan ti mausar a nagan ket maikabil iti rehion nga addaan iti kaasitgan a centroid iti nailokasion a point-na. Nalaka a basaen, natibker, ken awan ti parameter a kasapulan na, ngem administratibo dagiti rehion: mabalin a nakadumduma unay ti kadakkel ken populasionda, ken ti rehion ket naiguhit ditoy kas bubble iti centroid-na, saan a kas beddeng.

--- key: p3 src: 97233bbec5
**Cluster: ti density ti mangikeddeng.** Ti DBSCAN ket mangpadakkel iti cluster manipud iti aniaman a point nga addaan iti saan a basbassit ngem *min_samples* a kaarruba iti uneg ti *eps*, ken markaan na a noise dagiti point a saan a kameng ti aniaman a napuskol a paset. Saan na a kasapulan nga ammuen nga umuna ti bilang dagiti cluster, ken saan na a pilitan nga iserrek ti tunggal point iti grupo. Napateg dagiti dua a knob: ti bassit nga eps ket mangbingbingay iti maysa a siudad iti adu a cluster, ti dakkel ket mangtipon kadagiti agkaarruba a siudad iti maysa a dakkel a bunggoy.

--- key: p4 src: 8655589831
**Projected a metro, saan a degree.** Kaadayo ti eps ti DBSCAN, isu nga umuna a mai-project ti coordinates iti UTM a metro. Ti maysa a degree ti longitude ket ab-ababa ngem ti maysa a degree ti latitude no adayo iti equator, isu a no patarayen ti DBSCAN iti gubsang a degree, ellipse ti maiguhit na, saan a circle.

--- key: p5 src: 6a40392629
**Ti k-distance elbow.** Para iti tunggal point, alaen ti kaadayo iti maika-k a kaasitgan a kaarrubana ken iurnos dagita a kaadayo. Kaaduan kadagiti point ket adda kadagiti napuskol a paset ken babassit ti value-da; dadakkel ti value dagiti naisina (stragglers), isu a dagus nga agpangato ti curve iti beddeng. Ti nasayaat nga eps ket asideg iti dayta a siko (elbow). Ikabil ti k nga asideg iti min_samples. Giya ti elbow, saan a pammaneknek: kitaen ti mapa ken siguraduen nga agtunos dagiti cluster kadagiti lugar a mabigbig mo.

--- key: p6 src: dbab5c1879
**Resulta ti noise.** Saan a biddut dagiti point a saan nga inkabil ti DBSCAN iti cluster. Dagiti komento iti away a naiwarawara iti nagbaetan dagiti ili ket masansan a noise, ket pudno daytoy: saan da a kameng ti napuskol a lugar. Iti Rehion a mode, dagiti komento laeng nga awan pulos ti lokasion ti awan ti lugar.

--- key: p7 src: fc3b88474e
**Dagiti natarimaan a point ket adda iti centroid ti ili.** No nangdakamat ti komento iti lugar ngem biddut ti GPS-na, ti natarimaan a point ket maikabil a mismo iti centroid dayta a lugar. Iti Cluster mode, ti DBSCAN kadagiti natarimaan a point ket kadawyan a mangbukel iti maysa a cluster iti tunggal nadakamat nga ili, ken kasla patag ti k-distance curve gapu ta adu a point ti agbingay iti isu met laeng a coordinates. Ti "No agtunos laeng ti dua" ket mangtaginayon kadagiti GPS-only a point, isu nga usaren daytoy kas view a pagidiligan.
