--- key: title src: c443695e58
Mga lugar: mula sa mga point papunta sa mga rehiyon at cluster

--- key: p1 src: 9e04298220
**Bakit kailangang mamangkat.** Ang isang komento ay isang kuwento lang; ang isang lugar ay isang sample. Pinaghahambing ng Chapter 2 ang sinasabi ng mga lugar, kaya kailangan munang may place label ang bawat komento. Dalawa ang paraan para makakuha nito, at magkaibang tanong ang sinasagot nila.

--- key: p2 src: f1707fe2eb
**Rehiyon: gamitin ang isinulat ng mga tao.** Kinukuha ng bawat komento ang rehiyon ng lugar na binabanggit nito (mula sa gazetteer). Ang komentong walang magagamit na pangalan ay kinukuha ang pinakamalapit na region centroid sa point nito. Madali itong basahin, matatag, at walang kailangang parameter, pero administratibo ang mga rehiyon: puwedeng malaki ang agwat nila sa laki at populasyon, at dito ay iginuguhit ang isang rehiyon bilang bubble sa centroid nito, hindi bilang hangganan.

--- key: p3 src: 97233bbec5
**Cluster: hayaang ang density ang magpasya.** Pinapalaki ng DBSCAN ang isang cluster mula sa kahit anong point na may hindi bababa sa *min_samples* na kapitbahay sa loob ng *eps*, at minamarkahang noise ang mga point na hindi kabilang sa kahit anong siksik na lugar. Hindi nito kailangang malaman ang bilang ng cluster nang maaga, at hindi nito pinipilit na isama sa grupo ang bawat point. Parehong mahalaga ang dalawang knob: ang maliit na eps ay naghahati sa isang lungsod sa maraming cluster, at ang malaki ay pinagsasama ang magkakatabing lungsod sa iisang bloke.

--- key: p4 src: 8655589831
**Projected na metro, hindi degrees.** Distansya ang eps ng DBSCAN, kaya pina-project muna ang coordinates sa UTM na metro. Mas maikli ang isang degree ng longitude kaysa sa isang degree ng latitude habang lumalayo sa equator, kaya kung patatakbuhin ang DBSCAN sa hilaw na degrees, ellipse ang iguguhit nito, hindi bilog.

--- key: p5 src: 6a40392629
**Ang k-distance elbow.** Para sa bawat point, kunin ang distansya nito sa ika-k na pinakamalapit na kapitbahay at i-sort ang mga distansyang iyon. Karamihan sa mga point ay nasa siksik na lugar at maliit ang value; malaki naman ang sa mga napag-iwanan, kaya biglang tumataas ang curve sa hangganan. Ang magandang eps ay malapit sa elbow na iyon. Itakda ang k malapit sa min_samples. Gabay ang elbow, hindi patunay: tingnan ang mapa at suriin kung tumutugma ang mga cluster sa mga lugar na kilala mo.

--- key: p6 src: dbab5c1879
**Resulta rin ang noise.** Hindi error ang mga point na hindi naisama ng DBSCAN sa kahit anong cluster. Kadalasang magiging noise ang mga komento mula sa probinsya na nakakalat sa pagitan ng mga bayan, at tapat iyon: hindi sila kabilang sa isang siksik na lugar. Sa Region mode, ang mga komentong walang kahit anong lokasyon lang ang walang lugar.

--- key: p7 src: fc3b88474e
**Nakapatong sa centroid ng bayan ang mga inayos na point.** Kapag may binanggit na lugar ang isang komento pero mali ang GPS nito, eksaktong inilalagay ang inayos na point sa centroid ng lugar na iyon. Kaya sa Cluster mode, ang DBSCAN sa mga inayos na point ay kadalasang bumubuo ng isang cluster kada binanggit na bayan, at mukhang patag ang k-distance curve dahil maraming point ang may parehong-parehong coordinates. Ang "Kung saan lang tugma ang dalawa" ay nagpapanatili ng mga GPS-only na point, kaya gamitin ito bilang view na pangkumpara.
