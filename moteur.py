"""Moteur du dilemme du prisonnier itéré.

Une stratégie est une simple fonction :
    strategie(mes_coups, coups_adverses, rng) -> "C" ou "D"
- mes_coups / coups_adverses : listes des coups déjà joués (ex. ["C", "D", "C"])
- rng : générateur aléatoire (random.Random) fourni par le moteur,
        pour que tout le hasard dépende d'une seule graine.
"""

import random

# Matrice des gains du cours : (mon coup, coup adverse) -> (mon gain, gain adverse)
GAINS = {
    ("C", "C"): (3, 3),
    ("C", "D"): (0, 5),
    ("D", "C"): (5, 0),
    ("D", "D"): (2, 2),
}


def jouer_partie(strat1, strat2, n_tours=200, rng=None):
    """Fait jouer une partie de n_tours entre deux stratégies.

    Renvoie (score1, score2).
    """
    if rng is None:
        rng = random.Random()

    coups1, coups2 = [], []
    score1, score2 = 0, 0

    for _ in range(n_tours):
        # Les deux joueurs choisissent "en même temps" : chacun ne voit que
        # l'historique des tours précédents, jamais le coup actuel de l'autre.
        c1 = strat1(coups1, coups2, rng)
        c2 = strat2(coups2, coups1, rng)

        g1, g2 = GAINS[(c1, c2)]
        score1 += g1
        score2 += g2

        coups1.append(c1)
        coups2.append(c2)

    return score1, score2
