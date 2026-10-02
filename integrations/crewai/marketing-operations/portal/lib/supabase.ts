import { createServerClient } from "@supabase/ssr";
import { createClient } from "@supabase/supabase-js";
import { cookies } from "next/headers";

/** Cliente com a sessão do usuário (cookies). Serve só para saber quem está logado. */
export function sessao() {
  const jar = cookies();
  return createServerClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!, {
    cookies: {
      getAll: () => jar.getAll(),
      setAll: (lista: { name: string; value: string; options?: Record<string, unknown> }[]) => {
        try { lista.forEach(({ name, value, options }) => jar.set(name, value, options as never)); } catch { /* componente de servidor */ }
      },
    },
  });
}

/** Cliente de serviço: só no servidor, depois de validar sessão e papel. */
export function admin() {
  return createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!, {
    auth: { persistSession: false },
  });
}

export type Papel = "leitor" | "revisor" | "aprovador";
export type Usuario = { id: string; nome: string; papel: Papel };

export async function usuarioAtual(): Promise<Usuario | null> {
  const { data } = await sessao().auth.getUser();
  if (!data.user) return null;
  const { data: perfil } = await admin().from("portal_perfis").select("nome,papel").eq("user_id", data.user.id).maybeSingle();
  if (!perfil) return null; // autenticado mas sem perfil = sem acesso
  return { id: data.user.id, nome: perfil.nome, papel: perfil.papel as Papel };
}
