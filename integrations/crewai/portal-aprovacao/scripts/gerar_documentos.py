#!/usr/bin/env python3
"""
Gera lib/documentos.ts a partir da fonte única dos textos legais em marketing-operations/docs/lgpd/:
  - aviso-de-privacidade.md  → página /privacidade
  - termo-de-conduta.md      → página /termo
  - ../guia-do-analista.md   → página /guia (sem aceite) (a tabela de assinatura em papel, "## 7. Aceite", não vai para a web: o aceite é registrado no portal)
O hash do texto identifica a versão aceita: mudou o texto, as pessoas aceitam de novo.
Rode de novo sempre que um dos textos mudar:  python3 scripts/gerar_documentos.py
"""
import hashlib, json, re
from pathlib import Path

FONTE = Path(__file__).resolve().parents[2] / "marketing-operations/docs/lgpd"
SAIDA = Path(__file__).resolve().parents[1] / "lib/documentos.ts"

DOCS = {
    "aviso": ("Aviso de Privacidade", "aviso-de-privacidade.md", None),
    "termo": ("Termo de Conduta", "termo-de-conduta.md", "## 7. Aceite"),
}

saida = ["// GERADO por scripts/gerar_documentos.py a partir de marketing-operations/docs/lgpd/. Não edite aqui.",
         "export type Documento = { chave: \"aviso\" | \"termo\"; titulo: string; versao: string; hash: string; md: string };",
         "export const DOCUMENTOS: Record<\"aviso\" | \"termo\", Documento> = {"]
for chave, (titulo, arquivo, corte) in DOCS.items():
    texto = (FONTE / arquivo).read_text(encoding="utf-8")
    if corte:
        texto = texto.split(corte)[0].rstrip() + "\n"
    versao = (re.search(r"\*\*Versão:\*\*\s*([^\n(]+)", texto) or [None, "?"])[1].strip()
    h = hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]
    saida.append(f"  {chave}: {{ chave: {json.dumps(chave)}, titulo: {json.dumps(titulo, ensure_ascii=False)}, versao: {json.dumps(versao)}, hash: {json.dumps(h)}, md: {json.dumps(texto, ensure_ascii=False)} }},")
    print(chave, "versão", versao, "hash", h)
saida.append("};")
guia = (FONTE.parent / "guia-do-analista.md").read_text(encoding="utf-8")
saida.append("/** Guia de uso: página /guia, sem aceite. */")
saida.append(f"export const GUIA = {{ titulo: \"Guia do analista\", md: {json.dumps(guia, ensure_ascii=False)} }};")
print("guia", len(guia), "caracteres")
SAIDA.write_text("\n".join(saida) + "\n", encoding="utf-8")
