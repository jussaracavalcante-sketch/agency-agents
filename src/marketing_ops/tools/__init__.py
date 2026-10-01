"""
Ferramentas customizadas da Equipe de Operação de Marketing.

Todas são ESQUELETOS seguros: devolvem dados estimados/mockados e indicam claramente que
são estimativas até a integração real ser implementada (fase F4 do roadmap). A única
ferramenta de escrita (PublishTool) nasce desabilitada e exige aprovação G3 registrada.

Detalhes e contratos em ../../docs/ferramentas.md
"""

from .analytics_read import AnalyticsReadTool
from .crm_read import CrmReadTool
from .paid_media_read import PaidMediaReadTool
from .publish import PublishTool
from .seo_keyword import SeoKeywordTool

__all__ = [
    "AnalyticsReadTool",
    "CrmReadTool",
    "PaidMediaReadTool",
    "PublishTool",
    "SeoKeywordTool",
]
