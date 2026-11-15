# Journal de bord — Tournoi du dilemme du prisonnier itéré

HAI716I Projet 2 (partie 1) — Kevin HARAUT

Ce journal est tenu au fur et à mesure du travail. Les entrées sont dans l'ordre
chronologique ; chaque étape renvoie au commit correspondant.

---

## Protocole

| Paramètre | Valeur | Raison |
|---|---|---|
| Matrice des gains | CC = 3/3, CD = 0/5, DC = 5/0, DD = 2/2 | Celle du cours et du sujet. |
| Tours par partie | 200 | Format d'Axelrod |
| Parties par duel | 5 | Format d'Axelrod |
| Appariement | Chaque paire de stratégies distinctes, une fois | Pas de match contre soi-même |
| Score | Somme des points sur tous les duels | Le meilleur total gagne, pas le nombre de duels gagnés. |
| Graine aléatoire | 67 | Un seul générateur `random.Random(graine)` sert à tout le tournoi. Les essais des entrées 1 à 5 ont été faits avec la graine 42, avant le choix définitif (voir entrée 6). |
| Probabilité de trahison de JOSS | 10 % | « remplace C par D une fois sur dix ». |

### Choix de conception

- **Une stratégie = une fonction** `strategie(mes_coups, coups_adverses, rng) -> "C" | "D"`.
  Elle déduit tout de l'historique, sans état caché : rien à réinitialiser entre deux
  parties, et chaque stratégie se teste isolément.
- **Simultanéité** : au tour *t*, chaque stratégie ne reçoit que les coups des tours
  0 à *t-1*. Le coup de l'adversaire au tour *t* est calculé sans connaître le sien.
- **Hasard centralisé** : le moteur passe le même `rng` à toutes les stratégies.
  Aucune stratégie n'appelle `random.random()` directement, sinon la graine ne
  contrôlerait plus tout.

---

## Fiches des stratégies

### Population de base 

#### ALL-D
- **Règle :** trahit à tous les tours.
- **Devrait bien jouer contre :** les stratégies qui coopèrent sans punir (RANDOM).
- **Devrait mal jouer contre :** rien ne la bat en duel, mais face à des stratégies qui ripostent (TFT, TESTER, JOSS) elle tombe en D/D à 2 points par tour.

#### RANDOM
- **Règle :** C ou D avec une chance sur deux, sans regarder l'historique.
- **Devrait bien jouer contre :** personne en particulier ; elle gagne ses 5 points quand elle trahit un coopérateur.
- **Devrait mal jouer contre :** ALL-D, qui l'exploite chaque fois qu'elle coopère. Elle ne punit jamais.

#### TIT-FOR-TAT (TFT)
- **Règle :** C au premier tour, puis rejoue le coup de l'adversaire au tour précédent.
- **Devrait bien jouer contre :** les stratégies coopératives (coopération totale à 3 points par tour).
- **Devrait mal jouer contre :** ALL-D (perd le premier tour, puis D/D), et les stratégies qui trahissent par surprise (JOSS, TESTER).
- **Propriété :** elle ne bat jamais son adversaire en duel, elle fait match nul.

#### JOSS
- **Règle :** joue comme TFT, mais quand elle devrait coopérer, trahit avec une probabilité de 10 %.
- **Devrait bien jouer contre :** les coopérateurs naïfs. Elle exploite parfois sans être punie.
- **Devrait mal jouer contre :** TFT et elle-même : une seule trahison déclenche un écho, et une deuxième fait basculer en D/D permanent.
- **Interprétation :** « une fois sur dix » est lu comme une probabilité de 10 %.

#### TESTER
- **Règle :** D au premier tour. Si l'adversaire riposte (a déjà joué D), joue TFT ; sinon répète le motif C, C, D.
- **Devrait bien jouer contre :** les coopérateurs naïfs qui ne punissent jamais (exploités un tour sur trois).
- **Devrait mal jouer contre :** toutes les stratégies réactives. Sa sonde du premier tour déclenche une riposte ; comme elle ne s'excuse pas, l'écho de représailles ne s'arrête jamais.

### Nouvelles stratégies (étape 2)

#### GRIM 
- **Règle :** coopère tant que l'adversaire n'a jamais trahi ; dès sa première trahison, trahit jusqu'à la fin de la partie.
- **Devrait bien jouer contre :** les coopérateurs (coopération totale comme TFT) et RANDOM (elle l'exploite à partir de sa première trahison, contrairement à TFT qui continue à lui pardonner).
- **Devrait mal jouer contre :** les stratégies qui trahissent une seule fois par erreur ou par sonde (JOSS, TESTER) : elle ne pardonne jamais, donc D/D jusqu'à la fin. Elle sera très fragile au bruit (étape 3).
- **Raison de l'ajout :** c'est TFT sans pardon. La comparer à TFT montre ce que rapporte le pardon.

#### PAVLOV 
- **Règle :** coopère au premier tour. Ensuite, si le tour précédent a rapporté beaucoup (3 ou 5 points), rejoue le même coup ; sinon (0 ou 2 points), change de coup.
- **Devrait bien jouer contre :** les coopératives (coopération totale), et elle-même même après une erreur : deux PAVLOV qui se trahissent par accident tombent en D/D, changent toutes les deux et reviennent à C/C.
- **Devrait mal jouer contre :** ALL-D. Après un D/D (2 points, « perdu »), elle repasse à C et se fait reprendre : elle alterne C et D, soit 1 point par tour en moyenne, deux fois moins que TFT.
- **Raison de l'ajout :** une stratégie qui pardonne, mais d'une façon différente de TFT.

#### ALL-C
- **Règle :** coopère à tous les tours, quoi que fasse l'adversaire.
- **Devrait bien jouer contre :** les stratégies gentilles (TFT, GRIM, PAVLOV, elle-même) : coopération totale, 600 par partie.
- **Devrait mal jouer contre :** toutes celles qui trahissent, car elle ne punit jamais : ALL-D (0 point), RANDOM, TESTER (seule à subir le motif C, C, D) et JOSS.
- **Raison de l'ajout :** Elle sert à voir quelles stratégies profitent d'un pigeon, et donc comment la composition de la population change le classement.

---

## Chronologie

### Vendredi 13 novembre 2026 — séance

#### 1. Moteur d'une partie — commit `feat: moteur de partie et matrice des gains (ALL-D, TFT)`

Matrice des gains et fonction `jouer_partie`. Pour la tester : ALL-D et TFT.

Vérification à la main :

```
TFT  vs TFT  : (600, 600)    200 tours × 3
TFT  vs ALL-D: (398, 403)    tour 1 : 0/5, puis 199 × 2
ALL-D vs ALL-D: (400, 400)   200 × 2
```

Première observation : TFT perd son duel contre ALL-D, de 5 points.

#### 2. RANDOM — commit `feat: stratégie RANDOM`

```
graine 42 : (506, 501)
graine 42 : (506, 501)    -> même graine, même partie : reproductible
graine 7  : (513, 508)    -> autre graine, autre partie
part de C sur 10000 coups : 0.499
```

TFT perd encore de 5 points contre RANDOM : chaque trahison subie est rendue au tour
suivant, sauf la dernière. TFT ne peut jamais battre son adversaire.

#### 3. JOSS — commit `feat: stratégie JOSS`

```
JOSS vs TFT  : (409, 404)
JOSS vs ALL-D: (398, 403)
JOSS vs JOSS : (403, 403)
TFT  vs TFT  : (600, 600)   (pour comparer)

40 premiers coups de JOSS contre TFT :
JOSS: CDCDCDCDCDCDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
TFT : CCDCDCDCDCDCDDDDDDDDDDDDDDDDDDDDDDDDDDDD
```

**Écho des représailles :** la trahison surprise du tour 2 lance une alternance C/D ;
la deuxième trahison (tour 13) fait basculer les deux en D/D jusqu'à la fin.
JOSS « gagne » son duel 409 à 404, mais les deux perdent environ 200 points par rapport
à deux TFT qui coopèrent.

#### 4. TESTER — commit `feat: stratégie TESTER`

(La version corrigée ci-dessous a été écrite avant le commit : seule la version du cours
figure dans l'historique git.)

**Impasse :** la première version suivait la description de TESTER donnée par Hofstadter :
après la riposte, TESTER « s'excuse » en coopérant une fois, puis joue TFT ; sinon C, C,
puis D un tour sur deux. En relisant les diapositives du cours, la définition
attendue est différente : **pas d'excuse**, et le motif d'exploitation est **C, C, D**.
J'ai corrigé pour suivre le cours, puisque le sujet impose les stratégies du cours.

L'écart change beaucoup le résultat contre TFT :

| | Version Hofstadter (avec excuse) | Version du cours |
|---|---|---|
| TESTER vs TFT | 599 / 599 (coopération après l'excuse) | **500 / 500** (écho C/D permanent) |
| TESTER vs TESTER | 599 / 599 | **400 / 400** (D/D permanent) |

Version du cours, 12 premiers coups :

```
vs TFT    score (500, 500)  TESTER DCDCDCDCDCDC | TFT CDCDCDCDCDCD
vs ALL-C  score (734, 399)  TESTER DCCDCCDCCDCC | ALL-C CCCCCCCCCCCC
vs ALL-D  score (400, 400)  TESTER DDDDDDDDDDDD | ALL-D DDDDDDDDDDDD
vs TESTER score (400, 400)  TESTER DDDDDDDDDDDD | TESTER DDDDDDDDDDDD
vs JOSS   score (401, 401)  TESTER DCDDDDDDDDDD | JOSS CDDDDDDDDDDD
```

(ALL-C, « coopère toujours », n'est pas une stratégie du tournoi : c'est un adversaire
jetable pour vérifier la branche C, C, D, qui ne se déclenche jamais contre la population
du cours puisque toutes ripostent.)

Leçon : sans pardon, une seule trahison initiale suffit à détruire la coopération.

#### 5. Tournoi tous contre tous — commit `feat: tournoi tous contre tous et classement`

Fonction `tournoi` : chaque paire de stratégies distinctes (`itertools.combinations`)
joue 5 parties ; on cumule les scores. Fonction `classement` : tri décroissant.

**Validation sur le mini-tournoi du cours** — 2 TFT + 1 ALL-D, 10 tours, 1 partie :

```
Mini-tournoi du cours : [('TFT1', 48), ('TFT2', 48), ('ALL-D', 46)]
```

Deux lancements avec la graine 42 donnent le même résultat.

**Premier essai du tournoi d'Axelrod** (graine 42, 5 parties × 200 tours) :

```
1. ALL-D        9467
2. TIT-FOR-TAT  9056
3. TESTER       9042
4. JOSS         8721
5. RANDOM       8390

               ALL-D  RANDOM TIT-FOR  TESTER    JOSS
ALL-D              -    3440    2015    2000    2012
RANDOM          1040       -    2497    2485    2368
TIT-FOR-TAT     1990    2487       -    2500    2079
TESTER          2000    2510    2500       -    2032
JOSS            1992    2593    2104    2032       -
```

(Lecture : ligne = stratégie, colonne = adversaire, case = points de la ligne sur les 5 parties.)

Premières observations, à approfondir avec `main.py` :
- **ALL-D gagne grâce à RANDOM** : 3440 points contre lui, environ 1400 de plus que contre
  n'importe qui d'autre. Contre les autres, elle plafonne vers 2000 (D/D).
- **TFT n'a aucun partenaire coopératif** : écho permanent avec TESTER (2500), D/D avec
  JOSS (2079). Elle ne coopère pleinement avec personne.

### Dimanche 15 novembre 2026

#### 6. Point d'entrée `main.py` — commit `feat: main.py (graine, classement, tableau des duels, option --contre-soi)`

`main.py` lit les options (`--seed`, `--parties`, `--tours`), crée **un seul**
`random.Random(graine)`, lance le tournoi et affiche le classement et le tableau des duels.

**Choix de la graine :** les essais précédents utilisaient la graine 42. J'ai choisi
la graine **67** comme graine officielle du projet (valeur par défaut de `main.py`).
Le choix est arbitraire : ce qui compte, c'est qu'elle soit fixée et notée. Avec 42
comme avec 67, l'ordre du classement est identique dans les deux formats ; seuls les
duels contre RANDOM et JOSS varient de quelques dizaines de points.

Commande : `python3 main.py --seed 67`

![Classement de l'étape 1, format du cours, graine 67](captures/etape1_classement.png)

```
Tournoi : 5 stratégies, 5 parties de 200 tours par duel, sans match contre soi-même, graine 67

Classement
------------------------------
 1. ALL-D             9476
 2. TIT-FOR-TAT       9100
 3. TESTER            9051
 4. JOSS              8716
 5. RANDOM            8421

Points de la ligne contre la colonne
                     ALL-D       RANDOM  TIT-FOR-TAT       TESTER         JOSS
ALL-D                    -         3446         2015         2000         2015
RANDOM                1036            -         2538         2517         2330
TIT-FOR-TAT           1990         2518            -         2500         2092
TESTER                2000         2532         2500            -         2019
JOSS                  1990         2590         2117         2019            -
```

**Robustesse :** relancé avec les graines 1 à 10, ALL-D est **premier dans les 10 cas**.
Seul l'ordre TIT-FOR-TAT / TESTER (2e et 3e) change selon la graine : leurs scores ne
diffèrent que de quelques dizaines de points.

**Découverte : le match contre soi-même.** En cherchant pourquoi TFT ne gagne pas, j'ai
remarqué que le cours fait jouer le mini-tournoi sans match contre soi (CM4 p.68), alors
que dans le tournoi d'Axelrod de 1980, chaque programme affrontait aussi son double. J'ai
ajouté l'option `--contre-soi` pour tester les deux formats (on ne compte alors que le
score d'une des deux copies).

Commande : `python3 main.py --seed 67 --contre-soi`

![Classement de l'étape 1 avec matchs contre soi-même, graine 67](captures/etape1_contre_soi.png)

```
Tournoi : 5 stratégies, 5 parties de 200 tours par duel, avec matchs contre soi-même, graine 67

Classement
------------------------------
 1. TIT-FOR-TAT      12083
 2. ALL-D            11476
 3. TESTER           11037
 4. RANDOM           10937
 5. JOSS             10754

Points de la ligne contre la colonne
                     ALL-D       RANDOM  TIT-FOR-TAT       TESTER         JOSS
ALL-D                 2000         3446         2015         2000         2015
RANDOM                1036         2521         2508         2494         2378
TIT-FOR-TAT           1990         2493         3000         2500         2100
TESTER                2000         2504         2500         2000         2033
JOSS                  1990         2553         2125         2033         2053
```

Avec les graines 1 à 10 : TIT-FOR-TAT est **premier dans les 10 cas**.

#### Question de l'étape 1 : TIT-FOR-TAT gagne-t-il ?

**Non, pas au format du cours** : ALL-D gagne (9476 contre 9100 pour TFT, graine 67),
et c'est le cas avec toutes les graines testées. Le résultat diffère de 1980 pour trois raisons.

**1. TFT n'a personne avec qui coopérer.** TFT ne gagne jamais un duel : elle prospère
seulement en coopérant à 3 points par tour avec d'autres stratégies coopératives
(CM4 p.69). En 1980, une grande partie des programmes étaient « gentils » (ne trahissent
jamais en premier). Ici, aucune des quatre autres stratégies ne lui permet de coopérer
durablement :
- ALL-D trahit toujours ;
- RANDOM trahit une fois sur deux ;
- TESTER trahit au premier tour et ne s'excuse jamais : écho C/D pendant 200 tours (500 par partie au lieu de 600) ;
- JOSS trahit par surprise : écho, puis D/D permanent.

**2. ALL-D a une proie : RANDOM.** ALL-D marque 3446 contre RANDOM, soit environ 1400 points
de plus que contre n'importe quelle autre stratégie. C'est ce seul duel qui lui donne
l'avance. Contre les stratégies qui ripostent, elle plafonne à environ 2000 (D/D).

**3. Le format compte : sans match contre soi, TFT perd sa meilleure rencontre.** Contre
son double, TFT coopère pendant 200 tours (3000 points sur 5 parties), alors qu'ALL-D
contre son double ne fait que 2000. Ce seul match rapporte 1000 points d'écart en faveur
de TFT, assez pour renverser le classement (12083 contre 11476). Le double de TFT est le
« partenaire qui pense comme elle » qui lui manquait dans la population du cours.

**Conclusion :** le succès de TFT dépend de la population. Elle gagne dès qu'elle
rencontre assez de stratégies coopératives, ne serait-ce que son propre double ; dans une
petite population de stratégies agressives ou bruitées, la stratégie qui exploite le
mieux le maillon faible (ALL-D contre RANDOM) l'emporte.

---


## Étape 2 : nouvelles stratégies

#### 7. GRIM — commit `feat: stratégie GRIM`

Première stratégie absente du cours (fiche plus haut). Test contre chaque stratégie,
graine 67, 16 premiers coups :

```
GRIM vs TFT    score (600, 600)   GRIM CCCCCCCCCCCCCCCC | TFT CCCCCCCCCCCCCCCC
GRIM vs ALL-D  score (398, 403)   GRIM CDDDDDDDDDDDDDDD | ALL-D DDDDDDDDDDDDDDDD
GRIM vs RANDOM score (678, 218)   GRIM CCDDDDDDDDDDDDDD | RANDOM CDDCDCDDCCCCCCCC
GRIM vs TESTER score (401, 401)   GRIM CDDDDDDDDDDDDDDD | TESTER DCDDDDDDDDDDDDDD
GRIM vs JOSS   score (401, 401)   GRIM CDDDDDDDDDDDDDDD | JOSS DCDDDDDDDDDDDDDD
GRIM vs GRIM   score (600, 600)   GRIM CCCCCCCCCCCCCCCC | GRIM CCCCCCCCCCCCCCCC
```

Observations :
- **Contre RANDOM, GRIM fait 678 par partie**, contre environ 500 pour TFT. Dès que RANDOM
  trahit une fois (tour 2), GRIM passe en D définitif et récolte 5 points chaque fois que
  RANDOM coopère. GRIM combine la gentillesse de TFT (600 contre les coopérateurs) et
  l'exploitation de RANDOM par ALL-D.
- **Contre TESTER et JOSS, GRIM tombe en D/D dès le début** (401) : une seule trahison
  suffit. Ici, la partie avec JOSS a commencé par une trahison aléatoire de JOSS au
  premier tour.

Prédiction (avant de relancer le tournoi) : GRIM devrait se classer haut, peut-être
devant ALL-D, car elle gagne presque autant qu'ALL-D contre RANDOM et beaucoup plus
contre TFT.

#### 8. PAVLOV — commit `feat: stratégie PAVLOV`

Implémentation : avec la matrice du cours, « beaucoup gagné » (3 ou 5) arrive exactement
quand l'adversaire a coopéré, et « peu gagné » (0 ou 2) quand il a trahi. La règle s'écrit
donc : si l'adversaire a joué C, je garde mon coup ; s'il a joué D, je change.

Test contre chaque stratégie, graine 67, 16 premiers coups :

```
PAVLOV vs TFT    score (600, 600)   PAVLOV CCCCCCCCCCCCCCCC | TFT CCCCCCCCCCCCCCCC
PAVLOV vs ALL-D  score (200, 700)   PAVLOV CDCDCDCDCDCDCDCD | ALL-D DDDDDDDDDDDDDDDD
PAVLOV vs RANDOM score (490, 500)   PAVLOV CCDCCDDCDDDDDDDD | RANDOM CDDCDCDDCCCCCCCC
PAVLOV vs TESTER score (467, 467)   PAVLOV CDDCDDCDDCDDCDDC | TESTER DCDDCDDCDDCDDCDD
PAVLOV vs JOSS   score (440, 490)   PAVLOV CDDCDDCDDCDDCDDC | JOSS DCDDCDDCDDCDDCDD
PAVLOV vs GRIM   score (600, 600)   PAVLOV CCCCCCCCCCCCCCCC | GRIM CCCCCCCCCCCCCCCC
PAVLOV vs PAVLOV score (600, 600)   PAVLOV CCCCCCCCCCCCCCCC | PAVLOV CCCCCCCCCCCCCCCC
```

Observations :
- **Contre ALL-D, PAVLOV est le pire de toutes** : 200 points (C, D, C, D…). Après un D/D
  à 2 points, elle « croit » avoir perdu et revient à C, où elle prend 0. TFT, elle, reste
  en D et fait 398.
- **Contre TESTER, cycle de longueur 3** (PAVLOV C, D, D / TESTER D, C, D) : 0 + 5 + 2 = 7 points
  tous les 3 tours, soit 467 par partie, moins que TFT contre TESTER (500).
- **Contre les gentilles, coopération totale** (600), comme TFT et GRIM.

Prédiction (avant de relancer le tournoi) : sans bruit, PAVLOV devrait se classer **en
dessous de TFT**, à cause de la perte face à ALL-D (environ 1000 points de moins sur 5 parties).
Son avantage ne devrait apparaître qu'avec le bruit (étape 3).

#### 9. ALL-C — commit `feat: stratégie ALL-C`

Test contre chaque stratégie, graine 67, 12 premiers coups :

```
ALL-C vs ALL-D  score (0, 1000)    ALL-C CCCCCCCCCCCC | ALL-D DDDDDDDDDDDD
ALL-C vs RANDOM score (282, 812)   ALL-C CCCCCCCCCCCC | RANDOM CDDCDCDDCCCC
ALL-C vs TFT    score (600, 600)   ALL-C CCCCCCCCCCCC | TFT CCCCCCCCCCCC
ALL-C vs TESTER score (399, 734)   ALL-C CCCCCCCCCCCC | TESTER DCCDCCDCCDCC
ALL-C vs JOSS   score (516, 656)   ALL-C CCCCCCCCCCCC | JOSS DCCCCCCCCDCD
ALL-C vs GRIM   score (600, 600)   ALL-C CCCCCCCCCCCC | GRIM CCCCCCCCCCCC
ALL-C vs PAVLOV score (600, 600)   ALL-C CCCCCCCCCCCC | PAVLOV CCCCCCCCCCCC
ALL-C vs ALL-C  score (600, 600)   ALL-C CCCCCCCCCCCC | ALL-C CCCCCCCCCCCC
```

Observations :
- **Qui profite du pigeon ?** Uniquement les stratégies qui trahissent : ALL-D (1000 par
  partie, contre 400 contre elle-même), RANDOM (812), TESTER (734) et JOSS (656). Les
  gentilles (TFT, GRIM, PAVLOV) font 600, exactement comme contre n'importe quelle gentille :
  elles ne gagnent rien de plus avec un pigeon.
- **TESTER sort enfin sa branche d'exploitation** (motif C, C, D) : avec la population du
  cours, elle ne se déclenchait jamais, puisque tout le monde ripostait.

Prédiction (avant de relancer le tournoi) : ALL-C sera dernière. Elle devrait surtout
**profiter à ALL-D** (+1000 par partie, soit +5000 sur 5 parties), qui pourrait ainsi
rester en tête malgré l'arrivée de GRIM et PAVLOV.

#### 10. Tournoi avec la population élargie — commit `feat: option --etape 2 (population élargie)`

`main.py` accepte maintenant `--etape 1` (les 5 stratégies du cours) ou `--etape 2`
(les 5 du cours + GRIM, PAVLOV, ALL-C).

Commande : `python3 main.py --etape 2`

<!-- CAPTURE : captures/etape2_classement.png -->

```
Étape 2 — Tournoi : 8 stratégies, 5 parties de 200 tours par duel, sans match contre soi-même, graine 67

Classement
------------------------------
 1. ALL-D            19991
 2. GRIM             18578
 3. TIT-FOR-TAT      18085
 4. TESTER           17091
 5. PAVLOV           17071
 6. JOSS             16446
 7. RANDOM           15944
 8. ALL-C            15204

Points de la ligne contre la colonne
                     ALL-D       RANDOM  TIT-FOR-TAT       TESTER         JOSS         GRIM       PAVLOV        ALL-C
ALL-D                    -         3446         2015         2000         2015         2015         3500         5000
RANDOM                1036            -         2538         2517         2330         1007         2520         3996
TIT-FOR-TAT           1990         2518            -         2500         2077         3000         3000         3000
TESTER                2000         2532         2500            -         2049         2005         2335         3670
JOSS                  1990         2590         2102         2049            -         2081         2436         3198
GRIM                  1990         3507         3000         2005         2076            -         3000         3000
PAVLOV                1000         2455         3000         2335         2281         3000            -         3000
ALL-C                    0         1506         3000         1995         2703         3000         3000            -
```

**Robustesse :** avec les graines 1 à 10, les trois premières places sont toujours
ALL-D, GRIM, TIT-FOR-TAT, et ALL-C est toujours dernière. Seuls PAVLOV / TESTER
(4e et 5e) s'échangent une fois sur dix.

Avec les matchs contre soi-même (`python3 main.py --etape 2 --contre-soi`), **ALL-D reste
première** (21991, devant GRIM 21545 et TFT 21025), alors qu'à l'étape 1 ce format faisait
gagner TFT. Même résultat sur les graines 1 à 10.

**Comparaison avec l'étape 1**

| Rang | Étape 1 (5 stratégies) | Étape 2 (8 stratégies) |
|---|---|---|
| 1 | ALL-D | ALL-D |
| 2 | TIT-FOR-TAT | **GRIM** (nouvelle) |
| 3 | TESTER | TIT-FOR-TAT |
| 4 | JOSS | TESTER |
| 5 | RANDOM | **PAVLOV** (nouvelle) |
| 6 | | JOSS |
| 7 | | RANDOM |
| 8 | | **ALL-C** (nouvelle) |

L'ordre relatif des 5 stratégies du cours ne change pas. Les trois nouvelles s'insèrent :
GRIM juste sous ALL-D, PAVLOV au milieu, ALL-C en dernier.

**Vérification des prédictions faites en ajoutant les stratégies**

| Prédiction | Résultat |
|---|---|
| GRIM se classe haut, peut-être devant ALL-D | **En partie.** 2e, devant TFT, mais derrière ALL-D. |
| PAVLOV sous TFT sans bruit | **Oui.** 5e. Elle perd 1000 points contre ALL-D, là où TFT en fait 1990. |
| ALL-C dernière, et profite surtout à ALL-D | **Oui.** ALL-D prend 5000 points à ALL-C, les gentilles seulement 3000. |

**Pourquoi ALL-D reste en tête : elle vit de ses proies.** Sur ses 19991 points, ALL-D en
prend 5000 à ALL-C et 3500 à PAVLOV (qui revient sans cesse à C), en plus de 3446 à RANDOM.
Les trois stratégies qui ne punissent pas (ou mal) lui rapportent à elles seules 11946 points.

**Expérience : le même tournoi sans ALL-C.** Pour vérifier que c'est bien la proie qui fait
gagner ALL-D, j'ai relancé le tournoi en retirant uniquement ALL-C (graine 67) :

```
python3 -c "
import random
from moteur import tournoi, classement
from main import POPULATION_ELARGIE as P
pop = {n: s for n, s in P.items() if n != 'ALL-C'}
for n, s in classement(tournoi(pop, rng=random.Random(67))[0]): print(f'{n:12} {s}')
"

GRIM         15573
TIT-FOR-TAT  15106
ALL-D        14991
PAVLOV       14092
TESTER       13405
JOSS         13274
RANDOM       11948
```

**Sans ALL-C, ALL-D passe de la 1re à la 3e place, et GRIM gagne.** Une seule stratégie
naïve suffit à renverser le classement : ALL-C rapporte 5000 points à ALL-D mais seulement
3000 aux gentilles, soit 2000 points d'écart en faveur d'ALL-D.

**Pourquoi GRIM passe devant TFT.** Elles font exactement les mêmes scores contre les
gentilles (3000) et contre ALL-D (1990). La différence vient de RANDOM : GRIM lui prend
3507 points (elle passe en D définitif dès la première trahison), TFT seulement 2518
(elle pardonne chaque fois que RANDOM recoopère). Contre une stratégie qui ne réagit pas
aux punitions, pardonner ne rapporte rien.

**Conclusion de l'étape 2 :** comme à l'étape 1, le classement est fixé par la composition
de la population. Ajouter des stratégies gentilles (GRIM, PAVLOV) aide TFT, mais ajouter
une proie (ALL-C) aide encore plus ALL-D. Les stratégies qui gagnent sont celles qui
**punissent** (GRIM, TFT, ALL-D) ; celles qui ne punissent pas ou mal (ALL-C, PAVLOV
contre ALL-D, RANDOM) nourrissent les autres.
