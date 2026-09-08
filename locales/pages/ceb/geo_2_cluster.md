--- key: title src: 526b73ca6c
DBSCAN ug ang k-distance elbow (Lab 2)

--- key: p1 src: e816471bf6
Ang importanteng kalainan sa k-means: **wala gyud gisultihan ang DBSCAN kung pila ka cluster ang pangitaon.** Imong gihulagway kung unsa ang buot ipasabot sa "dense" ug gireport niini kung pila ka dense nga rehiyon ang naa — mahimong wala. Kini ra sab ang paagi dinhi nga gitugotan nga moingon nga *kining puntoha walay gisapian*, nga gilabelan og noise (`cluster_id = -1`). Para sa nagkatag nga panghitabo sa tinuod nga kalibotan, kanang pagkamatinud-anon mao ang tibuok bentaha.

--- key: p2 src: 946139baf8
**Duha ka parameter, usa ka kahulogan.** Ang `eps` kay radius sa metro ug ang `min_samples` kay ihap. Kung dungan, gitakda nila ang density: ang usa ka punto core point kung adunay dili moubos sa `min_samples` nga silingan sulod sa `eps`. Modako ang cluster pinaagi sa pagkadena sa mga core point. Tungod kay tinuod nga gilay-on ang `eps`, molihok lang kini sa projected nga layer nga nakabase sa metro gikan sa Lab 1 — padagana kini sa raw nga degree ug ang buot ipasabot sa `eps=15000` kay 15,000 ka degree, nga binuang nga malipayong kwentahon sa code.

--- key: p3 src: bf4bd3ad8e
**Pagbasa sa k-distance curve sa ibabaw.** Ang gilay-on sa matag punto ngadto sa k-th nga pinakaduol nga silingan, pataas ang han-ay. Ang patag nga bahin kay mga punto nga naa sa siksik nga palibot; ang pataas nga tumoy sa tuo kay mga punto nga nagkalayo. Ang tuhod sa taliwala nila mao kung asa nawad-an na og kahulogan ang "duol" — usa ka madepensahan nga sinugdanang `eps`. Sa maong data, ang gilay-on sa ika-10 nga silingan kay 7.8 km sa median apan 60.1 km sa ika-90 nga percentile, ug kanang tarong nga ikog mismo mao ang tuhod nga imong gipangita.

--- key: p4 src: a5e452a0e6
**Unsa kini ka sensitibo.** Gikuptan ang `min_samples=10` ug ang `eps` ra ang gilihok:

--- key: p5 src: 468c496062
- `eps = 5 km` → **109 clusters, 7,241 noise** (nagkabuak; halos tanang data gilabay)
- `eps = 15 km` → **29 clusters, 2,199 noise** (ang default sa lab)
- `eps = 40 km` → **17 clusters, 1,290 noise** (naghiusa sa lahi nga siyudad)

--- key: p6 src: bd80022295
Parehas nga data, parehas nga algorithm, tulo ka lahi nga istorya. Walay bisan unsa sa output nga mosulti kung hain ang husto — imoha kanang paghukom, ug mao kanay kinahanglan nimong madepensahan.

--- key: p7 src: 1d08a37e80
**Unsa ang dili usa ka cluster.** Usa kini ka rehiyon nga miabot sa density threshold nga *ikaw* ang nagtakda. Dili kini komunidad, catchment, o outbreak. Ug dili sayop ang noise: ang nahimulag nga punto mahimong mao ang pinaka-importanteng kaso sa tibuok dataset.
