--- key: title src: c6025acb69
Kasano nga agsilpo ti dua a track

--- key: p1 src: 1517eeab2a
Kaaduan kadagiti analytics tools ket sumungbat laeng iti maysa: *ania ti ibagbaga dagiti tattao* wenno *sadino ti pagpaspasamakanna*. Naaramid ti TALA tapno ipakita no apay a nakapkapsut dagita a dua a saludsod no agsina. Maysa a dataset a 12,000 a komento maipapan iti health services ti addaan `text` column ken addaan met `lon`/`lat`, ket ti tunggal page ket sabali a wagas ti panagbasa iti isu met laeng a 12,000 rows.

--- key: p2 src: e5bd9874b9
**Apay a napateg ti panagparis.** Ti text laeng ibagana kenka a 1,448 a komento ti nangdakamat iti oras ti panaguray, ngem saanna nga ibaga no maysa laeng a pasilidad a napno unay wenno pattern iti intero a pagilian. Ti location laeng ipakitana ti napuskol a cluster a 1,750 a points, ngem saanna nga ibaga a ti pagsasaritaan iti unegna ket kababalin ti staff saan ket a suplay ti agas. Ti maudi a geospatial page ti mangsilpo iti dua: keywords ken sentiment a nakwenta *iti kada cluster* — maysa a banag a saan a kabaelan nga ibaga ti uray ania kadagiti dua a track no agmaymaysa.

--- key: p3 src: d699ee1c44
**Dua a nagdumaan a porma ti trabaho.** Dagiti walo a text pages ket agsisina a lente — luktam iti aniaman nga urnos. Dagiti lima a geospatial pages ket maysa a *pipeline*, a ti tunggal addang ket agusar iti naggapuan iti immuna:

--- key: p4 src: 296c22204c
`Ingest → DBSCAN → Generalization → NLP iti kada cluster → Mapa ken exports`

--- key: p5 src: af3bbf8f25
Saan laeng daytoy nga urnos ti UI. Saan a marukod ti kaadayo agingga a saan a na-validate ken na-project ti coordinates; awan ti masarakan a cluster no awan ti kaadayo; kasapulan ti per-cluster text dagiti clusters tapno adda pagbatayan ti panaggrupo. No aglaktawka, adda latta rumuar a numero — saanmo laeng a kabaelan nga ikanawa.

--- key: p6 src: b97d314425
**Adda ginagara a palab-og ditoy.** Ginagara a narugit ti coordinates a kadua ti dataset — adda sumagmamano a natnag idiay London ken California. Awan ti mangikkat kadagita agingga a saan a dumanon iti land-clip iti maudi a page, a mangikkat iti 3,467 iti 11,715 a points. Aginggana iti apagkatlo ti dataset ket biddut iti wagas nga awan ti error message a mangibaga kenka, ket kasla umno latta ti tunggal mapa iti tengnga. Ti pannakamatikod iti daytoy ti mismo a punto.

--- key: p7 src: 5d07be679f
**Dumanon iti amin a page dagiti kontrol iti sidebar.** Global dagiti palettes, ti toggle para kadagiti Filipino stopwords, ken dagiti bukodmo a stopwords — isu a ti panagbaliw iti maysa a page ket siuulimek a mangsukat iti resulta kadagiti sabali. Isaganam dagitoy a siginagara sakbay a mangidilig kadagiti output.
