"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { supabaseNavegador } from "@/lib/browser";

const TABELAS = ["crewai_webhook_events", "portal_decisoes", "portal_disparos"];

/**
 * Mantém a tela em sincronia com o banco: o Realtime avisa que uma tabela mudou e a página recarrega os dados pelo servidor
 * (sem perder o texto digitado). Se o canal cair, um recarregamento a cada 30 s (aba visível) cobre a falha.
 */
export default function AoVivo() {
  const router = useRouter();
  const [ok, setOk] = useState(false);
  const [ultimo, setUltimo] = useState<Date | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const atualizar = () => {
      if (timer.current) clearTimeout(timer.current);
      timer.current = setTimeout(() => { router.refresh(); setUltimo(new Date()); }, 800);
    };
    const sb = supabaseNavegador();
    let canal = sb.channel("portal-ao-vivo");
    for (const t of TABELAS) canal = canal.on("postgres_changes", { event: "*", schema: "public", table: t }, atualizar);
    canal.subscribe((s) => setOk(s === "SUBSCRIBED"));
    const poll = setInterval(() => { if (document.visibilityState === "visible") { router.refresh(); setUltimo(new Date()); } }, 30_000);
    const volta = () => { if (document.visibilityState === "visible") atualizar(); };
    document.addEventListener("visibilitychange", volta);
    return () => { clearInterval(poll); document.removeEventListener("visibilitychange", volta); if (timer.current) clearTimeout(timer.current); sb.removeChannel(canal); };
  }, [router]);

  return (
    <span className={`st ${ok ? "ok" : "warn"}`} title={ultimo ? `Última atualização ${ultimo.toLocaleTimeString("pt-BR")}` : "Aguardando alterações"}>
      {ok ? "Ao vivo" : "Reconectando…"}
    </span>
  );
}
