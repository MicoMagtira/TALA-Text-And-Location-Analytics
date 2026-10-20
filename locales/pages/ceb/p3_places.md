--- key: title src: c443695e58
Mga lugar: gikan sa mga point ngadto sa mga rehiyon ug cluster

--- key: p1 src: 9e04298220
**Nganong mag-grupo man.** Ang usa ka komento kay anekdota; ang usa ka lugar kay sample. Ang Chapter 2 nagtandi sa gisulti sa mga lugar, busa ang matag komento kinahanglan una og label sa lugar. Duha ang paagi aron makakuha niini, ug lahi nga pangutana ang ilang gitubag.

--- key: p2 src: f1707fe2eb
**Rehiyon: gamita ang gisulat sa mga tawo.** Ang matag komento mokuha sa rehiyon sa lugar nga iyang gihisgotan (gikan sa gazetteer). Ang komento nga walay magamit nga ngalan mokuha sa rehiyon nga ang centroid labing duol sa iyang located point. Sayon kini basahon, stable, ug walay parameter nga kinahanglan, apan administratibo ang mga rehiyon: mahimo silang dili managsama kaayo sa gidak-on ug populasyon, ug ang rehiyon gidrowing diri isip bubble sa iyang centroid, dili isip utlanan.

--- key: p3 src: 97233bbec5
**Cluster: pasagdi ang density ang mohukom.** Ang DBSCAN motubo og cluster gikan sa bisan unsang point nga adunay labing menos *min_samples* ka silingan sulod sa *eps*, ug markahan nga noise ang mga point nga dili sakop sa bisan unsang dasok nga dapit. Dili kinahanglan nga mahibaloan daan ang gidaghanon sa cluster, ug dili niya pugson ang matag point nga mosulod sa usa ka grupo. Importante ang duha ka knob: ang gamay nga eps mobuak sa usa ka siyudad ngadto sa daghang cluster, ang dako nga eps mohiusa sa magkasikbit nga mga siyudad ngadto sa usa ka dakong lumpon.

--- key: p4 src: 8655589831
**Projected metres, dili degrees.** Gilay-on ang eps sa DBSCAN, busa ang coordinates i-project una ngadto sa UTM metres. Ang usa ka degree sa longitude mas mubo kaysa usa ka degree sa latitude kung layo na sa equator, busa kung padaganon ang DBSCAN sa hilaw nga degrees, ellipse ang madrowing, dili lingin.

--- key: p5 src: 6a40392629
**Ang k-distance elbow.** Para sa matag point, kuhaa ang gilay-on ngadto sa iyang ika-k nga labing duol nga silingan ug ihan-ay kining mga gilay-on. Kadaghanan sa mga point naa sa dasok nga dapit ug gagmay ang value; ang mga nahisalaag dagko, busa ang curve mosaka og kalit sa utlanan. Ang maayong eps kay duol sa maong elbow. I-set ang k duol sa min_samples. Giya ra ang elbow, dili pamatuod: tan-awa ang mapa ug susiha kung ang mga cluster ba motakdo sa mga lugar nga imong nailhan.

--- key: p6 src: dbab5c1879
**Resulta ang noise.** Ang mga point nga wala ma-assign sa DBSCAN dili sayop. Ang mga komento gikan sa kabaryohan nga nagkatag taliwala sa mga lungsod kasagaran mahimong noise, ug matinud-anon kana: dili sila sakop sa usa ka dasok nga lugar. Sa mode nga Rehiyon, ang mga komento ra nga walay location gyud ang dili ma-assign.

--- key: p7 src: fc3b88474e
**Ang giayong mga point naa sa centroid sa lungsod.** Kung ang komento naghisgot og lugar apan sayop ang GPS niini, ang giayong point ibutang gyud sa centroid sa maong lugar. Busa sa mode nga Cluster, ang DBSCAN sa giayong mga point hilig mohimo og usa ka cluster matag gihisgotang lungsod, ug murag patag ang k-distance curve kay daghang point ang managsama og coordinates. Ang "Kadtong mouyon ang duha ra" motipig sa mga GPS-only nga point, busa gamita kini isip view para sa pagtandi.
