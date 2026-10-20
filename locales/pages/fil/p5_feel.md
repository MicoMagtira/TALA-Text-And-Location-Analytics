--- key: title src: 17008c972b
Sentiment kada lugar na may tapat na interval

--- key: p1 src: 48406e3839
**VADER.** Isang rule-based na lexicon scorer: may valence ang bawat salita, may mga rule para sa negation, intensifier at bantas, at ang kabuuan ay pinipiga sa isang compound score sa pagitan ng -1 at 1. Negatibo ang isang komento kapag compound <= -0.05 (ang sariling cut-off ng VADER). Ginawa ito para sa English na social media, kaya bahagya lang nitong naiintindihan ang Filipino at Taglish na text; basahin ang resulta bilang *relative* sa pagitan ng mga lugar, hindi bilang ganap na katotohanan. Minsan lang sino-score ng TALA ang bawat komento kada dataset at ginagamit ito ulit sa mga hakbang 5, 6, 8 at 9.

--- key: p2 src: f32c570b08
**Bakit may interval.** Ang % negatibo ng isang lugar ay proportion na k/n, at kapag maliit ang n, maingay ito. Ang Wilson score interval sa z = 1.96 ay centre = (p + z^2/2n) / (1 + z^2/n), half-width = z * sqrt(p(1-p)/n + z^2/4n^2) / (1 + z^2/n). Hindi tulad ng nasa textbook na p +/- z*sqrt(p(1-p)/n), hindi ito kailanman lumalabas sa [0, 1] at maayos pa rin kapag maliit ang n o kapag malapit ang p sa 0 o 1.

--- key: p3 src: 6047d0f850
**Ang sinasabi ng bundled na data.** Sa kabuuan, 36% ng 12,000 komento ang negatibo ang score. Kada rehiyon, mula 31% (Ilocos Region, n = 575) hanggang 39% (Western Visayas, n = 895, 95% interval 35.6 hanggang 42.0). Malaki ang pagsasapawan ng mga interval na iyon: hindi sinusuportahan ng data ang pagra-rank sa karamihan ng mga rehiyon laban sa isa't isa. 157 komento lang ang National Capital Region, kaya malapad ang interval nito (26.8 hanggang 41.5). Iyan ang dahilan kung bakit naka-gray ang mga lugar na kulang sa minimum na n sa halip na i-rank.

**Magaspang na gabay ang pagsasapawan, hindi test.** Hindi napapatunayan ng nagsasapawang interval na walang pagkakaiba, at hindi rin napapatunayan ng hindi nagsasapawan na mayroon. Para sa pormal na paghahambing, gumamit ng two-proportion test, at tandaan na kapag maraming paghahambing nang sabay-sabay, dumarami ang false alarm.
