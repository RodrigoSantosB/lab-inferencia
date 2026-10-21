"""Mann-Whitney: alternativa não paramétrica ao t de Welch para dois grupos independentes."""
import numpy as np
from scipy import stats

import comum


def executar(x1, x2, nomes=("1", "2"), alpha=0.05, alternativa="bilateral", unidade=""):
    """Testa se P(X₁ > X₂) = 1/2, isto é, se um grupo tende a ter valores maiores que o outro."""
    alt = comum.alternativa(alternativa)
    a, b = comum.validar(x1, nomes[0]), comum.validar(x2, nomes[1])
    res = stats.mannwhitneyu(a, b, alternative=alt)
    p = float(res.pvalue)
    prob = float(res.statistic) / (a.size * b.size)
    dif_med = float(np.median(a) - np.median(b))
    ic = comum.ic_bootstrap(lambda u, v: np.median(u) - np.median(v), a, b, alpha=alpha)
    h0, h1 = comum.hipoteses(rf"P(X_{{{nomes[0]}}} > X_{{{nomes[1]}}})", 0.5, alt)
    return comum.relatorio({
        "nome": f"Mann-Whitney ({nomes[0]} × {nomes[1]}) — alternativa não paramétrica", "alt": alt,
        "alpha": alpha, "h0": h0, "h1": h1,
        "formula": r"U = \#\{(i, j): x_{1i} > x_{2j}\} + \tfrac{1}{2}\#\{\text{empates}\}",
        "substituicao": rf"U = {comum.n(float(res.statistic))}, \quad n_1 = {a.size}, \; n_2 = {b.size}",
        "referencia": "distribuição exata/aproximada de U (calculada pelo SciPy)",
        "p": p, "nome_estimativa": "diferença de medianas", "estimativa": dif_med, "ic": ic,
        "ic_metodo": "bootstrap percentil", "unidade": unidade,
        "efeito": {f"P(X_{nomes[0]} > X_{nomes[1]}) estimada": prob},
        "aviso": "Este teste não compara médias: a conclusão deve falar de qual grupo tende a ter valores maiores.",
    })


def executar_com(dados, cfg):
    (g1, x1), (g2, x2) = list(dados["grupos"].items())[:2]
    return executar(x1, x2, (g1, g2), cfg["alpha"], cfg["alternativa"], cfg.get("unidade", ""))
