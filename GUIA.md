# Guia de uso — Laboratório de Testes de Hipóteses

Este guia acompanha o notebook [`Lab_Inferencia_Simples.ipynb`](https://colab.research.google.com/github/RodrigoSantosB/lab-inferencia/blob/main/Lab_Inferencia_Simples.ipynb).
Ele explica o que preencher em cada etapa e como ler os resultados.

**Regra geral:** execute as células de cima para baixo. Ao mudar um campo, execute a célula de novo e as
etapas seguintes também.

---

## 0. Antes de começar: prepare a tabela

O notebook lê **CSV** ou **Excel**. A tabela deve estar no **formato longo**, com uma linha por observação:

| aluno | metodo | nota |
|---|---|---|
| A01 | A | 6.5 |
| A02 | A | 7.0 |
| B01 | B | 8.0 |

Se a sua tabela tiver **uma coluna por grupo** (formato largo), não precisa editá-la: o notebook tem uma célula
que faz a conversão (etapa 2).

| MLP | CNN |
|---|---|
| 85.2 | 89.5 |
| 84.8 | 90.1 |

Cuidados:
- Ponto ou vírgula decimal (`85.2` ou `85,2`) são aceitos, assim como CSV separado por `,` ou `;`. Valores não
  numéricos na coluna medida (texto, células vazias) são removidos, e o notebook avisa quantos foram.
- Os nomes das colunas devem ser simples e sem espaços (ex.: `tempo_h`, `nota_final`).

---

## 1. Configuração

Basta executar a célula. Ela deve mostrar três linhas começando com ✓ (`comum.py`, `exploracao.py`, `escolha.py`).
Não altere os campos, a não ser que o repositório mude de endereço.

---

## 2. Carregar o dataset

### Fonte dos dados
| Campo | O que colocar |
|---|---|
| **FONTE** | `exemplo` (dados prontos), `upload` (enviar arquivo do computador) ou `arquivo ou URL` |
| **EXEMPLO** | um dos exemplos, usado só se FONTE = `exemplo` |
| **CAMINHO** | usado só se FONTE = `arquivo ou URL` (ex.: link de um CSV público) |

Com `upload`, aparece o botão **Escolher arquivos** abaixo da célula. A saída mostra o tamanho da tabela, o tipo
de cada coluna, os valores ausentes e as primeiras linhas. **Use essa saída para copiar os nomes exatos das colunas.**

### (Opcional) Converter formato largo → longo
Marque **CONVERTER** e escreva em **COLUNAS_LARGAS** as colunas dos grupos, separadas por vírgula (ex.: `MLP,CNN`).
A tabela passa a ter as colunas `valor`, `grupo` e `linha`. Se a tabela já estiver no formato longo, deixe desmarcado.

### Quais colunas analisar?
| Campo | O que colocar | Exemplo |
|---|---|---|
| **COLUNA_VALOR** | a coluna com o **número medido** | `nota` |
| **COLUNA_GRUPO** | a coluna que diz o **grupo** de cada linha; **vazio** se for um grupo só | `metodo` |
| **COLUNA_PAR** | a coluna que identifica **o par** — **só** se o desenho for pareado | `execucao` |
| **ORDEM_GRUPOS** | `primeiro,segundo`: a diferença será **primeiro − segundo** | `B,A` |
| **UNIDADE** | rótulo para gráficos e resultados (não muda as contas) | `pontos` |

Depois de executar, confira a mensagem **"Diferença calculada como X − Y"** e a contagem de observações por grupo.

#### Meus dados são pareados ou independentes?
Pergunte-se: **a mesma unidade aparece nos dois grupos?**

| Situação | Desenho | COLUNA_PAR |
|---|---|---|
| Os mesmos alunos fizeram a prova antes e depois do curso | pareado | id do aluno |
| Os dois modelos rodaram com as mesmas sementes/partições, execução a execução | pareado | id da execução |
| Uma turma teve o método A e **outra** turma o método B | independente | vazio |
| Pacientes diferentes em cada tratamento | independente | vazio |

Ter grupos **do mesmo tamanho não torna** o desenho pareado. Quem decide é a forma como os dados foram coletados.

#### Exemplos prontos
| Exemplo | COLUNA_VALOR | COLUNA_GRUPO | COLUNA_PAR | ORDEM_GRUPOS |
|---|---|---|---|---|
| `equipe2_metodos_ensino` | `nota` | `metodo` | *(vazio)* | `B,A` |
| `equipe1_mlp_cnn` | `acuracia` | `modelo` | `execucao` | `CNN,MLP` |
| `embalagens` | `peso_g` | *(vazio)* | *(vazio)* | *(vazio)* |
| `tempos_resposta` | `tempo_resposta_h` | *(vazio)* | *(vazio)* | *(vazio)* |

---

## 3. Explorar a distribuição

Basta executar. Os gráficos mostram:
- **Histograma:** a forma da distribuição (simétrica? com cauda longa para um lado?).
- **Boxplot com pontos:** mediana, quartis e valores afastados.
- **Gráfico Q-Q:** se os pontos seguem a reta, a distribuição é próxima da normal; curvas e pontas afastadas
  indicam assimetria ou valores extremos.
- **Histograma das diferenças** (só no caso pareado): é a variável que o teste pareado analisa.

---

## 4. Média, mediana e dispersão, passo a passo

Basta executar. Para cada grupo, o notebook mostra as contas:

| Medida | O que é |
|---|---|
| Média $\bar{x}$ | soma dos valores ÷ n; estima a média da população μ |
| Mediana | valor do meio dos dados ordenados; menos sensível a valores extremos |
| Variância $s^2$ | dispersão, dividindo por **n − 1** |
| Desvio padrão $s$ | dispersão dos **dados**, na unidade original |
| Erro padrão $s/\sqrt{n}$ | incerteza da **média**; diminui quando n aumenta |

A tabela final compara as contas com o pandas: os valores devem coincidir. Média muito diferente da mediana é
sinal de assimetria.

---

## 5. Normalidade

Basta executar. A tabela mostra o Shapiro-Wilk e a assimetria da variável relevante: cada grupo ou, se pareado,
as diferenças.
- **p > 0,05 não prova normalidade**: com poucos dados, o teste quase nunca rejeita. Use também os gráficos.
- Se aparecer **"afastamento forte com n pequeno"**, a etapa 6 vai sugerir um teste não paramétrico.

---

## 6. Escolher o teste

| Campo | O que colocar |
|---|---|
| **SIGMA_CONHECIDO** | marque **só** se o desvio padrão **da população** vier de fonte externa (histórico, especificação). Calcular `s` nos dados **não** conta. Na dúvida, deixe desmarcado. |
| **SIGMA** | o valor desse σ externo (usado só se marcado) |
| **MU0** | valor de referência, usado **só com um grupo** (ex.: `500` para "o peso médio difere de 500 g?") |
| **ALTERNATIVA** | `bilateral`: há diferença em qualquer direção · `maior`: primeiro grupo > segundo (ou média > μ₀) · `menor`: o contrário |
| **ALPHA** | nível de significância; normalmente `0.05` |
| **TROCAR_TESTE** | vazio = usa o sugerido; ou escolha outro para comparar |

**Escolha a ALTERNATIVA antes de ver os resultados.** Trocar para "maior" ou "menor" depois de olhar as médias
infla a chance de falso positivo. Na dúvida, use `bilateral`.

Como a sugestão é feita:

| Situação | Teste sugerido |
|---|---|
| 1 grupo, σ conhecido por fonte externa | Z para uma média |
| 1 grupo, σ desconhecido | t para uma média |
| 2 grupos pareados | t pareado (sobre as diferenças) |
| 2 grupos independentes | t de Welch |
| Afastamento forte da normalidade com n pequeno | Wilcoxon (1 grupo ou pareado) ou Mann-Whitney (independentes) |

---

## 7. Executar o teste

Basta executar. O notebook baixa **só** o arquivo do teste escolhido e mostra:

| Item | Como ler |
|---|---|
| **Hipóteses** | H₀ (sem diferença) e H₁ (o que se quer mostrar) |
| **Fórmula e "Com os dados"** | a conta feita, com os seus números |
| **Região crítica** | valores da estatística que levam a rejeitar H₀ |
| **p-valor** | probabilidade de um resultado tão extremo **se H₀ fosse verdadeira** |
| **Decisão** | p < α → rejeita H₀; p ≥ α → não rejeita H₀ |
| **Estimativa e IC** | o tamanho da diferença e a faixa de valores plausíveis |
| **Tamanho de efeito** | magnitude padronizada (ex.: d de Cohen) |
| **Gráfico** | curva sob H₀, região crítica em vermelho, área do p-valor hachurada e valor observado |

Leituras corretas:
- **Não rejeitar H₀ não prova que não há diferença**; pode faltar dado.
- O **p-valor não é** a probabilidade de H₀ ser verdadeira.
- Um p-valor pequeno não significa um efeito grande: **olhe o IC** e pergunte se a diferença importa na prática.
- Testes não paramétricos (Wilcoxon, Mann-Whitney) falam de **medianas/postos**, não de médias.

A célula seguinte, opcional, mostra o código do teste carregado.

---

## 8. Conclusão

Escreva a pergunta de pesquisa em **PERGUNTA** e execute. O parágrafo gerado traz o teste, o p-valor, a decisão
e a estimativa com IC. Pode servir de base para o relatório, mas revise-o: a conclusão vale para a população que a
amostra representa e, sem sorteio dos grupos, mostra associação, não causa.

---

## Erros comuns

| Mensagem ou sintoma | Causa | Solução |
|---|---|---|
| `Coluna 'x' não existe` | nome digitado diferente do cabeçalho | copie o nome da tabela mostrada na etapa 2 |
| `O grupo 'x' não tem observações` | ORDEM_GRUPOS com nome errado | use os nomes listados na mensagem |
| "ordem ALFABÉTICA" no aviso da diferença | ORDEM_GRUPOS vazio | preencha `primeiro,segundo` |
| Resultado com a direção invertida | ORDEM_GRUPOS e ALTERNATIVA não combinam | "maior" sempre significa primeiro > segundo |
| `Há identificadores repetidos dentro de um mesmo grupo` | COLUNA_PAR errada, ou o desenho não é pareado | confira a coluna do par ou deixe-a vazia |
| `Pareamento exige exatamente 2 grupos` | coluna de grupo com mais de 2 valores | filtre a tabela antes ou use outra coluna |
| `compara no máximo 2 grupos` | 3 ou mais grupos | use ANOVA (notebook completo) |
| `valores ausentes` / `variância zero` | coluna vazia ou constante | confira os dados |
| Formulário não atualiza | a célula não foi executada de novo | execute a célula e as etapas seguintes |
| Erro ao baixar os módulos | sem internet ou endereço errado | confira a conexão e execute a etapa 1 de novo |

## Checklist rápido
- [ ] Tabela no formato longo (ou convertida na etapa 2)
- [ ] COLUNA_VALOR, COLUNA_GRUPO e ORDEM_GRUPOS conferidos na mensagem "Diferença calculada como…"
- [ ] COLUNA_PAR preenchida **somente** se a mesma unidade aparece nos dois grupos
- [ ] σ marcado como conhecido **somente** se vier de fonte externa
- [ ] ALTERNATIVA definida antes de ver os resultados
- [ ] Conclusão inclui p-valor, decisão **e** estimativa com IC
