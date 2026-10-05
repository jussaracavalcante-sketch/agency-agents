import { NextResponse } from "next/server";
import { sessao } from "@/lib/supabase";

/** Só caminhos do próprio portal: evita redirecionar para outro site. */
const caminhoSeguro = (n: string | null) => (n && /^\/[a-z0-9/_-]*$/i.test(n) && !n.startsWith("//") ? n : "/");

export async function GET(req: Request) {
  const url = new URL(req.url);
  const code = url.searchParams.get("code");
  if (code) await sessao().auth.exchangeCodeForSession(code);
  return NextResponse.redirect(new URL(caminhoSeguro(url.searchParams.get("next")), url.origin));
}
