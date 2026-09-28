# Instalação Vanguarda Martech

| Arquivo | Função |
|---|---|
| `BASE-CONHECIMENTO.md` | Contexto da agência que todos os agentes seguem |
| `agentes-vanguarda.txt` | Núcleo de marketing: 44 agentes prioritários (usado com `--selecao`) |
| `instalar.sh` | Instala os agentes, injeta o bloco de contexto e libera os conectores |

## Instalar / atualizar

```bash
./vanguarda/instalar.sh                              # todos os 279 agentes (.claude/agents) — já versionado
./vanguarda/instalar.sh --selecao                    # só o núcleo de marketing (44)
./vanguarda/instalar.sh ~/.claude/agents             # global, em uma máquina local
```

Hoje estão instalados **todos os 279 agentes**. Todos recebem o bloco de contexto Vanguarda e
herdam as ferramentas da sessão (conectores Google Ads, Semrush, Nekt, Notion etc.).

O núcleo de marketing (`agentes-vanguarda.txt`) exclui os agentes de plataformas chinesas e os de
áreas sem relação direta com marketing; use `--selecao` para instalar apenas esse núcleo.