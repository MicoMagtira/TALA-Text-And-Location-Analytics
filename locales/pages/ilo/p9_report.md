--- key: title src: 931679624d
Generalization, privacy ken dagiti report card

--- key: p1 src: 3a6975005f
**Apay a masapul ti generalization.** Ti point iti mapa ket mabalin a mangilasin iti maysa a tao uray awan dagiti saona, nangnangruna kadagiti lugar a bassit ti tao. Ti panag-generalize ket mangsukat kadagiti point iti aggregate: kuadrado a grid cell wenno maysa a centroid iti tunggal lugar. Ilemmeng ti slider ti aniaman a cell wenno lugar nga addaan basbassit a komento ngem k, sigun iti espiritu ti k-anonymity: awan ti marker a mangibagi iti basbassit ngem k a tao. Simple a suppression rule daytoy, saan a garantia; ti panagtipon iti adu a release, wenno bassit a k a nakadua ti data manipud iti ruar, ket mabalin latta a mangiparuar iti impormasion, isu a pilien ti k a kadua ti data owner-mo.

--- key: p2 src: ecbfb4d967
**Grid wenno centroids.** Dagiti cell nga addaan fixed a kadakkel (nakwenta iti UTM a metro) ket mangtaginayon iti spatial a detalye ken ipakita na laeng dagiti cell nga addaan komento; dagiti centroid ket mangpabassit iti tunggal lugar iti maysa a disc iti gazetteer centre-na (rehion) wenno iti mean dagiti kamengna (cluster). Dagiti dakdakkel a cell ken dakdakkel a k ket mangted iti ad-adu a privacy ken basbassit a detalye.

--- key: p3 src: 8f321a7e8f
**Dagiti report card.** Tunggal card ket mangtipon kadagiti resulta ti Kapitulo 2 para iti maysa a lugar: naisangsangayan a sao (log-odds maibusor kadagiti amin a sabali a lugar, nailemmeng dagiti nagan ti lugar, saan a basbassit ngem 10 a pannakadakamat), % negatibo agraman ti Wilson interval-na, ti kaaduan a mareklamo nga aspect (saan a basbassit ngem 15 a sentence), ti kangrunaan a tema (k = 4) ken hotspot flag. Mamarkaan ti lugar no saan a basbassit ngem 30% dagiti komentona ti adda kadagiti cell a hot iti 95% wenno 99% sigun kadagiti setting-mo iti addang 8 (default no linaktawam daytoy). Ti flag ket rule of thumb, saan a test.

--- key: p4 src: 77c64a582a
**Dagiti export.** Ti GeoJSON ket aglaon laeng kadagiti generalized a feature (bilang ken % negatibo), ti CSV ket addaan maysa a row iti tunggal lugar, ken ti metadata.json ket mangirekord no kasano a naaramid ti amin: generalization, dagiti setting ti DBSCAN, unit ti lugar, paggapuan ti lokasion, text-vs-GPS threshold, minimum a kadakkel ti grupo, sentiment method, ken dagiti setting ti hotspot ken tema. Ginagara nga English dagiti field name aniaman ti pagsasao ti interface, tapno agtalinaed a compatible dagiti maibingay a worksheet. Saan a pulos a ma-export ti text ti komento.
