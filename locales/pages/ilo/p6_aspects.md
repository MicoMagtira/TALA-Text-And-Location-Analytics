--- key: title src: e5da2baa99
Aspect sentiment babaen ti lexicon

--- key: p1 src: ba7c854479
**Ti ideya.** Ti pakabuklan a sentiment ket mangilemmeng no ania ti saan a pakapnekan dagiti tattao. Ti aspect sentiment ket bingayen na ti tunggal komento kadagiti sentence, taginayonen na dagiti sentence a mangdakamat iti aspect (panaguray, staff, gastos, agas, pasilidad, pannakadanon) ken dagitoy laeng ti iskoren ti VADER. Mabalin a mabilang ti maysa a sentence para iti adu nga aspect. Ti porsiento iti tunggal cell ket ti paset dagita a sentence a negatibo ti score; ti n ket bilang dagiti sentence, saan a komento.

--- key: p2 src: 30f89eefe1
**Ti lexicon.** Dagiti term ket adda iti data/aspects.json, English ken Filipino. Dagiti English a sao ket agtunos kas buo a sao nga addaan simple nga ending (wait, waited, waiting); dagiti Filipino a root ket agtunos met kalpasan ti ababa nga affix (hintay iti uneg ti naghintay). Nalawag, napardas ken nalaka a nayonan, isu a maitutop daytoy iti panagisuro.

--- key: p3 src: 045145260f
**Ania ti masarakan na.** Iti intero a bundled a data, ti panaguray ti kaaduan unay a mareklamo nga aspect: agarup 48% dagiti sentence maipapan iti panaguray ti negatibo, maibusor iti agarup 24% para iti staff ken pasilidad, 28% para iti agas, 29% para iti pannakadanon ken 32% para iti gastos. Ti kanegatibuan a cell ket Mimaropa iti panaguray (58%, n = 213). Bassit ti sentence ti gastos iti tunggal lugar (masansan a baba ti 60), isu a noisy dagiti cell-na ken ilemmeng ti minimum-sentences slider dagiti kakuttongan.

--- key: p4 src: 84747d3d7c
**Dagiti limitasion.** Ti lexicon ket agpares iti sao, saan nga iti kaipapanan: ti "line" ket agtunos met iti "the line moved fast", ken saan na a makita ti paraphrase ("two hours of my day") ken sarcasm. Ti sentence a mangdakamat iti dua nga aspect ket mangted iti isu met laeng a score kadagiti dua. Ti supervised wenno zero-shot a model ket nasaysayaat iti kaipapanan ngem narigrigat a sukimaten. Tapno ma-validate, basaen ti sample dagiti nagtunos a sentence ken bilangen no mano ti husto (precision), sa birukem dagiti sentence a rumbeng koma a nagtunos ngem saan (recall).
