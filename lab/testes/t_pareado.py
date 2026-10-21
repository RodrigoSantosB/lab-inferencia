"""Teste t pareado: teste t de uma amostra aplicado às diferenças dentro de cada par."""
import math

from scipy import stats

import comum


def executar(x1, x2, nomes=("1", "2"), alpha=0.05, alternativa="bilateral", unidade="", grafico=True):
    """d = x₁ − x₂ (par a par);  t = d̄ / (s_d/√n), com n − 1 graus de liberdade (n = número de pares)."""
    alt = comum.alternativa(alternativa)
    a = comum.validar(x1, nomes[0])
    b = comum.validar(x2, nomes[1])
    if a.size != b.size:
        raise ValueError("Os dois grupos precisam ter o mesmo número de pares alinhados.")
    d = comum.validar(a - b, "diferenças")
    k = d.size
    dbar, sd = d.mean(), d.std(ddof=1)
    ep = sd / math.sqrt(k)
    t = dbar / ep
    gl = k - 1
    dist = stats.t(gl)
    p = comum.p_valor(dist, t, alt)
    tq = dist.isf(alpha / 2)
    r_par = float(stats.pearsonr(a, b)[0])
    h0, h1 = comum.hipoteses(r"\mu_D", 0, alt)
    r = comum.relatorio({
        "nome": f"Teste t pareado (D = {nomes[0]} − {nomes[1]})", "alt": alt, "alpha": alpha, "h0": h0, "h1": h1,
        "formula": r"t = \frac{\bar{d}}{s_d/\sqrt{n}}, \qquad d_i = x_{1i} - x_{2i}, \qquad gl = n - 1",
        "substituicao": (rf"t = \frac{{{comum.n(dbar)}}}{{{comum.n(sd)}/\sqrt{{{k}}}}} = "
                         rf"\frac{{{comum.n(dbar)}}}{{{comum.n(ep)}}} = {comum.n(t)}, \qquad gl = {gl}"),
        "referencia": f"t de Student com {gl} graus de liberdade", "simbolo": "t",
        "crit": comum.criticos(dist, alpha, alt), "p": p, "estatistica": t, "gl": gl,
        "nome_estimativa": "média das diferenças d̄", "estimativa": dbar, "ic": (dbar - tq * ep, dbar + tq * ep),
        "ic_metodo": f"t com {gl} gl", "unidade": unidade,
        "efeito": {"média das diferenças": dbar, "d_z = d̄/s_d": dbar / sd, "correlação entre os pares r": r_par},
        "aviso": ("O pareamento vem do desenho do estudo (mesmo sujeito, mesma execução...), não do fato de os "
                  "grupos terem o mesmo tamanho." + (" Aqui r ≤ 0: o pareamento não reduziu a variabilidade."
                                                    if r_par <= 0 else "")),
    })
    ref = stats.ttest_rel(a, b, alternative=alt)
    r["confere_scipy"] = abs(ref.pvalue - p) < 1e-10 and abs(ref.statistic - t) < 1e-9
    if grafico:
        comum.grafico_h0(dist, t, alt, alpha, p, "t", f"Teste t pareado — t({gl})")
    return r


def executar_com(dados, cfg):
    if dados["pares"] is None:
        raise ValueError("O teste pareado exige a coluna de identificação dos pares na etapa de carregamento.")
    g1, g2 = list(dados["grupos"])[:2]
    return executar(dados["pares"][g1].to_numpy(), dados["pares"][g2].to_numpy(), (g1, g2),
                    cfg["alpha"], cfg["alternativa"], cfg.get("unidade", ""))
