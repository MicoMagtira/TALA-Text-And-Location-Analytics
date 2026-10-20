--- key: title
How TALA works

--- key: what
### What TALA does
TALA reads a set of comments that each carry some text and a pair of coordinates, and asks one question: **what are people saying, and where are they saying it?** The bundled example has 12,000 health-service comments. Instead of running a method on all the comments at once, TALA works with **places**: it works out where each comment is from, then compares places with each other.

--- key: chapters
### Two chapters, nine steps
**Lugar** (Filipino for *place*) asks **Where are people?** and has three steps that go in order, because each feeds the next: **1 Data** (load the file and map its columns), **2 Text vs GPS** (find the place each comment names and check it against its GPS point), and **3 Places** (group comments by region, or by cluster).

**Salita** (Filipino for *word*) asks **What is each place saying?** and has six steps you can open in any order: **4 What sets a place apart**, **5 How each place feels**, **6 What they praise or fault**, **7 What they talk about**, **8 Where complaints cluster** and **9 Place report**. If you open one of them before finishing Lugar, TALA runs the earlier steps with default settings and says so at the top of the page.

--- key: why
### Why place-first
A word count over all the comments says what is common, not where. Grouping comments by place lets every later step answer a comparison: which words set one place apart from the rest, which places lean negative once the sample size is taken into account, and where complaints cluster more than chance would explain. The place is the unit of analysis for steps 4 to 9, and you choose it at step 3: **Region** (from a place-name list, easy to read) or **Cluster** (found from the coordinates with DBSCAN).

--- key: dirty
### The deliberate dirty-coordinates lesson
The coordinates in the bundled data are wrong on purpose, and Step 2 is where this shows. About **31%** of the GPS points are invalid (out of range, or not on Philippine land), and about **8%** point somewhere far from the place the comment itself names. About **99.5%** of the place names in the text can be matched to a known place. TALA therefore offers three location sources: **Repaired** (GPS when it agrees or no place is named, otherwise the named place), **GPS only**, or **Agreeing only**. Notice how much a map changes with the choice: checking data before analysing it is part of the method.

--- key: langs
### Five languages
The whole interface is available in English, Filipino, Cebuano, Ilocano and Hiligaynon. Switch at any time from the language chips on Home or from Settings; your results and place choices stay as they are, because only the text on screen changes. Chapter names (Lugar and Salita) and code samples are not translated.

--- key: tips
### Using the pages
Each page opens with one sentence on what it shows. Its **Learn** panel, collapsed by default, holds the method and the code behind it, and can be switched off in Settings. The stars in the sidebar fill in as you finish steps, and you can jump to any step at any time. Progress is kept in this browser; **Forget me** in Settings clears it.
