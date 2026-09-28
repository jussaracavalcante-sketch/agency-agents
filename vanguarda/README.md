# Instalação Vanguarda Martech

| Arquivo | Função |
|---|---|
| `BASE-CONHECIMENTO.md` | Contexto da agência que todos os agentes seguem |
| `agentes-vanguarda.txt` | Seleção curada de 44 agentes (edite para incluir/remover) |
| `instalar.sh` | Instala a seleção e injeta o bloco de contexto em cada agente |

## Instalar / atualizar

```bash
./vanguarda/instalar.sh                    # no projeto (.claude/agents) — já versionado
./vanguarda/instalar.sh ~/.claude/agents   # global, em uma máquina local
```

Critério da seleção: aderência ao mercado brasileiro e ao portfólio da agência. Ficaram de fora os
agentes de plataformas chinesas (Baidu, Douyin, WeChat, Weibo, Xiaohongshu etc.) e os de
áreas sem relação com marketing (engenharia, games, saúde etc.) — continuam disponíveis no
repositório e podem ser adicionados em `agentes-vanguarda.txt`.
