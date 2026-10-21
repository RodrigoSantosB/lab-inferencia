"""Teste Z para uma média (σ populacional conhecido por fonte externa)."""
import math

from scipy import stats

import comum


def executar(x, mu0, sigma, alpha=0.05, alternativa="bilateral", unidade="", grafico=True):
    """Z = (x̄ − μ0) / (σ/√n). σ deve vir de fonte externa (histórico, especificação), não da amostra."""
    alt = comum.alternativa(alternativa)
    if sigma is None or sigma <= 0:
        raise ValueError("O teste Z exige o σ populacional (número positivo) informado na configuração.")
    x = comum.validar(x, minimo=1)
    k = x.size
    media = x.mean()
    ep = sigma / math.sqrt(k)
    z = (media - mu0) / ep
    dist = stats.norm()
    p = comum.p_valor(dist, z, alt)
    zq = dist.isf(alpha / 2)
    h0, h1 = comum.hipoteses(r"\mu", mu0, alt)
    r = comum.relatorio({
        "nome": "Teste Z para uma média (σ conhecido)", "alt": alt, "alpha": alpha, "h0": h0, "h1": h1,
        "formula": r"Z = \frac{\bar{x} - \mu_0}{\sigma/\sqrt{n}}",
        "substituicao": (rf"Z = \frac{{{comum.n(media)} - {comum.n(mu0)}}}{{{comum.n(sigma)}/\sqrt{{{k}}}}}"
                         rf" = \frac{{{comum.n(media - mu0)}}}{{{comum.n(ep)}}} = {comum.n(z)}"),
        "referencia": "normal padrão N(0, 1)", "simbolo": "Z",
        "crit": comum.criticos(dist, alpha, alt), "p": p, "estatistica": z,
        "nome_estimativa": "média x̄", "estimativa": media, "ic": (media - zq * ep, media + zq * ep),
        "ic_metodo": "Z com σ conhecido", "unidade": unidade,
        "efeito": {"diferença x̄ − μ₀": media - mu0, "d = (x̄ − μ₀)/σ": (media - mu0) / sigma},
        "aviso": "Use este teste só se σ vier de fonte externa confiável; calcular s na amostra não torna σ conhecido.",
    })
    if grafico:
        comum.grafico_h0(dist, z, alt, alpha, p, "Z", "Teste Z para uma média — N(0, 1)")
    return r


def executar_com(dados, cfg):
    x = next(iter(dados["grupos"].values()))
    return executar(x, cfg["mu0"], cfg["sigma"], cfg["alpha"], cfg["alternativa"], cfg.get("unidade", ""))
