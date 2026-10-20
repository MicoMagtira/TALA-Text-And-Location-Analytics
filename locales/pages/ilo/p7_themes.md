--- key: title src: 1e3ffeb078
TF-IDF + K-Means a tema, naidilig kadagiti lugar

--- key: p1 src: 23d3d4d8f2
**Kasano nga agkakadua dagiti paset.** Ti TF-IDF ket mangtimbang iti tunggal term sigun iti kasano kasansan nga agparang daytoy iti maysa a komento maibusor iti kasano kaitit ti panagparang na iti amin a komento, isu a madurog dagiti sao a masarakan iti amin a lugar ken mapapigsa dagiti sao a mangidumduma. Kalpasan na, bunggoyen ti K-Means dagiti komento nga agaasideg iti dayta a natimbangan nga espasio. Ti TF-IDF ti mangikeddeng no ania ti kayat a sawen ti "agpada"; agtulnog laeng ti K-Means. Agusar ti TALA iti unigrams ken bigrams, max_df 0.9, min_df 3 ken 1,200 a features.

--- key: p2 src: e8f66dee7e
**Panagpili iti k babaen ti silhouette.** Para iti tunggal komento, ti a ket ti mean cosine distance-na iti bukodna a tema ken ti b ket ti mean distance-na iti kaasitgan a sabali a tema; s = (b - a) / max(a, b). Ti average ket manipud -1 agingga iti 1. No asideg iti 1, nasayaat ti panagsisina; no asideg iti 0, agsasampaw dagiti tema. Iti daytoy a data, nababa dagiti score (agarup 0.05 iti k = 4 ken 0.08 iti k = 8) gapu ta ababa dagiti komento ken agpada ti vocabulary-da. Ti nangatngato a score para iti dakdakkel a k ket saan nga automatiko a nasaysayaat: isaludsod no dagiti card ket mabasa kas naisangsangayan a tema a mabalin a nagananan.

--- key: p3 src: c6c4891f57
**Ti palab-og ti nagan ti probinsia (pudno latta).** No mabati dagiti nagan ti lugar, ti k = 4 ket mangpataud iti tema a 1,131 a komento a dagiti kangrunaan a term-na ket *del*, *del norte*, *del sur*, *norte*, *sur*, *surigao*. Geography dayta, saan a tema: saan a gagangay dagiti nagan ti probinsia, isu nga iniskor ida ti IDF kas naisangsangayan. Gapu iti dayta, ilemmeng ti TALA dagiti nagan ti lugar a kas default, ket marunaw ti geographic a tema kadagiti tema ti linaon (panaguray, staff, rural health units, kadawyan a kapadasan). Ikkaten ti check iti kahon tapno makita mo a mismo ti palab-og, ken ibaga iti write-up-mo nga inikkat mo dagiti nagan ti lugar.

--- key: p4 src: 8563de396e
**Bingay ti tema iti tunggal lugar.** Ipakita ti stacked bar, iti uneg ti tunggal lugar, no mano a porsiento dagiti komento ti maibilang iti tunggal tema (100% ti dagup ti tunggal row). Gapu ta agpada ti vocabulary dagiti tema, agpapada dagiti bingay kadagiti lugar ditoy. Dagiti auto-label ket naggapu iti rank-weighted a panagtutunos dagiti kangrunaan a term ken ti aspect lexicon; kanayon nga idilig dagitoy iti listaan dagiti term.
