--- key: title src: d1849dc686
Ang preprocessing pipeline (gikan sa NLP.ipynb)

--- key: p1 src: 0772da8ad5
Sa preprocessing nimo mahukman kung unsa ang gitugotan nimo nga makita sa computer. Adunay punctuation, dagkong letra, filler words, emoji, numero, typo ug sinagol nga pinulongan ang raw text. Ang uban niana kay signal ug ang uban kay saba, ug *ang kung hain sa hain nagdepende gyud sa imong pangutana sa panukiduki.* Dili ritwal sa paglimpyo ang preprocessing — desisyon kini sa panukiduki nga kinahanglan nimong madepensahan.

--- key: p2 src: 59f67efe58
**Kini ang gibuhat sa pipeline, sunod-sunod.** Lowercase → tangtanga ang URLs → tangtanga ang `@mentions` ug `#hashtags` → tangtanga ang punctuation (Unicode-aware, mao nga kaya niini ang kulot nga panipi) → tangtanga ang mga numero → hiusaha ang espasyo → bahina sa espasyo → kuhaa ang tokens nga wala pay 3 ka letra → kuhaa ang stopwords.

--- key: p3 src: 6b6f3058ba
**Kini ang bayad niini sa maong corpus.** Ang 292,674 ka raw nga pulong mahimong 174,562 ka tokens — 40% sa text ang imong gilabay. Ang nahibiling bokabularyo kay 551 ka lahi nga pulong. Dako kanang kunhod, ug mao ra gyud kanay punto: ang nahibilin angay nga mao ang bahin nga takos ihapon.

--- key: p4 src: ab9dc72244
**Ang desisyon sa stopwords.** Ang 318 ka English stopwords gikan sa standard nga listahan sa scikit-learn; ang 147 ka Filipino stopwords (`ang`, `sa`, `mga`, `naman`) bulag nga gikabit ug gi-toggle sa sidebar. Palonga ang Filipino list dayon padagana pag-usab ang bisan unsang page unya — mobaha ang mga Tagalog function word sa ibabaw sa matag frequency chart, ug mao gyud kanay mahitabo kung English-only nga tools ang gamiton nimo sa Taglish nga data.

--- key: p5 src: 0a2726eb69
**Dinhi ka masakitan sa defaults.** Gipapas sa lagda sa numero ang `24/7`, `3 hours` ug `P500`. Gipapas sa lagda sa punctuation ang `!` sa "three hours again!" — kung kasuko ang imong gitun-an, bag-o lang kang nagtangtang og kasuko. Gipapas sa 3-letra nga minimum ang `ER`, `OB` ug `IV`. Walay sayop niini sa kinatibuk-an, ug mahimong tanan kini sayop para nimo.

--- key: p6 src: 3e1be010df
**Buhata kini sa dili pa ka mopadayon.** Basaha ang magparis nga raw ug cleaned sa ubos. Kung ang komento nga imong nasabtan mahimong komento nga dili na nimo masabtan, ibalik sa pikas ang nawala nga mga pulong sa custom stopword box sa sidebar — buot ipasabot, hunahunaa pag-usab ang lagda, dili ang pananglitan.
