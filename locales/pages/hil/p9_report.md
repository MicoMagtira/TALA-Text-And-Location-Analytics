--- key: title src: 931679624d
Generalization, privacy kag mga report card

--- key: p1 src: 3a6975005f
**Ngaa i-generalize.** Ang isa ka point sa mapa makapakilala sang isa ka tawo bisan wala ang iya mga pulong, labi na sa mga lugar nga diutay ang tawo. Ang generalizing nagabaylo sang points sang aggregates: square nga grid cells ukon isa ka centroid kada lugar. Ginatago sang slider ang bisan ano nga cell ukon lugar nga kulang sa k ang komento, suno sa espiritu sang k-anonymity: wala sing marker nga nagarepresentar sang kubos sa k ka tawo. Isa lang ini ka simple nga suppression rule, indi garantiya; ang pagtingob sang pila ka release, ukon ang diutay nga k upod ang data halin sa gwa, mahimo gihapon magpaguwa sang impormasyon, gani pilia ang k upod ang tag-iya sang imo data.

--- key: p2 src: ecbfb4d967
**Grid vs centroids.** Ang cells nga pirmi ang kadakuon (ginkwenta sa UTM metres) nagatipig sang spatial nga detalye kag ginapakita lang ang cells nga may sulod; ang centroids nagapaliit sa kada lugar sa isa ka disc sa iya gazetteer centre (mga rehiyon) ukon sa mean sang iya mga miyembro (mga cluster). Ang mas daku nga cells kag mas daku nga k nagahatag sang mas daku nga privacy kag mas diutay nga detalye.

--- key: p3 src: 8f321a7e8f
**Mga report card.** Ang kada card nagatingob sang mga resulta sang Kapitulo 2 para sa isa ka lugar: pinasahi nga mga pulong (log-odds kontra sa tanan nga iban nga lugar, nakatago ang mga ngalan sang lugar, indi magkubos sa 10 ka beses ginsambit), % negatibo upod ang iya Wilson interval, ang pinakaginareklamo nga aspect (indi magkubos sa 15 ka sentence), ang panguna nga theme (k = 4) kag isa ka hotspot flag. Ginaflag ang lugar kon indi magkubos sa 30% sang iya mga komento ang ara sa cells nga hot sa 95% ukon 99% suno sa imo settings sa tikang 8 (defaults kon ginlaktawan mo ini). Ang flag isa ka rule of thumb, indi test.

--- key: p4 src: 77c64a582a
**Exports.** Ang GeoJSON may sulod lang nga generalized features (counts kag % negatibo), ang CSV may isa ka row kada lugar, kag ang metadata.json nagarekord kon paano ginhimo ang tanan: generalization, DBSCAN settings, place unit, location source, text-vs-GPS threshold, minimum group size, sentiment method, hotspot kag theme settings. Hungod nga English ang mga ngalan sang field bisan ano pa ang lenguahe sang interface, agod magpabilin nga compatible ang mga shared worksheet. Wala gid sing text sang komento nga gina-export.
