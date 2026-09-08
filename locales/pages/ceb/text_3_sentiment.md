--- key: title src: 203f32e9f9
Giunsa paghatag og score sa VADER

--- key: p1 src: 47e8ca8aa1
Gipangutana sa sentiment analysis kung unsang emosyonal nga panahon ang dala sa usa ka text. Adunay komento nga init, adunay bagyo, kadaghanan panganod — ug pinakadili kasaligan ang report sa panahon sa dili pamilyar nga lugar. Dili pamilyar nga lugar ang maong corpus para sa VADER.

--- key: p2 src: b9bbd410ea
**Ingon niini natukod ang score.** Rule-and-lexicon model ang VADER, dili gibansay nga classifier. Adunay kamot nga gibutang nga valence ang matag pulong, dayon adunay mga lagda nga nag-ayo sa kinatibuk-an: gipakusog sa `ALL CAPS`, gipakusog sa `!!!`, gipalig-on sa `very`, gibaliktad sa `not`. Ang mogawas kay compound score gikan -1 hangtod +1, gibahin sa mga label sa ±0.05 isip default. Tungod kay gibasa niadtong mga lagda ang punctuation ug dagkong letra, **sa raw nga komento modagan ang VADER, dili sa nalimpyohan nga tokens** — kini ra ang page diin dili moabot ang preprocessing.

--- key: p3 src: 33d60ebae2
**Basaha ang distribusyon, dili lang ang headline.** Ang maong corpus kay 47% positive, 36% negative, 17% neutral. Apan ang mean compound kay +0.115 samtang ang *median kay eksaktong 0.000* — kapin sa ikaunom sa mga komento ang nahulog sa hustong sero, buot ipasabot walay nailhan nga lexicon word ang VADER didto. Dili neutralidad ang patag nga sero; kahilom kana. Ilihok ang threshold slider ug tan-awa kung pila sa neutral band ang tinuod nga sagol ug pila ang wala lang na-score.

--- key: p4 src: 24e25a343f
**Dinhi kini masayop, gyud.** Limpyo nga baliktad ang sarcasm ug dili kini makita sa VADER — ang "Great, I waited three hours again" mahimong positive tungod sa `Great`. Nagbangga ang klinikal ug emosyonal nga bokabularyo: dautan nga balita ang `positive` nga resulta sa test, severity ang `critical` ug dili reklamo, ug kasagaran kahupayan ang `discharged`. Halos dili makita sa English lexicon ang Taglish, mao nga ang hanas nga reklamo sa Filipino mahimong 0.000 ug mahulog sa imong neutral bucket. Ug gipahumok sa pagkamatinahuron ang kawalay katagbawan, nga nagtukmod pataas sa tibuok distribusyon.

--- key: p5 src: 6fb97aea01
**Busa isipa kini nga triage, dili gyud label.** Kini ang husto nga agi: basaha ang distribusyon, i-sort padulong sa duha ka tumoy, ablihi ang tinuod nga komento, ug hukmi kung maayo ba ang binuhatan sa himan *sa imong data*. Ireport lang ang porsyento uban sa imong nakit-an dihang imong gisusi.
