from __future__ import annotations

import os

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CrmReadInput(BaseModel):
    consulta: str = Field(..., description="O que consultar: 'segmentos', 'fluxos', 'metricas_email'")


class CrmReadTool(BaseTool):
    name: str = "crm_read"
    description: str = (
        "Consulta SOMENTE LEITURA ao CRM/automação (RD Station, HubSpot…): segmentos existentes, "
        "fluxos ativos e métricas agregadas de e-mail. Nunca retorna dados pessoais."
    )
    args_schema: type[BaseModel] = CrmReadInput

    def _run(self, consulta: str) -> str:
        if not os.getenv("RD_STATION_TOKEN"):
            return (
                f"[SEM INTEGRAÇÃO] consulta='{consulta}'. Use os dados do briefing e marque "
                "tamanhos de segmento como estimativa [VALIDAR]."
            )
        # TODO (F4): implementar chamadas de leitura agregada à API do CRM.
        return f"[INTEGRAÇÃO PENDENTE] consulta='{consulta}'."
