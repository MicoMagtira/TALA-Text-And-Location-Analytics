--- key: title src: e5da2baa99
Aspect sentiment gamit ang lexicon

--- key: p1 src: ba7c854479
**Ang ideya.** Ginatago sang kabilugan nga sentiment kon ano gid ang wala ginakalipayan sang mga tawo. Ginabulag sang aspect sentiment ang kada komento sa mga sentence, ginatipig ang mga sentence nga nagasambit sang aspect (paghulat, staff, gasto, bulong, pasilidad, access), kag yadto lang ang ginascore gamit ang VADER. Ang isa ka sentence mahimo maisip para sa pila ka aspect. Ang percentage sa kada cell amo ang bahin sang sina nga mga sentence nga negatibo ang score; ang n amo ang kadamuon sang sentences, indi sang komento.

--- key: p2 src: 30f89eefe1
**Ang lexicon.** Ang mga termino ara sa data/aspects.json, English kag Filipino. Ang English nga mga pulong nagatugma bilang bug-os nga pulong nga may simple nga endings (wait, waited, waiting); ang Filipino nga mga root nagatugma man pagkatapos sang malip-ot nga affix (hintay sa sulod sang naghintay). Maathag, madasig kag mahapos dugangan, amo ina nga bagay ini sa pagtudlo.

--- key: p3 src: 045145260f
**Ano ang iya nakita.** Sa bug-os nga bundled data, ang paghulat amo gid ang pinakaginareklamo nga aspect: mga 48% sang sentences parte sa paghulat ang negatibo, kontra sa mga 24% para sa staff kag pasilidad, 28% para sa bulong, 29% para sa access kag 32% para sa gasto. Ang pinakanegatibo nga cell amo ang Mimaropa sa paghulat (58%, n = 213). Diutay ang sentences parte sa gasto kada lugar (kasagaran kubos sa 60), gani magulo ang iya mga cell kag ginatago sang minimum-sentences slider ang pinakanipis.

--- key: p4 src: 84747d3d7c
**Mga limitasyon.** Mga pulong ang ginatugma sang lexicon, indi kahulugan: ang "line" nagatugma man sa "the line moved fast", kag indi niya makuha ang paraphrase ("two hours of my day") kag sarcasm. Ang sentence nga nagasambit sang duha ka aspect nagahatag sang parehas nga score sa duha. Ang supervised ukon zero-shot nga model mas maayo sa kahulugan pero mas budlay usisaon. Agod i-validate, basaha ang sample sang mga sentence nga nagtugma kag isipa kon pila ang husto (precision), dayon pangitaa ang mga sentence nga dapat nagtugma pero wala (recall).
