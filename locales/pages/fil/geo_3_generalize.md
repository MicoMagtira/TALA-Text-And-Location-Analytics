--- key: title src: 22f7bc5e5a
Generalization: grid at centroids (Lab 3)

--- key: p1 src: 5f5bd3cea2
Ang mga tumpak na punto ay tumpak na tao. Ang generalization ay kusang pagpapalabo ng resolusyon — nagpapalit ng tumpak na lokasyon para sa buod na hindi nagtuturo sa kaninuman, habang pinapanatili ang pattern na sinusubukan mong ipakita.

--- key: p2 src: afc33240cb
**Ano ang ginagawa ng grid aggregation.** Naglalapat ito ng parisukat na sala sa ibabaw ng mapa at binibilang ang mga puntong bumabagsak sa bawat kahon. Ang lokasyon ay nagiging "kung saan-saan sa loob ng 20 km na parisukat na ito", at ang bilang ang naging datos. Ang mga walang lamang kahon ay hindi kailanman ginagawa, kaya ang laki ng file ay sumusunod sa kung saan may tao — hindi sa laki ng mundo.

--- key: p3 src: 149fc09d53
**Ang laki ng cell ang buong desisyon.** Maliit na cell, mataas ang detalye at mahina ang proteksyon; malaking cell, malakas ang proteksyon at posibleng malabo na ang pattern. Walang tamang sagot — mayroon lang tanong na sinasagot mo, at obligasyon sa mga taong nasa dataset. Kapag ang isang cell ay may isang punto lang, hindi ka talaga nagpapalabo ng kahit ano.

--- key: p4 src: c74f69a278
**Ano ang ibang bagay na sinasabi ng cluster centroids.** Ang centroid ay isang punto kada cluster, na inilagay sa gitna ng mga miyembro nito at nagdadala ng bilang. Nawawala nito ang hugis nang tuluyan — ang mahaba't makitid na cluster sa tabi ng highway at ang bilog na cluster sa isang lungsod ay parehong nagiging isang tuldok. Ang nakukuha mo ay linaw: 29 na tuldok na nababasa nang isang sulyap, samantalang ang 11,715 na punto ay hindi.

--- key: p5 src: ff9c223a57
**Hindi anonymity ang aggregation.** Ang isang cell na may tatlong punto sa isang liblib na lugar ay maaaring makapagpakilala pa rin kapag isinama sa ibang alam ng tao. Ang tunay na tanong ay hindi "nag-aggregate ba ako?" kundi "gaano karaming tao ang pwedeng maging ang kahon na ito?" Itakda ang laki ng cell mula sa sagot na iyon.

--- key: p6 src: 4f1764d6b7
**Ano ang dadalhin sa susunod na page.** Anumang layer ang gawin mo dito ay maide-download bilang GeoJSON at siyang ligtas na ibabahagi. Ang orihinal na punto ay hindi.
