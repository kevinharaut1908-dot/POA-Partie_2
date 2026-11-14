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

> `main.py` arrive à l'étape suivante. Les commandes seront :

```
python3 main.py --seed 42        # Étape 1 : tournoi de base (5 stratégies du cours)
```

La graine (`--seed`) fixe tout le hasard du tournoi : la même graine redonne
exactement le même classement.

## Organisation du code

| Fichier | Rôle |
|---|---|
| `moteur.py` | Matrice des gains, `jouer_partie` (une partie entre deux stratégies), `tournoi` (tous contre tous) et `classement`. |
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


