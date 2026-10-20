--- key: title src: c6025acb69
Paano nag-uugnay ang dalawang track

--- key: p1 src: 1517eeab2a
Karamihan sa analytics tools ay sumasagot lang ng isa: *ano ang sinasabi ng mga tao* o *saan ito nangyayari*. Ginawa ang TALA para ipakita kung bakit mas mahina ang dalawang tanong na iyon kapag magkahiwalay. Isang dataset ng 12,000 komento tungkol sa health services ang may `text` column at may `lon`/`lat` din, at ang bawat page ay ibang paraan ng pagbasa sa parehong 12,000 rows.

--- key: p2 src: e5bd9874b9
**Bakit mahalaga ang pagpapares.** Sasabihin sa iyo ng text lang na 1,448 komento ang bumanggit ng oras ng paghihintay, pero hindi nito sasabihin kung iisang punong-puno bang pasilidad iyon o pattern na sa buong bansa. Ang location naman mag-isa ay magpapakita ng makapal na cluster ng 1,750 points, pero hindi nito sasabihin na ang pinag-uusapan sa loob noon ay asal ng staff at hindi supply ng gamot. Pinagdudugtong ng huling geospatial page ang dalawa: keywords at sentiment na kinukuwenta *kada cluster* — isang bagay na hindi kayang sabihin ng kahit alin sa dalawang track nang mag-isa.

--- key: p3 src: d699ee1c44
**Dalawang magkaibang hugis ng trabaho.** Ang walong text pages ay magkakahiwalay na lente — buksan mo sa kahit anong pagkakasunod-sunod. Ang limang geospatial pages ay isang *pipeline*, kung saan ang bawat hakbang ay gumagamit ng galing sa nauna:

--- key: p4 src: 296c22204c
`Ingest → DBSCAN → Generalization → NLP kada cluster → Mapa at exports`

--- key: p5 src: af3bbf8f25
Hindi lang ito ayos ng UI. Hindi masusukat ang distansya hangga't hindi na-validate at na-project ang coordinates; walang mahahanap na cluster kung walang distansya; kailangan ng clusters ang per-cluster text para may pagbatayan ng paggrupo. Kapag lumaktaw ka, may lalabas pa rin na numero — hindi mo lang ito kayang ipagtanggol.

--- key: p6 src: b97d314425
**May sadyang bitag dito.** Sadyang madumi ang coordinates na kasama sa dataset — may ilang bumagsak sa London at California. Walang nag-aalis sa mga iyon hangga't hindi umabot sa land-clip sa huling page, na nagtatanggal ng 3,467 sa 11,715 points. Halos ikatlo ng dataset na ito ay mali sa paraang walang error message na magsasabi sa iyo, at mukhang kapani-paniwala pa rin ang bawat mapa sa pagitan. Ang mapansin ito ang mismong punto.

--- key: p7 src: 5d07be679f
**Umaabot sa lahat ng page ang mga kontrol sa sidebar.** Global ang palettes, ang toggle para sa Filipino stopwords, at ang sarili mong stopwords — kaya ang pagbabago sa isang page ay tahimik na nagpapalit ng resulta sa iba. Ayusin mo ito nang sadya bago ka maghambing ng mga output.
