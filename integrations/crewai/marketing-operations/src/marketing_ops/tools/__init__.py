"""
Ferramentas customizadas da Equipe de Operação de Marketing.

Todas são ESQUELETOS seguros: devolvem dados estimados/mockados e indicam claramente que
são estimativas até a integração real ser implementada (fase F4 do roadmap). A única
ferramenta de escrita (PublishTool) nasce desabilitada e exige aprovação G3 registrada.

Detalhes e contratos em ../../docs/ferramentas.md
"""

from marketing_ops.tools.analytics_read import AnalyticsReadTool
from marketing_ops.tools.brand_book import BrandBookTool
from marketing_ops.tools.crm_read import CrmReadTool
from marketing_ops.tools.paid_media_read import PaidMediaReadTool
from marketing_ops.tools.publish import PublishTool
from marketing_ops.tools.seo_keyword import SeoKeywordTool

__all__ = [
    "AnalyticsReadTool",
    "BrandBookTool",
    "CrmReadTool",
    "PaidMediaReadTool",
    "PublishTool",
    "SeoKeywordTool",
]
