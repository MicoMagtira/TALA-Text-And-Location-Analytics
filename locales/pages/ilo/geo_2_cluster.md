--- key: title src: 526b73ca6c
DBSCAN ken ti k-distance elbow (Lab 2)

--- key: p1 src: e816471bf6
Ti napateg a paggidiatan iti k-means: **saan a pulos a maibaga iti DBSCAN no mano a cluster ti birukenna.** Iladawam no ania ti kayat a sawen ti "dense" ket ireportna no mano a dense a rehion ti adda — mabalin nga awan. Daytoy laeng met ti wagas ditoy a mapalubosan a mangibaga a *daytoy a punto ket awan ti pakaibilanganna*, a malabelan a noise (`cluster_id = -1`). Para kadagiti naiwaras a pasamak iti pudno a lubong, dayta a kinapudno ti intero a pagimbagan.

--- key: p2 src: 946139baf8
**Dua a parameter, maysa a kaipapanan.** Ti `eps` ket radius iti metro ket ti `min_samples` ket bilang. Sangsangkamaysa, ikeddengda ti density: ti maysa a punto ket core point no adda saan a kumurang iti `min_samples` a kaarruba iti uneg ti `eps`. Dumakkel ti cluster babaen ti panagkawar dagiti core point. Gapu ta pudno a kaadayo ti `eps`, agtrabaho laeng daytoy iti projected a layer a naibatay iti metro manipud iti Lab 1 — patarayem iti raw a degree ket ti kayat a sawen ti `eps=15000` ket 15,000 a degree, a kinamaag a sirarag-o a kwentaen ti code.

--- key: p3 src: bf4bd3ad8e
**Panagbasa iti k-distance curve iti ngato.** Ti kaadayo ti tunggal punto iti k-th a kaasitgan a kaarruba, sipapangato ti urnos. Ti patad a paset ket dagiti punto nga adda iti nadagsen a kaarruba; ti sumang-at a pungto iti kannawan ket dagiti punto nga umad-adayo. Ti tumeng iti nagbaetanda ti pakaawanan ti kaipapanan ti "asideg" — maysa a maikanawa a pangrugian nga `eps`. Iti daytoy a data, ti kaadayo iti maika-10 a kaarruba ket 7.8 km iti median ngem 60.1 km iti maika-90 a percentile, ket dayta a natarik nga ipus mismo ti tumeng a birbirukem.

--- key: p4 src: a5e452a0e6
**Kasano kasensitibo daytoy.** Naiggaman ti `min_samples=10` ket ti `eps` laeng ti naigawid:

--- key: p5 src: 468c496062
- `eps = 5 km` → **109 clusters, 7,241 noise** (naburak; gistay amin a data naibelleng)
- `eps = 15 km` → **29 clusters, 2,199 noise** (ti default ti lab)
- `eps = 40 km` → **17 clusters, 1,290 noise** (pagtiponenna dagiti nagduduma a siudad)

--- key: p6 src: bd80022295
Agpadpada a data, agpadpada nga algorithm, tallo a nagduduma nga estoria. Awan ti aniaman iti output a mangibaga no ania ti umno — kukuam dayta a panangukom, ket dayta ti masapul nga ikanawam.

--- key: p7 src: 1d08a37e80
**Ania ti saan a cluster.** Maysa a rehion daytoy a nakadanon iti density threshold nga *sika* ti nangikeddeng. Saan a komunidad, catchment, wenno outbreak. Ket saan a biddut ti noise: ti naisina a punto ket mabalin a ti kapatgan a kaso iti intero a dataset.
