--- key: title src: cd2b6a3532
Getis-Ord Gi* hotspots

--- key: p1 src: 5a038d0939
**Ang pamangkot.** Ang pila ka tipon sang negatibo nga komento tsamba lang. Ginapamangkot sang Gi* kon ang isa ka cell kag ang iya mga kaingod, kon pagtingubon, mas negatibo (hot) ukon mas diutay ang negatibo (cold) sangsa mahatag sang random nga pagsimbog sang amo man nga mga value. Ginabutang sang TALA ang mga komento sa square nga cells, ginabutang ang value x sang kada cell bilang iya bahin sang negatibo nga komento (ginahalin ang cells nga kulang sa minimum ang komento), kag ginakwenta ang Gi* sa sina nga mga cell.

--- key: p2 src: fc9b1bbb8c
**Ang formula.** Sa n ka cells, mean X-bar kag standard deviation S sang x, kag binary weights w_ij = 1 kon ang cell j ara sa sulod sang radius sang cell i (upod ang i): Gi*_i = (sum_j w_ij x_j - X-bar * W_i) / (S * sqrt((n * sum_j w_ij^2 - W_i^2) / (n - 1))), diin W_i = sum_j w_ij. Ang resulta isa na ka z-score: ang values nga pareho ukon labaw sa 1.645, 1.960 kag 2.576 hot sa 90%, 95% kag 99% confidence (ang negatibo nga katumbas cold). Ang mga kaingod halin sa BallTree sa metric (UTM) nga coordinates.

--- key: p3 src: 5e521fc88c
**Multiple testing.** Ang isa ka test sa 95% sayop sa 5% sang tion, pero diri ang kada cell gina-test, gani may pila ka cell nga daw "significant" paagi sa suwerte bisan wala sing pattern. Amo ina nga ang 99% nga klase ang pinakasegurado nga basa kag ang 90% nga cells dapat duhaduhaan. Sa bundled nga data gamit ang defaults (20 km nga cells, 50 km nga radius, indi magkubos sa 10 ka komento), 309 ka cells ang gin-test; 4 ang hot (wala sa 99%) kag 7 ang cold. Ang pinakamabaskog nga hot cell (z = 2.4, 50% negatibo sa 10 ka komento) ara malapit sa Apayao. Mga 3.6% lang sang cells ang significant sa bisan diin nga direksyon, mas diutay sangsa 10% nga mahatag sang tsamba lang sa 90% nga level, gani wala sing makombinsir nga tipon sang reklamo sa sini nga dataset sa kabilugan. Lehitimo ina nga resulta.

--- key: p4 src: 4e61c4f9aa
**Importante ang mga pinili.** Dapat indi magkubos sa duha ka cell ang radius, kon indi, halos wala ginapaanggid ang kada cell sa iya mga kaingod. Ang mas daku nga cells mas stable pero ginapalubog ang lokal nga detalye (ang modifiable areal unit problem). Kon pilion ang "paghulat", ang mapa nagalimite sa mga komento nga nagasambit sang paghulat kag ginaisip nga negatibo ang komento kon negatibo ang basa sang iya nagtugma nga mga sentence. Ang binary weights nagatratar sa tanan nga kaingod nga parehas; ang inverse-distance weights isa ka komon nga alternatibo.
