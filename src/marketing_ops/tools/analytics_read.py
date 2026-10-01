from __future__ import annotations

from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class AnalyticsReadInput(BaseModel):
    caminho: str = Field(..., description="Caminho de um CSV/JSON exportado (GA4, Ads, Meta, CRM)")
    linhas: int = Field(50, description="Número máximo de linhas a retornar")


class AnalyticsReadTool(BaseTool):
    name: str = "analytics_read"
    description: str = (
        "Lê um arquivo CSV/JSON exportado de plataformas de analytics ou anúncios e devolve "
        "as primeiras linhas para análise. Somente leitura; nunca exporta dados identificáveis."
    )
    args_schema: type[BaseModel] = AnalyticsReadInput

    def _run(self, caminho: str, linhas: int = 50) -> str:
        p = Path(caminho)
        if not p.exists():
            return f"[ERRO] Arquivo não encontrado: {caminho}"
        conteudo = p.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(conteudo[: max(1, linhas)])
