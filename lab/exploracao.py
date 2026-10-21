"""Carregamento do dataset, análise exploratória, cálculo passo a passo e verificação da normalidade."""
import io
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from comum import md, n


# ----------------------------------------------------------------------------
# Carregamento
# ----------------------------------------------------------------------------
def ler_tabela(caminho):
    """Lê CSV (separador detectado automaticamente) ou Excel."""
    if str(caminho).lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(caminho)
    return pd.read_csv(caminho, sep=None, engine="python")


def upload_colab():
    """Abre o seletor de arquivos do Colab e lê o primeiro arquivo enviado."""
    from google.colab import files
    enviados = files.upload()
    nome, conteudo = next(iter(enviados.items()))
    if nome.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(conteudo))
    return pd.read_csv(io.BytesIO(conteudo), sep=None, engine="python")


def visao_geral(df):
    """Tamanho, tipos, valores ausentes e primeiras linhas."""
    md(f"**{df.shape[0]} linhas × {df.shape[1]} colunas.**")
    display_df(pd.DataFrame({"tipo": df.dtypes.astype(str), "válidos": df.notna().sum(),
                             "ausentes": df.isna().sum()}))
    display_df(df.head())


def display_df(df):
    try:
        from IPython.display import display
        display(df)
    except ImportError:
        print(df)


def organizar(df, coluna_valor, coluna_grupo="", coluna_par="", ordem_grupos=""):
    """Separa os valores por grupo e, se houver identificador de par, alinha os pares.

    Retorna um dicionário com:
      grupos: {nome do grupo: array de valores}  (a ordem define a diferença grupo1 − grupo2)
      pares: DataFrame com as colunas grupo1, grupo2 e diferenca (ou None)
    Valores ausentes na coluna de valores são removidos e a quantidade é informada.
    """
    if coluna_valor not in df.columns:
        raise ValueError(f"Coluna '{coluna_valor}' não existe. Colunas: {list(df.columns)}")
    dados = df.copy()
    dados[coluna_valor] = pd.to_numeric(dados[coluna_valor], errors="coerce")
    ausentes = int(dados[coluna_valor].isna().sum())
    dados = dados.dropna(subset=[coluna_valor])
    if ausentes:
        md(f"⚠️ {ausentes} valor(es) ausente(s) ou não numérico(s) em `{coluna_valor}` foram removidos.")
    if not coluna_grupo:
        return {"grupos": {coluna_valor: dados[coluna_valor].to_numpy()}, "pares": None, "valor": coluna_valor}
    nomes = [g.strip() for g in ordem_grupos.split(",")] if ordem_grupos else \
        sorted(dados[coluna_grupo].astype(str).unique())
    dados[coluna_grupo] = dados[coluna_grupo].astype(str)
    grupos = {g: dados.loc[dados[coluna_grupo] == g, coluna_valor].to_numpy() for g in nomes}
    for g, v in grupos.items():
        if v.size == 0:
            raise ValueError(f"O grupo '{g}' não tem observações. Grupos existentes: "
                             f"{sorted(dados[coluna_grupo].unique())}")
    pares = None
    if coluna_par:
        if len(nomes) != 2:
            raise ValueError("Pareamento exige exatamente 2 grupos.")
        largo = dados.pivot_table(index=coluna_par, columns=coluna_grupo, values=coluna_valor, aggfunc="count")
        if (largo > 1).any().any():
            raise ValueError("Há identificadores repetidos dentro de um mesmo grupo: o pareamento é ambíguo.")
        largo = dados.pivot(index=coluna_par, columns=coluna_grupo, values=coluna_valor)[nomes]
        incompletos = int(largo.isna().any(axis=1).sum())
        pares = largo.dropna().copy()
        pares["diferenca"] = pares[nomes[0]] - pares[nomes[1]]
        md(f"**Pareamento por `{coluna_par}`:** {len(pares)} pares completos"
           + (f"; {incompletos} incompleto(s) removido(s)." if incompletos else "."))
    return {"grupos": grupos, "pares": pares, "valor": coluna_valor}


# ----------------------------------------------------------------------------
# Gráficos
# ----------------------------------------------------------------------------
def graficos(dados, unidade=""):
    """Histograma, boxplot com pontos e gráfico Q-Q de cada grupo."""
    grupos = dados["grupos"]
    rotulo = f"{dados['valor']} ({unidade})" if unidade else dados["valor"]
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.2))
    for g, v in grupos.items():
        axes[0].hist(v, bins="auto", alpha=0.55, edgecolor="white", label=g)
    axes[0].set(title="Histograma", xlabel=rotulo, ylabel="frequência")
    axes[0].legend()
    axes[1].boxplot(list(grupos.values()), showfliers=False)
    axes[1].set_xticks(range(1, len(grupos) + 1), list(grupos))
    rng = np.random.default_rng(0)
    for i, v in enumerate(grupos.values(), start=1):
        axes[1].scatter(i + rng.uniform(-0.08, 0.08, v.size), v, s=12, color="black", alpha=0.6)
    axes[1].set(title="Boxplot (caixa = Q1 a Q3) + pontos", ylabel=rotulo)
    for g, v in grupos.items():
        (teo, amo), (inc, inter, _) = stats.probplot(v, dist="norm")
        axes[2].scatter(teo, amo, s=14, label=g)
        axes[2].plot(teo, inc * np.asarray(teo) + inter, lw=1)
    axes[2].set(title="Gráfico Q-Q normal (pontos na reta ≈ normal)", xlabel="quantis teóricos N(0,1)",
                ylabel="quantis da amostra")
    axes[2].legend()
    plt.tight_layout()
    plt.show()
    if dados["pares"] is not None:
        d = dados["pares"]["diferenca"]
        g1, g2 = list(grupos)
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.hist(d, bins="auto", edgecolor="white", color="#9ecae1")
        ax.axvline(0, color="#d62728", ls="--", label="diferença zero")
        ax.axvline(d.mean(), color="black", label=f"média das diferenças = {d.mean():.3f}")
        ax.set(title=f"Diferenças dentro de cada par ({g1} − {g2})", xlabel=rotulo, ylabel="frequência")
        ax.legend()
        plt.show()


# ----------------------------------------------------------------------------
# Passo a passo
# ----------------------------------------------------------------------------
def passo_a_passo(x, nome="amostra", unidade=""):
    """Média, mediana, variância, desvio padrão e erro padrão, com as contas à mostra."""
    x = np.asarray(x, dtype=float)
    k = x.size
    un = f" {unidade}" if unidade else ""
    soma = x.sum()
    media = soma / k
    ordenados = np.sort(x)
    if k % 2:
        mediana = ordenados[k // 2]
        txt_med = f"n = {k} é ímpar: a mediana é o valor na posição {(k + 1) // 2} dos dados ordenados"
    else:
        mediana = (ordenados[k // 2 - 1] + ordenados[k // 2]) / 2
        txt_med = (f"n = {k} é par: a mediana é a média dos valores nas posições {k // 2} e {k // 2 + 1} "
                   f"dos dados ordenados: ({n(ordenados[k // 2 - 1])} + {n(ordenados[k // 2])})/2")
    sq = ((x - media) ** 2).sum()
    var = sq / (k - 1)
    dp = math.sqrt(var)
    ep = dp / math.sqrt(k)
    mostrar = ", ".join(n(v) for v in ordenados[:12]) + (", …" if k > 12 else "")
    md(f"""#### {nome} (n = {k})
1. **Média** $\\bar{{x}} = \\frac{{\\sum x_i}}{{n}} = \\frac{{{n(soma)}}}{{{k}}} = {n(media)}${un}
2. **Mediana:** dados ordenados: {mostrar}. {txt_med} → **{n(mediana)}**{un}
3. **Variância** $s^2 = \\frac{{\\sum (x_i - \\bar{{x}})^2}}{{n-1}} = \\frac{{{n(sq)}}}{{{k - 1}}} = {n(var)}$ (divide por n − 1)
4. **Desvio padrão** $s = \\sqrt{{s^2}} = {n(dp)}${un}: dispersão dos **dados**
5. **Erro padrão da média** $EP = s/\\sqrt{{n}} = {n(dp)}/\\sqrt{{{k}}} = {n(ep)}${un}: incerteza da **média**""")
    conf = pd.DataFrame({"passo a passo": [media, mediana, var, dp, ep],
                         "pandas": [pd.Series(x).mean(), pd.Series(x).median(), pd.Series(x).var(),
                                    pd.Series(x).std(), pd.Series(x).sem()]},
                        index=["média", "mediana", "variância", "desvio padrão", "erro padrão"])
    return conf


def resumo(dados, unidade=""):
    """Passo a passo para cada grupo (e para as diferenças, se pareado) + tabela de conferência."""
    tabelas = {}
    for g, v in dados["grupos"].items():
        tabelas[g] = passo_a_passo(v, g, unidade)
    if dados["pares"] is not None:
        g1, g2 = list(dados["grupos"])
        tabelas[f"{g1} − {g2}"] = passo_a_passo(dados["pares"]["diferenca"], f"diferenças {g1} − {g2}", unidade)
    md("**Conferência com o pandas** (os valores devem coincidir):")
    return pd.concat(tabelas, axis=1)


# ----------------------------------------------------------------------------
# Normalidade
# ----------------------------------------------------------------------------
def verificar_normalidade(dados, pareado=False):
    """Shapiro-Wilk + assimetria na variável relevante: cada grupo ou, se pareado, as diferenças.

    Retorna {'grave': bool, 'tabela': DataFrame}. 'grave' indica afastamento forte (assimetria acentuada ou
    Shapiro com p < 0,01) em amostra pequena (n < 30), situação em que o teste t fica mal justificado.
    """
    if pareado and dados["pares"] is not None:
        alvos = {"diferenças": dados["pares"]["diferenca"].to_numpy()}
    else:
        alvos = dados["grupos"]
    linhas, grave = [], False
    for nome, x in alvos.items():
        w, p = stats.shapiro(x) if x.size >= 3 else (float("nan"), float("nan"))
        g1 = float(stats.skew(x, bias=False)) if x.size > 2 else float("nan")
        forte = x.size < 30 and (abs(g1) >= 1 or p < 0.01)
        grave |= forte
        leitura = ("afastamento forte com n pequeno" if forte else
                   "sem evidência relevante contra a normalidade" if p >= 0.05 else
                   "afastamento detectado, mas moderado para este n")
        linhas.append({"variável": nome, "n": x.size, "W (Shapiro)": w, "p (Shapiro)": p,
                       "assimetria": g1, "leitura": leitura})
    md("**Lembrete:** p > 0,05 no Shapiro-Wilk **não prova** normalidade (com n pequeno o teste tem pouco poder); "
       "olhe também o histograma e o gráfico Q-Q. Testes de médias toleram afastamentos moderados quando n cresce.")
    return {"grave": grave, "tabela": pd.DataFrame(linhas)}
