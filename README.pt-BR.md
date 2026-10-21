# Claude Code + Obsidian + Graphify: O Guia Definitivo para Economia de Tokens e Memória Persistente

> **Memória persistente entre sessões** com Obsidian Zettelkasten e contexto seletivo de código com Graphify. A economia depende da tarefa; as alegações históricas de 71,5x/sessão e 499x/consulta são autorrelatadas e não são reproduzíveis com os dados publicados.

🇺🇸 [Read in English](./README.md)

Setup completo para transformar o Claude Code em um agente com memória de longo prazo e consciência total do seu codebase — sem desperdiçar tokens relendo arquivos.

---

## Índice

1. [O Problema](#o-problema)
2. [A Solução (Visão Geral)](#a-solução-visão-geral)
3. [Parte 1 — Obsidian como Memória Persistente](#parte-1--obsidian-como-memória-persistente)
4. [Parte 2 — Pipeline de Importação de Chats](#parte-2--pipeline-de-importação-de-chats)
5. [Parte 3 — Graphify (Knowledge Graph do Codebase)](#parte-3--graphify-knowledge-graph-do-codebase)
6. [Parte 4 — Fluxo de Trabalho Completo](#parte-4--fluxo-de-trabalho-completo)
7. [Parte 5 — Hook de Auto-Save (Rede de Segurança)](#parte-5--hook-de-auto-save-rede-de-segurança)
8. [Resultados Reais](#resultados-reais)
9. [Troubleshooting](#troubleshooting)

---

## O Problema

Quando você trabalha com o Claude Code, dois problemas consomem seus tokens silenciosamente:

**Problema 1 — Amnésia entre sessões.** Toda vez que você abre uma sessão nova, precisa re-explicar o projeto: stack, decisões tomadas, bugs em andamento, o que falta fazer. O Claude Code não lembra de nada da sessão anterior.

**Problema 2 — Releitura do codebase.** Explorar o código repetidamente pode consumir tokens de contexto, mas o consumo depende da tarefa e das ferramentas de navegação. A ilustração histórica compara ~20.000 tokens de contexto de código com ~280 tokens de saída de consulta ao grafo: cerca de 71,4x menos contexto de recuperação, não uma redução medida no consumo da sessão completa. Ela pressupõe que a saída menor responde à mesma pergunta; os payloads originais e o tokenizer não foram publicados.

---

## A Solução (Visão Geral)

Dois sistemas complementares, cada um resolvendo um problema:

| Camada | Ferramenta | O que resolve | Custo |
|--------|-----------|---------------|-------|
| Memória do projeto | Obsidian Zettelkasten | Amnésia entre sessões | Gratuito |
| Mapa do código | Graphify | Releitura do codebase | Gratuito (modo AST) |
| Histórico de conversas | Pipeline de importação | Chats perdidos | Gratuito |
| Continuidade | Comandos `/retomar` e `/salvar` | Retomar de onde parou | Gratuito |

O Obsidian cuida de **o que foi decidido** (memória declarativa). O Graphify cuida de **como o código está organizado** (mapa estrutural). Juntos, eles podem ajudar o Claude Code a recuperar contexto relevante. A leitura do código continua necessária quando o grafo ou as notas estão incompletos ou desatualizados.

---

## Parte 1 — Obsidian como Memória Persistente

### Conceito

Um vault Obsidian único e centralizado funciona como o "segundo cérebro" do Claude Code. Ele armazena decisões, contexto, progresso e conhecimento de todos os seus projetos. As notas seguem o método Zettelkasten: atômicas, densamente interligadas, com metadados padronizados.

O Claude Code acessa esse vault através do `CLAUDE.md` e de skills customizados.

### Estrutura Recomendada

```
~/vault/                              # vault ÚNICO para todos os projetos
├── CLAUDE.md                         # instruções globais para o Claude Code
├── permanent/                        # notas atômicas consolidadas
├── inbox/                            # captura bruta (ideias, rascunhos)
├── fleeting/                         # rascunhos temporários
├── templates/                        # templates para novas notas
├── logs/                             # session logs globais
├── references/                       # material de referência
├── meu-projeto/                      # MOCs e notas do projeto X
│   ├── projeto/                      #   arquitetura, decisões, convenções
│   ├── pipeline/                     #   fluxos de dados, APIs
│   ├── dados/                        #   schema, modelo de dados
│   ├── features/                     #   features planejadas/implementadas
│   └── logs/                         #   session logs do projeto
├── outro-projeto/                    # MOCs e notas do projeto Y
│   └── ...
├── chats/                            # chats importados do Claude
│   ├── code/                         #   do Claude Code
│   └── web/                          #   do Claude Web/App
└── graphify/                         # knowledge graphs dos codebases
    ├── meu-projeto/                  #   notas do grafo do projeto X
    └── outro-projeto/                #   notas do grafo do projeto Y
```

> **Por que um vault único?** Ter um vault por projeto fragmenta o conhecimento. Com vault único, uma nota sobre "Supabase Auth" é linkada tanto pelo projeto A quanto pelo B. O graph view mostra conexões entre projetos que você não esperava.

> **⚠️ Mantenha código FORA do vault** O vault guarda **apenas notas**. Nunca
> coloque um repositório de código (com `node_modules/`, `.next/`, `dist/`, output de build) *dentro* de `~/vault/` —
> o Obsidian vai tentar indexar dezenas de milhares de arquivos, travar até parar, e inundar o graph com
> ruído. Mantenha cada repositório de código em seu próprio local (ex.: `~/meu-projeto/`); a pasta
> `meu-projeto/` do vault guarda apenas as **notas** daquele projeto (`projeto/`, `logs/`, `features/`, …).

### Setup Passo a Passo

**Pré-requisitos:**
- Claude Code instalado e autenticado
- Obsidian instalado (gratuito: [obsidian.md](https://obsidian.md))

**1. Criar o vault:**

Obsidian → "Create new vault" → escolha nome e local.

**2. Criar a estrutura:**

```bash
cd ~/vault  # ajuste para seu path
mkdir -p permanent inbox fleeting templates logs references
mkdir -p meu-projeto/{projeto,pipeline,dados,features,logs}
```

**3. Criar o CLAUDE.md:**

Este é o arquivo que o Claude Code lê automaticamente. Crie `CLAUDE.md` na raiz do vault:

```markdown
# Vault — Instruções para o Claude Code

## O que é este vault
Base de conhecimento centralizada para todos os projetos.
Memória persistente entre sessões.

## Stack dos projetos
- Projeto X: React + Supabase
- Projeto Y: Python + FastAPI
(adapte para seus projetos)

## Regras Zettelkasten

### Criação de notas
- Use wikilinks: [[nome-da-nota]] (não links markdown)
- Frontmatter YAML obrigatório em toda nota
- Nomes de arquivo em kebab-case: `auth-flow.md`, não `Auth Flow.md`
- 1 conceito por nota permanente (atomicidade)
- Mínimo 2 wikilinks por nota (linking denso)

### Frontmatter padrão
---
title: Nome da Nota
tags: [projeto, tema]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
type: permanent
---

### Nunca faça
- Não delete notas sem perguntar
- Não use links markdown para notas internas (use wikilinks)
- Não crie notas sem frontmatter
- Não mude a estrutura de pastas sem documentar

## Comandos de Sessão
/retomar, /salvar, /memorizar e /commit são instalados da pasta commands/
do guia em ~/.claude/commands/ (veja o passo 6). As instruções completas
ficam lá; este arquivo guarda só as regras do vault que eles seguem.
```

**4. Criar template de nota:**

```bash
cat > templates/nota-padrao.md << 'EOF'
---
title: {{title}}
tags: []
created: {{date}}
updated: {{date}}
status: draft
type: permanent
---

# {{title}}

## Contexto

## Detalhes

## Links relacionados
EOF
```

**5. Transforme os comandos de sessão em skills (recomendado):**

Os blocos `/retomar` e `/salvar` acima funcionam como instruções no `CLAUDE.md`, mas a forma mais
confiável de fazê-los disparar em *qualquer* projeto é implementá-los como **skills globais** em
`~/.claude/skills/`. O Claude Code descobre essas skills automaticamente e as invoca pelo nome — sem
precisar repetir o texto no `CLAUDE.md` de cada projeto.

Crie uma pasta por comando, cada uma contendo um `SKILL.md`:

```bash
mkdir -p ~/.claude/skills/salvar ~/.claude/skills/retomar
```

- `~/.claude/skills/salvar/SKILL.md` — no `/salvar`, escreve um session log datado em `logs/` do
  projeto e incorpora quaisquer decisões novas em `projeto/`.
- `~/.claude/skills/retomar/SKILL.md` — no `/retomar`, lê `projeto/` do projeto mais os session logs
  mais recentes e resume o estado atual e o que falta.

Cada `SKILL.md` precisa de frontmatter YAML com um `name:` que **corresponde à pasta** (`salvar` →
`/salvar`) e uma `description:` (usada para dispará-lo), seguido das instruções — reutilize os passos
do bloco Comandos de Sessão acima. Depois registre ambos no seu `~/.claude/CLAUDE.md` **global**
para que fiquem disponíveis em todos os projetos:

```markdown
# comandos de sessão
- **salvar** (`~/.claude/skills/salvar/SKILL.md`) — escreve um session log no vault. Trigger: `/salvar`
- **retomar** (`~/.claude/skills/retomar/SKILL.md`) — rehidrata o contexto do projeto. Trigger: `/retomar`
```

> **Dica:** a forma mais rápida de escrever os dois arquivos `SKILL.md` é entregar os bullets acima
> ao Claude Code e deixá-lo redigir, depois ajustar ao seu gosto.

**6. Plugins recomendados no Obsidian:**

| Plugin | Para que serve | Como instalar |
|--------|---------------|---------------|
| BRAT | Instalar plugins beta | Community Plugins → Browse |
| 3D Graph | Visualização 3D do vault | Via BRAT (v2.4.1) |
| Folders to Graph | Pastas como nós no graph | Community Plugins → Browse |
| Calendar | Navegação por daily notes | Community Plugins → Browse |

**6. Instalar os comandos de sessão:**

A pasta [commands/](./commands/) traz `/save`, `/resume`, `/memorize` e `/commit` como arquivos de comando prontos (em inglês). Para usar os nomes em português, copie com rename seguindo o mapeamento `save` → `salvar`, `resume` → `retomar`, `memorize` → `memorizar` (o `commit` mantém o nome) e reinicie o Claude Code:

```bash
cp commands/save.md ~/.claude/commands/salvar.md
cp commands/resume.md ~/.claude/commands/retomar.md
cp commands/memorize.md ~/.claude/commands/memorizar.md
cp commands/commit.md ~/.claude/commands/commit.md
# /memorizar e /commit leem o save.md em tempo de execução: aponte para o novo nome
perl -pi -e 's|commands/save\.md|commands/salvar.md|g' ~/.claude/commands/memorizar.md ~/.claude/commands/commit.md
export VAULT_DIR=~/vault  # opcional; ~/vault é o padrão
```

Os arquivos usam os nomes de pasta da versão em inglês (`architecture/decisions.md`, `data/`). Se o seu vault segue a estrutura deste guia (`projeto/decisoes.md`, `dados/`), troque esses caminhos no `salvar.md` e no `retomar.md`. Veja [commands/README.md](./commands/README.md) para o que cada comando faz.

Como alternativa, empacote as mesmas instruções como skills globais (`~/.claude/skills/<nome>/SKILL.md`, uma pasta por comando). Skills também viram slash commands e podem levar arquivos de referência extras, mas os arquivos de comando são mais simples de manter em sincronia com este repo.

---

## Parte 2 — Pipeline de Importação de Chats

### Conceito

Seus chats com o Claude (tanto no Code quanto no Web) contêm decisões, insights e contexto valioso que se perdem no histórico. Este pipeline exporta, processa e importa essas conversas como notas no vault — com frontmatter, tags automáticas e wikilinks para notas existentes.

### Componentes

```
~/scripts/
├── claude_to_obsidian.py          # processador (frontmatter, tags, wikilinks)
└── sync_claude_obsidian.sh        # automação (export + process)

~/claude-exports/                   # staging area temporária (fora do vault)
├── code/                           # exports do Claude Code
└── web/                            # exports do Claude Web
```

### Setup

**1. Instalar o extractor do Claude Code:**

```bash
pip install claude-conversation-extractor
```

**2. Criar diretórios de staging:**

```bash
mkdir -p ~/claude-exports/code ~/claude-exports/web
```

**3. Criar o script de pós-processamento (`~/scripts/claude_to_obsidian.py`):**

O script deve:
- Ler cada `.md` exportado
- Detectar origem (Code vs Web)
- Gerar tags automáticas baseadas em keywords do conteúdo
- Adicionar frontmatter YAML padronizado
- Inserir `[[wikilinks]]` para notas que já existem no vault
- Copiar para `chats/code/` ou `chats/web/` dentro do vault

Exemplo de mapeamento de keywords para tags:

```python
KEYWORD_TAG_MAP = {
    "python": "python",
    "react": "react",
    "supabase": "supabase",
    "deploy": "deploy",
    "bug": "debugging",
    "refactor": "refactoring",
    # adicione os seus
}
```

**4. Criar o script de automação (`~/scripts/sync_claude_obsidian.sh`):**

```bash
#!/bin/bash
EXPORT_DIR="$HOME/claude-exports"
VAULT_DIR="$HOME/vault"  # ajuste para seu path
SCRIPT_DIR="$HOME/scripts"
LOG="$SCRIPT_DIR/sync.log"

echo "[$(date)] Sync iniciado" >> "$LOG"

# Exporta chats do Claude Code
claude-extract --all --output "$EXPORT_DIR/code" 2>> "$LOG"

# Processa e envia pro vault
python3 "$SCRIPT_DIR/claude_to_obsidian.py" \
    --export-dir "$EXPORT_DIR" \
    --vault-dir "$VAULT_DIR" \
    --move 2>> "$LOG"

echo "[$(date)] Sync concluído" >> "$LOG"
```

**5. Agendar execução automática:**

```bash
chmod +x ~/scripts/sync_claude_obsidian.sh

# Roda todo dia às 22h
(crontab -l 2>/dev/null; echo "0 22 * * * $HOME/scripts/sync_claude_obsidian.sh") | crontab -
```

**6. Para chats do Claude Web:**

Instale a extensão **"Export Claude Chat to Markdown"** no Chrome/Edge. Faça bulk export periódico, salve os `.md` em `~/claude-exports/web/` e o cron cuida do resto.

**7. Adicionar seção ao CLAUDE.md do vault:**

```markdown
## Pipeline de Importação de Chats

### Estrutura
- `chats/code/` → conversas importadas do Claude Code
- `chats/web/` → conversas importadas do Claude Web/App
- Todos os chats recebem frontmatter com `type: chat` e tag `chat-import`

### Filtrar no Graph View
- `tag:chat-import` → só chats
- `-path:chats` → esconder chats
```

---

## Parte 3 — Graphify (Knowledge Graph do Codebase)

### Conceito

[Graphify](https://github.com/safishamsi/graphify) transforma seu codebase em um knowledge graph consultável. Em vez do Claude Code reler cada arquivo, ele consulta o grafo — que é persistente entre sessões e pesa uma fração dos tokens.

- **Código:** processado 100% localmente via tree-sitter AST. Nenhum conteúdo sai da sua máquina.
- **Cache:** SHA256 — re-runs só processam arquivos modificados.
- **Custo:** 0 tokens no modo padrão (AST puro). Modo `--deep` usa LLM para edges semânticas.
- **Linguagens:** Python, JavaScript, TypeScript, Go, Rust, Java, C, C++, Ruby, C#, Kotlin, Scala, PHP, Swift, Lua, Zig e mais (20 linguagens via tree-sitter).

### Setup

**1. Instalar:**

```bash
pip install graphifyy
graphify install --platform claude
```

O `graphify install --platform claude` cria o skill em `~/.claude/skills/graphify/SKILL.md`. Outras plataformas também são suportadas (`cursor`, `codex`, `opencode`, etc.).

**1.5. Configurar API key (necessário para extração semântica):**

O Graphify precisa de uma API key de LLM da Anthropic ou da Moonshot (Kimi) para extração semântica. Exporte uma antes de rodar:

```bash
export ANTHROPIC_API_KEY="sua-chave-aqui"
# ou
export MOONSHOT_API_KEY="sua-chave-aqui"
```

Se quiser pular custos de LLM completamente, use o modo AST-only:

```bash
graphify extract . --out ./graphify-out --no-cluster
```

Isso gera um grafo estrutural sem edges semânticas.

**2. Gerar o grafo:**

O Graphify tem dois caminhos de execução e as flags `--obsidian*` originais só funcionam em um deles. Escolha o formato que corresponde a como você está invocando:

**A. Dentro do Claude Code (skill — recomendado para este guia):**

```
/graphify . --obsidian --obsidian-dir ~/vault/graphify/nome-do-projeto
```

Isso roda o slash command `/graphify`, que o skill em `~/.claude/skills/graphify/SKILL.md` interpreta. O skill chama `graphify.export.to_obsidian()` em Python diretamente, então `--obsidian` e `--obsidian-dir` são reconhecidas aqui — elas não fazem parte do parser do shell headless.

**B. Do terminal / CI (CLI headless):**

```bash
graphify extract . --out ./graphify-out
```

O CLI headless usa subcomandos (`extract`, `update`, `watch`, `tree`) e **não** expõe `--obsidian` / `--obsidian-dir` / `--wiki` / `--mode deep`. Se quiser integração com Obsidian a partir do terminal, faça um symlink do diretório de output para o vault depois da extração:

```bash
ln -s $(pwd)/graphify-out ~/vault/graphify/nome-do-projeto/graphify-out
```

Output gerado (varia conforme o caminho e as flags):

```
seu-projeto/
└── graphify-out/
    ├── graph.json          # grafo consultável (sempre)
    ├── graph.html          # viz interativa (skill auto-gera; headless: ver passo 3)
    ├── GRAPH_REPORT.md     # god nodes, conexões, métricas (sempre)
    ├── wiki/               # artigos estilo Wikipedia (só skill com --wiki)
    └── cache/              # cache SHA256

~/vault/graphify/nome-do-projeto/    # só quando o skill recebeu --obsidian
    └── (notas Obsidian)              # uma nota por função/módulo
```

**3. Gerar visualização interativa (só no caminho headless):**

O skill auto-gera `graph.html` durante a extração. Para o caminho headless, rode a visualização como passo separado:

```bash
graphify tree --graph ./graphify-out/graph.json --output ./graphify-out/GRAPH_TREE.html
```

Abra o arquivo HTML no navegador para explorar o grafo interativamente.

**4. Atualizar .gitignore:**

```gitignore
# Graphify
graphify-out/cache/
```

Mantenha `graph.json` e `GRAPH_REPORT.md` versionados — são úteis para o time.

**5. Adicionar ao CLAUDE.md do projeto:**

Adicione ao final do CLAUDE.md na raiz do repositório:

```markdown
## Context Navigation (Graphify)

### Regra de consulta em 3 camadas
1. **Primeiro:** consulte `graphify-out/graph.json` ou `graphify-out/wiki/index.md`
   para entender a estrutura e conexões do código
2. **Segundo:** consulte o vault Obsidian para contexto de decisões e progresso
3. **Terceiro:** só leia arquivos de código brutos quando for editar
   ou quando as camadas anteriores não tiverem a resposta

### Quando reconstruir o grafo
- Após mudanças estruturais (novos módulos, refactors)
- Headless: `graphify update .` (só processa arquivos modificados)
- Skill: `/graphify . --update` (mesmo comportamento, rodando via skill — também aceita `--obsidian` para atualizar o vault)
- O grafo é persistente — NÃO precisa reconstruir a cada sessão

### O que NÃO fazer
- Não modifique arquivos dentro de `graphify-out/` manualmente
- Não releia o codebase inteiro se o grafo já tem a informação
```

**6. Adicionar ao CLAUDE.md do vault:**

```markdown
## Graphify (Mapas de Codebase)

### Estrutura
- `graphify/projeto-x/` → knowledge graph do projeto X
- Futuros projetos terão subpastas próprias
- Notas geradas automaticamente — NÃO editar manualmente

### No Graph View
- Filtrar por `path:graphify` para ver só nós de código
- Filtrar por `-path:graphify` para esconder nós de código
```

**7. Git Hook (opcional):**

Reconstrói o grafo automaticamente a cada commit:

```bash
graphify hook install
```

**8. Watch Mode (opcional):**

Rebuild automático ao salvar arquivos. Escolha o formato conforme como você invoca o graphify.

Headless (terminal separado):

```bash
graphify watch .
```

Skill (dentro do Claude Code):

```
/graphify . --watch
```

### Comandos Úteis

A tabela abaixo lista os subcomandos do **CLI headless** que você rodaria no terminal. Dentro do Claude Code, as mesmas operações estão disponíveis via o slash command `/graphify` documentado em `~/.claude/skills/graphify/SKILL.md` — esse formato aceita adicionalmente `--obsidian`, `--obsidian-dir`, `--wiki` e `--mode deep` (que o parser headless não expõe).

| Comando | Descrição |
|---------|-----------|
| `graphify extract .` | Extração completa no diretório atual |
| `graphify extract ./src` | Escanear pasta específica |
| `graphify update .` | Só processa arquivos modificados |
| `graphify watch .` | Auto-rebuild ao salvar |
| `graphify query "pergunta"` | Consultar o grafo diretamente |
| `graphify explain "NomeDoNo"` | Explicação em linguagem natural de um nó |
| `graphify path "A" "B"` | Caminho mais curto entre dois nós |
| `graphify tree --graph ./graphify-out/graph.json --output ./graphify-out/GRAPH_TREE.html` | Gerar visualização interativa |
| `open graphify-out/graph.html` | Abrir visualização interativa (skill gera) ou `GRAPH_TREE.html` (headless) |

### Adicionando Novos Projetos

Com vault centralizado, cada projeto é uma subpasta. Mesmos dois caminhos do setup inicial.

Skill (dentro do Claude Code):

```
/graphify ~/outro-projeto --obsidian --obsidian-dir ~/vault/graphify/outro-projeto
```

Headless (terminal):

```bash
cd ~/outro-projeto
graphify extract . --out ./graphify-out
ln -s $(pwd)/graphify-out ~/vault/graphify/outro-projeto/graphify-out
```

Pule a linha do `ln -s` se você não precisa que o Obsidian enxergue o grafo. As notas aparecem no graph view do Obsidian junto com tudo o mais.

---

## Parte 4 — Fluxo de Trabalho Completo

### Sessão típica

```
Abrir sessão no Claude Code
    │
    ├── /retomar                     ← carrega contexto do vault
    │                                   (últimos logs, decisões, progresso)
    │
    ├── Claude consulta graph.json    ← entende a estrutura do código
    │                                   sem reler todos os arquivos
    │
    ├── Trabalha no código            ← features, bugs, refactors
    │
    ├── /memorizar (opcional)        ← gatilho explícito no meio da
    │                                   sessão: fixa decisão ou insight já
    │
    ├── /salvar                      ← session log + consolidação de memória
    │                                   (decisões, insights, fatos)
    │
    └── /commit                      ← commit + push, depois roda o /salvar
                                        (hook post-commit reconstrói o grafo)
```

### O que o /salvar memoriza

Depois de escrever o session log, o `/salvar` roda uma fase de consolidação. Ele grava só conhecimento durável; na dúvida, não grava nada, porque o log já preserva o contexto.

| Entra na memória | Fica de fora |
|------------------|--------------|
| Decisão técnica ou arquitetural com justificativa (houve alternativas consideradas) | Progresso, tarefas concluídas, pendências (já estão no log) |
| Insight reutilizável: padrão, armadilha, causa raiz de bug não óbvia, comportamento de ferramenta | Investigações sem conclusão |
| Convenção do projeto criada ou alterada | Detalhes de implementação que não generalizam |
| Fato durável do projeto: schema, estrutura, pipeline, path, bug conhecido com causa | Item já memorizado sem nenhuma mudança |
| Correção de algo memorizado que se mostrou errado | |

**Deduplicação:** antes de gravar, cada candidato passa por grep em `<vault>/permanent/`, na pasta do projeto e no `CLAUDE.md` do projeto. Se já existe nota equivalente, ela é atualizada (conteúdo e campo `updated`), nunca duplicada.

**Destinos:**

- Decisão → anexada a `<vault>/<projeto>/projeto/decisoes.md`
- Insight reutilizável → nota nova em `<vault>/permanent/`, mais um ponteiro de uma linha em `## Permanent facts` do `<vault>/<projeto>/CLAUDE.md`
- Fato do projeto → a nota correspondente em `dados/`, `projeto/`, `features/` ou `pipeline/`, ou uma linha em `## Permanent facts`
- Convenção → proposta para `## Conventions` no `CLAUDE.md` do projeto, gravada só depois que você confirmar (y/n)

O `<vault>/<projeto>/CLAUDE.md` só é criado quando a primeira linha é gravada nele, e arquiva as seções mais antigas em `projeto/claude-archive.md` ao passar de 300 linhas.

**Formato do relatório:**

```
Session log: <vault>/<projeto>/logs/2026-10-21-descricao-curta.md
Memory:
- created: <vault>/permanent/algum-insight.md (motivo em uma linha)
- updated: <vault>/<projeto>/projeto/decisoes.md (motivo em uma linha)
```

Quando nada se qualifica, a segunda linha é `Memory: nothing to consolidate this session`.

### Economia por camada

| Camada | Sem ela | Com ela |
|--------|---------|---------|
| `/retomar` | Re-explicar projeto a cada sessão | Claude já sabe o contexto |
| Graphify | Ilustração histórica: ~40 arquivos (~20k tokens) | Saída seletiva de consulta (~280 tokens); estimativa de payload não verificada, não consumo da sessão |
| Pipeline de chats | Insights perdidos no histórico | Tudo indexado e buscável |
| `/salvar` + logs | Esquecer o que foi feito | Histórico com wikilinks |

### Filtros no Graph View

| Filtro | O que mostra |
|--------|-------------|
| `path:permanent` | Só notas permanentes (conhecimento consolidado) |
| `path:graphify` | Só nós do codebase (funções, módulos, imports) |
| `tag:chat-import` | Só chats importados |
| `-path:graphify -path:chats` | Só notas manuais (vault "puro") |

---

## Parte 5 — Hook de Auto-Save (Rede de Segurança)

### Conceito

O comando `/salvar` gera session logs ricos, mas depende de você lembrar de rodá-lo. Esqueceu uma vez e a sessão evapora. Este hook resolve isso: o Claude Code dispara um evento `SessionEnd` quando uma sessão fecha (exit, `/clear`, logout), e um pequeno script Python extrai mecanicamente os fatos da sessão a partir do transcript e escreve um log mínimo no seu vault.

Princípios de design (inspirado no [ai-memory](https://github.com/akitaonrails/ai-memory)):

- **Zero chamadas de LLM.** Parsing puro de JSONL. Roda em milissegundos, não precisa de API key.
- **Rede de segurança, não substituto.** O `/salvar` continua sendo o log rico (decisões, pendências, wikilinks). O auto-log garante que sessões esquecidas ainda deixem rastro: objetivo (primeiro prompt), arquivos tocados, comandos executados, estatísticas.
- **Sem consolidação de memória.** O hook é mecânico e nunca roda a fase de consolidação do `/salvar`; só o `/salvar` atualiza decisões, notas permanentes e fatos do projeto.
- **Falha silenciosa.** Um hook nunca pode quebrar sua sessão. Erros vão para `~/scripts/autosave.log` e o Claude Code nem percebe.
- **Filtro de ruído.** Sessões com menos de 2 mensagens do usuário são ignoradas.

### Setup

**1. Copie o script:**

O script vive neste repo em [scripts/session_autosave.py](./scripts/session_autosave.py).

```bash
mkdir -p ~/scripts
cp scripts/session_autosave.py ~/scripts/
chmod +x ~/scripts/session_autosave.py
```

**2. Registre o hook no `~/.claude/settings.json`:**

Se o arquivo já existir, faça merge da chave `hooks` sem remover nada:

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "VAULT_DIR=$HOME/vault python3 $HOME/scripts/session_autosave.py"
          }
        ]
      }
    ]
  }
}
```

Ajuste o `VAULT_DIR` para o caminho do seu vault.

**3. Teste:**

Abra uma sessão do Claude Code em qualquer projeto, troque 2-3 mensagens com uma edição de arquivo e saia. Verifique:

```bash
tail -5 ~/scripts/autosave.log
# deve mostrar: OK: wrote /caminho/do/vault/.../logs/YYYY-MM-DD-HHMM-auto-session.md
```

### Como funciona o roteamento

O script deriva o nome do projeto do diretório de trabalho da sessão (basename do `cwd`):

- Se `<vault>/<projeto>/` existir → o log vai para `<vault>/<projeto>/logs/`
- Caso contrário → cai no fallback `<vault>/logs/`

Se o nome da pasta do repo for diferente do nome da pasta no vault (ex.: repo `my-app-monorepo`, pasta do vault `my-app`), crie um symlink:

```bash
ln -s ~/vault/my-app ~/vault/my-app-monorepo
```

### Filtrando auto-logs no Obsidian

Auto-logs recebem a tag `auto-log` e o frontmatter `status: imported`:

| Filtro | O que mostra |
|--------|-------------|
| `tag:auto-log` | Só session logs gerados automaticamente |
| `-tag:auto-log` | Esconde auto-logs (só notas manuais) |

### Fluxo de trabalho atualizado

```
Abrir sessão no Claude Code
    │
    ├── /retomar                     ← carrega contexto do vault
    ├── Trabalha no código
    ├── /salvar (opcional)           ← log rico com decisões
    └── exit                         ← hook SessionEnd dispara
                                        auto-log escrito mesmo se
                                        você esqueceu o /salvar
```

---

## Resultados Reais

Exemplo autorrelatado de um projeto React + Supabase com 126 arquivos TypeScript. O snapshot do código, grafo, prompts, tokenizer e logs de consumo não foram publicados; portanto, as contagens de inventário e a razão de tokens não podem ser reproduzidas atualmente:

| Métrica | Valor |
|---------|-------|
| Nós no grafo | 332 |
| Edges (conexões) | 258 |
| Comunidades detectadas | 124 |
| Tamanho do graph.json | 172 KB |
| Notas Obsidian geradas | 456 |
| Redução histórica de tokens por consulta | **499x, autorrelatada; contagens da baseline e da consulta indisponíveis** |
| Consumo LLM relatado na geração do grafo | **0 tokens** (modo AST); exclui leituras do agente, consultas e consumo da sessão |
| Chats importados no vault | 137 |
| Notas permanentes acumuladas | 65+ |
| Total de notas no vault | 780+ |

### Evidências e benchmark

A chamada histórica de **71,5x por sessão** não tem um registro publicado de consumo de sessões. A ilustração ~20.000 / ~280 resulta em **~71,4x para contexto de recuperação** (cerca de 98,6% menos), enquanto **499x por consulta** é outra comparação sem protocolo documentado. Nenhuma delas demonstra economia da sessão completa ou economia financeira.

A Hlido informa **82/100** na avaliação do repositório; as evidências públicas acessíveis não validam essas razões de tokens. Veja a [issue #12](https://github.com/lucasrosati/claude-code-memory-setup/issues/12) e a [auditoria de evidências e o protocolo de benchmark, em inglês](./benchmarks/README.md) para origem, divergências de datas, pressupostos e limitações.

O protocolo define entradas fixas, execuções pareadas com navegação de código e memória, critérios de correção, contabilização de cache, custos de construção do grafo e medições separadas por consulta e sessão. Inclui um [sumarizador offline de consumo](./benchmarks/summarize.py). O exemplo sintético verifica apenas a aritmética; não são apresentados novos resultados de desempenho nem execuções pagas.

---

## Arquitetura Final

```
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (único)                    │
│                                                             │
│  permanent/  ← conhecimento consolidado (Zettelkasten)      │
│  logs/       ← session logs (/salvar)                       │
│  chats/      ← conversas importadas (pipeline cron)         │
│  graphify/   ← knowledge graphs dos codebases               │
│  projeto-x/  ← MOCs, decisões, arquitetura                  │
│                                                             │
│  CLAUDE.md   ← instruções globais pro Claude Code           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                    Claude Code lê/escreve
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                   REPOSITÓRIO DO PROJETO                     │
│                                                             │
│  src/            ← código-fonte                             │
│  CLAUDE.md       ← instruções + Context Navigation          │
│  graphify-out/   ← graph.json, graph.html, report           │
│  .git/hooks/     ← post-commit reconstrói o grafo           │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

**Notas do Graphify não aparecem no Obsidian:**
Confirme que as notas estão dentro do diretório real do vault. O Obsidian nem sempre aponta para onde você acha — crie uma nota pelo Obsidian e rode `find ~ -name "nome.md"` para descobrir o path real. Depois mova as notas para lá e faça Cmd+Q / reabra.

**Graph view vazio com filtro aplicado:**
Desative "Orphans" e "Existing files only" nos filtros do graph. Faça Cmd+Q e reabra o Obsidian para forçar reindexação.

**Claude Code não consulta o grafo:**
Verifique se o CLAUDE.md do projeto tem a seção "Context Navigation" e se `graphify-out/graph.json` existe na raiz do repo.

**Cron não roda (macOS):**
Dê permissão de Full Disk Access ao terminal em Preferências do Sistema → Privacidade e Segurança.

**Graphify não gera wiki:**
A pasta `wiki/` só é produzida pelo **formato skill com `--wiki`** (`/graphify . --wiki` dentro do Claude Code). O subcomando headless `graphify extract` não expõe `--wiki`. Do terminal, use `graphify query "pergunta"` contra o `graph.json`, ou rode o formato skill se precisar dos artigos estilo Wikipedia.

**Arquivos com parênteses no nome:**
O Graphify gera notas como `minhaFuncao().md`. O Obsidian pode ter dificuldades de indexação com `()` nos nomes. Se necessário, renomeie em batch:
```bash
cd ~/vault/graphify/projeto
for f in *"("*; do mv "$f" "$(echo "$f" | sed 's/[()]//g')"; done
```
**Erro "Unknown Command" no graphify:**
Se `graphify .` der erro `unknown command '.'`, você está rodando o **CLI headless** — que exige um subcomando (`extract`, `update`, `watch`, etc.) antes do caminho. Use o formato headless:
```bash
graphify extract . --out ./graphify-out
# ou, para atualizar um grafo existente:
graphify update .
```
Ou, dentro do Claude Code, use o **formato skill** com a barra inicial — que passa pelo skill `/graphify` em vez do parser do shell e suporta o conjunto completo de flags (`--obsidian`, `--obsidian-dir`, `--wiki`, `--mode deep`, etc.):
```
/graphify . --obsidian --obsidian-dir ~/vault/graphify/nome-do-projeto
```

**Erro Unknown Command no graphify:**
Se `graphify .` falha com `unknown command '.'`, você está rodando a **CLI headless** — que exige um subcomando (`extract`, `update`, `watch`, etc.) antes do path. Use o formato headless:
```bash
graphify extract . --out ./graphify-out
# or, to refresh an existing graph:
graphify update .
```
Ou, dentro do Claude Code, use o **formato skill** com a barra inicial — que passa pela skill `/graphify` em vez do parser do shell e suporta o conjunto completo de flags (`--obsidian`, `--obsidian-dir`, `--wiki`, `--mode deep`, etc.):
```
/graphify . --obsidian --obsidian-dir ~/vault/graphify/project-name
```

**O /salvar memorizou algo irrelevante:**
A fase de consolidação segue os critérios da etapa 2.1 do `~/.claude/commands/salvar.md`. Aperte esses critérios: remova o que você não quer ou acrescente o caso à lista "Not candidates". Depois apague ou edite a nota gravada.

**Notas duplicadas em permanent/:**
Confira a etapa 2.2 do `~/.claude/commands/salvar.md`: o grep precisa rodar antes de qualquer gravação e cobrir `<vault>/permanent/`. Se suas notas usam termos diferentes para o mesmo conceito, acrescente aliases no frontmatter ou tags para o grep encontrá-las e junte as duplicatas à mão.

---

## Créditos e Links

- [Graphify](https://github.com/safishamsi/graphify) — knowledge graph para codebases (MIT)
- [Obsidian](https://obsidian.md) — PKM e second brain (gratuito)
- [Claude Code](https://docs.anthropic.com) — coding agent da Anthropic
- Inspirado no sistema de Andrej Karpathy e na comunidade r/ClaudeAI

---

**Se este guia te ajudou, dê uma ⭐ no repo e compartilhe com outros devs que usam Claude Code.**
