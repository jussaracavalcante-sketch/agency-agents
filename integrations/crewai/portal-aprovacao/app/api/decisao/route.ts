import { NextResponse } from "next/server";
import { admin, usuarioAtual, podeDecidir, ehAprovador } from "@/lib/supabase";
import { registrar } from "@/lib/auditoria";
import { obterExecucao } from "@/lib/execucoes";
import { retomar, textoDeDecisao, motivoDaRecusa } from "@/lib/crewai";
import { MAX_FEEDBACK } from "@/lib/limites";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const usuario = await usuarioAtual();
  if (!usuario) return NextResponse.json({ erro: "Sessão inválida" }, { status: 401 });
  if (!ehAprovador(usuario)) return NextResponse.json({ erro: "Apenas aprovadores decidem" }, { status: 403 });

  const corpo = (await req.json().catch(() => null)) as { execucaoId?: unknown; decisao?: unknown; instrucoes?: unknown; ignorarTexto?: unknown } | null;
  if (!corpo || typeof corpo.execucaoId !== "string" || !corpo.execucaoId || (corpo.instrucoes != null && typeof corpo.instrucoes !== "string")) {
    return NextResponse.json({ erro: "Pedido inválido" }, { status: 400 });
  }
  const execucaoId = corpo.execucaoId;
  const decisao = corpo.decisao as "aprovar" | "devolver" | "reprovar";
  const instrucoes = corpo.instrucoes as string | undefined;
  const ignorarTexto = corpo.ignorarTexto === true;
  if ((instrucoes || "").length > MAX_FEEDBACK) return NextResponse.json({ erro: `As instruções passam de ${MAX_FEEDBACK} caracteres` }, { status: 400 });
  if (!["aprovar", "devolver", "reprovar"].includes(decisao)) return NextResponse.json({ erro: "Decisão inválida" }, { status: 400 });
  if (decisao === "devolver" && !(instrucoes || "").trim()) {
    return NextResponse.json({ erro: "Informe as instruções ao devolver" }, { status: 400 });
  }

  // Texto escrito + Aprovar/Reprovar: o texto não vai à plataforma. Foi a causa de decisões registradas diferentes da pretendida;
  // o servidor só aceita quando a pessoa confirmou que sabe disso.
  if (decisao !== "devolver" && (instrucoes || "").trim() && !ignorarTexto) {
    return NextResponse.json({ erro: "Há instruções escritas, mas esta decisão não as envia. Use Devolver com ajustes ou confirme que o texto será ignorado." }, { status: 409 });
  }

  // O servidor decide qual é o portão pendente: o navegador não escolhe o taskId.
  const exec = await obterExecucao(execucaoId);
  if (!exec?.pendente) return NextResponse.json({ erro: "Nenhum portão pendente nesta execução" }, { status: 409 });
  const taskId = exec.pendente.task_name!;
  if (!podeDecidir(usuario, exec.portao)) {
    return NextResponse.json({ erro: `Você não é aprovador do portão ${exec.portao ?? ""}` }, { status: 403 });
  }

  // Evita duplo clique: já existe decisão para ESTE pedido? Uma devolução reabre o portão com o mesmo taskId,
  // por isso só conta decisão posterior ao pedido pendente (não qualquer decisão antiga do mesmo taskId).
  const db = admin();
  const { data: jaDecidido } = await db
    .from("portal_decisoes")
    .select("id")
    .eq("task_id", taskId)
    .gt("criado_em", exec.pendente.recebido_em)
    .or("enviado_ao_crewai.eq.true,decisao.eq.reprovar")   // envio recusado pela plataforma (ex.: limite do plano) não trava nova tentativa
    .limit(1);
  if (jaDecidido?.length) return NextResponse.json({ erro: "Este pedido já recebeu uma decisão" }, { status: 409 });

  const registro = {
    execucao_id: execucaoId, task_id: taskId, portao: exec.portao, decisao, instrucoes: instrucoes ?? null,
    humano_id: usuario.id, humano_nome: usuario.nome,
  };

  if (decisao === "reprovar") {
    // Reprovar não chama a plataforma (não existe cancelamento): a decisão fica registrada e o portal passa a tratar a
    // execução como encerrada (ver execucoes.ts), então ela sai de "Aguardando". Nada é publicado.
    await db.from("portal_decisoes").insert({ ...registro, enviado_ao_crewai: false });
    await registrar(usuario, { acao: "decisao.reprovar", entidade: "portal_decisoes", entidade_id: execucaoId, depois: { portao: exec.portao, decisao, instrucoes: instrucoes || "" }, detalhe: `Portão ${exec.portao ?? ""} reprovado; execução encerrada no portal.` });
    return NextResponse.json({ ok: true, mensagem: "Reprovado e registrado. A execução foi encerrada no portal e não será retomada." });
  }

  const r = await retomar({
    executionId: execucaoId,
    taskId,
    humanFeedback: textoDeDecisao({ decisao, portao: exec.portao, nome: usuario.nome, instrucoes: instrucoes ?? "" }),
  });
  await db.from("portal_decisoes").insert({
    ...registro, enviado_ao_crewai: r.ok, novo_kickoff_id: r.kickoff, resposta_crewai: r.texto,
  });
  await registrar(usuario, { acao: `decisao.${decisao}`, entidade: "portal_decisoes", entidade_id: execucaoId, depois: { portao: exec.portao, decisao, instrucoes: instrucoes || "", enviado_ao_crewai: r.ok, novo_kickoff_id: r.kickoff }, detalhe: `Portão ${exec.portao ?? ""}: ${decisao === "aprovar" ? "aprovado" : "devolvido com ajustes"}${r.ok ? "" : " (plataforma recusou o envio)"}.` });
  if (!r.ok) {
    const m = motivoDaRecusa(r.texto);
    return NextResponse.json({ erro: `${m.mensagem} Sua decisão ficou registrada como NÃO enviada; o portão continua aberto e você poderá decidir de novo.`, motivo: m.tipo }, { status: m.tipo === "limite" ? 503 : 502 });
  }
  return NextResponse.json({ ok: true, mensagem: "Decisão enviada. A execução foi retomada.", kickoff: r.kickoff });
}
