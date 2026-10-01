from __future__ import annotations

import os

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class PaidMediaReadInput(BaseModel):
    plataforma: str = Field(..., description="google_ads | meta | linkedin")
    consulta: str = Field(..., description="'benchmarks', 'historico_conta', 'termos_busca'")


class PaidMediaReadTool(BaseTool):
    name: str = "paid_media_read"
    description: str = (
        "Leitura de métricas históricas e benchmarks de contas de anúncios. Somente leitura: "
        "não cria, edita nem ativa campanhas."
    )
    args_schema: type[BaseModel] = PaidMediaReadInput

    def _run(self, plataforma: str, consulta: str) -> str:
        chaves = {
            "google_ads": "GOOGLE_ADS_DEVELOPER_TOKEN",
            "meta": "META_ACCESS_TOKEN",
            "linkedin": "LINKEDIN_ACCESS_TOKEN",
        }
        if not os.getenv(chaves.get(plataforma, "")):
            return (
                f"[SEM INTEGRAÇÃO] {plataforma}/{consulta}. Use benchmarks públicos com fonte "
                "citada e declare as premissas de CPC/CTR/CVR como estimativa."
            )
        # TODO (F4): implementar leitura via APIs oficiais (GAQL, Marketing API).
        return f"[INTEGRAÇÃO PENDENTE] {plataforma}/{consulta}."
