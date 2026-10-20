--- key: title src: 53d0ca32cf
Data ug paglimpyo

--- key: p1 src: 0acbd8af98
**Unsay kinahanglan sa pipeline.** Usa ka text column ang gusto sa TALA ug, para sa mga lakang bahin sa lugar, usa ka longitude ug usa ka latitude column. Ang tanan sa ulahi sa journey mobasa niining tulo ka column pinaagi sa ngalan, mao nga diri nimo kini i-map kausa ug dili na pag-usab. Ang mapping gitipigan isip mga ngalan sa column sa imong session, dili gyud isip kopya sa data.

--- key: p2 src: c2c781aeb0
**Gamay ug pirmi nga pipeline ang paglimpyo.** Himoong lower-case, tangtangon ang mga link, @mention ug #hashtag, kuhaon ang punctuation ug mga digit, hiusahon ang whitespace, dayon bahinon sa mga space. Ilabay ang mga token nga mubo sa tulo ka letra ug ang mga token nga naa sa stopword set. Gamita ang slider aron tan-awon ang usa ka komento nga moagi sa matag stage. Ang punto: ang matag lakang usa ka makita nga lagda, dili black box.

--- key: p3 src: 14c1228658
**Analytical nga desisyon ang stopwords.** Ang mga pulong sama sa "the", "ang" o "sa" nagdala og grammar, dili content, busa modominar kini sa bisan unsang word count. Ang default set kay English ug usa ka lista sa Filipino. Idugang ang imoha: kung makit-an nimo unya nga ang mga ngalan sa lugar o ang pulong "hospital" ang molamoy sa mga resulta, ibutang kini sa kahon sa dugang nga mga pulong ug isulti kini sa imong write-up. Ang pag-exclude og pulong usa ka desisyon nga kinahanglan nimong madepensahan.

--- key: p4 src: bd954a89f2
**Nganong mauna ang paglimpyo sa pagbasa sa lugar.** Ang geoparsing sa sunod nga lakang mogamit sa *orihinal* nga text, kay ang mga ngalan sa lugar nagdepende sa capital letters ("Baguio" ang siyudad, dili "baguio" ang pulong). Ang nalimpyohan nga mga token gamiton sa ulahi, sa Chapter 2, kung itandi na nato unsay gisulti sa matag lugar.
