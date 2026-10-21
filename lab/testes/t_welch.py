"""Teste t de Welch para duas médias de grupos independentes."""
import math

from scipy import stats

import comum


def executar(x1, x2, nomes=("1", "2"), alpha=0.05, alternativa="bilateral", unidade="", grafico=True):
    """t = (x̄₁ − x̄₂) / √(s₁²/n₁ + s₂²/n₂), com gl de Welch-Satterthwaite. Não supõe variâncias iguais."""
    alt = comum.alternativa(alternativa)
    a, b = comum.validar(x1, nomes[0]), comum.validar(x2, nomes[1])
    n1, n2 = a.size, b.size
    m1, m2 = a.mean(), b.mean()
    v1, v2 = a.var(ddof=1), b.var(ddof=1)
    ep = math.sqrt(v1 / n1 + v2 / n2)
    dif = m1 - m2
    t = dif / ep
    gl = (v1 / n1 + v2 / n2) ** 2 / ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))
    dist = stats.t(gl)
    p = comum.p_valor(dist, t, alt)
    tq = dist.isf(alpha / 2)
    sp = math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    d = dif / sp
    g = d * (1 - 3 / (4 * (n1 + n2) - 9))
    par = rf"\mu_{{{nomes[0]}}} - \mu_{{{nomes[1]}}}"
    h0, h1 = comum.hipoteses(par, 0, alt)
    r = comum.relatorio({
        "nome": f"Teste t de Welch ({nomes[0]} × {nomes[1]}, grupos independentes)", "alt": alt, "alpha": alpha,
        "h0": h0, "h1": h1,
        "formula": (r"t = \frac{\bar{x}_1 - \bar{x}_2}{\sqrt{s_1^2/n_1 + s_2^2/n_2}}, \qquad "
                    r"gl = \frac{(s_1^2/n_1 + s_2^2/n_2)^2}{\frac{(s_1^2/n_1)^2}{n_1-1} + \frac{(s_2^2/n_2)^2}{n_2-1}}"),
        "substituicao": (rf"t = \frac{{{comum.n(m1)} - {comum.n(m2)}}}{{\sqrt{{{comum.n(v1)}/{n1} + {comum.n(v2)}/{n2}}}}}"
                         rf" = \frac{{{comum.n(dif)}}}{{{comum.n(ep)}}} = {comum.n(t)}, \qquad gl = {comum.n(gl, 3)}"),
        "referencia": f"t de Student com {gl:.2f} graus de liberdade (Welch)", "simbolo": "t",
        "crit": comum.criticos(dist, alpha, alt), "p": p, "estatistica": t, "gl": gl,
        "nome_estimativa": f"diferença x̄({nomes[0]}) − x̄({nomes[1]})", "estimativa": dif,
        "ic": (dif - tq * ep, dif + tq * ep), "ic_metodo": f"Welch, {gl:.2f} gl", "unidade": unidade,
        "efeito": {"diferença de médias": dif, "g de Hedges": g},
    })
    ref = stats.ttest_ind(a, b, equal_var=False, alternative=alt)
    r["confere_scipy"] = abs(ref.pvalue - p) < 1e-10 and abs(ref.statistic - t) < 1e-10
    if grafico:
        comum.grafico_h0(dist, t, alt, alpha, p, "t", f"Teste t de Welch — t({gl:.1f})")
    return r


def executar_com(dados, cfg):
    (g1, x1), (g2, x2) = list(dados["grupos"].items())[:2]
    return executar(x1, x2, (g1, g2), cfg["alpha"], cfg["alternativa"], cfg.get("unidade", ""))
