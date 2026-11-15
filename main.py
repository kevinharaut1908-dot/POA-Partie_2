"""Point d'entrée : lance un tournoi et affiche le classement.

Etape 1 :
    python3 main.py --seed 67                
    python3 main.py --seed 67 --contre-soi   
Etape 2 :
    python3 main.py --seed 67 --etape 2
Etape 3 (bruit) :
    python3 main.py --seed 67 --etape 2 --bruit 0.05
Etape 3 (sélection) :
    python3 main.py --seed 67 --etape 2 --generations 100 --graphique captures/selection.svg
Une partie entre deux stratégies :
    python3 main.py --duel TIT-FOR-TAT JOSS
"""

import argparse
import random

from moteur import tournoi, classement, selection, jouer_partie
from graphique import ecrire_svg
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


def afficher_selection(strategies, historique):
    noms = list(strategies)
    dernieres = len(historique) - 1
    a_afficher = [g for g in range(dernieres + 1)
                  if g <= 5 or g % 10 == 0 or g == dernieres]
    largeur = 9
    print("Évolution de la population (part de chaque stratégie, en %)")
    print("Gén." + "".join(f"{nom[:largeur - 1]:>{largeur}}" for nom in noms))
    for g in a_afficher:
        print(f"{g:>4}" + "".join(f"{100 * historique[g][nom]:>{largeur}.1f}" for nom in noms))


def lancer_duel(nom1, nom2, args):
    # Fait jouer deux stratégies l'une contre l'autre et affiche les scores et les coups.
    rng = random.Random(args.seed)
    s1, s2 = POPULATION_ELARGIE[nom1], POPULATION_ELARGIE[nom2]
    texte_bruit = f", bruit {args.bruit:.0%}" if args.bruit > 0 else ""
    mot_partie = "partie" if args.parties == 1 else "parties"
    print(f"Duel {nom1} contre {nom2} : {args.parties} {mot_partie} de {args.tours} tours"
          f"{texte_bruit}, graine {args.seed}\n")

    total1, total2 = 0, 0
    for partie in range(1, args.parties + 1):
        score1, score2, coups1, coups2 = jouer_partie(s1, s2, args.tours, rng, args.bruit, avec_coups=True)
        total1 += score1
        total2 += score2
        print(f"Partie {partie} : {nom1} {score1} - {score2} {nom2}")
        if partie == 1:
            premiere = (coups1, coups2)
    print(f"Total    : {nom1} {total1} - {total2} {nom2}\n")

    # Coups de la première partie, 50 tours par ligne (C = coopère, D = trahit)
    largeur = max(len(nom1), len(nom2))
    print("Coups de la partie 1 (C = coopère, D = trahit)")
    for debut in range(0, args.tours, 50):
        fin = min(debut + 50, args.tours)
        print(f"Tours {debut + 1:>3} à {fin:>3}")
        print(f"  {nom1:<{largeur}}  {''.join(premiere[0][debut:fin])}")
        print(f"  {nom2:<{largeur}}  {''.join(premiere[1][debut:fin])}")


def main():
    parser = argparse.ArgumentParser(description="Tournoi du dilemme du prisonnier itéré")
    parser.add_argument("--etape", type=int, choices=[1, 2], default=1,
                        help="1 : stratégies du cours ; 2 : population élargie (défaut : 1)")
    parser.add_argument("--seed", type=int, default=67, help="graine aléatoire (défaut : 67)")
    parser.add_argument("--parties", type=int, default=5, help="parties par duel (défaut : 5)")
    parser.add_argument("--tours", type=int, default=200, help="tours par partie (défaut : 200)")
    parser.add_argument("--bruit", type=float, default=0.0,
                        help="probabilité qu'un coup soit inversé par erreur")
    parser.add_argument("--generations", type=int, default=0,
                        help="nombre de générations de sélection après le tournoi (défaut : 0, pas de sélection)")
    parser.add_argument("--graphique", metavar="FICHIER.svg",
                        help="avec --generations : enregistre la courbe d'évolution dans ce fichier SVG")
    parser.add_argument("--contre-soi", action="store_true",
                        help="chaque stratégie affronte aussi son double")
    parser.add_argument("--duel", nargs=2, metavar=("STRAT1", "STRAT2"),
                        help="fait jouer une seule paire de stratégies, ex. --duel TIT-FOR-TAT JOSS. "
                             "Noms possibles : " + ", ".join(POPULATION_ELARGIE))
    args = parser.parse_args()

    if args.duel:
        noms = [nom.upper() for nom in args.duel]
        for nom in noms:
            if nom not in POPULATION_ELARGIE:
                parser.error(f"stratégie inconnue : {nom}. Noms possibles : {', '.join(POPULATION_ELARGIE)}")
        lancer_duel(noms[0], noms[1], args)
        return

    strategies = POPULATIONS[args.etape]
    rng = random.Random(args.seed)

    format_tournoi = "avec matchs contre soi-même" if args.contre_soi else "sans match contre soi-même"
    texte_bruit = f", bruit {args.bruit:.0%}" if args.bruit > 0 else ""
    print(f"Étape {args.etape} — Tournoi : {len(strategies)} stratégies, {args.parties} parties de "
          f"{args.tours} tours par duel, {format_tournoi}{texte_bruit}, graine {args.seed}\n")

    scores, duels = tournoi(strategies, args.parties, args.tours, rng, args.contre_soi, args.bruit)

    afficher_classement(scores)
    print()
    afficher_duels(strategies, duels)

    if args.generations > 0:
        print()
        historique = selection(strategies, duels, args.generations, args.contre_soi)
        afficher_selection(strategies, historique)
        if args.graphique:
            ecrire_svg(historique, args.graphique,
                       f"Sélection sur {args.generations} générations (graine {args.seed}{texte_bruit})")
            print(f"\nGraphique enregistré dans {args.graphique}")


if __name__ == "__main__":
    main()
