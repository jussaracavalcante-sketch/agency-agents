import { NextResponse } from "next/server";
import { usuarioAtual } from "@/lib/supabase";
import { COOKIE_ACEITE, SELO_VIGENTE, pendentesDe } from "@/lib/aceite";

export const dynamic = "force-dynamic";

/** Quem já aceitou (em outro navegador, por exemplo) recebe o cookie de conveniência e segue. Quem não aceitou volta para /aceite. */
export async function GET(req: Request) {
  const origem = new URL(req.url).origin;
  const u = await usuarioAtual({ semAceite: true });
  if (!u) return NextResponse.redirect(new URL("/login", origem));
  if ((await pendentesDe(u.id)).length) return NextResponse.redirect(new URL("/aceite", origem));
  const r = NextResponse.redirect(new URL("/", origem));
  r.cookies.set(COOKIE_ACEITE, SELO_VIGENTE, { httpOnly: true, sameSite: "lax", secure: true, path: "/", maxAge: 60 * 60 * 24 * 30 });
  return r;
}
