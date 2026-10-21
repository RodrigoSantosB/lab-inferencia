"""Funções comuns a todos os testes: direção da hipótese, p-valor, valores críticos, relatório e gráfico."""
import math

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

try:
    from IPython.display import Markdown, display
except ImportError:  # fora do Jupyter: imprime o texto
    Markdown = str
    display = print

ALTERNATIVAS = {"bilateral": "two-sided", "maior": "greater", "menor": "less",
                "two-sided": "two-sided", "greater": "greater", "less": "less"}
SINAL_H0 = {"two-sided": "=", "greater": r"\leq", "less": r"\geq"}
SINAL_H1 = {"two-sided": r"\neq", "greater": ">", "less": "<"}
NOME_ALT = {"two-sided": "bilateral", "greater": "unilateral à direita", "less": "unilateral à esquerda"}
SEMENTE = 2026


def md(texto):
    """Mostra texto Markdown (com LaTeX) na saída da célula."""
    display(Markdown(texto))


def alternativa(a):
    """Converte 'bilateral' / 'maior' / 'menor' para o vocabulário do SciPy."""
    if a not in ALTERNATIVAS:
        raise ValueError(f"Alternativa '{a}' inválida: use 'bilateral', 'maior' ou 'menor'.")
    return ALTERNATIVAS[a]


def fp(p):
    """Formata o p-valor sem nunca mostrar 'p = 0'."""
    if p <= 0:
        return "< 1e-300"
    return f"{p:.3e}" if p < 1e-4 else f"{p:.4f}"


def n(x, casas=4):
    """Número compacto para textos e fórmulas."""
    return f"{x:.{casas}g}" if abs(x) >= 1e4 or (0 < abs(x) < 1e-3) else f"{x:.{casas}f}".rstrip("0").rstrip(".")


def p_valor(dist, estat, alt):
    """P-valor pela cauda indicada em H1 (usa sf/cdf, precisos nas caudas). dist: normal ou t do SciPy."""
    if alt == "greater":
        return float(dist.sf(estat))
    if alt == "less":
        return float(dist.cdf(estat))
    return float(min(1.0, 2 * dist.sf(abs(estat))))


def criticos(dist, alpha, alt):
    """Valor(es) crítico(s) da região de rejeição de tamanho α."""
    if alt == "greater":
        return (None, float(dist.isf(alpha)))
    if alt == "less":
        return (float(dist.ppf(alpha)), None)
    return (float(dist.ppf(alpha / 2)), float(dist.isf(alpha / 2)))


def texto_regiao(crit, simbolo):
    lo, hi = crit
    partes = []
    if lo is not None:
        partes.append(f"${simbolo} \\leq {n(lo)}$")
    if hi is not None:
        partes.append(f"${simbolo} \\geq {n(hi)}$")
    return " ou ".join(partes)


def hipoteses(parametro, valor, alt):
    return (f"{parametro} {SINAL_H0[alt]} {n(valor)}", f"{parametro} {SINAL_H1[alt]} {n(valor)}")


def relatorio(r):
    """Exibe o resultado de um teste a partir de um dicionário padronizado."""
    rejeita = r["p"] < r["alpha"]
    linhas = [f"### {r['nome']}",
              f"**Hipóteses ({NOME_ALT[r['alt']]}):** $H_0: {r['h0']}$ contra $H_1: {r['h1']}$"]
    if r.get("formula"):
        linhas.append(f"**Fórmula:** $${r['formula']}$$")
    if r.get("substituicao"):
        linhas.append(f"**Com os dados:** $${r['substituicao']}$$")
    if r.get("referencia"):
        linhas.append(f"**Distribuição sob H₀:** {r['referencia']}.  ")
    if r.get("crit"):
        linhas.append(f"**Região crítica (α = {r['alpha']}):** {texto_regiao(r['crit'], r['simbolo'])}.  ")
    linhas.append(f"**p-valor:** {fp(r['p'])}  ")
    if rejeita:
        linhas.append(f"**Decisão:** p < α = {r['alpha']} → **rejeita-se H₀**.")
    else:
        linhas.append(f"**Decisão:** p ≥ α = {r['alpha']} → **não se rejeita H₀** "
                      "(isso não prova que H₀ seja verdadeira).")
    if r.get("ic"):
        un = f" {r['unidade']}" if r.get("unidade") else ""
        linhas.append(f"**Estimativa:** {r['nome_estimativa']} = {n(r['estimativa'])}{un}; "
                      f"IC {100 * (1 - r['alpha']):.0f}%: [{n(r['ic'][0])}; {n(r['ic'][1])}]{un} ({r['ic_metodo']}).")
    if r.get("efeito"):
        linhas.append("**Tamanho de efeito:** " + "; ".join(f"{k} = {n(v, 3)}" for k, v in r["efeito"].items()) + ".")
    if r.get("aviso"):
        linhas.append(f"⚠️ {r['aviso']}")
    linhas.append("*Lembrete:* o p-valor é calculado supondo H₀ verdadeira; ele não é a probabilidade de H₀ ser "
                  "verdadeira nem mede o tamanho do efeito. Interprete-o junto com o IC.")
    md("\n\n".join(linhas))
    r["rejeita"] = rejeita
    return r


def grafico_h0(dist, estat, alt, alpha, p, simbolo, titulo):
    """Distribuição sob H0 com região crítica (vermelho), área do p-valor (azul) e valor observado."""
    lo, hi = float(dist.ppf(0.0005)), float(dist.isf(0.0005))
    lo, hi = min(lo, estat - 0.5), max(hi, estat + 0.5)
    xs = np.linspace(lo, hi, 1500)
    ys = dist.pdf(xs)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(xs, ys, color="black", lw=1.5, label="distribuição sob H₀")
    c_lo, c_hi = criticos(dist, alpha, alt)
    regiao = np.zeros_like(xs, bool)
    if c_lo is not None:
        regiao |= xs <= c_lo
    if c_hi is not None:
        regiao |= xs >= c_hi
    ax.fill_between(xs, ys, where=regiao, color="#d62728", alpha=0.35, label=f"região crítica (α = {alpha})")
    if alt == "greater":
        area = xs >= estat
    elif alt == "less":
        area = xs <= estat
    else:
        area = np.abs(xs) >= abs(estat)
    ax.fill_between(xs, ys, where=area, facecolor="none", hatch="///", edgecolor="#1f77b4",
                    label=f"área do p-valor (p = {fp(p)})")
    ax.axvline(estat, color="#1f77b4", lw=2, label=f"{simbolo} observado = {estat:.3f}")
    ax.set(title=titulo, xlabel=simbolo, ylabel="densidade")
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=8)
    plt.show()


def ic_bootstrap(estatistica, *amostras, alpha=0.05, B=5000):
    """IC bootstrap percentil com semente fixa (usado nos testes não paramétricos)."""
    rng = np.random.default_rng(SEMENTE)
    valores = [estatistica(*[a[rng.integers(0, a.size, a.size)] for a in amostras]) for _ in range(B)]
    return tuple(np.percentile(valores, [100 * alpha / 2, 100 * (1 - alpha / 2)]))


def validar(x, nome="amostra", minimo=2):
    """Converte para array e recusa ausentes, amostras pequenas e variância nula."""
    arr = np.asarray(x, dtype=float).ravel()
    if np.isnan(arr).any():
        raise ValueError(f"{nome} tem valores ausentes; remova-os ou trate-os antes do teste.")
    if arr.size < minimo:
        raise ValueError(f"{nome} tem n = {arr.size}; são necessárias ao menos {minimo} observações.")
    if np.var(arr) == 0:
        raise ValueError(f"{nome} tem todos os valores iguais (variância zero).")
    return arr


def conclusao(r, pergunta=""):
    """Parágrafo de conclusão: decisão, estimativa com IC e limites do que foi mostrado."""
    nivel = f"{100 * (1 - r['alpha']):.0f}%"
    un = f" {r['unidade']}" if r.get("unidade") else ""
    texto = (f"Para {pergunta or 'responder à pergunta de pesquisa'}, aplicou-se o {r['nome']} "
             f"({NOME_ALT[r['alt']]}, α = {r['alpha']}). Obteve-se p = {fp(r['p'])}; ")
    if r["p"] < r["alpha"]:
        texto += f"portanto, rejeitou-se $H_0: {r['h0']}$, havendo evidência a favor de $H_1: {r['h1']}$. "
    else:
        texto += (f"portanto, não se rejeitou $H_0: {r['h0']}$. Isso indica falta de evidência, "
                  "não prova de que não há diferença. ")
    if r.get("ic"):
        texto += (f"A estimativa ({r['nome_estimativa']}) foi {n(r['estimativa'])}{un}, com IC {nivel} de "
                  f"{n(r['ic'][0])} a {n(r['ic'][1])}{un}: esse intervalo mostra a magnitude plausível do efeito, "
                  "que deve ser julgada no contexto do problema. ")
    texto += ("A conclusão vale para a população que a amostra representa e depende de as observações serem "
              "independentes; sem alocação aleatória, ela indica associação, não causa.")
    md("### Conclusão\n" + texto)
    return texto
