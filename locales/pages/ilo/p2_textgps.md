--- key: title src: ed749f742e
Text vs GPS: panagbasa iti lugar, panangsukimat iti coordinates

--- key: p1 src: a48d5f2680
**Dua a saksi para iti maysa a lokasion.** Tunggal komento ket addaan iti GPS point ken, kadawyan, nagan ti lugar a nailanad iti bukodna a sasao. Awan kadagitoy ti mapagtalkan no agmaymaysa: mabalin nga awan ti GPS, nabaliktad, wenno ti naudi a fix ti device ti default-na, ken mabalin a biddut ti panangisurat dagiti tattao iti nagan ti ili. Daytoy nga addang ti mangidilig kadagitoy. No agtunos, sigurado tayo; no saan, maysa kadagitoy ti biddut, ken ti pattern ti di panagtunos ti mangibaga kadatayo no ania.

--- key: p2 src: d1aa520507
**Geoparsing babaen dagiti rule, saan a babaen ti model.** Sukimaten ti parser ti tunggal komento para iti kaatiddogan a sinnaruno a token (agingga iti uppat) nga agtunos iti nagan wenno alias iti bundled a gazetteer dagiti rehion, probinsia, siudad ken munisipalidad (GeoNames, CC BY 4.0). Gapu ta nairikep ti vocabulary ken kanayon a naka-capitalize dagiti komento, ti rule-based a matcher ket deterministic, napardas, ken mailawlawag iti maysa a paragraph — maysa a banag a saan a kabaelan ti statistical a named-entity model. Napateg ti longest match: masapul a ti "Cagayan de Oro" ti mangabak imbes a ti "Cagayan", ken ti "Davao de Oro" imbes a ti "Davao". Malabsan dagiti sao kalpasan ti *Brgy*, *Purok* wenno *Sitio*, gapu ta nagan ti barangay dagita, saan a munisipalidad.

--- key: p3 src: 3d30c0a8e7
**Ambiguity ken no kasano a marisut.** Nagan ti adu a lugar ti "San Fernando". Umuna a biruken ti parser ti probinsia wenno rehion a nadakamat met iti isu met laeng a komento ("San Fernando, Pampanga"). No awan, ipalubos na nga abaken ti nalawag a dominante a nagan babaen ti populasion (ti siudad ti Bacolod ket saan a basbassit ngem 1.5 a daras a dakdakkel ngem aniaman a kanaganna), malaksid kadagiti nagan ti santo, a saan a pulos a marisut iti kasta a wagas. Ti saan pay laeng a nakeddeng ket mamarkaan a *ambiguous* ken maikkat iti panagdilig imbes a pattapattaen.

--- key: p4 src: 6115d6a5ea
**Kaadayo, ken no apay a napateg ti threshold.** Maidilig ti GPS ken ti nadakamat a lugar babaen ti haversine great-circle distance iti sphere nga addaan radius a 6371 km. *Agtunos* ti komento no dayta a kaadayo ket adda iti uneg ti threshold. Ti lugar ket maysa a point (ti gazetteer centroid-na), ngem ti probinsia ket mabalin nga 100 km ti kaakabana, isu a ti nainget a threshold ket mangmarka kadagiti komento a nasayaat met laeng, ken ti nalukay ket mangpakawan kadagiti pudno a biddut. Iyakar ti slider ket kitaen ti panagbaliw ti bilang dagiti saan nga agtunos: ti numero ket agpannuray iti threshold-mo, saan laeng nga iti data.

--- key: p5 src: 703c7760b2
**Ti palab-og iti daytoy a dataset.** Agarup 31% dagiti bundled a coordinates ti invalid: naan-anay nga adda iti ruar ti Filipinas (ti umuna a row ket mangdakamat iti Cagayan de Oro ngem adda iti asideg ti London). Ti sabali pay a 8% ket balido a point nga adayo iti lugar a nadakamat. No pagtiponen, agarup uppat iti kada sangapulo a coordinates. Ti mapa a direkta a naiguhit manipud iti GPS column ket kasla umno ngem nakaro ti biddutna. Ginagara ti urnos ti status: ti invalid a GPS ket maireport nga invalid uray no adda met text, gapu ta masapul a matarimaan daytoy aniaman ti ibaga ti text.

--- key: p6 src: fb06ec710e
**Panagpili iti usaren dagiti sumaruno nga addang.** Ti *Tarimaanen manipud iti text* ket mangtaginayon iti GPS no balido ken agtunos (wenno no awan ti nadakamat a lugar), ket no saan, isukat na ti coordinates ti nadakamat a lugar. Ti *GPS laeng ti pagtalkan* ket mangtaginayon laeng kadagiti balido a point iti daga ti Filipinas. Ti *No agtunos laeng ti dua* ti kanaingetan ken kabassitan a sample. Ti panagtarimaan ket mangnayon iti coverage, ngem ti bayadna ket ti panangidekket ti komento iti centroid ti lugar, isu a ti natarimaan a point ket lugar, saan a street address.
