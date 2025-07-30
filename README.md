# gen-ai-memory

The length of original, raw text stories are as following (stories in original order):

## D'Artagnan Romances (Dumas)

[pg1257_The_three_musketeers,
pg1259_Twenty_years_after,
pg2609_The_Vicomte_de_Bragelonne,
pg2710_Louise_de_la_Vallière,
pg2759_The_Man_in_the_Iron_Mask]

- pg1257_The_three_musketeers:
    Word count: 232479
    Token count: 330458

- pg1259_Twenty_years_after:
    Word count: 245095
    Token count: 352110

- pg2609_The_Vicomte_de_Bragelonne:
    Word count: 192302
    Token count: 276980

- pg2710_Louise_de_la_Vallière:
    Word count: 170809
    Token count: 243877

- pg2759_The_Man_in_the_Iron_Mask:
    Word count: 176619
    Token count: 255468

Total number of words:1017304
Total number of tokens: 1458893




## La Comédie humaine (Balzac)

Balzac intentionally created a universe of interrelated stories, characters, families, and social dynamics that span across different classes, regions, and decades of French life, primarily during the Restoration and July Monarchy periods (1815–1848). He structured the series into sections and subseries to represent different layers of society.

stories = [
    "pg1680_At_the_Sign_of_the_Cat_and_Racket",
    "pg1305_The_Ball_at_Sceaux",
    "pg1196_The_Purse",
    "pg1374_Vendetta",
    "pg1357_Madame_Firmiani",
    "pg1810_A_Second_Home",
    "pg1411_Domestic_Peace",
    "pg1369_Paz_(La_Fausse_Maitresse)",
    "pg1373_Etude_de_femme",
    "pg1714_Another_Study_of_Woman",
    "pg1710_La_Grand_Breteche",
    "pg1898_Albert_Savarus",
    "pg1941_Letters_of_Two_Brides",
    "pg1481_A_Daughter_of_Eve",
    "pg1950_A_Woman_of_Thirty",
    "pg1729_The_Deserted_Woman",
    "pg1428_La_Grenadiere",
    "pg1189_The_Message",
    "pg1389_Gobseck",
    "pg1556_A_Marriage_Contract",
    "pg1403_A_Start_in_Life",
    "pg1482_Modeste_Mignon",
    "pg1957_Beatrix",
    "pg1683_Honorine",
    "pg1954_Colonel_Chabert",
    "pg1220_The_Atheist's_Mass",
    "pg1410_The_Commission_in_Lunacy",
    "pg1230_Pierre_Grassou",
    "pg1715_Eugenie_Grandet",
    "pg7927_The_Celibates",
    "pg1345_The_Vicar_of_Tours",
    "pg1380_The_Two_Brothers",
    "pg1474_The_Illustrious_Gaudissart",
    "pg1912_The_Muse_of_the_Department",
    "pg1352_An_Old_Maid",
    "pg1405_The_Collection_of_Antiquities",
    "pg1569_The_Lily_of_the_Valley"
]


file: texts/la_comédie_humaine_(balzac)/original/pg1680_At_the_Sign_of_the_Cat_and_Racket.txt
Word count: 24490
Token count: 33168
file: texts/la_comédie_humaine_(balzac)/original/pg1305_The_Ball_at_Sceaux.txt
Word count: 24911
Token count: 33924
file: texts/la_comédie_humaine_(balzac)/original/pg1196_The_Purse.txt
Word count: 14964
Token count: 20254
file: texts/la_comédie_humaine_(balzac)/original/pg1374_Vendetta.txt
Word count: 27997
Token count: 39143
file: texts/la_comédie_humaine_(balzac)/original/pg1357_Madame_Firmiani.txt
Word count: 10694
Token count: 14834
file: texts/la_comédie_humaine_(balzac)/original/pg1810_A_Second_Home.txt
Word count: 29380
Token count: 39674
file: texts/la_comédie_humaine_(balzac)/original/pg1411_Domestic_Peace.txt
Word count: 16484
Token count: 22637
file: texts/la_comédie_humaine_(balzac)/original/pg1369_Paz_(La_Fausse_Maitresse).txt
Word count: 22233
Token count: 30913
file: texts/la_comédie_humaine_(balzac)/original/pg1373_Etude_de_femme.txt
Word count: 6653
Token count: 9236
file: texts/la_comédie_humaine_(balzac)/original/pg1714_Another_Study_of_Woman.txt
Word count: 18449
Token count: 25703
file: texts/la_comédie_humaine_(balzac)/original/pg1710_La_Grand_Breteche.txt
Word count: 11168
Token count: 15440
file: texts/la_comédie_humaine_(balzac)/original/pg1898_Albert_Savarus.txt
Word count: 44579
Token count: 62380
file: texts/la_comédie_humaine_(balzac)/original/pg1941_Letters_of_Two_Brides.txt
Word count: 87819
Token count: 117127
file: texts/la_comédie_humaine_(balzac)/original/pg1481_A_Daughter_of_Eve.txt
Word count: 44729
Token count: 62330
file: texts/la_comédie_humaine_(balzac)/original/pg1950_A_Woman_of_Thirty.txt
Word count: 73569
Token count: 99574
file: texts/la_comédie_humaine_(balzac)/original/pg1729_The_Deserted_Woman.txt
Word count: 20005
Token count: 27285
file: texts/la_comédie_humaine_(balzac)/original/pg1428_La_Grenadiere.txt
Word count: 12180
Token count: 16470
file: texts/la_comédie_humaine_(balzac)/original/pg1189_The_Message.txt
Word count: 8223
Token count: 11066
file: texts/la_comédie_humaine_(balzac)/original/pg1389_Gobseck.txt
Word count: 25820
Token count: 35970
file: texts/la_comédie_humaine_(balzac)/original/pg1556_A_Marriage_Contract.txt
Word count: 52305
Token count: 71526
file: texts/la_comédie_humaine_(balzac)/original/pg1403_A_Start_in_Life.txt
Word count: 61499
Token count: 88167
file: texts/la_comédie_humaine_(balzac)/original/pg1482_Modeste_Mignon.txt
Word count: 97004
Token count: 136026
file: texts/la_comédie_humaine_(balzac)/original/pg1957_Beatrix.txt
Word count: 119234
Token count: 168596
file: texts/la_comédie_humaine_(balzac)/original/pg1683_Honorine.txt
Word count: 33475
Token count: 45651
file: texts/la_comédie_humaine_(balzac)/original/pg1954_Colonel_Chabert.txt
Word count: 27204
Token count: 37380
file: texts/la_comédie_humaine_(balzac)/original/pg1220_The_Atheist's_Mass.txt
Word count: 9921
Token count: 13506
file: texts/la_comédie_humaine_(balzac)/original/pg1410_The_Commission_in_Lunacy.txt
Word count: 31036
Token count: 43225
file: texts/la_comédie_humaine_(balzac)/original/pg1230_Pierre_Grassou.txt
Word count: 10907
Token count: 15389

Total counts for all files:
Total Word count: 966932
Total Token count: 1336594