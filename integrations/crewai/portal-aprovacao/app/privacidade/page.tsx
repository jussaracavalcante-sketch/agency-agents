import Markdown from "@/components/Markdown";
import { AVISO_MD, AVISO_VERSAO } from "@/lib/avisoPrivacidade";

export const metadata = { title: "Aviso de Privacidade · Marketing Ops" };

/** Página pública (sem login): o aviso precisa estar acessível antes do primeiro acesso. */
export default function Privacidade() {
  const pendentes = (AVISO_MD.match(/\[(?:PREENCHER|CONFIRMAR)\]/g) || []).length;
  return (
    <div className="doc">
      {pendentes > 0 && (
        <div className="aviso-minuta" role="status">
          <b>Minuta em validação.</b> Esta versão ({AVISO_VERSAO}) ainda tem {pendentes} campo(s) a preencher ou confirmar, destacados no texto. Ela só vale como aviso definitivo depois da validação do jurídico e do encarregado.
        </div>
      )}
      <article className="card doc-corpo"><Markdown texto={AVISO_MD} /></article>
    </div>
  );
}
