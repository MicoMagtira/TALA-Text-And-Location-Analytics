--- key: title src: cd2b6a3532
Dagiti Getis-Ord Gi* hotspot

--- key: p1 src: 5a038d0939
**Ti saludsod.** Dadduma a bunggoy dagiti negatibo a komento ket gapu laeng iti gasat. Isaludsod ti Gi* no ti maysa a cell ken dagiti kaarrubana, no pagtiponen, ket ad-adda (hot) wenno kurang (cold) a negatibo ngem iti maited ti random a panagbaraha (shuffling) kadagiti isu met laeng a value. Ikabil ti TALA dagiti komento kadagiti kuadrado a cell, ikeddeng ti value x ti tunggal cell kas paset dagiti negatibo a komento (maikkat dagiti cell nga addaan basbassit a komento ngem ti minimum), ken kwentaen ti Gi* kadagita a cell.

--- key: p2 src: fc9b1bbb8c
**Ti formula.** No adda n a cell, mean X-bar ken standard deviation S ti x, ken binary weights w_ij = 1 no ti cell j ket adda iti uneg ti radius ti cell i (agraman ti i): Gi*_i = (sum_j w_ij x_j - X-bar * W_i) / (S * sqrt((n * sum_j w_ij^2 - W_i^2) / (n - 1))), a ti W_i = sum_j w_ij. Ti resulta ket z-score metten: dagiti value a 1.645, 1.960 ken 2.576 wenno nangatngato ket hot iti 90%, 95% ken 99% a confidence (cold dagiti negatibo). Dagiti kaarruba ket naggapu iti BallTree iti metric (UTM) a coordinates.

--- key: p3 src: 5e521fc88c
**Multiple testing.** Ti maysa a test iti 95% ket biddut iti 5% ti oras, ngem ditoy tunggal cell ket masubok, isu nga adda dagiti cell a kasla "significant" gapu iti gasat uray awan ti pattern. Isu dayta ti gapuna a ti 99% a klase ti kanatalgedan a basa, ken rumbeng a pagduaduaan dagiti 90% a cell. Iti bundled a data nga addaan kadagiti default (20 km a cell, 50 km a radius, saan a basbassit ngem 10 a komento), 309 a cell ti masubok; 4 ti hot (awan iti 99%) ken 7 ti cold. Ti kapigsaan a hot cell (z = 2.4, 50% negatibo iti 10 a komento) ket adda iti asideg ti Apayao. Agarup 3.6% laeng dagiti cell ti significant iti aniaman a direksion, basbassit ngem ti 10% a maited ti gasat laeng iti 90% a level, isu nga awan ti makapakombinsir a bunggoy ti reklamo iti daytoy a dataset iti pakabuklan. Lehitimo a natakuatan dayta.

--- key: p4 src: 4e61c4f9aa
**Napateg dagiti pili.** Ti radius ket rumbeng a sakupen na ti saan a basbassit ngem dua a cell; no saan, gistay saan a maidilig ti tunggal cell kadagiti kaarrubana. Natibtibker dagiti dakdakkel a cell ngem lumabo ti lokal a detalye (ti modifiable areal unit problem). No piliem ti "panaguray", dagiti komento laeng a mangdakamat iti panaguray ti maikabil iti mapa, ken maibilang a negatibo ti komento no negatibo ti basa dagiti nagtunos a sentence-na. Agpapada ti trato dagiti binary weight kadagiti amin a kaarruba; ti inverse-distance weights ket gagangay nga alternatibo.
