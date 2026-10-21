"""Gera Lab_Inferencia_Simples.ipynb.  Uso: python gerar_notebook.py"""
import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

M = new_markdown_cell
C = new_code_cell

celulas = [
M(r"""# Laboratório de Testes de Hipóteses — versão simples

**Roteiro:** 1) carregar os módulos → 2) carregar o dataset → 3) explorar a distribuição → 4) calcular média,
mediana, variância e desvio padrão passo a passo → 5) verificar a normalidade → 6) escolher o teste →
7) carregar **só** o teste escolhido e executá-lo → 8) conclusão.

Os módulos ficam no GitHub e são baixados sob demanda: o notebook só traz o código do teste que for escolhido.

📘 **Primeira vez?** Leia o [guia de uso](https://github.com/RodrigoSantosB/lab-inferencia/blob/main/GUIA.md):
ele explica cada campo, como saber se os dados são pareados e os erros mais comuns.

**Como usar:** execute as células **de cima para baixo**. Nas células com formulário, preencha os campos e execute
a célula de novo. Se mudar algo numa etapa, execute novamente as etapas seguintes."""),

M("## 1. Configuração e módulos básicos"),
C(r'''#@title Endereço do repositório { display-mode: "form" }
USUARIO_GITHUB = "RodrigoSantosB"  #@param {type:"string"}
REPO = "lab-inferencia"  #@param {type:"string"}
BRANCH = "main"  #@param {type:"string"}
URL_BASE = ""  #@param {type:"string"}
#@markdown URL_BASE é opcional: se preenchida, substitui o endereço do GitHub.

import importlib, os, sys, urllib.request

PASTA_MODULOS = "modulos_baixados"
os.makedirs(PASTA_MODULOS, exist_ok=True)
LOCAL = os.path.isdir("lab") and not URL_BASE  # executando dentro de uma cópia do repositório
BASE = URL_BASE or f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO}/{BRANCH}/"


def baixar_arquivo(caminho):
    """Baixa um arquivo do repositório (ou usa a cópia local) e devolve o caminho no disco."""
    if LOCAL:
        return caminho
    if not URL_BASE and not USUARIO_GITHUB:
        raise ValueError("Preencha USUARIO_GITHUB com o usuário dono do repositório.")
    destino = os.path.join(PASTA_MODULOS, os.path.basename(caminho))
    urllib.request.urlretrieve(BASE + caminho, destino)
    return destino


def carregar_modulo(caminho):
    """Baixa um módulo .py e o importa (recarrega se já tiver sido importado)."""
    origem = baixar_arquivo(caminho)
    pasta = os.path.dirname(os.path.abspath(origem))
    if pasta not in sys.path:
        sys.path.insert(0, pasta)
    nome = os.path.splitext(os.path.basename(caminho))[0]
    modulo = importlib.reload(sys.modules[nome]) if nome in sys.modules else importlib.import_module(nome)
    print(f"✓ {caminho}  ({'cópia local' if LOCAL else BASE + caminho})")
    return modulo


comum = carregar_modulo("lab/comum.py")
exploracao = carregar_modulo("lab/exploracao.py")
escolha = carregar_modulo("lab/escolha.py")'''),

M(r"""## 2. Carregar o dataset

Use uma tabela no **formato longo**: uma linha por observação, uma coluna com os valores medidos e, se houver,
uma coluna com o grupo e outra com o identificador do par.

| exemplo | coluna de valores | coluna de grupo | coluna do par | ordem dos grupos |
|---|---|---|---|---|
| `equipe2_metodos_ensino` | nota | metodo | (vazio: grupos independentes) | B,A |
| `equipe1_mlp_cnn` | acuracia | modelo | execucao | CNN,MLP |
| `embalagens` (sintético) | peso_g | (vazio: um grupo) | (vazio) | (vazio) |
| `tempos_resposta` (sintético, assimétrico) | tempo_resposta_h | (vazio) | (vazio) | (vazio) |

**Seus dados:** escolha `upload` e envie um CSV ou Excel. Se a tabela tiver **uma coluna por grupo** (formato largo,
ex.: colunas `MLP` e `CNN`), use a célula opcional de conversão logo abaixo."""),
C(r'''#@title Fonte dos dados { display-mode: "form" }
FONTE = "exemplo"  #@param ["exemplo", "upload", "arquivo ou URL"]
EXEMPLO = "equipe2_metodos_ensino"  #@param ["equipe2_metodos_ensino", "equipe1_mlp_cnn", "embalagens", "tempos_resposta"]
CAMINHO = ""  #@param {type:"string"}

import pandas as pd
if FONTE == "exemplo":
    df = exploracao.ler_tabela(baixar_arquivo(f"dados/{EXEMPLO}.csv"))
elif FONTE == "upload":
    df = exploracao.upload_colab()
else:
    df = exploracao.ler_tabela(CAMINHO)
exploracao.visao_geral(df)'''),
C(r'''#@title (Opcional) Converter formato largo → longo { display-mode: "form" }
#@markdown Marque só se cada grupo estiver numa coluna separada. Liste as colunas, separadas por vírgula.
CONVERTER = False  #@param {type:"boolean"}
COLUNAS_LARGAS = "MLP,CNN"  #@param {type:"string"}
if CONVERTER:
    df = exploracao.largo_para_longo(df, [c.strip() for c in COLUNAS_LARGAS.split(",")])
    exploracao.visao_geral(df)
    print("Na próxima célula use COLUNA_VALOR = 'valor' e COLUNA_GRUPO = 'grupo'. Se cada linha original "
          "tinha medidas da mesma unidade (pareado), use também COLUNA_PAR = 'linha'.")
else:
    print("Nada a converter: a tabela já está no formato longo.")'''),
M(r"""**Como preencher a próxima célula** (os nomes devem ser iguais aos cabeçalhos mostrados acima):
- **COLUNA_VALOR**: a coluna com o número medido (nota, peso, acurácia…).
- **COLUNA_GRUPO**: a coluna que diz o grupo de cada linha. **Vazio** se houver um grupo só, comparado a um valor de referência.
- **COLUNA_PAR**: só para desenho **pareado** (a mesma unidade nos dois grupos: o mesmo aluno antes/depois, a mesma
  execução). Vazio se os grupos têm unidades diferentes.
- **ORDEM_GRUPOS**: `primeiro,segundo`; a diferença será primeiro − segundo. **Preencha sempre que houver 2 grupos.**
- **UNIDADE**: só um rótulo para os gráficos."""),
C(r'''#@title Quais colunas analisar? { display-mode: "form" }
COLUNA_VALOR = "nota"  #@param {type:"string"}
COLUNA_GRUPO = "metodo"  #@param {type:"string"}
#@markdown Preencha a coluna do par **somente** se o desenho for pareado (mesmo sujeito/execução nos dois grupos).
COLUNA_PAR = ""  #@param {type:"string"}
#@markdown Ordem dos grupos: a diferença será calculada como primeiro − segundo.
ORDEM_GRUPOS = "B,A"  #@param {type:"string"}
UNIDADE = "pontos"  #@param {type:"string"}

DADOS = exploracao.organizar(df, COLUNA_VALOR, COLUNA_GRUPO, COLUNA_PAR, ORDEM_GRUPOS)
PAREADO = DADOS["pares"] is not None
{g: len(v) for g, v in DADOS["grupos"].items()}'''),

M("## 3. Explorar a distribuição"),
C("exploracao.graficos(DADOS, UNIDADE)"),
M(r"""**O que observar:** o formato do histograma (simétrico? assimétrico?), valores muito afastados no boxplot e se os
pontos do gráfico Q-Q seguem a reta (sinal de distribuição próxima da normal)."""),

M(r"""## 4. Média, mediana e dispersão, passo a passo

Estas são **estatísticas da amostra**. Elas estimam os **parâmetros da população** ($\bar{x}$ estima $\mu$,
$s$ estima $\sigma$) e são a matéria-prima dos testes de hipóteses."""),
C("exploracao.resumo(DADOS, UNIDADE)"),

M(r"""## 5. A distribuição é aproximadamente normal?

O teste t supõe normalidade da variável relevante: os valores de cada grupo ou, no caso pareado, **as diferenças**."""),
C(r'''NORMALIDADE = exploracao.verificar_normalidade(DADOS, PAREADO)
NORMALIDADE["tabela"]'''),

M(r"""## 6. Escolher o teste

- **SIGMA_CONHECIDO**: marque **apenas** se o desvio padrão *da população* vier de fonte externa (histórico do
  processo, especificação). Na dúvida, deixe desmarcado: o notebook usará o desvio padrão da amostra (teste t).
- **MU0**: valor de referência, usado só com **um grupo** (ex.: 500 g). Com dois grupos é ignorado.
- **ALTERNATIVA**: "bilateral" = há diferença; "maior" = primeiro grupo > segundo (ou média > μ₀); "menor" = o
  contrário. Escolha antes de olhar os resultados; na dúvida, use "bilateral".
- **ALPHA**: nível de significância, normalmente 0,05.
- **TROCAR_TESTE**: deixe vazio para usar o teste sugerido."""),
C(r'''#@title Hipóteses { display-mode: "form" }
#@markdown σ conhecido = desvio padrão **da população** vindo de fonte externa (histórico, especificação).
SIGMA_CONHECIDO = False  #@param {type:"boolean"}
SIGMA = 0.0  #@param {type:"number"}
#@markdown Valor de referência μ₀ (usado só quando há um único grupo).
MU0 = 0.0  #@param {type:"number"}
ALTERNATIVA = "maior"  #@param ["bilateral", "maior", "menor"]
ALPHA = 0.05  #@param [0.01, 0.05, 0.10] {type:"raw"}
#@markdown Para usar outro teste em vez do sugerido, escolha-o aqui.
TROCAR_TESTE = ""  #@param ["", "t_uma_amostra", "z_uma_amostra", "t_welch", "t_pareado", "wilcoxon", "mann_whitney"]

N_GRUPOS = len(DADOS["grupos"])
if N_GRUPOS > 2:
    raise ValueError("Este notebook compara no máximo 2 grupos; para 3 ou mais use ANOVA (notebook completo).")
SUGERIDO, ALTERNATIVO = escolha.sugerir_teste(N_GRUPOS, PAREADO, SIGMA_CONHECIDO, NORMALIDADE["grave"])
TESTE = TROCAR_TESTE or SUGERIDO
print("Teste que será carregado:", TESTE)'''),
M(r"""**Direção da hipótese:** "maior" significa $H_1$: primeiro grupo > segundo (ou média > μ₀). Use teste
unilateral apenas se a direção foi definida **antes** de olhar os dados; na dúvida, use "bilateral"."""),

M("## 7. Carregar e executar somente o teste escolhido"),
C(r'''teste = carregar_modulo(f"lab/testes/{TESTE}.py")
CFG = {"mu0": MU0, "sigma": SIGMA, "alpha": ALPHA, "alternativa": ALTERNATIVA, "unidade": UNIDADE}
RESULTADO = teste.executar_com(DADOS, CFG)'''),
C(r'''#@title Ver o código do teste carregado (opcional) { display-mode: "form" }
import inspect
print(inspect.getsource(teste.executar))'''),

M("## 8. Conclusão"),
C(r'''#@title Pergunta de pesquisa { display-mode: "form" }
PERGUNTA = "verificar se a nota média com o método ativo (B) é maior que com o tradicional (A)"  #@param {type:"string"}
comum.conclusao(RESULTADO, PERGUNTA);'''),
]

nb = new_notebook(cells=celulas)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nb.metadata["language_info"] = {"name": "python"}
nb.metadata["colab"] = {"provenance": [], "toc_visible": True}
nbformat.validate(nb)
nbformat.write(nb, "Lab_Inferencia_Simples.ipynb")
print(f"Lab_Inferencia_Simples.ipynb gerado ({len(celulas)} células)")
