#!/usr/bin/env bash
# Instala os agentes da The Agency para a Vanguarda Martech em .claude/agents/
# e injeta em cada um o bloco de contexto que aponta para a base de conhecimento.
#
# Uso:  ./vanguarda/instalar.sh                     (todos os agentes, em .claude/agents)
#       ./vanguarda/instalar.sh --selecao            (só a seleção de agentes-vanguarda.txt)
#       ./vanguarda/instalar.sh [--selecao] ~/.claude/agents   (global, em uma máquina local)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SELECAO=()
if [[ "${1:-}" == "--selecao" ]]; then
  SELECAO=(--agents-file "$ROOT/vanguarda/agentes-vanguarda.txt")
  shift
fi
DEST="${1:-$ROOT/.claude/agents}"
MARK="<!-- contexto-vanguarda -->"

"$ROOT/scripts/install.sh" --tool claude-code "${SELECAO[@]}" \
  --path "$DEST" --no-interactive

read -r -d '' BLOCK <<TXT || true
$MARK
> **Contexto de atuação — Vanguarda Martech.** Você trabalha para a Vanguarda Martech (agência de
> martech, mídia paga, dados e IA — Manaus/AM, SGQ ISO 9001:2015). Antes de qualquer entrega, leia
> \`vanguarda/BASE-CONHECIMENTO.md\` e siga suas regras: português do
> Brasil, R\$ e DD/MM/AAAA; nunca inventar números; confirmar a conta do cliente antes de analisar;
> respeitar LGPD, CONAR e CDC; entregar no padrão executivo (Resumo, Diagnóstico, Riscos, Plano de
> Ação com dono e prazo, KPIs, Ressalvas).
TXT

for f in "$DEST"/*.md; do
  # remove a lista fixa de ferramentas do frontmatter: sem ela o agente herda todas as
  # ferramentas da sessão, inclusive os conectores (Google Ads, Semrush, Nekt, Notion)
  sed -i '2,/^---$/{/^tools:/d}' "$f"
  grep -q "$MARK" "$f" && continue
  # insere o bloco logo após o fechamento do frontmatter YAML (segunda linha '---')
  awk -v block="$BLOCK" 'BEGIN{n=0} {print} /^---$/ && n<2 {n++; if(n==2){print ""; print block}}' "$f" > "$f.tmp"
  mv "$f.tmp" "$f"
done

echo "[OK] $(grep -l "$MARK" "$DEST"/*.md | wc -l) agentes com contexto Vanguarda em $DEST"
