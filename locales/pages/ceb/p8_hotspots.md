--- key: title src: cd2b6a3532
Getis-Ord Gi* nga mga hotspot

--- key: p1 src: 5a038d0939
**Ang pangutana.** Ang ubang pundok sa negatibong komento sulagma ra. Ang Gi* nangutana kung ang usa ka cell ug ang mga silingan niini, kung tingban, mas negatibo (hot) o dili kaayo negatibo (cold) kaysa sa ihatag sa random nga pag-shuffle sa samang mga value. Ibutang sa TALA ang mga komento ngadto sa square cells, i-set ang value x sa matag cell sa bahin niini sa negatibong komento (ilabay ang mga cell nga mas gamay og komento kaysa sa minimum), ug kuwentahon ang Gi* sa maong mga cell.

--- key: p2 src: fc9b1bbb8c
**Ang formula.** Uban sa n ka cell, mean X-bar ug standard deviation S sa x, ug binary weights w_ij = 1 kung ang cell j naa sulod sa radius sa cell i (apil ang i): Gi*_i = (sum_j w_ij x_j - X-bar * W_i) / (S * sqrt((n * sum_j w_ij^2 - W_i^2) / (n - 1))), diin W_i = sum_j w_ij. Z-score na ang resulta: ang mga value nga 1.645, 1.960 ug 2.576 o labaw kay hot sa 90%, 95% ug 99% confidence (ang mga negatibo kay cold). Ang mga silingan gikan sa BallTree sa metric (UTM) coordinates.

--- key: p3 src: 5e521fc88c
**Multiple testing.** Ang usa ka test sa 95% masayop 5% sa higayon, apan diri gi-test ang matag cell, busa adunay mga cell nga murag "significant" tungod sa swerte bisan walay pattern. Mao kana nganong ang 99% nga klase ang labing luwas nga pagbasa ug ang 90% nga mga cell angayang duhaduhaan. Sa bundled nga data gamit ang mga default (20 km nga cells, 50 km nga radius, labing menos 10 ka komento), 309 ka cell ang gi-test; 4 ang hot (walay sa 99%) ug 7 ang cold. Ang pinakakusog nga hot cell (z = 2.4, 50% negatibo sa 10 ka komento) naa duol sa Apayao. Mga 3.6% ra sa mga cell ang significant sa bisan asang direksyon, mas gamay kaysa 10% nga ihatag sa sulagma ra sa 90% nga level, busa walay makapakombinsir nga pundok sa reklamo kini nga dataset sa kinatibuk-an. Lehitimo kana nga kaplag.

--- key: p4 src: 4e61c4f9aa
**Importante ang mga pinili.** Ang radius kinahanglan motabon og labing menos duha ka cell, kay kung dili, halos dili matandi ang matag cell sa mga silingan. Ang mas dagkong cell mas stable apan mopalabo sa lokal nga detalye (ang modifiable areal unit problem). Ang pagpili sa "Paghulat" mopugong sa mapa sa mga komento nga naghisgot og paghulat ug moihap sa komento nga negatibo kung negatibo ang basa sa mga sentence niini nga nag-match. Ang binary weights motratar sa tanang silingan nga managsama; ang inverse-distance weights usa ka kasagarang alternatibo.
