--- key: title src: 2f80652ae8
CRS validation ug reprojection (Lab 1)

--- key: p1 src: eb57f71a7f
Ang duha ka numero sa spreadsheet dili pa lokasyon. Gihimo niining lab nga geometry ang `lon`/`lat` columns — usa ka butang nga masukod sa computer — ug nagdepende ang matag sunod nga page sa husto nga pagkabuhat niini.

--- key: p2 src: e14fc47c9f
**Ang gate sa validation.** Ang 12,000 ka input rows nawad-an og 29 tungod sa kulang nga coordinates ug 256 tungod sa bili nga gawas sa husto nga sakop (longitude ±180, latitude ±90), busa nahibilin ang 11,715 ka points. Matikdi kung unsa ang *dili* madakpan niana nga gate: ang komento bahin sa Cebu nga adunay coordinates sa London hingpit nga balido isip numero ug luwas nga makaagi. Gipamatud-an sa bounds checking nga maayo ang porma sa coordinate, dili gyud nga husto kini.

--- key: p3 src: e6a5ac63da
**`set_crs` batok `to_crs` — ang klasikong sayop.** Ang `set_crs` *nagdeklara* kung unsa ang buot ipasabot sa imong mga numero; ang `to_crs` *nag-convert* niini ngadto sa laing sistema. Ang pagtawag sa `set_crs` samtang `to_crs` ang buot nimong ipasabot hilom lang nga nag-ilis sa label sa imong data imbis nga ilihok kini, ug walay mogawas nga error — mahulog lang ang mga punto sa sayop nga dapit sa matag sunod nga mapa. Kung murag na-shift ang usa ka layer, kini ang unahon nimog duda.

--- key: p4 src: ed568a1182
**Nganong dili opsyonal ang reprojection.** Ang EPSG:4326 nagsukod sa degree, ug ang usa ka degree sa longitude kay mga 111 km sa ekwador apan momubo padulong sa polo, mao nga dili matandi ang gilay-on nga nakabase sa degree sa tibuok mapa. Ang `eps` sa DBSCAN sa sunod nga page usa ka *gilay-on*, mao nga kinahanglan una molihok ang data ngadto sa CRS nga nakabase sa metro — dinhi **EPSG:32651** (UTM zone 51N), nga awtomatikong gipili gikan sa median longitude.

--- key: p5 src: 76cdb997b0
**Basaha ang nearest-neighbour check isip diagnostic.** Ang median nga 2.3 km makataronganon para sa mga pasilidad sa panglawas. Ang duha ka tumoy mao ang makapainteres nga bahin: ang **minimum nga 0 m** nagpasabot nga adunay bisan duha ka puntos nga parehas og coordinates — duplicate, o pipila ka komento nga gitapok sa mao rang pasilidad — nga magpaburot sa density para sa DBSCAN. Ang **maximum nga 175 km** mao ang layo kaayo nga basura nga nagpaila sa kaugalingon sa wala pa madrowing ang bisan unsang mapa.

--- key: p6 src: 341c139e1a
**Bahin sa privacy.** Gikan dinhi, adunay ka na hawid nga tukma nga lokasyon nga gikabit sa personal nga asoy sa pagpatambal. Makapaila kanang kombinasyona. Tanan nga imong ipaambit gikan dinhi kinahanglan gitapok na — ug mao gyud kanay gitukod sa Lab 3 ug 5.
