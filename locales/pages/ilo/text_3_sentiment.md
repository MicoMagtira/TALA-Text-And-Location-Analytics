--- key: title src: 203f32e9f9
Kasano nga agited iti score ti VADER

--- key: p1 src: 47e8ca8aa1
Saludsoden ti sentiment analysis no ania nga emosional a tiempo ti aw-awiten ti maysa a text. Adda komento a nainit, adda nabagyo, kaaduanna naulep — ket kababaan ti pagtalkan ti report ti tiempo kadagiti saan a pamiliar a lugar. Saan a pamiliar a lugar daytoy a corpus para iti VADER.

--- key: p2 src: b9bbd410ea
**Kastoy ti pannakabukel ti score.** Rule-and-lexicon model ti VADER, saan a nasanay a classifier. Adda ima a nangikabil iti valence iti tunggal sao, sa adda dagiti pagannurotan a mangatur iti dagup: pabpabilgen ti `ALL CAPS`, pabpabilgen ti `!!!`, pabpabilgen ti `very`, balbaliktaden ti `not`. Ti rummuar ket compound score manipud -1 agingga iti +1, nabingay kadagiti label iti ±0.05 kas default. Gapu ta basbasaen dagita a pagannurotan ti punctuation ken dagiti dadakkel a letra, **iti raw a komento agtaray ti VADER, saan ket kadagiti nadalusan a tokens** — daytoy laeng ti page a saan a dumanon ti preprocessing.

--- key: p3 src: 33d60ebae2
**Basaem ti distribusion, saan laeng ti headline.** Daytoy a corpus ket 47% positive, 36% negative, 17% neutral. Ngem ti mean compound ket +0.115 bayat a ti *median ket eksakto a 0.000* — nasurok iti apagkanem dagiti komento ti matnag iti umiso a sero, kayatna a sawen awan ti nabigbig a lexicon word ti VADER sadiay. Saan a neutralidad ti patad a sero; kinaulimek dayta. Igawidmo ti threshold slider ket kitaem no mano iti neutral band ti pudpudno a naglaok ken mano ti saan laeng a na-score.

--- key: p4 src: 24e25a343f
**Ditoy nga agbiddut daytoy, mismo.** Nadalus a balintuag ti sarcasm ket saan a makita ti VADER — ti "Great, I waited three hours again" ket agbalin a positive gapu iti `Great`. Agdungpar ti klinikal ken emosional a bokabulario: dakes a damag ti `positive` a resulta ti test, severity ti `critical` saan ket a reklamo, ket kaaduanna bang-ar ti `discharged`. Gistay saan a makita ti English lexicon ti Taglish, isu a ti nalaing a reklamo iti Filipino ket mabalin nga agbalin a 0.000 sa matnag iti neutral bucket-mo. Ket palpalukneden ti kinaemma ti saan a pannakapnek, a mangiduron iti ngato iti intero a distribusion.

--- key: p5 src: 6fb97aea01
**Isu nga ibilangmo daytoy a triage, saan a pulos a label.** Daytoy ti umno nga aramid: basaem ti distribusion, i-sort agingga kadagiti dua a pungto, luktam dagiti pudno a komento, ket ikeddengmo no umno ti ar-aramiden ti alikamen *iti datam*. Ireportmo laeng ti porsiento a kadua ti nasarakam idi kinitam.
