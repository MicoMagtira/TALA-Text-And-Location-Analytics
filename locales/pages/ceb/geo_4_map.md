--- key: title src: ae2254e1e9
Land clipping ug ang output contract (Lab 4)

--- key: p1 src: 962793a257
Dinhi madakpan ang hugaw nga coordinates nga imong gisakyan sukad pa sa Lab 1. Ang clip nagdepensa og usa ka butang nga dili kaya sa bounds check: dili lang kung maayo ba ang porma sa coordinate, kondili kung naa ba kini sa lugar nga angay.

--- key: p2 src: e02eb06ade
**Unsa ang gikuha sa clip.** Gipatong ang layer sa polygon sa yuta sa Pilipinas ug gilabay ang mga punto nga naa sa gawas — 3,467 sa 11,715, mga usa ka ikatulo sa dataset. Nahulog kadto sa London, California ug sa tunga sa kadagatan. Naa sila sa matag mapa sukad pa sa Lab 1 ug walay bisan usa ka error message nga naghisgot kanila.

--- key: p3 src: 3d0e95524d
**Nganong sa kataposan kini mahitabo ug dili sa sinugdanan.** Kung nalimpyohan kini sa ingest, dili gyud nimo makita ang problema. Ang tibuok pipeline nagdagan nga adunay usa ka ikatulo nga basura aron masinati nimo ang paghimo og makombinsir nga mapa gikan sa data nga sayop — nga mao gyuy mahitabo sa tinuod nga trabaho kung ang paglimpyo awtomatiko ug hilom.

--- key: p4 src: ac2ef9bb07
**Usa ka pasidaan bahin sa utlanan.** Ang polygon sa yuta kay 110m Natural Earth, gitukod nga adunay mga 15 km nga buffer aron dili buhian sa hilaw nga baybayon ang lehitimong punto sa daplin. Buot ipasabot, luag ang clip sa utlanan — tinuyo nga giangkon niini ang pipila ka punto sa dagat imbis nga tangtangon ang tinuod nga klinika sa baybayon. Ang pagkahibalo kung asang matang sa sayop ang imong gipalabi kay bahin sa trabaho.

--- key: p5 src: 207869792b
**Ang output contract.** Ang GeoJSON ug ang `metadata.json` mogawas nga dungan ug tinuyo kana. Girekord sa metadata ang CRS, ang ihap sa feature, ang mga parameter sa DBSCAN, ug ang gigamit nga generalization. Kung wala kadto, ang layer usa lang ka set sa porma nga walay kasaysayan, ug walay makasubli sa imong nakit-an — apil ka sa sunod bulan.
