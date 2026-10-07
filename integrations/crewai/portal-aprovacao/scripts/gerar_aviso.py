#!/usr/bin/env python3
"""
Gera lib/avisoPrivacidade.ts a partir da fonte única do aviso: marketing-operations/docs/lgpd/aviso-de-privacidade.md.
O portal lê o texto como constante (sem ler arquivo em tempo de execução). Rode de novo sempre que o aviso mudar:  python3 scripts/gerar_aviso.py
"""
import json, re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2] / "marketing-operations/docs/lgpd/aviso-de-privacidade.md"
SAIDA = Path(__file__).resolve().parents[1] / "lib/avisoPrivacidade.ts"

texto = RAIZ.read_text(encoding="utf-8")
versao = (re.search(r"\*\*Versão:\*\*\s*([^\n(]+)", texto) or [None, "?"])[1].strip()
SAIDA.write_text(
    "// GERADO por scripts/gerar_aviso.py a partir de marketing-operations/docs/lgpd/aviso-de-privacidade.md. Não edite aqui.\n"
    f"export const AVISO_VERSAO = {json.dumps(versao, ensure_ascii=False)};\n"
    f"export const AVISO_MD = {json.dumps(texto, ensure_ascii=False)};\n",
    encoding="utf-8",
)
print("aviso versão", versao, "→", SAIDA.name)
