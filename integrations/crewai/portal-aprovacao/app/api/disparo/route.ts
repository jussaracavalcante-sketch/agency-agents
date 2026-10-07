import { NextResponse } from "next/server";
import { admin, usuarioAtual, ehAprovador } from "@/lib/supabase";
import { registrar } from "@/lib/auditoria";
import { textoDosAjustes } from "@/lib/admin";
import { execucaoAtiva } from "@/lib/execucoes";
import { iniciar } from "@/lib/crewai";
import { CHAVES, validar } from "@/lib/briefing";
import { contextoDoCliente } from "@/lib/conhecimento";
import { disparosNas24h, limiteDiario } from "@/lib/limites";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const u = await usuarioAtual();
  if (!u) return NextResponse.json({ erro: "Sessão inválida" }, { status: 401 });
  if (!ehAprovador(u)) return NextResponse.json({ erro: "Apenas aprovadores disparam campanhas" }, { status: 403 });

  const corpo = (await req.json().catch(() => null)) as { briefing?: Record<string, unknown>; confirmou?: boolean } | null;
  const briefing = corpo?.briefing; const confirmou = corpo?.confirmou;
  if (!briefing || typeof briefing !== "object" || confirmou !== true) return NextResponse.json({ erro: "Confirmação obrigatória" }, { status: 400 });
  const falha = validar(briefing);
  if (falha) return NextResponse.json({ erro: falha }, { status: 400 });

  // O cliente vem da lista cadastrada: o servidor usa o nome oficial, nunca o texto do navegador.
  const db = admin();
  const { data: cliente } = await db.from("portal_clientes").select("slug,nome").eq("slug", String(briefing.cliente_slug ?? "")).maybeSingle();
  if (!cliente) return NextResponse.json({ erro: "Cliente não encontrado na base de marcas" }, { status: 400 });

  const [feitos, teto] = await Promise.all([disparosNas24h(u.id), limiteDiario()]);
  if (feitos >= teto) return NextResponse.json({ erro: `Limite de ${teto} disparos em 24 horas atingido. Peça ao administrador para ajustar, se for necessário.` }, { status: 429 });

  const ativa = await execucaoAtiva();
  if (ativa.ativa) return NextResponse.json({ erro: `Já existe uma campanha rodando: ${ativa.motivo}. Aguarde terminar para não duplicar o custo.` }, { status: 409 });

  const inputs: Record<string, string> = {};
  for (const k of CHAVES) inputs[k] = String(k === "cliente" ? cliente.nome : briefing[k]).trim();

  // Base de conhecimento editada no portal: vai como contexto_cliente (o crew já usa esse insumo quando vem preenchido).
  const ctx = await contextoDoCliente(cliente.slug);
  if (ctx.erro) return NextResponse.json({ erro: ctx.erro }, { status: 502 });
  // Ajustes do administrador por agente: entram no mesmo contexto (seção [AJUSTES DO ADMINISTRADOR]), antes da base de marca.
  const ajustes = await textoDosAjustes();
  const contexto = [ajustes, ctx.texto].filter(Boolean).join("\n\n");
  const enviados = contexto ? { ...inputs, contexto_cliente: contexto } : inputs;
  const r = await iniciar(enviados);
  const registro = { ...inputs, ...(ctx.texto ? { _conhecimento: { hash: ctx.hash, docs: ctx.docs, chars: ctx.chars, truncado: ctx.truncado } } : {}), ...(ajustes ? { _ajustes_agentes: ajustes.length } : {}) };
  await db.from("portal_disparos").insert({
    humano_id: u.id, humano_nome: u.nome, cliente_slug: cliente.slug, briefing: registro,
    enviado_ao_crewai: r.ok, kickoff_id: r.kickoff, resposta_crewai: r.texto,
  });
  await registrar(u, { acao: "disparo.criar", entidade: "portal_disparos", entidade_id: r.kickoff ?? cliente.slug, depois: { cliente: cliente.nome, briefing_titulo: inputs.briefing_titulo, enviado_ao_crewai: r.ok, kickoff_id: r.kickoff, ajustes_agentes: !!ajustes }, detalhe: `Campanha disparada para ${cliente.nome}${r.ok ? "" : " (plataforma recusou)"}.` });
  if (!r.ok) return NextResponse.json({ erro: "A plataforma recusou o disparo. O detalhe técnico ficou registrado; avise o administrador." }, { status: 502 });
  return NextResponse.json({ ok: true, kickoff: r.kickoff, mensagem: "Campanha disparada." + (ctx.texto ? ` Usando a base de conhecimento editada no portal (${ctx.docs} documento(s)${ctx.truncado ? ", texto cortado no limite" : ""}).` : "") + " O primeiro portão (G1) aparece na fila em alguns minutos." });
}
