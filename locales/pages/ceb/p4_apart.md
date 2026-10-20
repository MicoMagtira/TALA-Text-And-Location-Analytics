--- key: title src: 8c5bbd5d86
Contrastive keywords pinaagi sa weighted log-odds

--- key: p1 src: 510e357d91
**Nganong dili lang mag-ihap og mga pulong?** Ang labing kasagarang mga pulong sa bisan unsang lugar mao usab ang labing kasagaran bisan asa ("staff", "hospital"). Aron makita kung unsay naghimo sa usa ka lugar nga *lahi*, itandi nimo kini sa usa ka reference group ug pangutan-a kung unsang mga pulong ang mohilig sa usa ka bahin. Mapakyas usab ang hilaw nga ratio: ang pulong nga kaduha ra nakita sa lugar A ug wala gyud sa ubang dapit adunay infinite nga ratio.

--- key: p2 src: 32e35980c0
**Ang method (Monroe, Colaresi & Quinn 2008).** Para sa matag term w, ang y_a ug y_b mao ang iyang counts sa grupo A ug B, ang n_a ug n_b ang total nga mga pulong sa matag usa, ug ang alpha_w usa ka Dirichlet prior nga proporsyonal sa count sa pulong sa *tanang* komento, gi-scale aron ang sum sa mga alpha kay a0 = 500. Dayon delta = log((y_a + alpha_w) / (n_a + a0 - y_a - alpha_w)) - log((y_b + alpha_w) / (n_b + a0 - y_b - alpha_w)), ang variance niini kay 1/(y_a + alpha_w) + 1/(y_b + alpha_w), ug z = delta / sqrt(variance). Ang positibo nga z nagpasabot nga mas tipikal sa A, ang negatibo sa B. Kung baylohan ang A ug B, mobali gyud ang sign.

**Unsay buhaton sa prior.** Ginabira niini ang talagsaong mga pulong paingon sa ilang kinatibuk-ang rate, busa ang pulong nga katulo ra nakita dili makapanguna sa chart. Ang mas dako nga prior mas mainampingon. Ang pagbahin sa standard deviation mohimo sa "unsa kalahi" ngadto sa "unsa ka sigurado": ang kasagarang mga pulong nga gamay ra og hilig mahimong molabaw sa talagsaong mga pulong nga dako og hilig.

--- key: p3 src: cc51916d54
**Modaog ang mga ngalan sa lugar gawas kung itago nimo.** Para sa Central Luzon, ang top terms kay *nueva*, *central*, *fernando*, *bulacan*, *zambales* (z gikan 21 paubos sa 11), kay ginganlan sa mga tawo didto ang ilang kaugalingong probinsya. Tinuod kana apan dili balita, busa gitago sa page ang mga ngalan sa lugar sa default (mga pulong gikan sa ngalan sa rehiyon, probinsya ug siyudad, ug ang matag lugar nga nakit-an sa geoparser). Mas hilom ang nahibilin: ang pinakakusog nga nahibiling mga term adunay z nga mga 4. Niini nga dataset, ang mga komento nagsunod sa managsamang template, busa gamay ra ang kalainan sa gisulti sa mga lugar. Ang pagbasa nga "wala kaayoy nagpalahi niini nga lugar" usa ka resulta, dili kapakyasan.

--- key: p4 src: d0ab8fed44
**Mga limitasyon.** Ang mga term kay usa ka pulong ug duha-ka-pulong nga phrase human tangtangon ang stopwords, busa ang mga phrase mogawas nga pares ("handled lab"). Ang minimum-count slider (dili gyud ubos sa 5) mopugong sa usa ka term nga maghulagway lang og usa o duha ka tawo. Uban sa 17 ka rehiyon ug liboan ka candidate terms, adunay pipila ka taas nga z value nga motungha tungod sa sulagma; isipa nga makapainteres ang z nga kapin sa mga 3, ug i-verify gamit ang aggregated counts, dili gyud pinaagi sa pagbasa sa indibidwal nga mga komento.
