--- key: title src: e5da2baa99
Aspect sentiment gamit ang lexicon

--- key: p1 src: ba7c854479
**Ang ideya.** Ang kinatibuk-ang sentiment motago kung unsa gyud ang wala makapalipay sa mga tawo. Ang aspect sentiment mobahin sa matag komento ngadto sa mga sentence, motipig sa mga sentence nga naghisgot og aspect (paghulat, staff, gasto, tambal, pasilidad, access), ug kana ra ang i-score gamit ang VADER. Ang usa ka sentence mahimong maihap sa pipila ka aspect. Ang porsyento sa matag cell kay ang bahin sa maong mga sentence nga negatibo ang score; ang n kay gidaghanon sa mga sentence, dili sa mga komento.

--- key: p2 src: 30f89eefe1
**Ang lexicon.** Ang mga term naa sa data/aspects.json, English ug Filipino. Ang English nga mga pulong mo-match sa tibuok pulong uban ang simple nga ending (wait, waited, waiting); ang Filipino nga mga gamut mo-match usab human sa mubo nga affix (hintay sulod sa naghintay). Klaro kini, paspas, ug sayon padakoon, mao nga haom kini sa pagtudlo.

--- key: p3 src: 045145260f
**Unsay makit-an niini.** Sa tibuok bundled nga data, ang paghulat mao ang labing gireklamo nga aspect, layo kaayo sa uban: mga 48% sa mga sentence bahin sa paghulat ang negatibo, batok sa mga 24% para sa staff ug pasilidad, 28% para sa tambal, 29% para sa access ug 32% para sa gasto. Ang labing negatibo nga cell kay Mimaropa sa paghulat (58%, n = 213). Gamay ra ang sentence bahin sa gasto matag lugar (kasagaran ubos sa 60), busa noisy ang mga cell niini, ug ang minimum-sentences slider motago sa pinakanipis.

--- key: p4 src: 84747d3d7c
**Mga limitasyon.** Pulong ang gi-match sa lexicon, dili kahulogan: ang "line" mo-match usab sa "the line moved fast", ug malusutan niini ang paraphrase ("two hours of my day") ug sarcasm. Ang sentence nga naghisgot og duha ka aspect mohatag sa duha og samang score. Ang supervised o zero-shot model mas maayo sa kahulogan apan mas lisod susihon. Aron ma-validate, basaha ang sample sa nag-match nga mga sentence ug ihapa pila ang sakto (precision), dayon pangitaa ang mga sentence nga unta nag-match apan wala (recall).
