"""Wilcoxon dos postos sinalizados: alternativa não paramétrica ao t de uma amostra ou ao t pareado."""
import numpy as np
from scipy import stats

import comum


def executar(x, mu0=0.0, alpha=0.05, alternativa="bilateral", unidade="", rotulo="valores"):
    """Testa se a distribuição de (x − μ0) é simétrica em torno de zero (localização/pseudomediana).

    Para dados pareados, passe as diferenças x₁ − x₂ com μ0 = 0.
    """
    alt = comum.alternativa(alternativa)
    x = comum.validar(x)
    res = stats.wilcoxon(x - mu0, alternative=alt)
    p = float(res.pvalue)
    mediana = float(np.median(x))
    ic = comum.ic_bootstrap(np.median, x, alpha=alpha)
    h0, h1 = comum.hipoteses(r"\tilde{\mu}", mu0, alt)
    return comum.relatorio({
        "nome": f"Wilcoxon dos postos sinalizados ({rotulo}) — alternativa não paramétrica", "alt": alt,
        "alpha": alpha, "h0": h0, "h1": h1,
        "formula": r"W = \sum_{i:\, x_i - \mu_0 > 0} \text{posto}(|x_i - \mu_0|)",
        "substituicao": rf"W = {comum.n(float(res.statistic))}, \quad n = {x.size}",
        "referencia": "distribuição exata/aproximada da soma dos postos (calculada pelo SciPy)",
        "p": p, "nome_estimativa": "mediana", "estimativa": mediana, "ic": ic,
        "ic_metodo": "bootstrap percentil da mediana", "unidade": unidade,
        "aviso": ("Este teste compara a localização (pseudomediana), não a média: a conclusão deve falar de "
                  "mediana/tendência central, e supõe distribuição aproximadamente simétrica."),
    })


def executar_com(dados, cfg):
    if dados["pares"] is not None:
        g1, g2 = list(dados["grupos"])[:2]
        return executar(dados["pares"]["diferenca"].to_numpy(), 0.0, cfg["alpha"], cfg["alternativa"],
                        cfg.get("unidade", ""), rotulo=f"diferenças {g1} − {g2}")
    x = next(iter(dados["grupos"].values()))
    return executar(x, cfg["mu0"], cfg["alpha"], cfg["alternativa"], cfg.get("unidade", ""))
