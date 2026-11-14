"""Moteur du dilemme du prisonnier itéré.

Une stratégie est une simple fonction :
    strategie(mes_coups, coups_adverses, rng) -> "C" ou "D"
- mes_coups / coups_adverses : listes des coups déjà joués (ex. ["C", "D", "C"])
- rng : générateur aléatoire (random.Random) fourni par le moteur,
        pour que tout le hasard dépende d'une seule graine.
"""

import itertools
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


def tournoi(strategies, n_parties=5, n_tours=200, rng=None):
    """Tournoi tous contre tous au format d'Axelrod.

    strategies : dictionnaire {nom: fonction de stratégie}
    Chaque paire de stratégies distinctes joue n_parties parties de n_tours.
    Une stratégie ne joue pas contre elle-même (comme le mini-tournoi du cours, CM4 p.68).

    Renvoie (scores, duels) :
    - scores : {nom: score total sur tout le tournoi}
    - duels  : {(nom1, nom2): score total de nom1 contre nom2}
    """
    if rng is None:
        rng = random.Random()

    scores = {nom: 0 for nom in strategies}
    duels = {}

    # itertools.combinations -> donne toutes les paires possibles, une seule fois chacune sans jouer contre elle meme (A contre A)
    for (nom1, s1), (nom2, s2) in itertools.combinations(strategies.items(), 2):
        total1, total2 = 0, 0
        for _ in range(n_parties):
            score1, score2 = jouer_partie(s1, s2, n_tours, rng)
            total1 += score1
            total2 += score2

        duels[(nom1, nom2)] = total1
        duels[(nom2, nom1)] = total2
        scores[nom1] += total1
        scores[nom2] += total2

    return scores, duels


def classement(scores):
    """Renvoie la liste [(nom, score), ...] triée du meilleur au moins bon."""
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)
