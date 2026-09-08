--- key: title src: d1849dc686
Ti preprocessing pipeline (manipud iti NLP.ipynb)

--- key: p1 src: 0772da8ad5
Iti preprocessing ti pangikeddengam no ania ti palubosam a makita ti computer. Adda punctuation, dadakkel a letra, filler words, emoji, numero, typo ken naglaok a pagsasao iti raw text. Ti dadduma kadagita ket signal ket ti dadduma ket ariwawa, ket *ti no ania ti ania ket agpannuray talaga iti saludsodmo iti panagsukisok.* Saan a ritual ti panagdalus ti preprocessing — desision daytoy iti panagsukisok a masapul a kabaelam nga ikanawa.

--- key: p2 src: 59f67efe58
**Daytoy ti ar-aramiden ti pipeline, sagsaganad.** Lowercase → ikkaten dagiti URLs → ikkaten dagiti `@mentions` ken `#hashtags` → ikkaten ti punctuation (Unicode-aware, isu a kabaelanna dagiti kulot a panipi) → ikkaten dagiti numero → pagtiponen ti espasio → biangen iti espasio → ikkaten dagiti tokens nga awan pay 3 a letrana → ikkaten dagiti stopwords.

--- key: p3 src: 6b6f3058ba
**Daytoy ti bayadna iti daytoy a corpus.** Ti 292,674 a raw a sao ket agbalin a 174,562 a tokens — 40% ti text ti ibelbellengmo. Ti nabatbati a bokabulario ket 551 a nagdumaan a sao. Dakkel dayta a bassit, ket dayta mismo ti punto: ti nabati ket rumbeng a ti paset a maikari a bilangen.

--- key: p4 src: ab9dc72244
**Ti desision kadagiti stopwords.** Dagiti 318 nga English stopwords ket manipud iti standard a listaan ti scikit-learn; dagiti 147 a Filipino stopwords (`ang`, `sa`, `mga`, `naman`) ket sabali a naikapet ken ma-toggle iti sidebar. Iddepem ti Filipino list sa patarayem manen ti aniaman a page — agluppias dagiti Tagalog function word iti ngato ti tunggal frequency chart, ket dayta mismo ti mapaspasamak no English-only a tools ti usarem iti Taglish a data.

--- key: p5 src: 0a2726eb69
**Ditoy ka masaktan ti defaults.** Ikkaten ti pagannurotan iti numero ti `24/7`, `3 hours` ken `P500`. Ikkaten ti pagannurotan iti punctuation ti `!` iti "three hours again!" — no unget ti ad-adalem, kaikkatmo laeng iti unget. Ikkaten ti 3-letra a minimum ti `ER`, `OB` ken `IV`. Awan ti biddut iti daytoy iti sapasap, ket mabalin nga amin daytoy ket biddut para kenka.

--- key: p6 src: 3e1be010df
**Aramidem daytoy sakbay nga agtuloyka.** Basaem dagiti agparis a raw ken cleaned iti baba. No ti komento a matarusam ket agbalin a komento a saanmon a matarusan, isublim iti sabali a bangir dagiti napukaw a sao iti custom stopword box ti sidebar — kayatna a sawen, panunotem manen ti pagannurotan, saan ket a ti pagarigan.
