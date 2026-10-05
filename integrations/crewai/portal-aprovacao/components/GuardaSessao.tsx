"use client";
import { useEffect } from "react";
import { supabaseNavegador } from "@/lib/browser";

/** "Manter conectado" desmarcado no login: ao reabrir o navegador (sessionStorage vazio), encerra a sessão. */
export default function GuardaSessao() {
  useEffect(() => {
    try {
      if (localStorage.getItem("ma_manter") === "0" && !sessionStorage.getItem("ma_ativa")) {
        supabaseNavegador().auth.signOut().finally(() => { localStorage.removeItem("ma_manter"); window.location.href = "/saiu"; });
      }
    } catch { /* sem acesso ao storage: mantém o padrão */ }
  }, []);
  return null;
}
