--- key: title src: d1849dc686
Ang preprocessing pipeline (mula sa NLP.ipynb)

--- key: p1 src: 0772da8ad5
Sa preprocessing mo ipinapasya kung ano ang pinapayagan mong mapansin ng computer. May bantas, malalaking letra, filler words, emoji, numero, typo at halong wika ang raw text. Ang iba doon ay signal at ang iba ay ingay, at *ang kung alin sa alin ay nakadepende talaga sa tanong mo sa pananaliksik.* Hindi ritwal ng paglilinis ang preprocessing — desisyon ito sa pananaliksik na kailangan mong kayang ipagtanggol.

--- key: p2 src: 59f67efe58
**Ito ang ginagawa ng pipeline, sunod-sunod.** Lowercase → tanggalin ang URLs → tanggalin ang `@mentions` at `#hashtags` → tanggalin ang bantas (Unicode-aware, kaya kaya nito ang mga kulot na panipi) → tanggalin ang mga numero → pagsama-samahin ang espasyo → hatiin sa espasyo → alisin ang tokens na wala pang 3 letra → alisin ang stopwords.

--- key: p3 src: 6b6f3058ba
**Ito ang halaga nito sa corpus na ito.** Ang 292,674 na raw na salita ay nagiging 174,562 tokens — 40% ng text ang itinatapon mo. Ang natitirang bokabularyo ay 551 na magkakaibang salita. Malaking bawas iyon, at iyon mismo ang punto: ang natira dapat ay ang bahaging sulit bilangin.

--- key: p4 src: ab9dc72244
**Ang desisyon sa stopwords.** Ang 318 English stopwords ay mula sa standard na listahan ng scikit-learn; ang 147 Filipino stopwords (`ang`, `sa`, `mga`, `naman`) ay hiwalay na nakakabit at bina-toggle sa sidebar. Patayin mo ang Filipino list tapos patakbuhin mo ulit ang kahit anong page mamaya — bubuhos ang mga Tagalog function word sa itaas ng bawat frequency chart, at iyon mismo ang nangyayari kapag English-only na tools ang ginamit mo sa Taglish na data.

--- key: p5 src: 0a2726eb69
**Dito ka masasaktan ng defaults.** Binubura ng patakaran sa numero ang `24/7`, `3 hours` at `P500`. Binubura ng patakaran sa bantas ang `!` sa "three hours again!" — kung galit ang pinag-aaralan mo, kakatanggal mo lang ng galit. Binubura ng 3-letrang minimum ang `ER`, `OB` at `IV`. Walang mali rito sa pangkalahatan, at pwedeng lahat ito ay mali para sa iyo.

--- key: p6 src: 3e1be010df
**Gawin mo ito bago ka magpatuloy.** Basahin mo ang magkapares na raw at cleaned sa ibaba. Kung ang komentong naiintindihan mo ay naging komentong hindi mo na maintindihan, ibalik mo sa kabila ang mga nawalang salita sa custom stopword box ng sidebar — ibig sabihin, pag-isipan mong muli ang patakaran, hindi ang halimbawa.
