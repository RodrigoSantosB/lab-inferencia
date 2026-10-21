"""Sugere o teste a partir das respostas do usuário e do diagnóstico de normalidade."""
from comum import md

NOMES = {
    "z_uma_amostra": "Teste Z para uma média (σ conhecido)",
    "t_uma_amostra": "Teste t para uma média (σ desconhecido)",
    "t_welch": "Teste t de Welch (dois grupos independentes)",
    "t_pareado": "Teste t pareado",
    "wilcoxon": "Wilcoxon dos postos sinalizados (alternativa não paramétrica)",
    "mann_whitney": "Mann-Whitney (alternativa não paramétrica)",
}


def sugerir_teste(n_grupos, pareado, sigma_conhecido, normalidade_grave):
    """Regras explícitas de escolha. Retorna (módulo sugerido, alternativa ou None).

    * 1 grupo: σ populacional conhecido por fonte externa → Z; caso contrário → t.
      (Ter n grande NÃO torna σ conhecido.)
    * 2 grupos pareados (mesma unidade nas duas condições) → t pareado sobre as diferenças.
    * 2 grupos independentes → t de Welch (não exige variâncias iguais).
    * Normalidade com afastamento forte e n pequeno → o não paramétrico passa a ser o sugerido.
    """
    motivos = []
    if n_grupos == 1:
        if sigma_conhecido:
            principal = "z_uma_amostra"
            motivos.append("há **um grupo** comparado a um valor de referência e o **σ populacional é conhecido** "
                           "por fonte externa (não calculado na amostra)")
        else:
            principal = "t_uma_amostra"
            motivos.append("há **um grupo** comparado a um valor de referência e o **σ populacional é desconhecido**, "
                           "então ele é estimado pelo desvio padrão da amostra s (por isso a distribuição t)")
        nao_param = "wilcoxon"
    elif pareado:
        principal = "t_pareado"
        motivos.append("há **dois grupos pareados**: cada observação de um grupo tem um par natural no outro "
                       "(mesmo sujeito, mesma execução...), então analisamos as **diferenças** dentro de cada par")
        nao_param = "wilcoxon"
    else:
        principal = "t_welch"
        motivos.append("há **dois grupos independentes** (unidades diferentes em cada grupo) com σ desconhecidos; "
                       "o t de Welch não exige que as variâncias dos grupos sejam iguais")
        nao_param = "mann_whitney"

    if normalidade_grave:
        sugerido, alternativa = nao_param, principal
        motivos.append("porém a verificação de normalidade mostrou **afastamento forte com amostra pequena**, então "
                       f"sugerimos o **{NOMES[nao_param]}**. Atenção: ele compara medianas/postos, não médias")
    else:
        sugerido, alternativa = principal, nao_param
        motivos.append("a verificação de normalidade não mostrou problema grave")

    md(f"### Teste sugerido: **{NOMES[sugerido]}** (`{sugerido}`)\n\nPorque " + "; ".join(motivos) + ".\n\n"
       f"Alternativa, se quiserem comparar: `{alternativa}` ({NOMES[alternativa]}).")
    return sugerido, alternativa
