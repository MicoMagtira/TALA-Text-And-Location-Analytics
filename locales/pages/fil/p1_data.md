--- key: title src: 53d0ca32cf
Data at paglilinis

--- key: p1 src: 0acbd8af98
**Ang kailangan ng pipeline.** Isang text column ang hinahanap ng TALA at, para sa mga hakbang tungkol sa lugar, isang longitude at isang latitude column. Lahat ng susunod sa journey ay bumabasa sa tatlong column na iyon ayon sa pangalan, kaya dito mo sila imi-map nang minsanan at hindi na uulit. Naka-store ang mapping bilang mga pangalan ng column sa session mo, at hindi kailanman bilang kopya ng data.

--- key: p2 src: c2c781aeb0
**Maliit at nakapirming pipeline ang paglilinis.** Gawing lower-case, tanggalin ang mga link, @mention at #hashtag, alisin ang bantas at mga numero, pagsamahin ang sobrang whitespace, tapos hatiin ayon sa espasyo. Tinatanggal ang mga token na kulang sa tatlong character at ang mga token na nasa stopword set. Gamitin ang slider para panoorin ang isang komento habang dumadaan ito sa bawat yugto. Ang punto: bawat hakbang ay isang rule na nakikita mo, hindi black box.

--- key: p3 src: 14c1228658
**Desisyong analytical ang stopwords.** Ang mga salitang tulad ng "the", "ang" o "sa" ay may dalang grammar, hindi laman, kaya sila ang mangingibabaw sa kahit anong word count. Ang default na set ay English kasama ang isang listahan ng Filipino. Magdagdag ka ng sarili mo: kung mapansin mo mamaya na ang mga pangalan ng lugar o ang salitang "hospital" ang lumulunod sa resulta, ilagay sila sa box ng dagdag na salita at banggitin ito sa write-up mo. Ang pagtanggal ng isang salita ay desisyong dapat kaya mong ipagtanggol.

--- key: p4 src: bd954a89f2
**Bakit nauuna ang paglilinis bago ang pagbasa ng lugar.** Ang geoparsing sa susunod na hakbang ay gumagamit ng *orihinal* na text, dahil nakasalalay sa malalaking titik ang mga pangalan ng lugar ("Baguio" na lungsod, hindi "baguio" na salita). Ang mga nalinis na token ay gagamitin mamaya, sa Chapter 2, kapag pinaghahambing na natin ang sinasabi ng bawat lugar.
