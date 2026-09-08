--- key: title src: 962ec51ea4
LDA topic modeling at katatagan

--- key: p1 src: ae477dc46d
Ang Latent Dirichlet Allocation ay naghahanap ng mga pangkat ng salitang madalas magsama-sama sa iisang dokumento, tapos tinatawag itong topic. Hindi ito nagbabasa. Walang naiintindihang kahulugan. Nagbibilang ito ng magkakasabay na paglitaw at nag-aalok ng mga pangkat — ikaw ang nagpapasya kung ano ang tawag sa kanila, at kung may kahulugan ba talaga sila.

--- key: p2 src: e3f2ad5a20
**Bakit ikaw ang pumipili ng bilang ng topic.** Kailangan ng LDA na sabihin mo ang `k` bago ito magsimula. Walang tamang sagot na maghihintay para matuklasan. Ang mababang `k` ay pinagsasama ang magkakaibang usapan sa isang malabong topic; ang mataas na `k` ay pinaghahati-hati ang isang totoong paksa sa maraming halos-kaparehong bersyon. Igalaw mo ang slider at panoorin mo iyon mismong mangyari.

--- key: p3 src: 95ee30d230
**Ang mga timbang ay kaugnayan, hindi bilang.** Ang bawat topic ay isang distribusyon sa buong bokabularyo, at ang ipinapakitang bar ay ang pinakamabigat na salita sa distribusyong iyon. Ang salitang nangunguna sa dalawang topic ay hindi bug — normal iyon. Ang topic ay isang timpla, hindi isang kahon.

--- key: p4 src: 45c3880ea9
**Ang stability check ang pinakamahalagang bahagi ng page na ito.** Sa bawat pagpatakbo, nagsisimula ang LDA sa random na estado. Ibang seed, ibang topic — minsan bahagya lang, minsan malaki. Pinapatakbo ng check ang parehong modelo sa tatlong seed at sinusukat kung gaano kadalas muling lumilitaw ang parehong pangkat ng salita. Ang mataas na Jaccard ay nangangahulugang totoo ang istrukturang nakita mo; ang mababa ay nangangahulugang isang guhit lang iyon sa ingay.

--- key: p5 src: 1800cbcad8
**Bago mo pangalanan ang isang topic, basahin ang mga quote.** Ang listahan ng salita ang pinakamahinang ebidensya na mayroon ka. Ang mga kinatawang komento sa ibaba ang magsasabi kung ang topic ay tunay na paksa, isang template ng survey, o isang pangkat ng maiikling komento na pinagsama lang dahil pare-pareho silang maikli. Ang pagpapangalan ay interpretasyon, at ikaw ang may pananagutan doon — hindi ang modelo.
