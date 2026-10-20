--- key: title src: 1e3ffeb078
TF-IDF + K-Means themes, ginpaanggid sa tunga sang mga lugar

--- key: p1 src: 23d3d4d8f2
**Paano nagatakos ang mga piraso.** Ginahatagan sang TF-IDF sang weight ang kada termino suno sa kon ano kasunson ini nagaguwa sa isa ka komento kontra sa kon ano ini katalagsa sa tanan nga komento, gani ang mga pulong nga makita bisan diin ginapiga kag ang mga pulong nga nagapabulag ginapabaskog. Dayon ginagrupo sang K-Means ang mga komento nga malapit sa isa kag isa sa sina nga weighted space. Ang TF-IDF ang nagadesisyon kon ano ang buot silingon sang "pareho"; ang K-Means nagasunod lang. Ginagamit sang TALA ang unigrams kag bigrams, max_df 0.9, min_df 3 kag 1,200 ka features.

--- key: p2 src: e8f66dee7e
**Pagpili sang k gamit ang silhouette.** Para sa kada komento, ang a amo ang iya mean cosine distance sa iya kaugalingon nga theme kag ang b amo ang iya mean distance sa pinakamalapit nga iban nga theme; s = (b - a) / max(a, b). Ang average halin -1 tubtob 1. Kon malapit sa 1, maayo ang pagkabulag; kon malapit sa 0, nagasapaw ang mga theme. Sa sini nga data, manubo ang scores (mga 0.05 sa k = 4 kag 0.08 sa k = 8) kay malip-ot ang mga komento kag parehas ang ila vocabulary. Ang mas mataas nga score para sa mas daku nga k indi awtomatiko nga mas maayo: pamangkuta kon ang mga card mabasa bilang lain-lain nga theme nga mahatagan sang ngalan.

--- key: p3 src: c6c4891f57
**Ang siod sang ngalan sang probinsya (matuod gihapon).** Kon ginbilin ang mga ngalan sang lugar, ang k = 4 nagahimo sang theme nga may 1,131 ka komento nga ang top terms amo ang *del*, *del norte*, *del sur*, *norte*, *sur*, *surigao*. Geography ina, indi theme: talagsa ang mga ngalan sang probinsya, gani ginscore sila sang IDF nga pinasahi. Gani ginatago sang TALA ang mga ngalan sang lugar sa default, kag ang geographic nga theme nagatunaw sa mga content theme (paghulat, staff, rural health units, kabilugan nga eksperyensya). I-untick ang kahon agod makita mo mismo ang siod, kag isugid sa imo write-up nga ginhalin mo ang mga ngalan sang lugar.

--- key: p4 src: 8563de396e
**Bahin sang theme kada lugar.** Ang stacked bar nagapakita, sa sulod sang kada lugar, kon pila ka porsiyento sang mga komento ang nahulog sa kada theme (ang kada row nagasum sa 100%). Tungod kay parehas nga vocabulary ang mga theme, halos parehas ang bahin sa tanan nga lugar diri. Ang auto-labels halin sa rank-weighted matches sa tunga sang top terms kag sang aspect lexicon; pirmi ini usisaa kontra sa listahan sang mga termino.
