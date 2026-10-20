--- key: title src: 1e3ffeb078
TF-IDF + K-Means na mga tema, pinaghahambing sa mga lugar

--- key: p1 src: 23d3d4d8f2
**Paano nagkakabit ang mga piraso.** Binibigyan ng TF-IDF ng timbang ang bawat term ayon sa dalas nito sa isang komento laban sa kung gaano ito kabihira sa lahat ng komento, kaya nadudurog ang mga salitang nasa lahat ng dako at lumalakas ang mga salitang nagpapaiba. Pagkatapos, pinapangkat ng K-Means ang mga komentong magkakalapit sa weighted space na iyon. Ang TF-IDF ang nagpapasya kung ano ang ibig sabihin ng "magkahawig"; sumusunod lang ang K-Means. Gumagamit ang TALA ng unigrams at bigrams, max_df 0.9, min_df 3 at 1,200 features.

--- key: p2 src: e8f66dee7e
**Pagpili ng k gamit ang silhouette.** Para sa bawat komento, ang a ay ang mean cosine distance nito sa sarili nitong tema at ang b ay ang mean distance nito sa pinakamalapit na ibang tema; s = (b - a) / max(a, b). Mula -1 hanggang 1 ang average. Kapag malapit sa 1, maayos ang paghihiwalay; kapag malapit sa 0, nagsasapawan ang mga tema. Sa data na ito, mababa ang mga score (mga 0.05 sa k = 4 at 0.08 sa k = 8) dahil maiikli ang mga komento at magkakapareho ang vocabulary. Hindi awtomatikong mas mabuti ang mas mataas na score sa mas malaking k: itanong kung ang mga card ay nababasa bilang magkakaiba at napapangalanang tema.

--- key: p3 src: c6c4891f57
**Ang bitag ng pangalan ng probinsya (totoo pa rin).** Kapag iniwan ang mga pangalan ng lugar, ang k = 4 ay bumubuo ng temang may 1,131 komento na ang mga nangungunang term ay *del*, *del norte*, *del sur*, *norte*, *sur*, *surigao*. Heograpiya iyon, hindi tema: bihira ang mga pangalan ng probinsya, kaya tinuring silang distinctive ng IDF. Kaya itinatago ng TALA ang mga pangalan ng lugar bilang default, at natutunaw ang temang heograpiko papunta sa mga temang tungkol sa laman (paghihintay, staff, rural health units, pangkalahatang karanasan). Alisin ang check sa box para makita mo mismo ang bitag, at banggitin sa write-up mo na tinanggal mo ang mga pangalan ng lugar.

--- key: p4 src: 8563de396e
**Bahagi ng bawat tema kada lugar.** Ipinapakita ng stacked bar, sa loob ng bawat lugar, kung ilang porsyento ng mga komento ang napupunta sa bawat tema (100% ang kabuuan ng bawat row). Dahil magkakaparehong vocabulary ang mga tema, halos magkakapareho ang mga bahagi sa iba't ibang lugar dito. Ang mga auto-label ay galing sa rank-weighted na pagtutugma ng mga nangungunang term at ng aspect lexicon; laging suriin ang mga ito laban sa listahan ng mga term.
