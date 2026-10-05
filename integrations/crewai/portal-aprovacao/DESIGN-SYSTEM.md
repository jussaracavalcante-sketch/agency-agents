# Design system do portal · Vanguarda Growth Company

Fonte das cores: o logotipo da marca (medidas por amostragem de pixels do arquivo de identidade), conferidas com o guia de marca
`knowledge/vanguarda_growth_company/guia_identidade_visual.md`. Tokens em `app/globals.css`.

## Paleta da marca
| Token | HEX | Uso |
|---|---|---|
| `--v-red` | `#E10D16` | **Vermelho Vanguarda**, cor de ação: botões preenchidos, logotipo, marcas de destaque (`--ac-solid`) |
| `--v-red-600` | `#C50C13` | Texto e links vermelhos no tema claro (`--ac`), estado de pressionado |
| `--v-red-700` | `#AB0A10` | Hover de links e botões no tema claro |
| `--v-red-900` | `#3E0102` | Transição do degradê, fundos de destaque no escuro |
| `--v-black` | `#050000` | **Preto institucional**: fundos escuros e centro do degradê |
| `--v-white` | `#FFFFFF` | **Branco estratégico**: cards, texto sobre vermelho e sobre preto |
| `--grad-brand` | `135deg, #D10F18 → #3E0102 → #050000 → #3E0102 → #C50C13` | Tela de login e saída (vermelho nos cantos, preto no centro, como no fundo da identidade) |

Observação: o guia de marca traz o vermelho como "HEX estimado `#ED1121`". O valor **medido no logotipo é `#E10D16`**, que é o usado aqui.
Vale corrigir o guia (agora editável em **Conhecimento**) quando a marca confirmar o HEX oficial.

## Tokens da interface
| Papel | Tema claro | Tema escuro |
|---|---|---|
| Fundo (`--bg`) | `#F7F5F5` | `#080303` |
| Card (`--card`) | `#FFFFFF` | `#130A0B` |
| Texto (`--tx`) | `#140A0B` | `#F6EFEF` |
| Texto secundário (`--mut`) | `#6B5C5E` | `#A99B9C` |
| Borda (`--bd`) | `#E8E0E1` | `#2C1A1C` |
| Destaque em texto/links (`--ac`) | `#C50C13` | `#FF5A62` |
| Destaque preenchido (`--ac-solid`) | `#E10D16` | `#E10D16` |
| Tinta de destaque (`--ac-bg`) | `#FDEBEC` | `#2A0A0D` |
| Sucesso / alerta / erro | `#15803D` / `#A15C00` / `#B3261E` | `#4CC38A` / `#E0B44C` / `#FF9A8F` |

Status (sucesso, alerta, erro) continuam em verde, âmbar e vermelho-escuro, sempre acompanhados de rótulo ou ícone, para não se confundir com o
vermelho de marca.

## Contraste (WCAG 2.1, mínimo 4,5:1 para texto normal)
| Combinação | Razão |
|---|---|
| Branco sobre `#E10D16` (botão) | 4,92:1 |
| `#C50C13` sobre branco (link, tema claro) | 6,11:1 |
| `#FF5A62` sobre `#130A0B` (link, tema escuro) | 6,40:1 |
| Texto `#140A0B` sobre branco | 19,48:1 |
| Texto secundário `#6B5C5E` sobre branco | 6,33:1 |
| `#A99B9C` sobre `#130A0B` | 7,30:1 |
| `#E10D16` sobre `#050000` | 4,24:1: **só para ícones e elementos grandes**; texto vermelho no escuro usa `#FF5A62` |

## Logotipo e tipografia
- `public/logo-vanguarda.png` e `app/icon.png`: ícone do "V" recortado do arquivo de identidade (cantos arredondados, fundo transparente).
- A marca usa a **Monument Extended**, fonte licenciada que não está no projeto: a interface usa a fonte do sistema. Para usá-la, é preciso o
  arquivo de fonte licenciado (`@font-face` em `globals.css`).

## Regras de uso
1. Vermelho é cor de **ação**: botão principal, link, item ativo. Não usar vermelho para decoração nem para erro sem ícone.
2. Preto e vermelho juntos só em fundo escuro (login, saída); áreas de leitura ficam em branco.
3. Um botão preenchido por tela (`.p`); os demais são contornados.
