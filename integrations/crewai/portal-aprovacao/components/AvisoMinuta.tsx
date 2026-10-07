/** Faixa de minuta: aparece enquanto o texto tiver campos a preencher ou confirmar. */
export function pendencias(md: string) {
  return (md.match(/\[(?:PREENCHER|CONFIRMAR)\]/g) || []).length;
}

export default function AvisoMinuta({ md, versao }: { md: string; versao: string }) {
  const n = pendencias(md);
  if (!n) return null;
  return (
    <div className="aviso-minuta" role="status">
      <b>Minuta em validação.</b> Esta versão ({versao}) ainda tem {n} campo(s) a preencher ou confirmar, destacados no texto. Ela só vale como definitiva depois da validação do jurídico e do encarregado.
    </div>
  );
}
