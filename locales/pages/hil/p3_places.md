--- key: title src: c443695e58
Mga Lugar: halin sa points pakadto sa mga rehiyon kag cluster

--- key: p1 src: 9e04298220
**Ngaa maggrupo pa.** Ang isa ka komento isa lang ka estorya; ang isa ka lugar isa ka sample. Ginapaanggid sang Kapitulo 2 kon ano ang ginahambal sang mga lugar, gani kinahanglan anay sang kada komento ang place label. May duha ka paagi sa pagkuha sini, kag lain-lain nga pamangkot ang ila ginasabat.

--- key: p2 src: f1707fe2eb
**Rehiyon: gamita ang ginsulat sang mga tawo.** Ang kada komento nagakuha sang rehiyon sang lugar nga iya ginasambit (halin sa gazetteer). Ang komento nga wala sing magamit nga ngalan nagakuha sang pinakamalapit nga region centroid sa iya located point. Mahapos ini basahon, stable, kag wala sing kinahanglan nga parameters, pero administratibo ang mga rehiyon: mahimo nga indi gid sila parehas sa kadakuon kag populasyon, kag diri ang rehiyon gindrowing bilang bubble sa iya centroid, indi bilang dulunan.

--- key: p3 src: 97233bbec5
**Cluster: pasugta ang density ang magdesisyon.** Ginapadaku sang DBSCAN ang isa ka cluster halin sa bisan ano nga point nga may indi magkubos sa *min_samples* nga kaingod sa sulod sang *eps*, kag ginamarkahan nga noise ang mga point nga wala sa bisan ano nga dense region. Wala ini nagakinahanglan sang kadamuon sang cluster antes pa, kag wala ini nagapilit sa kada point nga mag-upod sa isa ka grupo. Importante ang duha ka knob: ang diutay nga eps nagapihak sang isa ka siyudad sa madamo nga cluster, ang daku nagatingob sang magkaingod nga mga siyudad sa isa ka daku nga blob.

--- key: p4 src: 8655589831
**Projected metres, indi degrees.** Kalayuon ang eps sang DBSCAN, gani una nga gina-project ang coordinates sa UTM metres. Ang isa ka degree sang longitude mas malip-ot sangsa isa ka degree sang latitude kon malayo sa equator, gani kon padalagan ang DBSCAN sa hilaw nga degrees, ellipse ang madrowing, indi circle.

--- key: p5 src: 6a40392629
**Ang k-distance elbow.** Para sa kada point, kuhaa ang kalayuon sa iya k-th nearest neighbour kag i-sort ina nga mga kalayuon. Ang kalabanan nga points ara sa dense nga lugar kag diutay ang ila value; ang mga nagaisahanon daku, gani ang curve nagabalikutot pataas sa dulunan. Ang maayo nga eps ara malapit sa sina nga elbow. Ibutang ang k nga malapit sa min_samples. Giya lang ang elbow, indi pamatuod: tan-awa ang mapa kag usisaa kon ang mga cluster nagatugma sa mga lugar nga imo kilala.

--- key: p6 src: dbab5c1879
**Resulta man ang noise.** Ang points nga wala ginbutangan sang DBSCAN indi sayop. Ang mga komento sa uma nga nagkalaplap sa tunga sang mga banwa kasagaran noise, kag matuod ina: wala sila sa isa ka dense nga lugar. Sa Rehiyon mode, ang mga komento lang nga wala gid sing location ang wala sing lugar.

--- key: p7 src: fc3b88474e
**Ang gin-ayo nga points ara sa centroid sang banwa.** Kon ang komento nagasambit sang isa ka lugar pero sayop ang iya GPS, ang gin-ayo nga point ginabutang gid sa centroid sang sina nga lugar. Gani sa Cluster mode, ang DBSCAN sa gin-ayo nga points nagahilig maghimo sang isa ka cluster kada ginsambit nga banwa, kag ang k-distance curve daw patag kay madamo nga points ang may parehas gid nga coordinates. Ang "Kon diin lang nagauyon ang duha" nagatipig sang GPS-only nga points, gani gamita ini bilang view para sa pagpaanggid.
