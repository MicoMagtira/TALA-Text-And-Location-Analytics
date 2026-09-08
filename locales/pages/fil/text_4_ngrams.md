--- key: title src: 78e35e9dfc
N-grams at co-occurrence networks

--- key: p1 src: c7f883d096
Iisang salita ang binibilang ng nakaraang page. Iniiwan noon ang pagkakasunod-sunod, at kadalasan ang pagkakasunod-sunod ang mismong kahulugan. Ang `waiting` at `time` na magkahiwalay ay hindi kasing-linaw ng `waiting time`; ang `emergency room` ay isang lugar samantalang ang `emergency` at `room` ay dalawang ideya.

--- key: p2 src: 9ee6538d28
**Ano ang binibilang ng n-gram.** Ang bigram ay dalawang magkatabing salita, ang trigram ay tatlo. Kinukuha ang mga ito pagkatapos ng paglilinis, kaya ang mga naalis na stopword ay naglalapit sa mga salitang hindi naman magkatabi sa orihinal na pangungusap. Iyon ay bentahe at kapintasan nang sabay: nakikita mo ang `staff kind` na hindi mo makikita sa raw text, pero hindi na iyon eksaktong sinabi ng tao.

--- key: p3 src: 4a08faaed5
**Ano ang ginagawa ng minimum document frequency.** Ang `min_df` ay nagtatapon ng mga parirala na lumilitaw sa mas kaunting dokumento kaysa sa itinakda mo. Itaas mo ito at matitira lang ang matatatag na pattern; ibaba mo ito at makikita mo ang mahabang buntot, kasama ang mga typo at ang minsanang parirala. Walang tamang halaga — mayroon lang tanong na sinasagot mo.

--- key: p4 src: 8a9b0e701d
**Basahin ang network bilang mapa, hindi bilang sukatan.** Ang bawat gilid ay isang bigram at ang laki ng node ay bilang ng koneksyon. Ang layout ay pinipili ng spring algorithm at may random seed, kaya ang *posisyon* sa canvas ay walang kahulugan — dalawang node na magkalapit ay hindi mas magkaugnay kaysa sa dalawang magkalayo. Ang koneksyon lang ang totoo. Kapag binago mo ang seed, magbabago ang hugis at hindi magbabago ang istruktura.

--- key: p5 src: d645d4a2af
**Ano ang hahanapin.** Mga bungkos na nagkakabit sa paligid ng iisang termino — kadalasan iyon ay tunay na paksa. At mga tulay: salitang nag-uugnay ng dalawang bungkos na kung hindi ay magkahiwalay. Sa data na ito, ang `staff` ay ganoong tulay, at iyon ang senyales na maraming ibang bagay ang sinusukat sa pamamagitan ng mga tao.
