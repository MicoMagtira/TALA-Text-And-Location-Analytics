--- key: title src: 2f80652ae8
CRS validation at reprojection (Lab 1)

--- key: p1 src: eb57f71a7f
Ang dalawang numero sa spreadsheet ay hindi pa lokasyon. Ginagawa ng lab na ito na geometry ang `lon`/`lat` columns — isang bagay na kayang sukatin ng computer — at nakadepende ang bawat susunod na page sa tamang pagkakagawa nito.

--- key: p2 src: e14fc47c9f
**Ang gate ng validation.** Ang 12,000 input rows ay nawawalan ng 29 dahil sa kulang na coordinates at 256 dahil sa halagang labas sa tamang saklaw (longitude ±180, latitude ±90), kaya natitira ang 11,715 points. Pansinin kung ano ang *hindi* nahuhuli ng gate na iyon: ang komento tungkol sa Cebu na may coordinates ng London ay perpektong wasto bilang numero at ligtas na nakakadaan. Pinapatunayan ng bounds checking na maayos ang porma ng coordinate, hindi kailanman na tama ito.

--- key: p3 src: e6a5ac63da
**`set_crs` laban sa `to_crs` — ang klasikong mali.** Ang `set_crs` ay *nagdedeklara* kung ano ang ibig sabihin ng mga numero mo; ang `to_crs` ay *nagko-convert* ng mga ito sa ibang sistema. Ang pagtawag ng `set_crs` gayong `to_crs` ang ibig mong sabihin ay tahimik na pinapalitan lang ang label ng data mo sa halip na igalaw ito, at walang lalabas na error — basta mapupunta ang mga punto sa maling lugar sa bawat susunod na mapa. Kung mukhang naka-shift ang isang layer, ito ang unang hinalaan mo.

--- key: p4 src: ed568a1182
**Bakit hindi opsyonal ang reprojection.** Ang EPSG:4326 ay sumusukat sa degree, at ang isang degree ng longitude ay humigit-kumulang 111 km sa ekwador pero umiikli papuntang polo, kaya hindi maihahambing ang distansyang nasa degree sa buong mapa. Ang `eps` ng DBSCAN sa susunod na page ay isang *distansya*, kaya kailangan munang lumipat ang data sa CRS na nakabatay sa metro — dito ay **EPSG:32651** (UTM zone 51N), na awtomatikong pinili mula sa median longitude.

--- key: p5 src: 76cdb997b0
**Basahin ang nearest-neighbour check bilang diagnostic.** Ang median na 2.3 km ay makatuwiran para sa mga pasilidad ng kalusugan. Ang dalawang dulo ang kawili-wiling bahagi: ang **minimum na 0 m** ay nangangahulugang may kahit dalawang puntong pareho ang coordinates — duplicate, o ilang komentong pinagsama sa parehong pasilidad — na magpapalobo sa density para sa DBSCAN. Ang **maximum na 175 km** ay ang malalayong basura na nagpapakilala sa sarili bago pa man may maiguhit na mapa.

--- key: p6 src: 341c139e1a
**Tungkol sa privacy.** Mula rito, may hawak ka nang tumpak na lokasyon na nakakabit sa personal na salaysay ng pagpapagamot. Nakakapagpakilala ang kombinasyong iyon. Lahat ng ibabahagi mo mula rito ay dapat pinagsama-sama na — at iyon mismo ang binubuo ng Lab 3 at 5.
