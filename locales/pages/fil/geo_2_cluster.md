--- key: title src: 526b73ca6c
DBSCAN at ang k-distance elbow (Lab 2)

--- key: p1 src: e816471bf6
Ang mahalagang pagkakaiba sa k-means: **hindi kailanman sinasabihan ang DBSCAN kung ilang cluster ang hahanapin.** Inilalarawan mo kung ano ang ibig sabihin ng "dense" at iniuulat nito kung ilang dense na rehiyon ang meron — pwedeng wala. Ito rin lang ang paraan dito na pinapayagang sabihin na *ang puntong ito ay walang kinabibilangan*, na nilalagyan ng label na noise (`cluster_id = -1`). Para sa magkakalat na pangyayari sa totoong mundo, ang katapatang iyon ang buong bentahe.

--- key: p2 src: 946139baf8
**Dalawang parameter, isang kahulugan.** Ang `eps` ay radius sa metro at ang `min_samples` ay bilang. Magkasama, tinutukoy nila ang density: ang isang punto ay core point kung may hindi bababa sa `min_samples` na kapitbahay sa loob ng `eps`. Lumalaki ang cluster sa pamamagitan ng pagkakadena ng mga core point. Dahil tunay na distansya ang `eps`, gumagana lang ito sa projected na layer na nakabatay sa metro mula sa Lab 1 — patakbuhin mo sa raw na degree at ang ibig sabihin ng `eps=15000` ay 15,000 degree, na kalokohang masaya namang kukuwentahin ng code.

--- key: p3 src: bf4bd3ad8e
**Pagbasa sa k-distance curve sa itaas.** Ang distansya ng bawat punto sa k-th na pinakamalapit na kapitbahay, pataas ang ayos. Ang patag na bahagi ay mga puntong nasa masikip na kapaligiran; ang pataas na dulo sa kanan ay mga puntong papalayo nang papalayo. Ang tuhod sa pagitan nila ay kung saan nawawalan na ng saysay ang "malapit" — isang maipagtatanggol na panimulang `eps`. Sa data na ito, ang distansya sa ika-10 kapitbahay ay 7.8 km sa median pero 60.1 km sa ika-90 percentile, at ang matarik na buntot na iyon mismo ang tuhod na hinahanap mo.

--- key: p4 src: a5e452a0e6
**Gaano ito ka-sensitibo.** Hawak ang `min_samples=10` at ang `eps` lang ang ginagalaw:

--- key: p5 src: 468c496062
- `eps = 5 km` → **109 clusters, 7,241 noise** (durog-durog; halos lahat ng data itinapon)
- `eps = 15 km` → **29 clusters, 2,199 noise** (ang default ng lab)
- `eps = 40 km` → **17 clusters, 1,290 noise** (pinagsasama ang magkaibang lungsod)

--- key: p6 src: bd80022295
Parehong data, parehong algorithm, tatlong magkaibang kuwento. Walang anuman sa output ang nagsasabi kung alin ang tama — sa iyo ang paghuhusgang iyon, at iyon ang kailangan mong ipagtanggol.

--- key: p7 src: 1d08a37e80
**Ano ang hindi isang cluster.** Isa itong rehiyong umabot sa density threshold na *ikaw* ang nagtakda. Hindi ito komunidad, catchment, o outbreak. At hindi kamalian ang noise: ang nakabukod na punto ay pwedeng ang pinakamahalagang kaso sa buong dataset.
