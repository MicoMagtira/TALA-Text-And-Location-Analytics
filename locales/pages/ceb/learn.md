--- key: title src: c6025acb69
Giunsa pagsumpay ang duha ka track

--- key: p1 src: 1517eeab2a
Kadaghanan sa analytics tools motubag lang og usa: *unsa ang gisulti sa mga tao* o *asa kini nahitabo*. Gihimo ang TALA aron ipakita nganong mas huyang kanang duha ka pangutana kung bulag. Usa ka dataset nga 12,000 ka komento bahin sa health services ang adunay `text` column ug adunay `lon`/`lat` sab, ug ang matag page kay lahi nga paagi sa pagbasa sa mao ra nga 12,000 rows.

--- key: p2 src: e5bd9874b9
**Nganong importante ang pagpares.** Ang text lang mosulti nimo nga 1,448 ka komento ang naghisgot sa oras sa paghulat, apan dili mosulti kung usa ra ba kini ka pasilidad nga puno kaayo o pattern na sa tibuok nasod. Ang location lang magpakita og bagang cluster nga 1,750 ka points, apan dili mosulti nga ang gihisgotan sa sulod niini kay batasan sa staff ug dili suplay sa tambal. Ang kataposang geospatial page nagsumpay sa duha: keywords ug sentiment nga gikwenta *matag cluster* — usa ka butang nga dili masulti sa bisan asa sa duha ka track nga mag-inusara.

--- key: p3 src: d699ee1c44
**Duha ka lahi nga porma sa trabaho.** Ang walo ka text pages kay bulag-bulag nga lente — ablihi sa bisan unsang han-ay. Ang lima ka geospatial pages kay usa ka *pipeline*, diin ang matag lakang mogamit sa gikan sa nauna:

--- key: p4 src: 296c22204c
`Ingest → DBSCAN → Generalization → NLP matag cluster → Mapa ug exports`

--- key: p5 src: af3bbf8f25
Dili lang kini han-ay sa UI. Dili masukod ang gilay-on hangtod dili ma-validate ug ma-project ang coordinates; walay makit-ang cluster kung walay gilay-on; kinahanglan sa per-cluster text ang clusters aron adunay basihan sa paggrupo. Kung molaktaw ka, adunay mogawas gihapon nga numero — dili lang nimo kini madepensahan.

--- key: p6 src: b97d314425
**Adunay tinuyo nga lit-ag dinhi.** Tinuyo nga hugaw ang coordinates nga kauban sa dataset — adunay pipila nga nahulog sa London ug California. Walay nagtangtang niini hangtod moabot sa land-clip sa kataposang page, nga nagtangtang og 3,467 sa 11,715 ka points. Halos ikatulo sa dataset kay sayop sa paagi nga walay error message nga mosulti nimo, ug murag tinuod gihapon ang matag mapa sa taliwala. Ang pagmatikod niini mao ang punto.

--- key: p7 src: 5d07be679f
**Moabot sa tanang page ang mga kontrol sa sidebar.** Global ang palettes, ang toggle para sa Filipino stopwords, ug ang imong kaugalingong stopwords — busa ang kausaban sa usa ka page hilom nga mag-usab sa resulta sa uban. Ayoha kini og set nga tinuyo sa dili pa ka motandi og mga output.
