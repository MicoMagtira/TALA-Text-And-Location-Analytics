--- key: title src: cd2b6a3532
Getis-Ord Gi* hotspots

--- key: p1 src: 5a038d0939
**Ang tanong.** May mga kumpol ng negatibong komento na tsamba lang. Tinatanong ng Gi* kung ang isang cell at ang mga kapitbahay nito, kapag pinagsama, ay mas negatibo (hot) o hindi gaanong negatibo (cold) kaysa sa ibibigay ng random na pag-shuffle ng parehong mga value. Inilalagay ng TALA ang mga komento sa mga parisukat na cell, itinatakda ang value x ng bawat cell bilang bahagi ng mga negatibong komento nito (tinatanggal ang mga cell na mas kaunti ang komento kaysa sa minimum), at kinukuwenta ang Gi* sa mga cell na iyon.

--- key: p2 src: fc9b1bbb8c
**Ang formula.** Kung may n na cell, mean na X-bar at standard deviation na S ng x, at binary weights na w_ij = 1 kapag nasa loob ng radius ng cell i ang cell j (kasama ang i mismo): Gi*_i = (sum_j w_ij x_j - X-bar * W_i) / (S * sqrt((n * sum_j w_ij^2 - W_i^2) / (n - 1))), kung saan W_i = sum_j w_ij. Z-score na agad ang resulta: ang mga value na nasa o lampas sa 1.645, 1.960 at 2.576 ay hot sa 90%, 95% at 99% confidence (cold naman ang mga negatibo). Ang mga kapitbahay ay galing sa isang BallTree sa metric (UTM) na coordinates.

--- key: p3 src: 5e521fc88c
**Multiple testing.** Ang isang test sa 95% ay mali 5% ng pagkakataon, pero dito sinusuri ang bawat cell, kaya may ilang cell na magmumukhang "significant" dahil sa tsamba kahit walang pattern. Kaya ang 99% na klase ang pinakaligtas na basahin at dapat pagdudahan ang mga 90% cell. Sa bundled na data na may default na settings (20 km na cell, 50 km na radius, hindi bababa sa 10 komento), 309 cell ang sinusuri; 4 ang hot (walang 99%) at 7 ang cold. Ang pinakamalakas na hot cell (z = 2.4, 50% negatibo sa 10 komento) ay malapit sa Apayao. Mga 3.6% lang ng mga cell ang significant sa alinmang direksyon, mas kaunti pa sa 10% na ibibigay ng tsamba lang sa 90% na level, kaya walang kapani-paniwalang kumpol ng reklamo ang dataset na ito sa kabuuan. Lehitimong natuklasan iyon.

--- key: p4 src: 4e61c4f9aa
**Mahalaga ang mga pinipili mo.** Dapat sumaklaw ang radius ng hindi bababa sa dalawang cell, kung hindi ay halos hindi naihahambing ang bawat cell sa mga kapitbahay nito. Mas matatag ang mas malalaking cell pero lumalabo ang lokal na detalye (ang modifiable areal unit problem). Kapag pinili ang "waiting", nalilimitahan ang mapa sa mga komentong bumabanggit ng paghihintay, at binibilang na negatibo ang isang komento kapag negatibo ang dating ng mga tumugmang pangungusap nito. Pantay ang tingin ng binary weights sa lahat ng kapitbahay; karaniwang alternatibo ang inverse-distance weights.
