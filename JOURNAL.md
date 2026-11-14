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
| Graine aléatoire | 42 | Un seul générateur `random.Random(graine)` sert à tout le tournoi. |
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

---

