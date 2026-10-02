#!/usr/bin/env python3
"""
Gera os dados estáticos do portal a partir da fonte (marketing-operations/), sem digitação manual:
  - lib/agentes.json : os agentes (papel, objetivo, ferramentas) e as tarefas que cada um executa, em ordem
  - clientes.sql     : carga de portal_clientes a partir de knowledge/INDEX.md
Rode de novo sempre que agents.yaml, tasks.yaml, crew.py ou o INDEX.md mudarem:  python3 scripts/gerar_dados.py
"""
import json, re, sys
from pathlib import Path
import yaml

RAIZ = Path(__file__).resolve().parents[2] / "marketing-operations"
SAIDA = Path(__file__).resolve().parents[1]

agentes = yaml.safe_load((RAIZ / "src/marketing_ops/config/agents.yaml").read_text(encoding="utf-8"))
tarefas = yaml.safe_load((RAIZ / "src/marketing_ops/config/tasks.yaml").read_text(encoding="utf-8"))
crew = (RAIZ / "src/marketing_ops/crew.py").read_text(encoding="utf-8")

limpo = lambda s: re.sub(r"\s+", " ", (s or "")).strip()

# ferramentas por agente, lidas do crew.py
nomes_ferramentas = {
    "brand_book": "Guia de marca do cliente", "search": "Pesquisa web (Serper)", "scrape": "Leitura de sites",
    "read_file": "Leitura de arquivos", "seo_tool": "Palavras-chave (SEO)", "crm_tool": "CRM (leitura)",
    "paid_media_tool": "Mídia paga (leitura)", "analytics_tool": "Analytics (leitura)", "publish_tool": "Publicação (desligada)",
}
ferramentas = {}
for m in re.finditer(r'def (\w+)\(self\) -> Agent:(.*?)(?=\n    @agent|\n    # ──|\Z)', crew, re.S):
    chave, corpo = m.group(1), m.group(2)
    t = re.search(r"tools=(?:_tools\()?\[?([^\]\)]*)", corpo)
    itens = [x.strip() for x in (t.group(1).split(",") if t else []) if x.strip()]
    ferramentas[chave] = [nomes_ferramentas.get(i, i) for i in itens]

ordem = list(tarefas.keys())
por_agente = {}
for i, (nome, t) in enumerate(tarefas.items()):
    if nome == "relatorio_performance":
        continue
    por_agente.setdefault(t.get("agent"), []).append({"nome": nome, "ordem": i + 1})

lista = []
for chave, a in agentes.items():
    lista.append({
        "chave": chave,
        "papel": limpo(a.get("role")),
        "objetivo": limpo(a.get("goal")).replace('"{briefing_titulo}"', "da campanha"),
        "delega": bool(a.get("allow_delegation")),
        "ferramentas": ferramentas.get(chave, []),
        "tarefas": por_agente.get(chave, []),
    })
mapa = {t["nome"]: {"agente": ag["chave"], "papel": ag["papel"], "ordem": t["ordem"]} for ag in lista for t in ag["tarefas"]}
(SAIDA / "lib/agentes.json").write_text(json.dumps({"agentes": lista, "tarefas": mapa}, ensure_ascii=False, indent=1), encoding="utf-8")

# clientes (INDEX.md)
linhas = []
# Não usa split por "|": o título do Drive pode conter "|" (ex.: "Leapmotor | Via Marconi"). Ancora no slug e no arquivo.
padrao = re.compile(r"^\|\s*(.+?)\s*\|\s*([a-z0-9_]+)\s*\|\s*\2/[^|]+\|.*\|\s*(\d+)\s*\|\s*(sim|\*\*n[ãa]o\*\*)\s*\|\s*$")
for l in (RAIZ / "knowledge/INDEX.md").read_text(encoding="utf-8").splitlines():
    m = padrao.match(l)
    if m:
        linhas.append((m.group(1), m.group(2), m.group(4) == "sim", int(m.group(3))))
dirs = {p.name for p in (RAIZ / "knowledge").iterdir() if p.is_dir()}
faltam = dirs - {x[1] for x in linhas}
if faltam:
    sys.exit(f"INDEX.md sem linha reconhecida para: {sorted(faltam)}")
q = lambda s: "'" + s.replace("'", "''") + "'"
sql = ["create table if not exists public.portal_clientes (",
       "  slug text primary key, nome text not null, guia_completo boolean not null, guia_caracteres int not null default 0,",
       "  atualizado_em timestamptz not null default now());",
       "alter table public.portal_clientes enable row level security;",
       "insert into public.portal_clientes (slug, nome, guia_completo, guia_caracteres) values"]
sql.append(",\n".join(f"({q(s)}, {q(n)}, {str(c).lower()}, {k})" for n, s, c, k in linhas))
sql.append("on conflict (slug) do update set nome=excluded.nome, guia_completo=excluded.guia_completo, guia_caracteres=excluded.guia_caracteres, atualizado_em=now();")
(SAIDA / "clientes.sql").write_text("\n".join(sql) + "\n", encoding="utf-8")
print(f"{len(lista)} agentes, {len(mapa)} tarefas mapeadas, {len(linhas)} clientes")
