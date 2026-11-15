import itertools
import random

# Matrice des gains du cours : (mon coup, coup adverse) -> (mon gain, gain adverse)
GAINS = {
    ("C", "C"): (3, 3),
    ("C", "D"): (0, 5),
    ("D", "C"): (5, 0),
    ("D", "D"): (2, 2),
}


def inverser(coup):
    return "D" if coup == "C" else "C"


def jouer_partie(strat1, strat2, n_tours=200, rng=None, bruit=0.0, avec_coups=False):
    # avec_coups=True : renvoie aussi les coups joués (pour afficher un duel)

    if rng is None:
        rng = random.Random()

    coups1, coups2 = [], []
    score1, score2 = 0, 0

    for _ in range(n_tours):
        c1 = strat1(coups1, coups2, rng)
        c2 = strat2(coups2, coups1, rng)

        # Bruit : chaque coup peut être inversé.
        if bruit > 0:
            if rng.random() < bruit:
                c1 = inverser(c1)
            if rng.random() < bruit:
                c2 = inverser(c2)

        g1, g2 = GAINS[(c1, c2)]
        score1 += g1
        score2 += g2

        coups1.append(c1)
        coups2.append(c2)

    if avec_coups:
        return score1, score2, coups1, coups2
    return score1, score2


def tournoi(strategies, n_parties=5, n_tours=200, rng=None, contre_soi=False, bruit=0.0):

    if rng is None:
        rng = random.Random()

    scores = {nom: 0 for nom in strategies}
    duels = {}

    # itertools.combinations -> donne toutes les paires possibles, une seule fois chacune sans jouer contre elle meme (A contre A)
    # itertools.combinations_with_replacement -> pareil, mais ajoute les paires (A, A)
    if contre_soi:
        paires = itertools.combinations_with_replacement(strategies.items(), 2)
    else:
        paires = itertools.combinations(strategies.items(), 2)

    for (nom1, s1), (nom2, s2) in paires:
        total1, total2 = 0, 0
        for _ in range(n_parties):
            score1, score2 = jouer_partie(s1, s2, n_tours, rng, bruit)
            total1 += score1
            total2 += score2

        if nom1 == nom2:
            # Match contre son double : on ne compte qu'une seule copie
            duels[(nom1, nom1)] = total1
            scores[nom1] += total1
            continue

        duels[(nom1, nom2)] = total1
        duels[(nom2, nom1)] = total2
        scores[nom1] += total1
        scores[nom2] += total2

    return scores, duels


def classement(scores):
    # Renvoie la liste [(nom, score), ...] triée du meilleur au moins bon.
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def selection(strategies, duels, n_generations=100, contre_soi=False):

    noms = list(strategies)
    parts = {nom: 1 / len(noms) for nom in noms}  # au départ, toutes à égalité
    historique = [dict(parts)]

    for _ in range(n_generations):
        scores = {}
        for nom in noms:
            adversaires = [autre for autre in noms if autre != nom or contre_soi]
            poids_total = sum(parts[autre] for autre in adversaires)
            if poids_total == 0:
                scores[nom] = 0
                continue
            points = sum(parts[autre] * duels[(nom, autre)] for autre in adversaires)
            scores[nom] = points / poids_total

        moyenne = sum(parts[nom] * scores[nom] for nom in noms)
        parts = {nom: parts[nom] * scores[nom] / moyenne for nom in noms}
        historique.append(dict(parts))

    return historique
