import { NextResponse } from "next/server";
import { usuarioAtual } from "@/lib/supabase";
import { COOKIE_ACEITE, SELO_VIGENTE, registrarAceite } from "@/lib/aceite";

export const dynamic = "force-dynamic";

const opcoesCookie = { httpOnly: true, sameSite: "lax" as const, secure: true, path: "/", maxAge: 60 * 60 * 24 * 30 };

export async function POST(req: Request) {
  const u = await usuarioAtual({ semAceite: true });
  if (!u) return NextResponse.json({ erro: "Sessão inválida" }, { status: 401 });
  const { documentos, confirmou } = (await req.json().catch(() => ({}))) as { documentos?: string[]; confirmou?: boolean };
  if (confirmou !== true || !Array.isArray(documentos) || !documentos.length) return NextResponse.json({ erro: "Marque a leitura e o aceite de cada documento" }, { status: 400 });
  try {
    await registrarAceite(u, documentos);
  } catch (e) {
    console.error("[aceite]", e);
    return NextResponse.json({ erro: "Não foi possível registrar o aceite. Tente de novo." }, { status: 500 });
  }
  // Só marca o cookie se, depois do registro, não restar nada pendente.
  const { pendentesDe } = await import("@/lib/aceite");
  const r = NextResponse.json({ ok: true });
  const restam = (await pendentesDe(u.id)).length;
  if (!restam) r.cookies.set(COOKIE_ACEITE, SELO_VIGENTE, opcoesCookie);
  return r;
}
