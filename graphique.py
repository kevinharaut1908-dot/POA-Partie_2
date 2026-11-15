
COULEURS = ["#d62728", "#7f7f7f", "#1f77b4", "#ff7f0e",
            "#9467bd", "#2ca02c", "#17becf", "#e377c2"]


def ecrire_svg(historique, chemin, titre="Évolution de la population"):
    noms = list(historique[0])
    n_gen = len(historique) - 1

    largeur, hauteur = 900, 460
    marge_g, marge_d, marge_h, marge_b = 60, 200, 40, 50
    zone_l = largeur - marge_g - marge_d
    zone_h = hauteur - marge_h - marge_b

    def x(gen):
        return marge_g + zone_l * gen / max(n_gen, 1)

    def y(part):
        return marge_h + zone_h * (1 - part)

    lignes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largeur}" height="{hauteur}" '
        f'viewBox="0 0 {largeur} {hauteur}" '
        f'font-family="sans-serif" font-size="13">',
        f'<rect width="{largeur}" height="{hauteur}" fill="white"/>',
        f'<text x="{largeur / 2}" y="24" text-anchor="middle" font-size="16">{titre}</text>',
    ]

    for pourcent in range(0, 101, 10):
        yy = y(pourcent / 100)
        lignes.append(f'<line x1="{marge_g}" y1="{yy}" x2="{marge_g + zone_l}" y2="{yy}" stroke="#e5e5e5"/>')
        lignes.append(f'<text x="{marge_g - 8}" y="{yy + 4}" text-anchor="end">{pourcent} %</text>')

    pas = 10 if n_gen >= 20 else 1
    for gen in range(0, n_gen + 1, pas):
        lignes.append(f'<text x="{x(gen)}" y="{marge_h + zone_h + 18}" text-anchor="middle">{gen}</text>')
    lignes.append(f'<text x="{marge_g + zone_l / 2}" y="{hauteur - 10}" text-anchor="middle">Génération</text>')

    lignes.append(f'<line x1="{marge_g}" y1="{marge_h}" x2="{marge_g}" y2="{marge_h + zone_h}" stroke="black"/>')
    lignes.append(f'<line x1="{marge_g}" y1="{marge_h + zone_h}" x2="{marge_g + zone_l}" '
                  f'y2="{marge_h + zone_h}" stroke="black"/>')

    for i, nom in enumerate(noms):
        couleur = COULEURS[i % len(COULEURS)]
        points = " ".join(f"{x(g):.1f},{y(pop[nom]):.1f}" for g, pop in enumerate(historique))
        lignes.append(f'<polyline points="{points}" fill="none" stroke="{couleur}" stroke-width="2.5"/>')
        y_legende = marge_h + 10 + i * 24
        x_legende = marge_g + zone_l + 20
        lignes.append(f'<line x1="{x_legende}" y1="{y_legende}" x2="{x_legende + 24}" y2="{y_legende}" '
                      f'stroke="{couleur}" stroke-width="3"/>')
        lignes.append(f'<text x="{x_legende + 32}" y="{y_legende + 4}">{nom}</text>')

    lignes.append("</svg>")

    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes))
