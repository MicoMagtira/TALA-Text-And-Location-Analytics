--- key: title src: 8c5bbd5d86
Contrastive keywords: weighted log-odds

--- key: p1 src: 510e357d91
**Bakit hindi na lang bilangin ang mga salita?** Ang pinakamadalas na salita sa kahit anong lugar ay ang pinakamadalas na salita rin kahit saan ("staff", "hospital"). Para makita kung ano ang *nagpapaiba* sa isang lugar, ihahambing mo ito sa isang reference group at itatanong kung aling mga salita ang kumikiling sa isang panig. Hindi rin uubra ang hilaw na ratio: ang salitang dalawang beses lumabas sa lugar A at hindi kailanman sa iba ay may infinite na ratio.

--- key: p2 src: 32e35980c0
**Ang method (Monroe, Colaresi & Quinn 2008).** Para sa bawat term w, hayaang y_a at y_b ang bilang nito sa grupong A at B, n_a at n_b ang kabuuang salita sa bawat isa, at alpha_w ang Dirichlet prior na proporsyonal sa bilang ng salita sa *lahat* ng komento, na iniskala para ang kabuuan ng mga alpha ay a0 = 500. Kung gayon, delta = log((y_a + alpha_w) / (n_a + a0 - y_a - alpha_w)) - log((y_b + alpha_w) / (n_b + a0 - y_b - alpha_w)), ang variance nito ay 1/(y_a + alpha_w) + 1/(y_b + alpha_w), at z = delta / sqrt(variance). Ang positibong z ay nangangahulugang mas karaniwan sa A, at ang negatibo ay sa B. Kapag pinagpalit ang A at B, eksaktong bumabaligtad ang sign.

**Ang ginagawa ng prior.** Hinihila nito ang mga bihirang salita papunta sa pangkalahatang rate nila, kaya hindi puwedeng manguna sa chart ang salitang tatlong beses lang lumabas. Mas maingat ang mas malaking prior. Kapag hinati sa standard deviation, ang "gaano kaiba" ay nagiging "gaano kasigurado": puwedeng malamangan ng mga karaniwang salitang may katamtamang kiling ang mga bihirang salitang may malaking kiling.

--- key: p3 src: cc51916d54
**Nananalo ang mga pangalan ng lugar maliban kung itatago mo sila.** Para sa Central Luzon, ang mga nangungunang term ay *nueva*, *central*, *fernando*, *bulacan*, *zambales* (z mula 21 pababa sa 11), dahil binabanggit ng mga tao roon ang sarili nilang probinsya. Totoo iyon pero hindi balita, kaya itinatago ng page ang mga pangalan ng lugar bilang default (mga salita mula sa pangalan ng rehiyon, probinsya at lungsod, kasama ang bawat lugar na nahanap ng geoparser). Mas tahimik ang natitira: nasa paligid ng 4 ang z ng pinakamalalakas na natirang term. Sa dataset na ito, sumusunod ang mga komento sa magkakaparehong template, kaya maliit ang pagkakaiba ng mga lugar sa sinasabi nila. Ang mabasang "walang gaanong nagpapaiba sa lugar na ito" ay isang resulta, hindi kabiguan.

--- key: p4 src: d0ab8fed44
**Mga limitasyon.** Ang mga term ay iisang salita at pariralang may dalawang salita pagkatapos tanggalin ang stopwords, kaya lumalabas ang mga parirala bilang pares ("handled lab"). Pinipigilan ng minimum-count slider (hindi kailanman bababa sa 5) na ang isang term ay maglarawan lang ng isa o dalawang tao. Sa 17 rehiyon at libu-libong posibleng term, may ilang mataas na z value na lilitaw dahil sa tsamba; ituring na kawili-wili ang z na lampas mga 3, at i-verify gamit ang pinagsama-samang bilang, hindi kailanman sa pagbasa ng mga indibidwal na komento.
