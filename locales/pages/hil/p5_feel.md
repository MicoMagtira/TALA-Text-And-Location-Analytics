--- key: title src: 17008c972b
Sentiment kada lugar nga may matinud-anon nga intervals

--- key: p1 src: 48406e3839
**VADER.** Isa ka rule-based lexicon scorer: ang kada pulong may valence, ang rules ang nagahandle sang negation, intensifiers kag punctuation, kag ang sum ginapiga sa isa ka compound score sa tunga sang -1 kag 1. Negatibo ang komento kon compound <= -0.05 (ang kaugalingon nga cut-off sang VADER). Ginhimo ini para sa English nga social media, gani ang Filipino kag Taglish nga text bahin lang ang naintiendihan; basaha ang resulta bilang *relative* sa tunga sang mga lugar, indi bilang absolute nga kamatuoran. Ginascore sang TALA ang kada komento sing isa ka beses kada dataset kag ginagamit ini liwat sa tikang 5, 6, 8 kag 9.

--- key: p2 src: f32c570b08
**Ngaa may intervals.** Ang % negatibo sang isa ka lugar isa ka proportion k/n, kag ang diutay nga n nagahimo sini nga magulo. Ang Wilson score interval sa z = 1.96 amo ang centre = (p + z^2/2n) / (1 + z^2/n), half-width = z * sqrt(p(1-p)/n + z^2/4n^2) / (1 + z^2/n). Indi pareho sang textbook nga p +/- z*sqrt(p(1-p)/n), indi gid ini maggwa sa [0, 1] kag maayo ang iya pamatasan bisan diutay ang n ukon ang p malapit sa 0 ukon 1.

--- key: p3 src: 6047d0f850
**Ano ang ginasiling sang bundled nga data.** Sa kabilugan, 36% sang 12,000 ka komento ang negatibo ang score. Kada rehiyon, halin ini sa 31% (Ilocos Region, n = 575) tubtob 39% (Western Visayas, n = 895, 95% interval 35.6 tubtob 42.0). Nagasapaw gid ina nga mga interval: wala ginasuportahan sang data ang pag-ranggo sang kalabanan nga rehiyon kontra sa isa kag isa. Ang National Capital Region may 157 lang ka komento, gani malapad ang iya interval (26.8 tubtob 41.5). Amo ina nga ang mga lugar nga kubos sa minimum n ginapa-abuhon imbes nga i-ranggo.

**Ang pagsapaw giya lang, indi test.** Ang nagasapaw nga intervals wala nagapamatuod nga wala sing kinalain, kag ang wala nagasapaw wala man nagapamatuod nga may ara. Para sa pormal nga pagpaanggid, gamita ang two-proportion test, kag dumdoma nga ang madamo nga pagpaanggid sing dungan nagapadamo sang false alarms.
