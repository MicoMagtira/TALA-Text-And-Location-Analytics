--- key: title src: 53d0ca32cf
Data kag pagtinlo

--- key: p1 src: 0acbd8af98
**Ano ang kinahanglan sang pipeline.** Isa ka text column ang kinahanglan sang TALA kag, para sa mga tikang parte sa lugar, isa ka longitude kag isa ka latitude column. Ang tanan nga ara sa ulihi sang journey nagabasa sang ini nga tatlo ka column suno sa ngalan, amo ina nga diri mo lang sila i-map sing isa ka beses kag indi na liwat. Ang mapping ginatipigan bilang mga ngalan sang column sa imo session, indi gid bilang kopya sang data.

--- key: p2 src: c2c781aeb0
**Ang pagtinlo isa ka diutay kag pirmi nga pipeline.** Himuon nga lower-case, kuhaon ang links, @mentions kag #hashtags, panason ang punctuation kag digits, tipunon ang whitespace, dayon bulagon suno sa spaces. Ginasikway ang tokens nga mas malip-ot sa tatlo ka character kag ang tokens nga ara sa stopword set. Gamita ang slider agod tan-awon ang isa ka komento nga nagaagi sa kada stage. Ang punto: ang kada tikang isa ka rule nga makita mo, indi black box.

--- key: p3 src: 14c1228658
**Ang stopwords isa ka analytical nga desisyon.** Ang mga pulong pareho sang "the", "ang" ukon "sa" nagadala sang grammar, indi sang sulod, gani sila ang magapanguna sa bisan ano nga word count. Ang default set English kag isa ka Filipino nga listahan. Idugang ang imo kaugalingon: kon makita mo sa ulihi nga ang mga ngalan sang lugar ukon ang pulong nga "hospital" amo ang nagatabon sa resulta, ibutang sila sa kahon sang dugang nga mga pulong kag isugid ini sa imo write-up. Ang pagsikway sang isa ka pulong isa ka desisyon nga dapat masarangan mo depensahan.

--- key: p4 src: bd954a89f2
**Ngaa una ang pagtinlo antes ang pagbasa sang lugar.** Ang geoparsing sa masunod nga tikang nagagamit sang *orihinal* nga text, kay ang mga ngalan sang lugar nagadepende sa dalagku nga letra ("Baguio" ang siyudad, indi "baguio" ang pulong). Ang natinluan nga tokens ginagamit sa ulihi, sa Kapitulo 2, kon ginapaanggid na naton kon ano ang ginahambal sang kada lugar.
