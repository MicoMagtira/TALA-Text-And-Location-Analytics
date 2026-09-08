--- key: title src: c6025acb69
Paano nagasumpay ang duha ka track

--- key: p1 src: 1517eeab2a
Kalabanan sa analytics tools nagasabat lang sang isa: *ano ang ginahambal sang mga tawo* ukon *diin ini nagakatabo*. Ginhimo ang TALA agod ipakita kon ngaa mas maluya ina nga duha ka pamangkot kon bulag. Isa ka dataset nga 12,000 ka komento parte sa health services ang may `text` column kag may `lon`/`lat` man, kag ang kada page isa ka lain nga paagi sang pagbasa sa amo man nga 12,000 rows.

--- key: p2 src: e5bd9874b9
**Ngaa importante ang pagpares.** Ang text lang magasugid sa imo nga 1,448 ka komento ang nagsambit sang oras sang paghulat, pero indi magasugid kon isa lang bala ka pasilidad nga puno gid ukon pattern na sa bug-os nga pungsod. Ang location lang magapakita sang mabaskog nga cluster nga 1,750 ka points, pero indi magasugid nga ang ginaestoryahan sa sulod sini amo ang panghikot sang staff kag indi ang suplay sang bulong. Ang katapusan nga geospatial page nagasumpay sa duha: keywords kag sentiment nga ginakwenta *kada cluster* — isa ka butang nga indi masarangan ihambal sang bisan diin sa duha ka track nga isahanon.

--- key: p3 src: d699ee1c44
**Duha ka lain nga porma sang trabaho.** Ang walo ka text pages bulag-bulag nga lente — buksi sa bisan ano nga sunod. Ang lima ka geospatial pages isa ka *pipeline*, nga ang kada tikang nagagamit sang halin sa nauna:

--- key: p4 src: 296c22204c
`Ingest → DBSCAN → Generalization → NLP kada cluster → Mapa kag exports`

--- key: p5 src: af3bbf8f25
Indi lang ini sunod sang UI. Indi masukat ang kalayuon tubtob wala ma-validate kag ma-project ang coordinates; wala sing makita nga cluster kon wala sing kalayuon; kinahanglan sang per-cluster text ang clusters agod may basihan sang paggrupo. Kon maglaktaw ka, may magaguwa gihapon nga numero — indi mo lang ini masarangan depensahan.

--- key: p6 src: b97d314425
**May hungod nga siod diri.** Hungod nga mahigko ang coordinates nga upod sa dataset — may pila nga nahulog sa London kag California. Wala sing nagakuha sini tubtob makaabot sa land-clip sa katapusan nga page, nga nagakuha sang 3,467 sa 11,715 ka points. Halos ikatlo sang dataset sayop sa paagi nga wala sing error message nga magasugid sa imo, kag daw matuod gihapon ang kada mapa sa tunga. Ang pagtalupangod sini amo gid ang punto.

--- key: p7 src: 5d07be679f
**Nagaabot sa tanan nga page ang mga kontrol sa sidebar.** Global ang palettes, ang toggle para sa Filipino stopwords, kag ang imo kaugalingon nga stopwords — gani ang pagbag-o sa isa ka page hipos nga nagabaylo sang resulta sa iban. Ipahamtang ini nga hungod antes ka magpaanggid sang mga output.
