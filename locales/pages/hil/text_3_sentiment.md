--- key: title src: 203f32e9f9
Paano nagahatag sang score ang VADER

--- key: p1 src: 47e8ca8aa1
Ginapamangkot sang sentiment analysis kon ano nga emosyonal nga tiempo ang dala sang isa ka text. May komento nga mainit, may unos, kalabanan gal-om — kag pinakaindi masaligan ang report sang tiempo sa indi pamilyar nga lugar. Indi pamilyar nga lugar ining corpus para sa VADER.

--- key: p2 src: b9bbd410ea
**Amo sini natukod ang score.** Rule-and-lexicon model ang VADER, indi ginhanas nga classifier. May kamot nga nagbutang sang valence sa kada pulong, dayon may mga pagsulundan nga nagaayo sang kabilugan: ginapabaskog sang `ALL CAPS`, ginapabaskog sang `!!!`, ginapabakod sang `very`, ginabaliskad sang `not`. Ang magaguwa amo ang compound score halin -1 tubtob +1, ginabahin sa mga label sa ±0.05 bilang default. Tungod nga ginabasa sadtong mga pagsulundan ang punctuation kag dalagko nga letra, **sa raw nga komento nagadalagan ang VADER, indi sa natinluan nga tokens** — amo lang ini ang page nga wala nagaabot ang preprocessing.

--- key: p3 src: 33d60ebae2
**Basaha ang distribusyon, indi lang ang headline.** Ining corpus 47% positive, 36% negative, 17% neutral. Pero ang mean compound +0.115 samtang ang *median eksakto nga 0.000* — kapin sa ikaanom sang mga komento ang nagahulog sa husto nga sero, buot silingon wala sing nakilala nga lexicon word ang VADER didto. Indi neutralidad ang patag nga sero; kalinong ina. Ihulag ang threshold slider kag tan-awa kon pila sa neutral band ang matuod nga simbog kag pila ang wala lang na-score.

--- key: p4 src: 24e25a343f
**Diri ini masayop, gid.** Matinlo nga baliskad ang sarcasm kag indi ini makita sang VADER — ang "Great, I waited three hours again" nangin positive tungod sa `Great`. Nagasumpakat ang klinikal kag emosyonal nga bokabularyo: malain nga balita ang `positive` nga resulta sang test, severity ang `critical` kag indi reklamo, kag masami kaumpawan ang `discharged`. Halos indi makita sang English lexicon ang Taglish, gani ang lantip nga reklamo sa Filipino mahimo mangin 0.000 kag mahulog sa imo neutral bucket. Kag ginapahumok sang pagkamatinahuron ang kawad-on sang kakontento, nga nagatulod paibabaw sang bug-os nga distribusyon.

--- key: p5 src: 6fb97aea01
**Gani kabiga ini nga triage, indi gid label.** Amo ini ang husto nga proseso: basaha ang distribusyon, i-sort padulong sa duha ka punta, buksi ang matuod nga komento, kag desisyuni kon nagakabagay bala ang ginahimo sang galamiton *sa imo data*. Ireport lang ang porsyento upod sa nakita mo sang gin-usisa mo.
