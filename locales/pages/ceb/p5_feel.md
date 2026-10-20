--- key: title src: 17008c972b
Sentiment matag lugar uban ang matinud-anon nga intervals

--- key: p1 src: 48406e3839
**VADER.** Usa ka rule-based lexicon scorer: ang matag pulong adunay valence, ang mga lagda modumala sa negation, intensifiers ug punctuation, ug ang sum pigaon ngadto sa compound score tali sa -1 ug 1. Negatibo ang komento kung compound <= -0.05 (ang kaugalingong cut-off sa VADER). Gihimo kini para sa English social media, busa bahin ra sa Filipino ug Taglish nga text ang masabtan niini; basaha ang mga resulta isip *relative* tali sa mga lugar, dili isip absolute nga kamatuoran. Gi-score sa TALA ang matag komento kausa matag dataset ug gigamit kini pag-usab sa mga lakang 5, 6, 8 ug 9.

--- key: p2 src: f32c570b08
**Nganong intervals.** Ang % negatibo sa usa ka lugar kay proportion k/n, ug ang gamay nga n mohimo niini nga noisy. Ang Wilson score interval sa z = 1.96 kay centre = (p + z^2/2n) / (1 + z^2/n), half-width = z * sqrt(p(1-p)/n + z^2/4n^2) / (1 + z^2/n). Dili sama sa textbook nga p +/- z*sqrt(p(1-p)/n), dili gyud kini mogawas sa [0, 1] ug maayo gihapon ang lihok bisan gamay ang n o ang p duol sa 0 o 1.

--- key: p3 src: 6047d0f850
**Unsay gisulti sa bundled nga data.** Sa kinatibuk-an, 36% sa 12,000 ka komento ang negatibo ang score. Matag rehiyon, gikan kini sa 31% (Ilocos Region, n = 575) hangtod 39% (Western Visayas, n = 895, 95% interval 35.6 hangtod 42.0). Daghan kaayo og overlap kining mga interval: dili suportado sa data ang pag-ranggo sa kadaghanan sa mga rehiyon batok sa usag usa. Ang National Capital Region adunay 157 ra ka komento, busa lapad ang interval niini (26.8 hangtod 41.5). Mao kana nganong ang mga lugar nga ubos sa minimum n gi-gray imbes nga i-ranggo.

**Giya ra ang overlap, dili test.** Ang nag-overlap nga mga interval dili mopamatuod nga walay kalainan, ug ang wala mag-overlap dili mopamatuod nga naa. Para sa pormal nga pagtandi, gamit og two-proportion test, ug hinumdumi nga ang daghang pagtandi dungan mopadaghan sa false alarms.
