import { NextResponse } from "next/server";
import { sessao } from "@/lib/supabase";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const code = url.searchParams.get("code");
  if (code) await sessao().auth.exchangeCodeForSession(code);
  return NextResponse.redirect(new URL("/", url.origin));
}
