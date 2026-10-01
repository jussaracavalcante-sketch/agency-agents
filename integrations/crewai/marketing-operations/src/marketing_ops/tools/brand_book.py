from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# knowledge/<slug>/*.md — um diretório por cliente (guia de identidade visual, ofertas, restrições…)
KNOWLEDGE_DIR = Path(__file__).resolve().parents[3] / "knowledge"


def _slug(texto: str) -> str:
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _clientes_disponiveis() -> list[str]:
    if not KNOWLEDGE_DIR.exists():
        return []
    return sorted(p.name for p in KNOWLEDGE_DIR.iterdir() if p.is_dir() and any(p.glob("*.md")))


def _localizar(cliente: str) -> Path | None:
    alvo = _slug(cliente)
    pastas = _clientes_disponiveis()
    if alvo in pastas:
        return KNOWLEDGE_DIR / alvo
    # correspondência parcial: "colmeia" ↔ "construtora_colmeia"; "hospital santa julia" ↔ "hospital_santa_julia"
    tokens = [t for t in alvo.split("_") if len(t) > 2]
    candidatos = [p for p in pastas if all(t in p for t in tokens)] or [p for p in pastas if any(t in p for t in tokens) and len(tokens) == 1]
    return KNOWLEDGE_DIR / candidatos[0] if len(candidatos) == 1 else None


class BrandBookInput(BaseModel):
    cliente: str = Field(..., description="Nome do cliente (ex.: 'Hospital Santa Júlia', 'Construtora Colmeia')")
    secao: str = Field("", description="Opcional: filtrar por título de seção (ex.: 'Paleta', 'Tipografia', 'DNA')")


class BrandBookTool(BaseTool):
    name: str = "brand_book_lookup"
    description: str = (
        "Devolve o guia de identidade visual e demais documentos de marca do cliente (DNA da marca, "
        "palavras-chave, paleta com HEX, tipografia, elementos gráficos, direção fotográfica, composição). "
        "USE SEMPRE antes de escrever copy, briefing criativo ou parecer de marca. Se o cliente não tiver "
        "guia, a resposta diz isso explicitamente e as decisões de marca devem ser marcadas [VALIDAR]."
    )
    args_schema: type[BaseModel] = BrandBookInput

    def _run(self, cliente: str, secao: str = "") -> str:
        pasta = _localizar(cliente)
        if pasta is None:
            disponiveis = ", ".join(_clientes_disponiveis()) or "nenhum"
            return (
                f"[SEM GUIA DE MARCA] Nenhum guia encontrado para '{cliente}'. "
                f"Clientes com guia: {disponiveis}. Marque decisões de marca como [VALIDAR]."
            )
        partes = []
        for arq in sorted(pasta.glob("*.md")):
            texto = arq.read_text(encoding="utf-8")
            if secao:
                blocos = re.split(r"(?m)^(?=#{1,3} )", texto)
                texto = "\n".join(b for b in blocos if secao.lower() in b.split("\n", 1)[0].lower()) or (
                    f"(seção '{secao}' não encontrada em {arq.name}; seções: "
                    + ", ".join(re.findall(r"(?m)^#{1,3} \**(.+?)\**\s*$", texto)[:20]) + ")"
                )
            aviso = ""
            if re.search(r"(?m)^completo:\s*(false|n[aã]o)\s*$", arq.read_text(encoding="utf-8")[:1500], re.I):
                aviso = "[GUIA INCOMPLETO: texto truncado na extração; marque decisões de marca não cobertas como [VALIDAR]]\n"
            partes.append(f"=== {arq.name} ===\n{aviso}{texto.strip()}")
        return "\n\n".join(partes)[:20000]
