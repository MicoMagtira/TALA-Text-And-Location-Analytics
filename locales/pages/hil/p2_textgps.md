--- key: title src: ed749f742e
Text vs GPS: pagbasa sang lugar, pag-usisa sang coordinates

--- key: p1 src: a48d5f2680
**Duha ka saksi para sa isa ka location.** Ang kada komento may GPS point kag, kasagaran, isa ka ngalan sang lugar sa kaugalingon nga pulong sang nagsulat. Wala sing isa sa ila nga masaligan nga isahanon: ang GPS mahimo nga wala, nabaylo, ukon nagbalik sa katapusan nga fix sang device, kag ang tawo mahimo nga masayop sa pag-type sang banwa. Ini nga tikang nagapaanggid sa duha. Kon nagauyon sila, sigurado kita; kon wala nagauyon, isa sa ila ang sayop, kag ang pattern sang wala pag-uyon ang nagasugid kon diin.

--- key: p2 src: d1aa520507
**Geoparsing paagi sa rules, indi paagi sa model.** Ginausisa sang parser ang kada komento para sa pinakalawig nga sunod-sunod nga tubtob apat ka tokens nga nagatugma sa isa ka ngalan ukon alias sa bundled nga gazetteer sang mga rehiyon, probinsya, siyudad kag munisipyo (GeoNames, CC BY 4.0). Tungod kay sarado ang vocabulary kag pirmi nga husto ang capitalisation sang mga komento, ang rule-based matcher deterministic, madasig, kag maathag sa isa lang ka paragraph — butang nga indi masarangan sang statistical named-entity model. Importante ang longest match: dapat magdaog ang "Cagayan de Oro" sa "Cagayan", kag ang "Davao de Oro" sa "Davao". Ginalaktawan ang mga pulong pagkatapos sang *Brgy*, *Purok* ukon *Sitio*, kay barangay ang ginangalanan sina, indi munisipyo.

--- key: p3 src: 3d30c0a8e7
**Ambiguity kag kon paano ini ginasolusyunan.** Ang "San Fernando" ngalan sang pila ka lugar. Una nga ginapangita sang parser ang probinsya ukon rehiyon nga ginsambit man sa amo man nga komento ("San Fernando, Pampanga"). Kon wala, ginapadaog niya ang ngalan nga klaro nga nagapanguna suno sa populasyon (ang siyudad sang Bacolod indi magkubos sa 1.5 ka pilo nga mas daku sangsa bisan ano nga kapareho sang ngalan), luwas lang sa mga ngalan sang santos, nga indi gid ginasolusyunan sa sina nga paagi. Ang wala gihapon madesisyunan ginamarkahan nga *ambiguous* kag ginahalin sa pagpaanggid imbes nga tag-anan.

--- key: p4 src: 6115d6a5ea
**Kalayuon, kag ngaa importante ang threshold.** Ginapaanggid ang GPS kag ang ginsambit nga lugar gamit ang haversine great-circle distance sa isa ka sphere nga may radius nga 6371 km. Ang komento *nagauyon* kon ina nga kalayuon ara sa sulod sang threshold. Ang lugar isa ka point (ang iya gazetteer centroid), pero ang isa ka probinsya mahimo nga 100 km ang kalapad, gani ang hugot nga threshold nagamarka sang mga komento nga wala man sing problema, kag ang maluwag nagapatawad sang matuod nga mga sayop. Hulaga ang slider kag tan-awa ang pagbag-o sang disagree count: ang numero kinaiya sang imo threshold, indi sang data lang.

--- key: p5 src: 703c7760b2
**Ang siod sa sini nga dataset.** Mga 31% sang bundled nga coordinates ang invalid: nahulog sila sa gwa gid sang Pilipinas (ang una nga row nagasambit sang Cagayan de Oro pero ara malapit sa London). Ang dugang nga 8% valid nga points pero malayo sa lugar nga ginsambit. Kon pagtingubon, mga apat sa kada napulo ka coordinates. Ang mapa nga gindrowing direkta halin sa GPS column daw matuod tan-awon pero sayop gid. Hungod ang sunod sang status: ang invalid nga GPS ginareport nga invalid bisan may text man, kay kinahanglan ini ayuhon bisan ano pa ang ginasiling sang text.

--- key: p6 src: fb06ec710e
**Pagpili kon ano ang gamiton sang masunod nga mga tikang.** Ang *Ayuhon halin sa text* nagatipig sang GPS kon valid ini kag nagauyon (ukon wala sing lugar nga ginsambit), kag kon indi, ginabaylo ini sang coordinates sang ginsambit nga lugar. Ang *GPS lang* nagatipig lang sang valid nga points sa duta sang Pilipinas. Ang *Kon diin lang nagauyon ang duha* amo ang pinakaistrikto kag pinakadiutay nga sample. Ang pag-ayo nagadugang sang coverage, pero ang kabayaran amo nga ginapilit ang komento sa centroid sang lugar — amo ina nga ang gin-ayo nga point isa ka lugar, indi address sang isa ka kalye.
