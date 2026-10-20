--- key: title src: ed749f742e
Text vs GPS: pagbasa sa lugar, pagsuri sa coordinates

--- key: p1 src: a48d5f2680
**Dalawang saksi para sa iisang lokasyon.** Bawat komento ay may GPS point at, kadalasan, isang pangalan ng lugar sa sarili nitong mga salita. Wala sa dalawa ang mapagkakatiwalaan nang mag-isa: puwedeng nawawala ang GPS, napagpalit, o naiwan sa huling fix ng device, at puwede ring magkamali ng type ang tao sa pangalan ng bayan. Pinaghahambing sila ng hakbang na ito. Kapag tugma sila, kampante tayo; kapag hindi, may isa sa kanilang mali, at ang pattern ng hindi pagtutugma ang nagsasabi kung alin.

--- key: p2 src: d1aa520507
**Geoparsing gamit ang mga rule, hindi gamit ang model.** Hinahanap ng parser sa bawat komento ang pinakamahabang sunud-sunod na hanggang apat na token na tugma sa isang pangalan o alias sa bundled na gazetteer ng mga rehiyon, probinsya, lungsod at munisipyo (GeoNames, CC BY 4.0). Dahil sarado ang vocabulary at pare-pareho ang capitalization ng mga komento, ang rule-based na matcher ay deterministic, mabilis, at kayang ipaliwanag sa isang talata, na hindi kaya ng isang statistical na named-entity model. Mahalaga ang longest match: dapat manalo ang "Cagayan de Oro" laban sa "Cagayan", at ang "Davao de Oro" laban sa "Davao". Nilalaktawan ang mga salita pagkatapos ng *Brgy*, *Purok* o *Sitio*, dahil barangay ang pinapangalanan ng mga iyon, hindi munisipyo.

--- key: p3 src: 3d30c0a8e7
**Kalabuan at kung paano ito nilulutas.** Maraming lugar ang may pangalang "San Fernando". Una, naghahanap ang parser ng probinsya o rehiyong kasabay na binanggit sa parehong komento ("San Fernando, Pampanga"). Kapag wala, pinapanalo nito ang pangalang malinaw na nangingibabaw ayon sa populasyon (ang lungsod ng Bacolod ay hindi bababa sa 1.5 beses na mas malaki kaysa sa kahit anong kapangalan nito), maliban sa mga pangalan ng santo, na hindi kailanman pinagpapasyahan sa ganoong paraan. Ang hindi pa rin napagpapasyahan ay minamarkahang *ambiguous* at hindi isinasama sa paghahambing, sa halip na hulaan.

--- key: p4 src: 6115d6a5ea
**Distansya, at kung bakit mahalaga ang threshold.** Pinaghahambing ang GPS at ang binanggit na lugar gamit ang haversine great-circle distance sa isang sphere na may radius na 6371 km. *Tugma* ang isang komento kapag nasa loob ng threshold ang distansyang iyon. Isang point ang lugar (ang centroid nito sa gazetteer), pero puwedeng 100 km ang lapad ng isang probinsya, kaya ang masikip na threshold ay nagfa-flag ng mga komentong ayos naman, at ang maluwag ay nagpapalampas ng totoong mali. Galawin ang slider at panoorin ang pagbabago ng bilang ng hindi tugma: katangian ng threshold mo ang numerong iyon, hindi lang ng data.

--- key: p5 src: 703c7760b2
**Ang bitag sa dataset na ito.** Mga 31% ng bundled na coordinates ang invalid: tuluyan silang nasa labas ng Pilipinas (binabanggit ng unang row ang Cagayan de Oro pero nasa malapit sa London ang point nito). Ang isa pang 8% ay valid na point pero malayo sa binanggit na lugar. Kung pagsasamahin, halos apat sa bawat sampung coordinate. Ang mapang diretsong iginuhit mula sa GPS column ay magmumukhang kapani-paniwala pero malaki ang mali. Sadya ang pagkakasunod-sunod ng status: iniuulat na invalid ang isang invalid na GPS kahit may text din, dahil kailangan pa rin itong ayusin anuman ang sabihin ng text.

--- key: p6 src: fb06ec710e
**Pagpili kung ano ang gagamitin ng mga susunod na hakbang.** Ang *Ayusin gamit ang text* ay nagpapanatili sa GPS kapag valid ito at tugma (o walang binanggit na lugar), at kung hindi, ipinapalit nito ang coordinates ng binanggit na lugar. Ang *GPS lang* ay nagpapanatili lang ng mga valid na point na nasa lupain ng Pilipinas. Ang *Kung saan lang tugma ang dalawa* ang pinakamahigpit at may pinakamaliit na sample. Mas maraming komento ang nasasaklaw kapag nag-repair, kapalit ng paglalagay ng komento sa centroid ng isang lugar, kaya ang inayos na point ay isang lugar, hindi isang street address.
