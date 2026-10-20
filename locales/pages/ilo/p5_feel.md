--- key: title src: 17008c972b
Sentiment iti tunggal lugar nga addaan napudno nga interval

--- key: p1 src: 48406e3839
**VADER.** Maysa a rule-based a lexicon scorer: ti tunggal sao ket addaan valence, dagiti rule ti mangtaming iti negation, intensifier ken puntuasion, ken ti dagup ket maipitpit iti compound score iti nagbaetan ti -1 ken 1. Negatibo ti komento no compound <= -0.05 (ti bukod a cut-off ti VADER). Naaramid daytoy para iti English a social media, isu a paset laeng ti maawatan na iti Filipino ken Taglish a text; basaen dagiti resulta kas *relative* iti nagbaetan dagiti lugar, saan a kas absolute a kinapudno. Iskoren ti TALA ti tunggal komento iti maminsan iti tunggal dataset ken usaren manen daytoy kadagiti addang 5, 6, 8 ken 9.

--- key: p2 src: f32c570b08
**Apay nga interval.** Ti % negatibo ti maysa a lugar ket proportion a k/n, ken ti bassit a n ket mangpagbalin iti daytoy a noisy. Ti Wilson score interval iti z = 1.96 ket centre = (p + z^2/2n) / (1 + z^2/n), half-width = z * sqrt(p(1-p)/n + z^2/4n^2) / (1 + z^2/n). Saan a kas iti textbook a p +/- z*sqrt(p(1-p)/n), saan a pulos a rummuar daytoy iti [0, 1] ken umno ti ikutna uray bassit ti n wenno asideg ti p iti 0 wenno 1.

--- key: p3 src: 6047d0f850
**Ania ti ibagbaga ti bundled a data.** Iti pakabuklan, 36% kadagiti 12,000 a komento ti negatibo ti score. Babaen ti rehion, manipud 31% (Ilocos Region, n = 575) agingga iti 39% (Western Visayas, n = 895, 95% interval 35.6 agingga iti 42.0). Nakaro ti panagsasampaw dagita nga interval: saan a suportaran ti data ti panangiranggo iti kaaduan kadagiti rehion maibusor iti tunggal maysa. 157 laeng a komento ti adda iti National Capital Region, isu a nalawa ti interval-na (26.8 agingga iti 41.5). Isu dayta ti gapuna a dagiti lugar nga adda iti baba ti minimum a n ket naka-grey imbes a mairanggo.

**Rough a giya ti panagsasampaw, saan a test.** Ti agsasampaw nga interval ket saan a mangpaneknek nga awan ti pagdudumaan, ken ti saan nga agsasampaw ket saan a mangpaneknek nga adda. Para iti pormal a panagdilig, usaren ti two-proportion test, ken laglagipen a ti adu a panagdilig iti maminsan ket mangpaadu kadagiti false alarm.
