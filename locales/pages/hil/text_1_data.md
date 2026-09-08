--- key: title src: d1849dc686
Ang preprocessing pipeline (halin sa NLP.ipynb)

--- key: p1 src: 0772da8ad5
Sa preprocessing mo ginadesisyunan kon ano ang ginatugutan mo nga makita sang computer. May punctuation, dalagko nga letra, filler words, emoji, numero, typo kag nagsimbog nga lenguahe ang raw text. Ang iban sina signal kag ang iban saba, kag *ang kon diin sa diin nagadepende gid sa imo pamangkot sa pagpanalawsaw.* Indi ritwal sang pagtinlo ang preprocessing — desisyon ini sa pagpanalawsaw nga kinahanglan mo masarangan depensahan.

--- key: p2 src: 59f67efe58
**Amo ini ang ginahimo sang pipeline, sunod-sunod.** Lowercase → kuhaa ang URLs → kuhaa ang `@mentions` kag `#hashtags` → kuhaa ang punctuation (Unicode-aware, gani kaya sini ang kurbado nga panipi) → kuhaa ang mga numero → tipuna ang espasyo → bahina sa espasyo → kuhaa ang tokens nga wala pa sing 3 ka letra → kuhaa ang stopwords.

--- key: p3 src: 6b6f3058ba
**Amo ini ang bayad sini sa amo nga corpus.** Ang 292,674 ka raw nga pulong nangin 174,562 ka tokens — 40% sang text ang imo ginahaboy. Ang nabilin nga bokabularyo 551 ka lain-lain nga pulong. Daku ina nga bawas, kag amo gid ina ang punto: ang nabilin dapat amo ang bahin nga takos isipon.

--- key: p4 src: ab9dc72244
**Ang desisyon sa stopwords.** Ang 318 ka English stopwords halin sa standard nga listahan sang scikit-learn; ang 147 ka Filipino stopwords (`ang`, `sa`, `mga`, `naman`) bulag nga ginsakot kag gina-toggle sa sidebar. Patya ang Filipino list dayon padalagana liwat ang bisan ano nga page sa ulihi — magabaha ang mga Tagalog function word sa ibabaw sang kada frequency chart, kag amo gid ina ang nagakatabo kon English-only nga tools ang gamiton mo sa Taglish nga data.

--- key: p5 src: 0a2726eb69
**Diri ka masakitan sang defaults.** Ginapanas sang pagsulundan sa numero ang `24/7`, `3 hours` kag `P500`. Ginapanas sang pagsulundan sa punctuation ang `!` sa "three hours again!" — kon kaakig ang imo ginatun-an, bag-o ka lang nagkuha sang kaakig. Ginapanas sang 3-letra nga minimum ang `ER`, `OB` kag `IV`. Wala sing sala diri sa kabilugan, kag mahimo tanan ini sala para sa imo.

--- key: p6 src: 3e1be010df
**Himua ini antes ka magpadayon.** Basaha ang magparis nga raw kag cleaned sa idalom. Kon ang komento nga nahangpan mo nangin komento nga indi mo na mahangpan, ibalik sa pihak ang nadula nga mga pulong sa custom stopword box sang sidebar — buot silingon, hunahunaa liwat ang pagsulundan, indi ang halimbawa.
