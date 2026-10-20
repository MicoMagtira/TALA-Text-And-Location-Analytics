--- key: title src: f6f73da18d
Paano gumagana ang TALA

--- key: what src: 8d6ec00963
### Ano ang ginagawa ng TALA
Binabasa ng TALA ang isang set ng mga komento na may kanya-kanyang text at pares ng coordinates, at iisa ang tanong nito: **ano ang sinasabi ng mga tao, at saan nila ito sinasabi?** May 12,000 komento tungkol sa health services ang bundled na halimbawa. Sa halip na patakbuhin ang isang method sa lahat ng komento nang sabay-sabay, **mga lugar** ang hawak ng TALA: inaalam muna nito kung saan galing ang bawat komento, tapos pinaghahambing nito ang mga lugar sa isa't isa.

--- key: chapters src: 5ed4c46751
### Dalawang chapter, siyam na hakbang
Ang **Lugar** ay nagtatanong ng **Nasaan ang mga tao?** at may tatlong hakbang na sunud-sunod, dahil ang bawat isa ay pinagkukunan ng kasunod: **1 Data** (i-load ang file at i-map ang mga column nito), **2 Text vs GPS** (hanapin ang lugar na binabanggit ng bawat komento at tingnan kung tugma ito sa GPS point nito), at **3 Mga lugar** (pangkatin ang mga komento ayon sa rehiyon, o ayon sa cluster).

Ang **Salita** ay nagtatanong ng **Ano ang sinasabi ng bawat lugar?** at may anim na hakbang na puwede mong buksan sa kahit anong ayos: **4 Ano ang nagpapaiba sa isang lugar**, **5 Damdamin ng bawat lugar**, **6 Ano ang pinupuri o inirereklamo**, **7 Ano ang pinag-uusapan nila**, **8 Saan nagkukumpol ang reklamo** at **9 Ulat ng lugar**. Kapag binuksan mo ang isa sa mga ito bago matapos ang Lugar, patatakbuhin ng TALA ang mga naunang hakbang gamit ang default na settings at sasabihin ito sa itaas ng page.

--- key: why src: 47756a40db
### Bakit lugar muna
Ang bilang ng salita sa lahat ng komento ay nagsasabi kung ano ang karaniwan, pero hindi kung saan. Kapag pinangkat ang mga komento ayon sa lugar, bawat susunod na hakbang ay nakakasagot ng paghahambing: aling mga salita ang nagpapaiba sa isang lugar kumpara sa iba, aling mga lugar ang mas negatibo kapag isinaalang-alang na ang laki ng sample, at saan nagkukumpol ang mga reklamo nang higit sa kayang ipaliwanag ng tsamba. Ang lugar ang unit of analysis sa mga hakbang 4 hanggang 9, at ikaw ang pipili nito sa hakbang 3: **Rehiyon** (mula sa listahan ng mga pangalan ng lugar, madaling basahin) o **Cluster** (hinahanap mula sa coordinates gamit ang DBSCAN).

--- key: dirty src: e7b2956f61
### Ang sadyang aral ng maruming coordinates
Sadyang mali ang coordinates sa bundled na data, at sa Hakbang 2 ito lumalabas. Mga **31%** ng mga GPS point ang invalid (labas sa range, o wala sa lupain ng Pilipinas), at mga **8%** ang tumuturo sa lugar na malayo sa lugar na mismong binabanggit ng komento. Mga **99.5%** ng mga pangalan ng lugar sa text ang naitutugma sa isang kilalang lugar. Kaya tatlong pagkukunan ng lokasyon ang inaalok ng TALA: **Inayos** (GPS kapag tugma ito o walang binanggit na lugar, kung hindi ay ang binanggit na lugar), **GPS lang**, o **Kung saan lang tugma**. Pansinin kung gaano kalaki ang ipinagbabago ng mapa depende sa pinili mo: bahagi ng method ang pagsuri sa data bago ito i-analyze.

--- key: langs src: 8ec9aa5ef0
### Limang wika
Available ang buong interface sa English, Filipino, Cebuano, Ilocano at Hiligaynon. Puwede kang lumipat kahit kailan gamit ang mga language chip sa Home o sa Settings; hindi nagbabago ang mga resulta at napili mong lugar, dahil ang text lang sa screen ang nagbabago. Hindi isinasalin ang mga pangalan ng chapter (Lugar at Salita) at ang mga code sample.

--- key: tips src: c3c91e1881
### Paggamit ng mga page
Nagsisimula ang bawat page sa isang pangungusap tungkol sa ipinapakita nito. Ang **Learn** panel nito, na nakasara sa simula, ang naglalaman ng method at ng code sa likod nito, at puwede itong i-off sa Settings. Napupuno ang mga bituin sa sidebar habang tinatapos mo ang mga hakbang, at puwede kang tumalon sa kahit anong hakbang kahit kailan. Nakatabi ang progress mo sa browser na ito; binubura ito ng **Kalimutan ako** sa Settings.
