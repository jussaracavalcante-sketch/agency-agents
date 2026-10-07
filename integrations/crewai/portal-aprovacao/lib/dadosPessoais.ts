/**
 * Detecção de dados pessoais no briefing (LGPD, art. 6º III, necessidade e minimização).
 * O briefing descreve a campanha e o público em termos agregados: não deve conter CPF, e-mail, telefone, nome de paciente nem prontuário.
 * Os textos seguem para a plataforma de agentes e para o armazenamento de eventos; por isso o bloqueio acontece antes do disparo.
 */

function cpfValido(digitos: string): boolean {
  if (digitos.length !== 11 || /^(\d)\1{10}$/.test(digitos)) return false;
  const dv = (base: string, pesoInicial: number) => {
    const soma = base.split("").reduce((s, d, i) => s + Number(d) * (pesoInicial - i), 0);
    const r = (soma * 10) % 11;
    return r === 10 ? 0 : r;
  };
  return dv(digitos.slice(0, 9), 10) === Number(digitos[9]) && dv(digitos.slice(0, 10), 11) === Number(digitos[10]);
}

export type AchadoPessoal = { tipo: string; trecho: string };

/** Devolve o que parece dado pessoal, com o trecho mascarado para não repetir o dado em mensagens e logs. */
export function dadosPessoais(texto: string): AchadoPessoal[] {
  const achados: AchadoPessoal[] = [];
  const mascara = (s: string) => (s.length <= 4 ? "****" : s.slice(0, 2) + "***" + s.slice(-2));
  for (const m of texto.matchAll(/\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b/g)) {
    if (cpfValido(m[0].replace(/\D/g, ""))) achados.push({ tipo: "CPF", trecho: mascara(m[0]) });
  }
  for (const m of texto.matchAll(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g)) achados.push({ tipo: "e-mail", trecho: mascara(m[0]) });
  for (const m of texto.matchAll(/(?<!\d)(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}(?!\d)/g)) {
    const so = m[0].replace(/\D/g, "");
    if (so.length >= 10 && so.length <= 13) achados.push({ tipo: "telefone", trecho: mascara(m[0]) });
  }
  for (const m of texto.matchAll(/\b(?:paciente|pacientes)\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+/g)) achados.push({ tipo: "nome de paciente", trecho: mascara(m[0]) });
  for (const m of texto.matchAll(/\bprontu[áa]rio\s*(?:n[º°o.]?\s*)?\d+/gi)) achados.push({ tipo: "prontuário", trecho: mascara(m[0]) });
  return achados;
}

export function mensagemDadosPessoais(achados: AchadoPessoal[]): string {
  const tipos = [...new Set(achados.map((a) => a.tipo))].join(", ");
  return `O briefing parece conter dado pessoal (${tipos}). Retire e descreva o público de forma agregada: o briefing não deve identificar pessoas (LGPD, princípio da necessidade).`;
}
