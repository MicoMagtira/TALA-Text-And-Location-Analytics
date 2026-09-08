--- key: title src: ae2254e1e9
Land clipping at ang output contract (Lab 4)

--- key: p1 src: 962793a257
Dito nahuhuli ang maruming coordinates na sinasakyan mo mula pa sa Lab 1. Ang clip ay nagtatanggol ng isang bagay na hindi kayang tanggulan ng bounds check: hindi lang kung ang coordinate ay maayos ang porma, kundi kung ito ay nasa lugar na dapat.

--- key: p2 src: e02eb06ade
**Ano ang inaalis ng clip.** Ang layer ay pinapatong sa polygon ng lupain ng Pilipinas at ang mga puntong nasa labas ay itinatapon — 3,467 sa 11,715, humigit-kumulang isang katlo ng dataset. Ang mga iyon ay bumagsak sa London, California at sa gitna ng karagatan. Nasa bawat mapa sila mula pa sa Lab 1 at wala ni isang error message ang bumanggit sa kanila.

--- key: p3 src: 3d0e95524d
**Bakit sa huli ito nangyayari at hindi sa una.** Kung nalinis ito noong ingest, hindi mo kailanman makikita ang problema. Ang buong pipeline ay tumatakbo nang may isang-katlo na basura para maranasan mo ang paggawa ng kumbinsidong mapa mula sa data na mali — na siyang mismong nangyayari sa totoong trabaho kapag ang paglilinis ay awtomatiko at tahimik.

--- key: p4 src: ac2ef9bb07
**Isang babala tungkol sa hangganan.** Ang polygon ng lupain ay 110m Natural Earth, na binuo nang may humigit-kumulang 15 km na buffer para hindi mabitawan ng magaspang na baybayin ang lehitimong puntong nasa dalampasigan. Ibig sabihin, ang clip ay maluwag sa hangganan — kusang inaamin nito ang ilang puntong nasa dagat sa halip na tanggalin ang totoong klinika sa baybayin. Ang alamin kung aling uri ng mali ang mas gusto mo ay bahagi ng trabaho.

--- key: p5 src: 207869792b
**Ang output contract.** Ang GeoJSON at ang `metadata.json` ay magkasamang lumalabas at sinasadya iyon. Ang metadata ay nagtatala ng CRS, ng bilang ng feature, ng mga parameter ng DBSCAN, at ng ginamit na generalization. Kung wala iyon, ang layer ay isang set ng hugis na walang kasaysayan, at walang makakaulit sa nakita mo — kasama ka na sa susunod na buwan.
