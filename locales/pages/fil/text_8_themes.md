--- key: title src: 5aa33596ce
Mga tema gamit ang TF-IDF at K-Means

--- key: p1 src: 671d1d25e3
Ang page na ito ay naglalagay ng bawat komento sa eksaktong isang tema. Iyon ang malaking pagkakaiba nito sa LDA sa nakaraang page, kung saan ang isang dokumento ay pwedeng bahagyang mapabilang sa maraming topic nang sabay. Alin ang tama ay depende sa iyong tanong, hindi sa alin ang mas bago.

--- key: p2 src: 8b4103c729
**Ano ang ginagawa ng TF-IDF.** Tinitimbang nito ang bawat salita ayon sa dalas nito sa isang dokumento at kung gaano ito kabihira sa lahat ng iba. Ang salitang nasa bawat komento ay tumatanggap ng halos zero na timbang, gaano man ito kadalas. Kaya nga hindi nangingibabaw ang `hospital` dito kahit ito ang nangibabaw sa frequency page — sinasabi nito ang naghahati sa mga komento, hindi ang nagbubuklod sa kanila.

--- key: p3 src: 9fbeea4028
**Kailangang sabihan ang K-Means ng K, at laging susunod ito.** Humingi ka ng apat na tema at apat ang makukuha mo, kahit tatlo lang o labindalawa ang totoong grupo sa data. Ang algorithm ay walang paraan para tumutol. Igalaw mo ang slider at tingnan mo kung ang mga nangungunang termino ay nananatiling nakikilala o nagsisimula nang umulit — kapag ang dalawang tema ay parehong-pareho na ang nangungunang salita, lumagpas ka na sa hangganan.

--- key: p4 src: c3b1b0c1b3
**Ang scatter plot ay isang anino, hindi ang mga tema.** Ang mga tema ay natagpuan sa 1,200 dimensyon. Ang plot ay dalawa, na kinuha gamit ang TruncatedSVD para lang makita ng tao ang bagay. Ang mga puntong magkapatong sa larawan ay pwedeng magkalayo sa totoong espasyo, at ang mga hangganang mukhang magulo ay pwedeng malinis doon. Gamitin ang plot para sa laki at magaspang na paghihiwalay, hindi bilang patunay ng pagkakahiwalay.

--- key: p5 src: 09069ede28
**Ang cross-tab ng tema at sentiment ang totoong resulta.** Ang tema mag-isa ay nagsasabi kung ano ang paksa; ang sentiment mag-isa ay nagsasabi kung anong pakiramdam. Magkasama, itinuturo nila kung aling paksa ang gumagawa ng problema. Isang temang 70% negative ang isang bagay na maaaksyunan; isang temang 70% positive ay isang bagay na dapat protektahan.

--- key: p6 src: 87de38c5ee
**Ang mga tema ay hindi kategorya.** Isa silang paghahati ng datos na ito, sa pamamagitan ng algorithm na ito, sa mga setting na ito. Patakbuhin mo muli sa susunod na buwan gamit ang bagong data at magbabago ang mga hangganan. Kung ipapasa mo ang mga tema sa ibang tao, ipasa mo rin ang K, ang seed, at ang mga nangungunang termino — kung wala ang mga iyon, hindi maulit ang resulta.
