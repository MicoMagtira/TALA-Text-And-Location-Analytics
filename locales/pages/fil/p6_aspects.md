--- key: title src: e5da2baa99
Aspect sentiment gamit ang lexicon

--- key: p1 src: ba7c854479
**Ang ideya.** Itinatago ng pangkalahatang sentiment kung ano talaga ang ikinadidismaya ng mga tao. Hinahati ng aspect sentiment ang bawat komento sa mga pangungusap, pinapanatili ang mga pangungusap na bumabanggit ng isang aspect (paghihintay, staff, gastos, gamot, pasilidad, access), at iyon lang ang sino-score gamit ang VADER. Puwedeng mabilang ang isang pangungusap sa ilang aspect. Ang porsyento sa bawat cell ay ang bahagi ng mga pangungusap na iyon na negatibo ang score; ang n ay bilang ng pangungusap, hindi ng komento.

--- key: p2 src: 30f89eefe1
**Ang lexicon.** Nasa data/aspects.json ang mga term, sa English at Filipino. Ang mga English na salita ay tumutugma bilang buong salita na may simpleng hulapi (wait, waited, waiting); ang mga ugat na Filipino ay tumutugma rin kahit may maikling panlapi (hintay sa loob ng naghintay). Malinaw, mabilis at madaling dagdagan, kaya bagay ito sa pagtuturo.

--- key: p3 src: 045145260f
**Ang nahahanap nito.** Sa buong bundled na data, ang paghihintay ang pinakainirereklamong aspect nang malayo: mga 48% ng mga pangungusap tungkol sa paghihintay ang negatibo, kumpara sa mga 24% para sa staff at pasilidad, 28% para sa gamot, 29% para sa access at 32% para sa gastos. Ang pinakanegatibong cell ay Mimaropa sa paghihintay (58%, n = 213). Kaunti ang pangungusap tungkol sa gastos kada lugar (madalas wala pang 60), kaya maingay ang mga cell nito at itinatago ng minimum-sentences slider ang pinakamanipis.

--- key: p4 src: 84747d3d7c
**Mga limitasyon.** Salita ang itinutugma ng lexicon, hindi kahulugan: tumutugma rin ang "line" sa "the line moved fast", at hindi nito nahuhuli ang paraphrase ("two hours of my day") at sarcasm. Ang pangungusap na bumabanggit ng dalawang aspect ay nagbibigay ng parehong score sa dalawa. Mas mahusay sa kahulugan ang isang supervised o zero-shot na model pero mas mahirap itong suriin. Para mag-validate, magbasa ng sample ng mga tumugmang pangungusap at bilangin kung ilan ang tama (precision), tapos hanapin ang mga pangungusap na dapat ay tumugma pero hindi (recall).
