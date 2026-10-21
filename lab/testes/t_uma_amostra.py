"""Teste t de Student para uma média (σ populacional desconhecido)."""
import math

from scipy import stats

import comum


def executar(x, mu0, alpha=0.05, alternativa="bilateral", unidade="", grafico=True):
    """t = (x̄ − μ0) / (s/√n), com n − 1 graus de liberdade."""
    alt = comum.alternativa(alternativa)
    x = comum.validar(x)
    k = x.size
    media, s = x.mean(), x.std(ddof=1)
    ep = s / math.sqrt(k)
    t = (media - mu0) / ep
    gl = k - 1
    dist = stats.t(gl)
    p = comum.p_valor(dist, t, alt)
    tq = dist.isf(alpha / 2)
    h0, h1 = comum.hipoteses(r"\mu", mu0, alt)
    r = comum.relatorio({
        "nome": "Teste t para uma média", "alt": alt, "alpha": alpha, "h0": h0, "h1": h1,
        "formula": r"t = \frac{\bar{x} - \mu_0}{s/\sqrt{n}}, \qquad gl = n - 1",
        "substituicao": (rf"t = \frac{{{comum.n(media)} - {comum.n(mu0)}}}{{{comum.n(s)}/\sqrt{{{k}}}}}"
                         rf" = \frac{{{comum.n(media - mu0)}}}{{{comum.n(ep)}}} = {comum.n(t)}, \qquad gl = {gl}"),
        "referencia": f"t de Student com {gl} graus de liberdade", "simbolo": "t",
        "crit": comum.criticos(dist, alpha, alt), "p": p, "estatistica": t, "gl": gl,
        "nome_estimativa": "média x̄", "estimativa": media, "ic": (media - tq * ep, media + tq * ep),
        "ic_metodo": f"t com {gl} gl", "unidade": unidade,
        "efeito": {"diferença x̄ − μ₀": media - mu0, "d de Cohen (x̄ − μ₀)/s": (media - mu0) / s},
    })
    ref = stats.ttest_1samp(x, mu0, alternative=alt)
    r["confere_scipy"] = abs(ref.pvalue - p) < 1e-10 and abs(ref.statistic - t) < 1e-10
    if grafico:
        comum.grafico_h0(dist, t, alt, alpha, p, "t", f"Teste t para uma média — t({gl})")
    return r


def executar_com(dados, cfg):
    """Usa o primeiro (único) grupo dos dados organizados."""
    x = next(iter(dados["grupos"].values()))
    return executar(x, cfg["mu0"], cfg["alpha"], cfg["alternativa"], cfg.get("unidade", ""))
