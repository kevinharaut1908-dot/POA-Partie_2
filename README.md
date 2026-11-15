# Tournoi du dilemme du prisonnier itéré — HAI716I Projet 2 (partie 1)

Kevin HARAUT — Master 1 Informatique, Université de Montpellier.

Moteur de tournoi du dilemme du prisonnier itéré, écrit sans code fourni, sur le
modèle du tournoi d'Axelrod.

- **Langage :** Python 3.10 ou plus
- **Dépendances :** aucune (bibliothèque standard uniquement)

## Le jeu

À chaque tour, les deux joueurs choisissent C (coopérer) ou D (trahir) en même temps.
Chacun connaît ensuite tous les coups passés de son adversaire.

|            | j joue C | j joue D |
|------------|----------|----------|
| **i joue C** | 3, 3   | 0, 5     |
| **i joue D** | 5, 0   | 2, 2     |

Format d'Axelrod : chaque stratégie affronte chaque autre sur **5 parties de 200 tours** ;
le meilleur score total gagne. Une stratégie ne joue pas contre elle-même
(comme le mini-tournoi du cours, CM4 p.68).

## Lancer les tournois

Depuis la racine du dépôt :

```
python3 main.py --seed 67                # Étape 1 : tournoi de base, format du cours
python3 main.py --seed 67 --contre-soi   # Étape 1 : idem, chaque stratégie affronte aussi son double (Axelrod 1980)
python3 main.py --seed 67 --etape 2       # Étape 2 : population élargie (8 stratégies)
python3 main.py --seed 67 --etape 2 --bruit 0.05   # Étape 3 : population élargie avec 5 % de bruit
python3 main.py --seed 67 --etape 2 --generations 100 --graphique captures/selection.svg   # Étape 3 : sélection sur 100 générations
```

Options :

| Option | Défaut | Rôle |
|---|---|---|
| `--etape` | 1 | population : 1 = stratégies du cours, 2 = population élargie |
| `--seed` | 67 | graine aléatoire |
| `--parties` | 5 | parties par duel |
| `--tours` | 200 | tours par partie |
| `--bruit` | 0 | probabilité qu'un coup soit inversé par erreur (ex. 0.05 = 5 %) |
| `--generations` | 0 | nombre de générations de sélection après le tournoi (0 = pas de sélection) |
| `--graphique` | aucun | avec `--generations`, enregistre la courbe d'évolution dans un fichier SVG |
| `--contre-soi` | désactivé | ajoute le match de chaque stratégie contre son double |

La graine (`--seed`) fixe tout le hasard du tournoi : la même graine redonne
exactement le même classement.

## Organisation du code

| Fichier | Rôle |
|---|---|
| `main.py` | Point d'entrée : lit les options, fixe la graine, lance le tournoi, affiche le classement et le tableau des duels. |
| `graphique.py` | Dessine la courbe d'évolution de la sélection dans un fichier SVG (sans bibliothèque). |
| `moteur.py` | Matrice des gains, `jouer_partie` (une partie entre deux stratégies), `tournoi` (tous contre tous), `classement`, le bruit et `selection` (évolution de la population). |
| `strategies.py` | Les stratégies. Chacune est une fonction `strategie(mes_coups, coups_adverses, rng) -> "C" ou "D"`. |

Une stratégie ne garde aucun état caché : elle déduit tout de l'historique des coups.
Le hasard passe par le générateur `rng` fourni par le moteur, ce qui rend les
tournois reproductibles avec une seule graine.

## Stratégies

### Population de base 

| Stratégie | Règle |
|---|---|
| ALL-D | Trahit toujours. |
| RANDOM | C ou D au hasard, une chance sur deux. |
| TIT-FOR-TAT | C au premier tour, puis rejoue le coup de l'adversaire au tour précédent. |
| TESTER | D au premier tour. Si l'adversaire riposte, joue TIT-FOR-TAT ; sinon répète C, C, D. |
| JOSS | TIT-FOR-TAT, mais remplace C par D avec une probabilité de 10 %. |

### Nouvelles stratégies (étape 2)

| Stratégie | Règle |
|---|---|
| GRIM | Coopère tant que l'adversaire n'a jamais trahi ; après sa première trahison, trahit jusqu'à la fin. |
| PAVLOV | Coopère au premier tour ; garde son coup s'il a rapporté 3 ou 5 points, en change sinon. |
| ALL-C | Coopère toujours. |


