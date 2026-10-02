import { NextResponse } from "next/server";
import { admin, usuarioAtual } from "@/lib/supabase";
import { execucaoAtiva } from "@/lib/execucoes";
import { iniciar } from "@/lib/crewai";
import { CHAVES, validar } from "@/lib/briefing";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const u = await usuarioAtual();
  if (!u) return NextResponse.json({ erro: "Sessão inválida" }, { status: 401 });
  if (u.papel !== "aprovador") return NextResponse.json({ erro: "Apenas aprovadores disparam campanhas" }, { status: 403 });

  const { briefing, confirmou } = (await req.json()) as { briefing?: Record<string, unknown>; confirmou?: boolean };
  if (!briefing || confirmou !== true) return NextResponse.json({ erro: "Confirmação obrigatória" }, { status: 400 });
  const falha = validar(briefing);
  if (falha) return NextResponse.json({ erro: falha }, { status: 400 });

  // O cliente vem da lista cadastrada: o servidor usa o nome oficial, nunca o texto do navegador.
  const db = admin();
  const { data: cliente } = await db.from("portal_clientes").select("slug,nome").eq("slug", String(briefing.cliente_slug ?? "")).maybeSingle();
  if (!cliente) return NextResponse.json({ erro: "Cliente não encontrado na base de marcas" }, { status: 400 });

  const ativa = await execucaoAtiva();
  if (ativa.ativa) return NextResponse.json({ erro: `Já existe uma campanha rodando: ${ativa.motivo}. Aguarde terminar para não duplicar o custo.` }, { status: 409 });

  const inputs: Record<string, string> = {};
  for (const k of CHAVES) inputs[k] = String(k === "cliente" ? cliente.nome : briefing[k]).trim();

  const r = await iniciar(inputs);
  await db.from("portal_disparos").insert({
    humano_id: u.id, humano_nome: u.nome, cliente_slug: cliente.slug, briefing: inputs,
    enviado_ao_crewai: r.ok, kickoff_id: r.kickoff, resposta_crewai: r.texto,
  });
  if (!r.ok) return NextResponse.json({ erro: "A plataforma recusou o disparo", detalhe: r.texto }, { status: 502 });
  return NextResponse.json({ ok: true, kickoff: r.kickoff, mensagem: "Campanha disparada. O primeiro portão (G1) aparece na fila em alguns minutos." });
}
