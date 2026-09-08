--- key: title src: ae2254e1e9
Land clipping ken ti output contract (Lab 4)

--- key: p1 src: 962793a257
Ditoy a matiliw dagiti narugit a coordinates a nakalugan kenka manipud pay iti Lab 1. Ti clip ket mangsalaknib iti maysa a banag a saan a kabaelan ti bounds check: saan laeng a no nasayaat ti porma ti coordinate, no di ket no adda daytoy iti lugar a rumbeng.

--- key: p2 src: e02eb06ade
**Ania ti ikkaten ti clip.** Naiparabaw ti layer iti polygon ti daga ti Filipinas ket naibelleng dagiti punto nga adda iti ruar — 3,467 iti 11,715, agarup apagkatlo ti dataset. Natnag dagita idiay London, California ken iti tengnga ti taaw. Addada iti tunggal mapa manipud pay iti Lab 1 ket awan ti uray maysa nga error message a nangdakamat kadakuada.

--- key: p3 src: 3d0e95524d
**Apay nga iti maudi daytoy mapasamak saan ket nga iti umuna.** No nadalusan daytoy idi ingest, saanmo a pulos a makita ti parikut. Ti intero a pipeline ket agtaray nga addaan apagkatlo a basura tapno mapadasam ti panagaramid iti makaallukoy a mapa manipud iti data a biddut — a dayta mismo ti mapaspasamak iti pudno a trabaho no ti panagdalus ket automatiko ken siuulimek.

--- key: p4 src: ac2ef9bb07
**Maysa a pakdaar maipapan iti beddeng.** Ti polygon ti daga ket 110m Natural Earth, naaramid nga addaan agarup 15 km a buffer tapno saan a mapukaw ti nakersang nga igid ti baybay dagiti lehitimo a punto iti aplaya. Kayatna a sawen, nalukay ti clip iti beddeng — ginagara nga aw-awatenna dagiti sumagmamano a punto iti taaw imbes nga ikkatenna ti pudno a klinika iti igid ti baybay. Ti pannakaammo no ania a kita ti biddut ti kaykayatmo ket paset ti trabaho.

--- key: p5 src: 207869792b
**Ti output contract.** Ti GeoJSON ken ti `metadata.json` ket rummuarda a sangsangkamaysa ket ginagara dayta. Iprekord ti metadata ti CRS, ti bilang dagiti feature, dagiti parameter ti DBSCAN, ken ti nausar a generalization. No awan dagita, ti layer ket maysa laeng a set dagiti porma nga awan pakasaritaanna, ket awan ti makaulit iti nakitam — mairaman ka iti sumaruno a bulan.
