import { NextResponse } from "next/server";
import { sessao } from "@/lib/supabase";

/** Encerra a sessão (apaga os cookies) e mostra a tela de saída. POST para não sair por link aberto sem querer. */
export async function POST(req: Request) {
  await sessao().auth.signOut();
  return NextResponse.redirect(new URL("/saiu", req.url), 303);
}
