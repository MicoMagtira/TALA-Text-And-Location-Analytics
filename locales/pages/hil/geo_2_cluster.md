--- key: title src: 526b73ca6c
DBSCAN kag ang k-distance elbow (Lab 2)

--- key: p1 src: e816471bf6
Ang importante nga kinatuhayan sa k-means: **wala gid ginasugiran ang DBSCAN kon pila ka cluster ang pangitaon.** Ginalaragway mo kon ano ang buot silingon sang "dense" kag ginareport sini kon pila ka dense nga rehiyon ang may ara — mahimo wala. Amo man lang ini ang paagi diri nga ginatugutan magsiling nga *ining punto wala sing ginasakupan*, nga gina-label nga noise (`cluster_id = -1`). Para sa naglapta nga hitabo sa matuod nga kalibutan, inang pagkabunayag amo ang bug-os nga bentaha.

--- key: p2 src: 946139baf8
**Duha ka parameter, isa ka kahulugan.** Ang `eps` radius sa metro kag ang `min_samples` isip. Kon dungan, ginatakda nila ang density: ang isa ka punto core point kon may indi manubo sa `min_samples` nga kaingod sa sulod sang `eps`. Nagadaku ang cluster paagi sa pagkadena sang mga core point. Tungod nga matuod nga kalayuon ang `eps`, nagaobra lang ini sa projected nga layer nga base sa metro halin sa Lab 1 — padalagana ini sa raw nga degree kag ang buot silingon sang `eps=15000` amo ang 15,000 ka degree, nga kabuangan nga malipayon nga kwentahon sang code.

--- key: p3 src: bf4bd3ad8e
**Pagbasa sa k-distance curve sa ibabaw.** Ang kalayuon sang kada punto sa k-th nga pinakalapit nga kaingod, pataas ang sunod. Ang patag nga bahin amo ang mga punto nga ara sa masiot nga palibot; ang pataas nga punta sa tuo amo ang mga punto nga nagalayo. Ang tuhod sa tunga nila amo kon diin nagadula na ang kahulugan sang "malapit" — isa ka madepensahan nga umpisa nga `eps`. Sa amo nga data, ang kalayuon sa ika-10 nga kaingod 7.8 km sa median pero 60.1 km sa ika-90 nga percentile, kag inang matarok nga ikog mismo amo ang tuhod nga imo ginapangita.

--- key: p4 src: a5e452a0e6
**Daw ano ini ka sensitibo.** Ginauyatan ang `min_samples=10` kag ang `eps` lang ang ginahulag:

--- key: p5 src: 468c496062
- `eps = 5 km` → **109 clusters, 7,241 noise** (nagkabuka; halos tanan nga data ginhaboy)
- `eps = 15 km` → **29 clusters, 2,199 noise** (ang default sang lab)
- `eps = 40 km` → **17 clusters, 1,290 noise** (nagatipon sang lain nga siyudad)

--- key: p6 src: bd80022295
Pareho nga data, pareho nga algorithm, tatlo ka lain nga estorya. Wala sing bisan ano sa output nga nagasugid kon diin ang husto — imo ina nga paghukom, kag amo ina ang kinahanglan mo depensahan.

--- key: p7 src: 1d08a37e80
**Ano ang indi isa ka cluster.** Isa ini ka rehiyon nga nakaabot sa density threshold nga *ikaw* ang nagtakda. Indi ini komunidad, catchment, ukon outbreak. Kag indi sala ang noise: ang nahamulag nga punto mahimo amo ang pinakaimportante nga kaso sa bug-os nga dataset.
