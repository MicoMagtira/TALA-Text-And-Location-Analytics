--- key: title src: 931679624d
Generalization, privacy ug mga report card

--- key: p1 src: 3a6975005f
**Nganong i-generalize.** Ang usa ka point sa mapa makaila sa usa ka tawo bisan wala ang iyang mga pulong, labi na sa mga dapit nga gamay og tawo. Ang pag-generalize mopuli sa mga point og aggregates: square grid cells o usa ka centroid matag lugar. Ang slider motago sa bisan unsang cell o lugar nga mas gamay og komento kaysa k, sa diwa sa k-anonymity: walay marker nga nagrepresentar og mas gamay sa k ka tawo. Simple kini nga suppression rule, dili garantiya; ang paghiusa sa daghang release, o gamay nga k nga giubanan og data gikan sa gawas, mahimo gihapong makaguwa og impormasyon, busa pilia ang k uban sa tag-iya sa imong data.

--- key: p2 src: ecbfb4d967
**Grid vs centroids.** Ang mga cell nga pirmi og gidak-on (gikuwenta sa UTM metres) motipig sa spatial nga detalye ug mopakita lang sa mga cell nga adunay sulod; ang centroids mopamubo sa matag lugar ngadto sa usa ka disc sa iyang gazetteer centre (para sa rehiyon) o sa mean sa iyang mga miyembro (para sa cluster). Ang mas dagkong cell ug mas dako nga k mohatag og dugang privacy apan gamay nga detalye.

--- key: p3 src: 8f321a7e8f
**Mga report card.** Ang matag card naghiusa sa mga resulta sa Chapter 2 para sa usa ka lugar: mga pulong nga nagpalahi (log-odds batok sa tanang ubang lugar, gitago ang mga ngalan sa lugar, labing menos 10 ka mention), % negatibo uban ang Wilson interval niini, ang labing gireklamo nga aspect (labing menos 15 ka sentence), ang pangunang tema (k = 4) ug usa ka hotspot flag. Ma-flag ang usa ka lugar kung labing menos 30% sa mga komento niini naa sa mga cell nga hot sa 95% o 99% ubos sa imong settings sa lakang 8 (default kung imo kining gilaktawan). Rule of thumb ra ang flag, dili test.

--- key: p4 src: 77c64a582a
**Exports.** Ang GeoJSON naa ra ang generalized features (counts ug % negatibo), ang CSV adunay usa ka row matag lugar, ug ang metadata.json motala kung giunsa paghimo ang tanan: generalization, DBSCAN settings, place unit, location source, text-vs-GPS threshold, minimum group size, sentiment method, hotspot ug theme settings. Tinuyo nga English ang mga field name bisan unsa pa ang pinulongan sa interface, aron magpabilin nga compatible ang gi-share nga mga worksheet. Walay text sa komento nga ma-export, bisan kanus-a.
