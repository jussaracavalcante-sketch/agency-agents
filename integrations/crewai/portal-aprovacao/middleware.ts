import { NextResponse, type NextRequest } from "next/server";
import { COOKIE_ACEITE, SELO_VIGENTE } from "./lib/selo";

/**
 * Portão de conveniência do aceite: quem tem sessão e ainda não tem o cookie de aceite em vigor vai para /aceite.
 * Não é controle de segurança. As rotas de API e as telas checam o aceite no banco (usuarioAtual). O cookie só evita ir ao banco a cada página.
 */
const LIVRES = ["/aceite", "/api", "/privacidade", "/termo", "/login", "/auth", "/recuperar", "/saiu", "/definir-senha", "/_next", "/icon.png", "/logo-vanguarda.png", "/favicon.ico"];

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  // Defesa contra requisição forjada de outro site: chamada que altera estado precisa vir do próprio portal.
  if (pathname.startsWith("/api/") && !["GET", "HEAD", "OPTIONS"].includes(req.method)) {
    const origem = req.headers.get("origin");
    if (origem && origem !== req.nextUrl.origin) return NextResponse.json({ erro: "Origem não permitida" }, { status: 403 });
  }
  if (LIVRES.some((p) => pathname === p || pathname.startsWith(p + "/"))) return NextResponse.next();
  const temSessao = req.cookies.getAll().some((c) => c.name.startsWith("sb-") && c.name.includes("auth-token"));
  if (!temSessao) return NextResponse.next();
  if (req.cookies.get(COOKIE_ACEITE)?.value === SELO_VIGENTE) return NextResponse.next();
  const url = req.nextUrl.clone();
  url.pathname = "/aceite";
  url.search = "";
  return NextResponse.redirect(url);
}

export const config = { matcher: ["/((?!_next/static|_next/image|.*\\..*).*)"] };
