--- key: title src: 8c5bbd5d86
Contrastive keywords: weighted log-odds

--- key: p1 src: 510e357d91
**Ngaa indi lang isipon ang mga pulong?** Ang pinakamasunson nga mga pulong sa bisan ano nga lugar amo man ang pinakamasunson sa tanan nga lugar ("staff", "hospital"). Agod makita kon ano ang *nagapalain* sa isa ka lugar, ipaanggid mo ini sa isa ka reference group kag pamangkuta kon diin nga mga pulong ang nagahilig sa isa ka bahin. Indi man mag-obra ang hilaw nga ratio: ang pulong nga nakita sing makaduha sa lugar A kag wala gid sa iban may infinite nga ratio.

--- key: p2 src: 32e35980c0
**Ang pamaagi (Monroe, Colaresi & Quinn 2008).** Para sa kada termino w, ang y_a kag y_b amo ang iya counts sa grupo A kag B, ang n_a kag n_b ang kabilugan nga pulong sa kada isa, kag ang alpha_w isa ka Dirichlet prior nga proportional sa count sang pulong sa *tanan* nga komento, gin-scale agod ang sum sang mga alpha amo ang a0 = 500. Dayon delta = log((y_a + alpha_w) / (n_a + a0 - y_a - alpha_w)) - log((y_b + alpha_w) / (n_b + a0 - y_b - alpha_w)), ang iya variance 1/(y_a + alpha_w) + 1/(y_b + alpha_w), kag z = delta / sqrt(variance). Ang positibo nga z buot silingon mas tipikal sa A, ang negatibo mas tipikal sa B. Kon bayluhan ang A kag B, nagabaliskad gid ang sign.

**Ano ang ginahimo sang prior.** Ginaguyod niya ang talagsa nga mga pulong palapit sa ila kabilugan nga rate, gani ang pulong nga nakita sing makatatlo indi makapanguna sa chart. Ang mas daku nga prior mas maandam. Ang pagbahin sa standard deviation nagabaylo sang "ano kalain" pakadto sa "ano kasigurado": ang komon nga mga pulong nga may diutay nga hilig mahimo nga mas mataas ang ranggo sangsa talagsa nga mga pulong nga may daku nga hilig.

--- key: p3 src: cc51916d54
**Ang mga ngalan sang lugar ang magadaog luwas kon taguon mo sila.** Para sa Central Luzon, ang top terms amo ang *nueva*, *central*, *fernando*, *bulacan*, *zambales* (z halin 21 pakubos sa 11), kay ginasambit sang mga tawo didto ang ila kaugalingon nga probinsya. Matuod ina pero indi bag-o nga balita, gani ginatago sang page ang mga ngalan sang lugar sa default (mga pulong halin sa ngalan sang rehiyon, probinsya kag siyudad, upod ang kada lugar nga nakita sang geoparser). Ang nabilin mas hilom gid: ang pinakamabaskog nga nabilin nga mga termino may z nga mga 4. Sa sini nga dataset, ang mga komento nagasunod sa parehas nga mga template, gani diutay lang ang kinalain sang ginahambal sang mga lugar. Ang pagbasa nga "wala gid sing nagapabulag sa sini nga lugar" isa ka resulta, indi kapaslawan.

--- key: p4 src: d0ab8fed44
**Mga limitasyon.** Ang mga termino isa ka pulong kag duha ka pulong nga phrase pagkatapos kuhaon ang stopwords, gani ang mga phrase nagaguwa bilang pares ("handled lab"). Ang minimum-count slider (indi gid magkubos sa 5) nagapugong sa isa ka termino nga maglaragway lang sang isa ukon duha ka tawo. Sa 17 ka rehiyon kag linibo ka kandidato nga termino, may pila ka mataas nga z nga nagaguwa paagi sa tsamba; kabiga nga makawiwili ang z nga labaw sa mga 3, kag usisaa paagi sa aggregated counts, indi gid paagi sa pagbasa sang tagsa-tagsa nga komento.
