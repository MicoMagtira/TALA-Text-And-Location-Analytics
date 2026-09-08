--- key: title src: 2f80652ae8
CRS validation ken reprojection (Lab 1)

--- key: p1 src: eb57f71a7f
Ti dua a numero iti spreadsheet ket saan pay a lokasion. Aramiden daytoy a lab a geometry dagiti `lon`/`lat` columns — maysa a banag a marukod ti computer — ket agpannuray ti tunggal sumaruno a page iti umno a pannakaaramidna ditoy.

--- key: p2 src: e14fc47c9f
**Ti gate ti validation.** Dagiti 12,000 nga input rows ket mapukawanda iti 29 gapu iti awan a coordinates ken 256 gapu kadagiti pateg a ruar ti umno a sakup (longitude ±180, latitude ±90), isu a mabati ti 11,715 a points. Matikodam no ania ti *saan* a matiliw dayta a gate: ti komento maipapan iti Cebu nga addaan coordinates ti London ket naan-anay a balido kas numero ket natalged a makalasat. Paneknekan ti bounds checking a nasayaat ti porma ti coordinate, saan a pulos nga umno daytoy.

--- key: p3 src: e6a5ac63da
**`set_crs` maibusor iti `to_crs` — ti klasiko a biddut.** Ti `set_crs` ket *mangideklara* no ania ti kayat a sawen dagiti numerom; ti `to_crs` ket *mang-convert* kadagitoy iti sabali a sistema. Ti panagtawag iti `set_crs` idinto ta `to_crs` ti kayatmo a sawen ket siuulimek a mangsukat laeng iti label ti datam imbes nga igawidna daytoy, ket awan ti rumuar nga error — matnag laeng dagiti punto iti biddut a lugar iti tunggal sumaruno a mapa. No kasla naiyakar ti maysa a layer, daytoy ti umuna a duaduaem.

--- key: p4 src: ed568a1182
**Apay a saan nga opsional ti reprojection.** Ti EPSG:4326 ket agrukod iti degree, ket ti maysa a degree ti longitude ket agarup 111 km iti ekwador ngem umababa nga agturong iti polo, isu a saan a maidilig ti kaadayo a naibatay iti degree iti intero a mapa. Ti `eps` ti DBSCAN iti sumaruno a page ket maysa a *kaadayo*, isu a masapul nga umuna nga agakar ti data iti CRS a naibatay iti metro — ditoy **EPSG:32651** (UTM zone 51N), a automatiko a napili manipud iti median longitude.

--- key: p5 src: 76cdb997b0
**Basaem ti nearest-neighbour check kas diagnostic.** Ti median a 2.3 km ket makatarnaw para kadagiti pasilidad ti salun-at. Dagiti dua a pungto ti makapainteres a paset: ti **minimum a 0 m** ket kayatna a sawen adda uray dua a punto nga agpada ti coordinates — duplicate, wenno sumagmamano a komento a naurnong iti isu met laeng a pasilidad — a mangpalukmeg iti density para iti DBSCAN. Ti **maximum a 175 km** ket ti adayo unay a basura a mangipakpakilala iti bagina sakbay pay a maiyukrad ti aniaman a mapa.

--- key: p6 src: 341c139e1a
**Maipapan iti privacy.** Manipud ditoy, addaanka itan iti umiso a lokasion a naikapet iti personal a salaysay ti panagpaagas. Makaipabigbig dayta a kombinasion. Amin nga ibingaymo manipud ditoy ket rumbeng a naurnong metten — ket dayta mismo ti bangbangonen ti Lab 3 ken 5.
