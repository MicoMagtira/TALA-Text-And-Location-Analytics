--- key: title src: 1e3ffeb078
TF-IDF + K-Means nga mga tema, gitandi tali sa mga lugar

--- key: p1 src: 23d3d4d8f2
**Giunsa pagsumpay sa mga piraso.** Ang TF-IDF mohatag og timbang sa matag term sumala sa kadaghan niini sa usa ka komento batok sa kanihit niini sa tanang komento, busa madugmok ang mga pulong nga makit-an bisan asa ug mapakusog ang mga pulong nga nagpalahi. Dayon igrupo sa K-Means ang mga komento nga duol sa usag usa niana nga weighted space. Ang TF-IDF ang mohukom kung unsay pasabot sa "similar"; mosunod ra ang K-Means. Ang TALA mogamit og unigrams ug bigrams, max_df 0.9, min_df 3 ug 1,200 ka features.

--- key: p2 src: e8f66dee7e
**Pagpili sa k gamit ang silhouette.** Para sa matag komento, ang a kay ang mean cosine distance niini sa iyang kaugalingong tema ug ang b ang mean distance sa labing duol nga laing tema; s = (b - a) / max(a, b). Ang average gikan -1 hangtod 1. Ang duol sa 1 nagpasabot nga bulag kaayo; ang duol sa 0 nagpasabot nga nag-overlap ang mga tema. Niini nga data, ubos ang mga score (mga 0.05 sa k = 4 ug 0.08 sa k = 8) kay mubo ang mga komento ug managsama og vocabulary. Ang mas taas nga score sa mas dako nga k dili awtomatik nga mas maayo: pangutan-a kung ang mga card ba mabasa nga lahi-lahi ug mangalanan nga mga tema.

--- key: p3 src: c6c4891f57
**Ang lit-ag sa ngalan sa probinsya (tinuod gihapon).** Kung dili itago ang mga ngalan sa lugar, ang k = 4 mohimo og tema nga 1,131 ka komento kansang top terms kay *del*, *del norte*, *del sur*, *norte*, *sur*, *surigao*. Geography kana, dili tema: talagsaon ang mga ngalan sa probinsya, busa gi-score kini sa IDF nga distinctive. Busa gitago sa TALA ang mga ngalan sa lugar sa default, ug ang geographic nga tema matunaw ngadto sa mga tema sa content (paghulat, staff, rural health units, kinatibuk-ang kasinatian). Tangtangi og tsek ang kahon aron makita nimo mismo ang lit-ag, ug isulti sa imong write-up nga imong gi-exclude ang mga ngalan sa lugar.

--- key: p4 src: 8563de396e
**Theme share matag lugar.** Ang stacked bar nagpakita, sulod sa matag lugar, pila ka porsyento sa mga komento ang nahulog sa matag tema (ang matag row mo-total og 100%). Tungod kay managsama og vocabulary ang mga tema, susama ra ang mga share sa tanang lugar diri. Ang auto-labels gikan sa rank-weighted nga matches tali sa top terms ug sa aspect lexicon; kanunay kini susiha batok sa lista sa mga term.
