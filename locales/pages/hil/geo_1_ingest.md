--- key: title src: 2f80652ae8
CRS validation kag reprojection (Lab 1)

--- key: p1 src: eb57f71a7f
Ang duha ka numero sa spreadsheet indi pa lokasyon. Ginahimo sini nga lab nga geometry ang `lon`/`lat` columns — isa ka butang nga masukat sang computer — kag nagadepende ang kada masunod nga page sa husto nga pagkahimo sini diri.

--- key: p2 src: e14fc47c9f
**Ang gate sang validation.** Ang 12,000 ka input rows nagadula sang 29 tungod sa kulang nga coordinates kag 256 tungod sa balor nga guwa sa husto nga sakop (longitude ±180, latitude ±90), gani nabilin ang 11,715 ka points. Talupangda kon ano ang *indi* madakop sina nga gate: ang komento parte sa Cebu nga may coordinates sang London himpit nga balido bilang numero kag luwas nga nakaagi. Ginapamatud-an sang bounds checking nga maayo ang porma sang coordinate, indi gid nga husto ini.

--- key: p3 src: e6a5ac63da
**`set_crs` batok `to_crs` — ang klasiko nga sala.** Ang `set_crs` *nagadeklarar* kon ano ang buot silingon sang imo mga numero; ang `to_crs` *nagakonberte* sini sa lain nga sistema. Ang pagtawag sang `set_crs` samtang `to_crs` ang buot mo silingon hipos lang nga nagabaylo sang label sang imo data sa baylo nga ihulag ini, kag wala sing magaguwa nga error — mahulog lang ang mga punto sa sala nga lugar sa kada masunod nga mapa. Kon daw na-shift ang isa ka layer, amo ini ang una mo duhaduhaan.

--- key: p4 src: ed568a1182
**Ngaa indi opsyonal ang reprojection.** Ang EPSG:4326 nagasukat sa degree, kag ang isa ka degree sang longitude mga 111 km sa ekwador pero nagalip-ot padulong sa polo, gani indi mapaanggid ang kalayuon nga base sa degree sa bug-os nga mapa. Ang `eps` sang DBSCAN sa masunod nga page isa ka *kalayuon*, gani kinahanglan anay maglipat ang data sa CRS nga base sa metro — diri **EPSG:32651** (UTM zone 51N), nga awtomatiko nga ginpili halin sa median longitude.

--- key: p5 src: 76cdb997b0
**Basaha ang nearest-neighbour check bilang diagnostic.** Ang median nga 2.3 km makatarunganon para sa mga pasilidad sang panglawas. Ang duha ka punta amo ang makawiwili nga bahin: ang **minimum nga 0 m** nagakahulugan nga may bisan duha ka punto nga pareho ang coordinates — duplicate, ukon pila ka komento nga gintipon sa amo man nga pasilidad — nga magapabaskog sang density para sa DBSCAN. Ang **maximum nga 175 km** amo ang malayo gid nga basura nga nagapakilala sang kaugalingon antes pa may mahimo nga mapa.

--- key: p6 src: 341c139e1a
**Parte sa privacy.** Halin diri, may ginauyatan ka na nga husto nga lokasyon nga nasumpay sa personal nga sugilanon sang pagpabulong. Makapakilala ina nga kombinasyon. Tanan nga ipaambit mo halin diri dapat gintipon na — kag amo gid ina ang ginatukod sang Lab 3 kag 5.
