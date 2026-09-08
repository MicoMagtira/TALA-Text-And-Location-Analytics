--- key: title src: ae2254e1e9
Land clipping kag ang output contract (Lab 4)

--- key: p1 src: 962793a257
Diri nadakpan ang mahigko nga coordinates nga imo ginsakyan halin pa sa Lab 1. Ang clip nagadepensa sang isa ka butang nga indi masarangan sang bounds check: indi lang kon maayo bala ang porma sang coordinate, kundi kon ara bala ini sa lugar nga dapat.

--- key: p2 src: e02eb06ade
**Ano ang ginakuha sang clip.** Ginpatong ang layer sa polygon sang duta sang Pilipinas kag ginhaboy ang mga punto nga ara sa guwa — 3,467 sa 11,715, mga ikatlo sang dataset. Nahulog ina sa London, California kag sa tunga sang dagat. Ara sila sa kada mapa halin pa sa Lab 1 kag wala gid sing isa ka error message nga nagsambit sa ila.

--- key: p3 src: 3d0e95524d
**Ngaa sa katapusan ini nagakatabo kag indi sa umpisa.** Kon natinluan ini sang ingest, indi mo gid makita ang problema. Ang bug-os nga pipeline nagadalagan nga may ikatlo nga basura agod maagyan mo ang paghimo sang makapakumbinsi nga mapa halin sa data nga sala — nga amo gid ang nagakatabo sa matuod nga trabaho kon ang pagtinlo awtomatiko kag hipos.

--- key: p4 src: ac2ef9bb07
**Isa ka paandam parte sa dulunan.** Ang polygon sang duta 110m Natural Earth, gintukod nga may mga 15 km nga buffer agod indi mabuy-an sang masapnot nga baybayon ang lehitimo nga punto sa binit. Buot silingon, maluag ang clip sa dulunan — hungod nga ginabaton sini ang pila ka punto sa dagat sa baylo nga kuhaon ang matuod nga klinika sa baybayon. Ang paghibalo kon ano nga sahi sang sala ang mas gusto mo bahin sang trabaho.

--- key: p5 src: 207869792b
**Ang output contract.** Ang GeoJSON kag ang `metadata.json` nagaguwa nga dungan kag hungod ina. Ginarekord sang metadata ang CRS, ang isip sang feature, ang mga parameter sang DBSCAN, kag ang gingamit nga generalization. Kon wala ina, ang layer isa lang ka set sang porma nga wala sing kasaysayan, kag wala sing makasulit sang nakita mo — lakip ikaw sa masunod nga bulan.
