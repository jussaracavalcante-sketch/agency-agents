from __future__ import annotations

from datetime import datetime

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class PublishInput(BaseModel):
    canal: str = Field(..., description="instagram | linkedin | blog | email | google_ads | meta_ads")
    peca_id: str = Field(..., description="Identificador da peça no pacote de publicação")
    agendar_para: str = Field(..., description="Data/hora ISO 8601 com fuso, ex.: 2026-10-15T09:00-04:00")
    aprovacao_g3: str = Field(..., description="Referência da decisão G3 (data + aprovador)")


class PublishTool(BaseTool):
    """
    Única ferramenta de ESCRITA da crew. Nasce desabilitada (CREW_ENABLE_WRITE_TOOLS=false)
    e, mesmo habilitada, recusa chamadas sem referência de aprovação G3.
    """

    name: str = "publish_or_schedule"
    description: str = (
        "Publica ou agenda uma peça aprovada em um canal. EXIGE referência de aprovação G3. "
        "Quando desabilitada, devolve o roteiro operacional para execução humana."
    )
    args_schema: type[BaseModel] = PublishInput
    enabled: bool = False

    def _run(self, canal: str, peca_id: str, agendar_para: str, aprovacao_g3: str) -> str:
        sem_aprovacao = not aprovacao_g3.strip() or "VALIDAR" in aprovacao_g3.upper()
        if sem_aprovacao:
            return "[BLOQUEADO] Publicação sem aprovação G3 registrada."
        if not self.enabled:
            return (
                f"[MODO ROTEIRO] Ferramenta de escrita desabilitada. Instrução para o operador: "
                f"publicar/agendar peça '{peca_id}' em '{canal}' para {agendar_para} "
                f"(aprovação G3: {aprovacao_g3})."
            )
        # TODO (F4): integrar com CMS/agendador/Ads. Registrar sempre no log.
        return (
            f"[SIMULADO] {datetime.now().isoformat()} — '{peca_id}' agendado em '{canal}' "
            f"para {agendar_para}. Aprovação G3: {aprovacao_g3}."
        )
