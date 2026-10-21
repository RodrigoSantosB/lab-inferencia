"""Confere cada módulo de teste com o SciPy e com casos de referência.  Uso: python verificar.py"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import numpy as np
import pandas as pd
from scipy import stats

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(AQUI, "lab"), os.path.join(AQUI, "lab", "testes")]
import comum  # noqa: E402

comum.md = lambda texto: None  # silencia os relatórios durante a verificação
import exploracao  # noqa: E402
import mann_whitney  # noqa: E402
import t_pareado  # noqa: E402
import t_uma_amostra  # noqa: E402
import t_welch  # noqa: E402
import wilcoxon  # noqa: E402
import z_uma_amostra  # noqa: E402
from escolha import sugerir_teste  # noqa: E402

TOL = 1e-10
falhas = []


def confere(nome, obtido, esperado, tol=TOL):
    ok = abs(obtido - esperado) <= tol
    print(f"{'OK  ' if ok else 'FALHA'} {nome}: {obtido:.12g} (esperado {esperado:.12g})")
    if not ok:
        falhas.append(nome)


rng = np.random.default_rng(1)
x = rng.normal(10.4, 2, 25)
y = rng.normal(9.5, 3.5, 18)
x_par = x - 0.3 + np.linspace(0, 1, 25)  # segundo membro de cada par
for alt, sp in (("bilateral", "two-sided"), ("maior", "greater"), ("menor", "less")):
    confere(f"t uma amostra p ({alt})", t_uma_amostra.executar(x, 10, alternativa=alt, grafico=False)["p"],
            stats.ttest_1samp(x, 10, alternative=sp).pvalue)
    confere(f"Welch p ({alt})", t_welch.executar(x, y, alternativa=alt, grafico=False)["p"],
            stats.ttest_ind(x, y, equal_var=False, alternative=sp).pvalue)
    confere(f"pareado p ({alt})", t_pareado.executar(x, x_par, alternativa=alt, grafico=False)["p"],
            stats.ttest_rel(x, x_par, alternative=sp).pvalue)
    confere(f"Wilcoxon p ({alt})", wilcoxon.executar(x, 10, alternativa=alt)["p"],
            stats.wilcoxon(x - 10, alternative=sp).pvalue)
    confere(f"Mann-Whitney p ({alt})", mann_whitney.executar(x, y, alternativa=alt)["p"],
            stats.mannwhitneyu(x, y, alternative=sp).pvalue)

# Z: x̄ = 105, μ0 = 100, σ = 15, n = 36 → Z = 2, p = 0,0455
amostra_105 = np.full(36, 105.0)
amostra_105[:2] = [104.0, 106.0]
rz = z_uma_amostra.executar(amostra_105, 100, 15, grafico=False)
confere("Z referência (estatística)", rz["estatistica"], 2.0)
confere("Z referência (p)", rz["p"], 0.04550026389635857)

# Estudos de caso
d1 = exploracao.organizar(pd.read_csv(os.path.join(AQUI, "dados/equipe1_mlp_cnn.csv")), "acuracia", "modelo",
                          "execucao", "CNN,MLP")
r1 = t_pareado.executar(d1["pares"]["CNN"], d1["pares"]["MLP"], ("CNN", "MLP"), grafico=False)
confere("Equipe 1: t pareado", r1["estatistica"], 20.86381922259447, 1e-8)
d2 = exploracao.organizar(pd.read_csv(os.path.join(AQUI, "dados/equipe2_metodos_ensino.csv")), "nota", "metodo",
                          "", "B,A")
r2 = t_welch.executar(d2["grupos"]["B"], d2["grupos"]["A"], ("B", "A"), alternativa="maior", grafico=False)
confere("Equipe 2: Welch t", r2["estatistica"], 2.747659781299754, 1e-8)
confere("Equipe 2: Welch p unilateral", r2["p"], stats.ttest_ind(d2["grupos"]["B"], d2["grupos"]["A"],
                                                                  equal_var=False, alternative="greater").pvalue)

# Regras de escolha
casos = [((1, False, False, False), "t_uma_amostra"), ((1, False, True, False), "z_uma_amostra"),
         ((2, True, False, False), "t_pareado"), ((2, False, False, False), "t_welch"),
         ((2, False, False, True), "mann_whitney"), ((1, False, False, True), "wilcoxon")]
for args, esperado in casos:
    obtido = sugerir_teste(*args)[0]
    print(f"{'OK  ' if obtido == esperado else 'FALHA'} escolha {args} → {obtido}")
    if obtido != esperado:
        falhas.append(f"escolha {args}")

print("\nTUDO CONFERE" if not falhas else f"\nFALHAS: {falhas}")
sys.exit(1 if falhas else 0)
