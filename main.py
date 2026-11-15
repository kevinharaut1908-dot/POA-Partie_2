"""Point d'entrée : lance un tournoi et affiche le classement.

Etape 1 :
    python3 main.py --seed 67                
    python3 main.py --seed 67 --contre-soi   
Etape 2 :
    python3 main.py --seed 67 --etape 2     
"""

import argparse
import random

from moteur import tournoi, classement
from strategies import all_d, random_strat, tit_for_tat, tester, joss, grim, pavlov, all_c

# Les 5 stratégies 
POPULATION_COURS = {
    "ALL-D": all_d,
    "RANDOM": random_strat,
    "TIT-FOR-TAT": tit_for_tat,
    "TESTER": tester,
    "JOSS": joss,
}

# Étape 2 : population du cours + stratégies absentes du cours
POPULATION_ELARGIE = {
    **POPULATION_COURS,
    "GRIM": grim,
    "PAVLOV": pavlov,
    "ALL-C": all_c,
}

POPULATIONS = {1: POPULATION_COURS, 2: POPULATION_ELARGIE}


def afficher_classement(scores):
    print("Classement")
    print("-" * 30)
    for rang, (nom, score) in enumerate(classement(scores), start=1):
        print(f"{rang:>2}. {nom:<14} {score:>7}")


def afficher_duels(strategies, duels):
    """Tableau croisé : ligne = stratégie, colonne = adversaire,
    case = points gagnés par la ligne contre la colonne."""
    noms = list(strategies)
    largeur = 13
    print("Points de la ligne contre la colonne")
    print(" " * largeur + "".join(f"{nom[:largeur - 1]:>{largeur}}" for nom in noms))
    for nom1 in noms:
        cases = []
        for nom2 in noms:
            case = str(duels[(nom1, nom2)]) if (nom1, nom2) in duels else "-"
            cases.append(f"{case:>{largeur}}")
        print(f"{nom1:<{largeur}}" + "".join(cases))


def main():
    parser = argparse.ArgumentParser(description="Tournoi du dilemme du prisonnier itéré")
    parser.add_argument("--etape", type=int, choices=[1, 2], default=1,
                        help="1 : stratégies du cours ; 2 : population élargie (défaut : 1)")
    parser.add_argument("--seed", type=int, default=67, help="graine aléatoire (défaut : 67)")
    parser.add_argument("--parties", type=int, default=5, help="parties par duel (défaut : 5)")
    parser.add_argument("--tours", type=int, default=200, help="tours par partie (défaut : 200)")
    parser.add_argument("--contre-soi", action="store_true",
                        help="chaque stratégie affronte aussi son double (comme Axelrod 1980)")
    args = parser.parse_args()

    strategies = POPULATIONS[args.etape]
    rng = random.Random(args.seed)

    format_tournoi = "avec matchs contre soi-même" if args.contre_soi else "sans match contre soi-même"
    print(f"Étape {args.etape} — Tournoi : {len(strategies)} stratégies, {args.parties} parties de "
          f"{args.tours} tours par duel, {format_tournoi}, graine {args.seed}\n")

    scores, duels = tournoi(strategies, args.parties, args.tours, rng, args.contre_soi)

    afficher_classement(scores)
    print()
    afficher_duels(strategies, duels)


if __name__ == "__main__":
    main()
