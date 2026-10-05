import { NextResponse } from "next/server";
import { admin, usuarioAtual, podeDecidir } from "@/lib/supabase";
import { obterExecucao } from "@/lib/execucoes";
import { retomar, textoDeDecisao } from "@/lib/crewai";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const usuario = await usuarioAtual();
  if (!usuario) return NextResponse.json({ erro: "Sessão inválida" }, { status: 401 });
  if (usuario.papel !== "aprovador") return NextResponse.json({ erro: "Apenas aprovadores decidem" }, { status: 403 });

  const { execucaoId, decisao, instrucoes } = (await req.json()) as {
    execucaoId: string; decisao: "aprovar" | "devolver" | "reprovar"; instrucoes?: string;
  };
  if (!["aprovar", "devolver", "reprovar"].includes(decisao)) return NextResponse.json({ erro: "Decisão inválida" }, { status: 400 });
  if (decisao === "devolver" && !(instrucoes || "").trim()) {
    return NextResponse.json({ erro: "Informe as instruções ao devolver" }, { status: 400 });
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
  if (!r.ok) return NextResponse.json({ erro: "A plataforma recusou o envio", detalhe: r.texto }, { status: 502 });
  return NextResponse.json({ ok: true, mensagem: "Decisão enviada. A execução foi retomada.", kickoff: r.kickoff });
}
