import { NextResponse } from "next/server";
import { ehAdmin, ehAprovador, usuarioAtual } from "@/lib/supabase";
import { listar, mudancas, rotuloAcao } from "@/lib/auditoria";

export const dynamic = "force-dynamic";

/** Exporta a trilha filtrada em CSV (mesmos filtros da tela). Leitura: admin e aprovadores. */
export async function GET(req: Request) {
  const u = await usuarioAtual();
  if (!u) return NextResponse.json({ erro: "Sessão inválida" }, { status: 401 });
  if (!ehAdmin(u) && !ehAprovador(u)) return NextResponse.json({ erro: "Seu papel não acessa a auditoria" }, { status: 403 });
  const p = new URL(req.url).searchParams;
  const linhas = await listar({ usuario: p.get("usuario") || undefined, acao: p.get("acao") || undefined, entidade: p.get("entidade") || undefined, de: p.get("de") || undefined, ate: p.get("ate") || undefined, busca: p.get("q") || undefined, limite: 2000 });
  const esc = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const fmt = (s: string) => new Date(s).toLocaleString("pt-BR", { timeZone: "America/Manaus" });
  const csv = ["id;data_hora;usuario;sessao;acao;descricao;entidade;entidade_id;o_que_mudou;detalhe",
    ...linhas.map((l) => [l.id, fmt(l.criado_em), l.usuario_nome, l.sessao ?? "", l.acao, rotuloAcao(l.acao), l.entidade, l.entidade_id ?? "", mudancas(l.antes, l.depois).join(" | "), l.detalhe ?? ""].map(esc).join(";"))].join("\n");
  return new NextResponse("﻿" + csv, { headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="auditoria-${new Date().toISOString().slice(0, 10)}.csv"` } });
}
