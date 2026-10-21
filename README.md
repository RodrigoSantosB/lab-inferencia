# lab-inferencia

Notebook simples para a aula de testes de hipóteses. A turma carrega um dataset, explora a distribuição, calcula
média, mediana e dispersão passo a passo, escolhe o teste com perguntas guiadas e baixa do GitHub **apenas o módulo
do teste escolhido**.

## Abrir no Colab

1. Abra `https://colab.research.google.com/github/RodrigoSantosB/lab-inferencia/blob/main/Lab_Inferencia_Simples.ipynb`.
2. Na primeira célula, confira se `USUARIO_GITHUB` é o dono do repositório (padrão: RodrigoSantosB).
3. Execute as células em ordem, ajustando os formulários de cada etapa.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `Lab_Inferencia_Simples.ipynb` | o notebook (21 células) |
| `lab/comum.py` | p-valor, valores críticos, relatório padronizado, gráfico da distribuição sob H₀, conclusão |
| `lab/exploracao.py` | leitura dos dados, gráficos, cálculo passo a passo, verificação de normalidade |
| `lab/escolha.py` | regras que sugerem o teste |
| `lab/testes/*.py` | um arquivo por teste: `t_uma_amostra`, `z_uma_amostra`, `t_welch`, `t_pareado`, `wilcoxon`, `mann_whitney` |
| `dados/` | exemplos: Equipe 1 (MLP × CNN), Equipe 2 (métodos de ensino), embalagens e tempos de resposta (sintéticos) |
| `verificar.py` | confere cada teste com o SciPy e com casos de referência |
| `gerar_notebook.py` | regera o `.ipynb` |

## Adicionar um teste

1. Crie `lab/testes/<nome>.py` com duas funções: `executar(...)`, que calcula e chama `comum.relatorio`, e
   `executar_com(dados, cfg)`, que lê os dados organizados pelo notebook.
2. Inclua o nome em `NOMES` e nas regras de `lab/escolha.py`.
3. Acrescente uma comparação com o SciPy em `verificar.py` e rode `python verificar.py`.
