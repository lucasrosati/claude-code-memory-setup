# Claude Code + Obsidian + Graphify: O Guia Definitivo para Economia de Tokens e Memória Persistente

> **71.5x menos tokens por sessão** com Graphify + **memória permanente entre sessões** com Obsidian Zettelkasten.

Setup completo para transformar o Claude Code em um agente com memória de longo prazo e consciência total do seu codebase — sem desperdiçar tokens relendo arquivos.

---

## Índice

1. [O Problema](#o-problema)
2. [A Solução (Visão Geral)](#a-solução-visão-geral)
3. [Parte 1 — Obsidian como Memória Persistente](#parte-1--obsidian-como-memória-persistente)
4. [Parte 2 — Pipeline de Importação de Chats](#parte-2--pipeline-de-importação-de-chats)
5. [Parte 3 — Graphify (Knowledge Graph do Codebase)](#parte-3--graphify-knowledge-graph-do-codebase)
6. [Parte 4 — Fluxo de Trabalho Completo](#parte-4--fluxo-de-trabalho-completo)
7. [Resultados Reais](#resultados-reais)
8. [Troubleshooting](#troubleshooting)

---

## O Problema

Quando você trabalha com o Claude Code, dois problemas consomem seus tokens silenciosamente:

**Problema 1 — Amnésia entre sessões.** Toda vez que você abre uma sessão nova, precisa re-explicar o projeto: stack, decisões tomadas, bugs em andamento, o que falta fazer. O Claude Code não lembra de nada da sessão anterior.

**Problema 2 — Releitura do codebase.** O Claude Code relê todos os seus arquivos de código a cada sessão para entender a estrutura. Um projeto com ~40 arquivos consome ~20.000 tokens só para o Claude se orientar — antes de você fazer a primeira pergunta. Se você faz 10 sessões por dia, são **200.000 tokens desperdiçados**.

---

## A Solução (Visão Geral)

Dois sistemas complementares, cada um resolvendo um problema:

| Camada | Ferramenta | O que resolve | Custo |
|--------|-----------|---------------|-------|
| Memória do projeto | Obsidian Zettelkasten | Amnésia entre sessões | Gratuito |
| Mapa do código | Graphify | Releitura do codebase | Gratuito (modo AST) |
| Histórico de conversas | Pipeline de importação | Chats perdidos | Gratuito |
| Continuidade | Comandos `/retomar` e `/salvar` | Retomar de onde parou | Gratuito |

O Obsidian cuida de **o que foi decidido** (memória declarativa). O Graphify cuida de **como o código está organizado** (mapa estrutural). Juntos, o Claude Code começa cada sessão sabendo tudo — sem reler nada.

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

### /retomar
Ao receber este comando:
1. Leia os 3 últimos session logs em logs/
2. Leia projeto/decisoes.md do projeto atual
3. Resuma o estado atual e o que falta fazer

### /salvar
Ao receber este comando:
1. Crie session log em logs/YYYY-MM-DD-descricao.md
2. Registre: o que foi feito, decisões tomadas, pendências
3. Adicione wikilinks para notas criadas/alteradas
4. Faça git commit + push se em repositório
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

**5. Plugins recomendados no Obsidian:**

| Plugin | Para que serve | Como instalar |
|--------|---------------|---------------|
| BRAT | Instalar plugins beta | Community Plugins → Browse |
| 3D Graph | Visualização 3D do vault | Via BRAT (v2.4.1) |
| Folders to Graph | Pastas como nós no graph | Community Plugins → Browse |
| Calendar | Navegação por daily notes | Community Plugins → Browse |

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
graphify install
```

O `graphify install` cria o skill em `~/.claude/skills/graphify/SKILL.md`.

**2. Gerar o grafo:**

Na raiz do seu projeto:

```bash
# Pipeline completa + notas Obsidian no vault centralizado
graphify . --obsidian --obsidian-dir ~/vault/graphify/nome-do-projeto
```

Output gerado:

```
seu-projeto/
└── graphify-out/
    ├── graph.json          # grafo consultável (o Claude Code usa este)
    ├── graph.html          # visualização interativa (abra no browser)
    ├── GRAPH_REPORT.md     # god nodes, conexões, métricas
    ├── wiki/               # artigos estilo Wikipedia (navegação do agente)
    └── cache/              # cache SHA256

~/vault/graphify/nome-do-projeto/
    └── (notas Obsidian)    # cada função/módulo como um nó no graph view
```

**3. Atualizar .gitignore:**

```gitignore
# Graphify
graphify-out/cache/
```

Mantenha `graph.json` e `GRAPH_REPORT.md` versionados.

**4. Adicionar ao CLAUDE.md do projeto:**

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
- Comando: `graphify . --update` (só processa arquivos modificados)
- O grafo é persistente — NÃO precisa reconstruir a cada sessão

### O que NÃO fazer
- Não modifique arquivos dentro de `graphify-out/` manualmente
- Não releia o codebase inteiro se o grafo já tem a informação
```

**5. Adicionar ao CLAUDE.md do vault:**

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

**6. Git Hook (opcional):**

Reconstrói o grafo automaticamente a cada commit:

```bash
graphify hook install
```

**7. Watch Mode (opcional):**

Rebuild automático ao salvar arquivos (rode em terminal separado):

```bash
graphify . --watch
```

### Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `graphify .` | Pipeline completa no diretório atual |
| `graphify ./src` | Escanear pasta específica |
| `graphify . --update` | Só processa arquivos modificados |
| `graphify . --mode deep` | Extração semântica (usa LLM, consome tokens) |
| `graphify . --watch` | Auto-rebuild ao salvar |
| `graphify query "pergunta"` | Consultar o grafo diretamente |
| `open graphify-out/graph.html` | Abrir visualização interativa |

### Adicionando Novos Projetos

Com vault centralizado, cada projeto é uma subpasta:

```bash
cd ~/outro-projeto
graphify . --obsidian --obsidian-dir ~/vault/graphify/outro-projeto
```

As notas aparecem automaticamente no graph view do Obsidian.

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
    ├── /salvar                      ← gera session log no vault
    │
    └── git commit                   ← hook reconstrói o grafo
```

### Economia por camada

| Camada | Sem ela | Com ela |
|--------|---------|---------|
| `/retomar` | Re-explicar projeto a cada sessão | Claude já sabe o contexto |
| Graphify | Reler ~40 arquivos (~20k tokens) | Consultar 1 grafo (~280 tokens) |
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

## Resultados Reais

Testado em um projeto React + Supabase com 126 arquivos TypeScript:

| Métrica | Valor |
|---------|-------|
| Nós no grafo | 332 |
| Edges (conexões) | 258 |
| Comunidades detectadas | 124 |
| Tamanho do graph.json | 172 KB |
| Notas Obsidian geradas | 456 |
| Redução de tokens por query | **499x** |
| Custo LLM da geração | **0 tokens** (modo AST) |
| Chats importados no vault | 137 |
| Notas permanentes acumuladas | 65+ |
| Total de notas no vault | 780+ |

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
A wiki requer edges semânticas. No modo AST-only, use `graphify query "pergunta"` ou rode `--mode deep` (consome tokens da API).

**Arquivos com parênteses no nome:**
O Graphify gera notas como `minhaFuncao().md`. O Obsidian pode ter dificuldades de indexação com `()` nos nomes. Se necessário, renomeie em batch:
```bash
cd ~/vault/graphify/projeto
for f in *"("*; do mv "$f" "$(echo "$f" | sed 's/[()]//g')"; done
```

---

## Créditos e Links

- [Graphify](https://github.com/safishamsi/graphify) — knowledge graph para codebases (MIT)
- [Obsidian](https://obsidian.md) — PKM e second brain (gratuito)
- [Claude Code](https://docs.anthropic.com) — coding agent da Anthropic
- Inspirado no sistema de Andrej Karpathy e na comunidade r/ClaudeAI

---

**Se este guia te ajudou, dê uma ⭐ no repo e compartilhe com outros devs que usam Claude Code.**
