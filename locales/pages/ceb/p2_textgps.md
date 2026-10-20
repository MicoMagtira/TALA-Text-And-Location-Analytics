--- key: title src: ed749f742e
Text vs GPS: pagbasa sa lugar, pagsusi sa coordinates

--- key: p1 src: a48d5f2680
**Duha ka saksi para sa usa ka location.** Ang matag komento adunay GPS point ug, kasagaran, usa ka ngalan sa lugar sa kaugalingon niyang mga pulong. Walay usa niini nga masaligan kung mag-inusara: ang GPS mahimong wala, nabaylo, o nag-default sa kataposang fix sa device, ug ang mga tawo mahimong masayop og type sa ngalan sa lungsod. Kini nga lakang nagtandi sa duha. Kung mouyon sila, kumpiyansa ta; kung dili, usa nila ang sayop, ug ang pattern sa dili pagkauyon mosulti nato kung hain.

--- key: p2 src: d1aa520507
**Geoparsing pinaagi sa mga lagda, dili sa model.** Gi-scan sa parser ang matag komento para sa pinakataas nga sunod-sunod nga hangtod upat ka token nga motakdo sa usa ka ngalan o alias sa bundled nga gazetteer sa mga rehiyon, probinsya, siyudad ug munisipyo (GeoNames, CC BY 4.0). Tungod kay sirado ang vocabulary ug konsistent ang capitalization sa mga komento, ang rule-based matcher kay deterministic, paspas, ug mapasabot sa usa ka paragraph — butang nga dili mahimo sa statistical named-entity model. Importante ang longest match: kinahanglan modaog ang "Cagayan de Oro" batok sa "Cagayan", ug ang "Davao de Oro" batok sa "Davao". Laktawan ang mga pulong human sa *Brgy*, *Purok* o *Sitio*, kay barangay ang ginganlan niini, dili munisipyo.

--- key: p3 src: 3d30c0a8e7
**Ambiguity ug unsaon kini pagsulbad.** Daghang lugar ang ginganlan og "San Fernando". Mangita una ang parser og probinsya o rehiyon nga gihisgotan usab sa samang komento ("San Fernando, Pampanga"). Kung wala, padaugon niya ang klarong dominanteng ngalan pinaagi sa populasyon (ang siyudad sa Bacolod labing menos 1.5 ka pilo nga mas dako kaysa bisan unsang kapangalan niini), gawas sa mga ngalan sa santos, nga dili gyud husayon sa ingon niana nga paagi. Ang dili pa gihapon matino markahan nga *ambiguous* ug dili iapil sa pagtandi, imbes nga tag-anan.

--- key: p4 src: 6115d6a5ea
**Gilay-on, ug nganong importante ang threshold.** Gitandi ang GPS ug ang gihisgotang lugar gamit ang haversine great-circle distance sa usa ka sphere nga 6371 km ang radius. *Mouyon* ang usa ka komento kung kana nga gilay-on naa sulod sa threshold. Ang usa ka lugar kay usa ka point (ang gazetteer centroid niini), apan ang probinsya mahimong 100 km ang gilapdon, busa ang hugot nga threshold mo-flag sa mga komento nga okay ra, ug ang luag nga threshold mopasaylo sa tinuod nga mga sayop. Iusab ang slider ug tan-awa ang pagbag-o sa disagree count: ang numero kay kinaiya sa imong threshold, dili sa data ra.

--- key: p5 src: 703c7760b2
**Ang lit-ag niini nga dataset.** Mga 31% sa bundled nga coordinates ang invalid: nahulog kini sa gawas gyud sa Pilipinas (ang unang row naghisgot sa Cagayan de Oro apan naa duol sa London). Laing 8% ang valid nga points apan layo sa gihisgotang lugar. Kung tingban, mga upat sa matag napulo ka coordinates. Ang mapa nga gidrowing diretso gikan sa GPS column murag tinuod tan-awon apan sayop kaayo. Tinuyo ang han-ay sa status: ang invalid nga GPS i-report nga invalid bisan pa adunay text, kay kinahanglan kini ayohon bisan unsa pay isulti sa text.

--- key: p6 src: fb06ec710e
**Pagpili kung unsay gamiton sa sunod nga mga lakang.** Ang *Ayohon gikan sa text* motipig sa GPS kung valid kini ug mouyon (o kung walay lugar nga gihisgotan), ug kung dili, ilisan kini sa coordinates sa gihisgotang lugar. Ang *GPS ra ang saligan* motipig lang sa valid nga mga point nga naa sa yuta sa Pilipinas. Ang *Kadtong mouyon ang duha ra* mao ang labing estrikto ug labing gamay nga sample. Ang pag-ayo makadugang og coverage, apan ang bayad niini kay ma-snap ang komento sa centroid sa lugar — mao nga ang giayong point usa ka lugar, dili address sa kalye.
