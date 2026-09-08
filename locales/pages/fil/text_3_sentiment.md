--- key: title src: 203f32e9f9
Paano nagbibigay ng score ang VADER

--- key: p1 src: 47e8ca8aa1
Tinatanong ng sentiment analysis kung anong emosyonal na panahon ang dala ng isang text. May komentong maaraw, may maulan, karamihan ay maulap — at pinakamahina ang report ng panahon sa mga lugar na hindi pamilyar. Hindi pamilyar na lugar ang corpus na ito para sa VADER.

--- key: p2 src: b9bbd410ea
**Ganito nabubuo ang score.** Rule-and-lexicon model ang VADER, hindi sanay na classifier. May kamay na itinakdang valence ang bawat salita, tapos may mga patakarang nag-aayos sa kabuuan: pinapatindi ng `ALL CAPS`, pinapatindi ng `!!!`, pinapalakas ng `very`, binabaligtad ng `not`. Ang lalabas ay compound score mula -1 hanggang +1, hinahati sa mga label sa ±0.05 bilang default. Dahil binabasa ng mga patakarang iyon ang bantas at malalaking letra, **sa raw na komento tumatakbo ang VADER, hindi sa mga nalinis na token** — ito lang ang page na hindi umaabot ang preprocessing.

--- key: p3 src: 33d60ebae2
**Basahin ang distribusyon, hindi lang ang headline.** Ang corpus na ito ay 47% positive, 36% negative, 17% neutral. Pero ang mean compound ay +0.115 samantalang ang *median ay eksaktong 0.000* — mahigit ikaanim ng mga komento ang bumabagsak sa tumpak na sero, ibig sabihin walang nakilalang lexicon word ang VADER doon. Hindi neutralidad ang patag na sero; katahimikan iyon. Igalaw mo ang threshold slider at tingnan kung gaano karami sa neutral band ang talagang halo-halo at gaano karami ang basta hindi na-score.

--- key: p4 src: 24e25a343f
**Dito ito magkakamali, mismo.** Malinis na baligtad ang sarcasm at hindi ito nakikita ng VADER — ang "Great, I waited three hours again" ay nagiging positive dahil sa `Great`. Nagbabanggaan ang klinikal at emosyonal na bokabularyo: masamang balita ang `positive` na resulta ng test, severity ang `critical` at hindi reklamo, at kadalasang ginhawa ang `discharged`. Halos hindi nakikita ng English lexicon ang Taglish, kaya ang matatas na reklamo sa Filipino ay pwedeng maging 0.000 at mapunta sa neutral bucket mo. At pinapalambot ng pagiging magalang ang hindi kasiyahan, na nagtutulak pataas sa buong distribusyon.

--- key: p5 src: 6fb97aea01
**Kaya ituring mo itong triage, hindi kailanman label.** Ito ang tamang daloy: basahin ang distribusyon, i-sort papunta sa dulo, buksan ang totoong komento, at pagpasyahan kung matino ba ang kilos ng tool *sa data mo*. Iulat mo lang ang porsyento kasabay ng nakita mo noong tiningnan mo.
