from __future__ import annotations

import os

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SeoKeywordInput(BaseModel):
    termo: str = Field(..., description="Palavra-chave ou tema a pesquisar")
    pais: str = Field("br", description="Base de dados do país (ex.: br, us)")


class SeoKeywordTool(BaseTool):
    name: str = "seo_keyword_research"
    description: str = (
        "Retorna volume estimado, dificuldade e intenção para uma palavra-chave. "
        "Sem SEMRUSH_API_KEY configurada, devolve ESTIMATIVA heurística marcada como tal."
    )
    args_schema: type[BaseModel] = SeoKeywordInput

    def _run(self, termo: str, pais: str = "br") -> str:
        if os.getenv("SEMRUSH_API_KEY"):
            # TODO (F4): chamar API Semrush (phrase_this / phrase_related) e normalizar.
            return f"[INTEGRAÇÃO PENDENTE] Semrush para '{termo}' ({pais})."
        return (
            f"[ESTIMATIVA — sem ferramenta de dados] termo='{termo}', pais='{pais}'. "
            "Volume e dificuldade devem ser declarados como estimativa heurística e marcados "
            "[VALIDAR] no relatório."
        )
