"""
runner.py — executa a Equipe de Operação de Marketing FORA da CrewAI AMP (Render), com a mesma crew, as mesmas travas e os mesmos portões.

Contrato com o portal (idêntico ao da AMP, para o portal não mudar de lógica):
  POST /kickoff  {"inputs": {...}}                                  → {"kickoff_id": "<id>"}      inicia uma campanha (uma por vez)
  POST /resume   {"executionId","taskId","humanFeedback"}           → {"ok": true}                entrega a decisão a um portão que espera
  POST /cancel   {"executionId"}                                    → {"ok": true}                encerra a execução (reprovação)
  GET  /health                                                       → {"ok": true, "ocupado": bool}
Autenticação: Authorization: Bearer RUNNER_TOKEN.

Eventos: o runner envia cada tarefa concluída, cada pedido de decisão (human_input) e o fim da execução ao MESMO webhook que a AMP usava
(WEBHOOK_BASE + WEBHOOK_KEY), no mesmo formato. O portal lê esses eventos como antes.

Portão humano: a thread da execução fica esperando a decisão (sem gastar tokens). "Aprovado." libera; qualquer outro texto reexecuta o portão com
o feedback e abre um novo pedido. Se o processo reiniciar durante a espera, a execução se perde (o /resume responde 404 e o portal avisa).
"""

from __future__ import annotations

import hmac
import json
import os
import threading
import time
import uuid
from contextvars import ContextVar
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
from dotenv import load_dotenv

load_dotenv()
os.environ["CREW_HUMAN_GATES"] = "true"   # o runner sempre executa com os portões G1, G2 e G3 (a crew os desliga sem esta variável)

LIMITE_CORPO = 1_000_000
ESPERA_MAXIMA_H = float(os.getenv("RUNNER_ESPERA_MAXIMA_HORAS", "72"))
AUTOMACAO = os.getenv("WEBHOOK_AUTOMACAO", "runner-render")


class _Execucao:
    def __init__(self, run_id: str):
        self.id = run_id
        self.cancelada = False
        self.decisao: dict[str, str] = {}          # task_id -> feedback entregue
        self.sinais: dict[str, threading.Event] = {}
        self.aguardando: str | None = None          # task_id do portão em espera
        self.lock = threading.Lock()


_ATUAL: _Execucao | None = None
_TRAVA = threading.Lock()


def _enviar(tipo: str, payload: dict) -> None:
    """Envia um evento ao webhook (mesmo receptor da AMP). Falha de rede nunca derruba a execução: tenta 3 vezes e segue."""
    base, chave = os.getenv("WEBHOOK_BASE", ""), os.getenv("WEBHOOK_KEY", "")
    if not base or not chave:
        print(f"[runner] webhook não configurado; evento {tipo} descartado", flush=True)
        return
    for tentativa in range(3):
        try:
            r = httpx.post(base, params={"tipo": tipo, "automacao": AUTOMACAO}, json=payload, timeout=30,
                           headers={"Authorization": f"Bearer {chave}"})
            if r.status_code < 300:
                return
            print(f"[runner] webhook {r.status_code} no evento {tipo}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"[runner] webhook falhou ({type(e).__name__})", flush=True)
        time.sleep(2 * (tentativa + 1))


class ProvedorPortao:
    """HumanInputProvider: no lugar do terminal, publica o pedido no portal e espera a decisão que chega por /resume."""

    def setup_messages(self, context) -> bool:
        return False

    def post_setup_messages(self, context) -> None:
        return None

    def handle_feedback(self, formatted_answer, context):
        ex = _ATUAL
        if ex is None:
            raise RuntimeError("portão sem execução do runner ativa")
        task_id = str(getattr(context.task, "id", "")) or uuid.uuid4().hex
        resposta = formatted_answer
        while context.ask_for_human_input:
            texto = resposta.output if isinstance(resposta.output, str) else resposta.output.model_dump_json()
            feedback = self._pedir(ex, task_id, texto)
            if feedback.strip().rstrip(".").lower() == "aprovado":
                context.ask_for_human_input = False
                break
            context.messages.append(context._format_feedback_message(feedback))
            resposta = context._invoke_loop()
        return resposta

    async def handle_feedback_async(self, formatted_answer, context):
        import asyncio

        return await asyncio.to_thread(self.handle_feedback, formatted_answer, context)

    @staticmethod
    def _get_output_string(answer) -> str:
        return answer.output if isinstance(answer.output, str) else answer.output.model_dump_json()

    @staticmethod
    def _pedir(ex: _Execucao, task_id: str, texto: str) -> str:
        sinal = threading.Event()
        with ex.lock:
            ex.sinais[task_id] = sinal
            ex.decisao.pop(task_id, None)
            ex.aguardando = task_id
        _enviar("human_input", {"execution_id": ex.id, "task_id": task_id, "output": texto})
        if not sinal.wait(timeout=ESPERA_MAXIMA_H * 3600):
            raise TimeoutError("tempo máximo de espera pela decisão humana esgotado")
        with ex.lock:
            ex.aguardando = None
            if ex.cancelada:
                raise InterruptedError("execução encerrada pelo portal (reprovada)")
            return ex.decisao.pop(task_id, "")


def _instalar_provedor() -> None:
    from crewai.core.providers import human_input

    human_input._provider = ContextVar("human_input_provider", default=ProvedorPortao())


def _executar(ex: _Execucao, inputs: dict) -> None:
    global _ATUAL
    try:
        from marketing_ops.crew import MarketingOpsCrew

        _instalar_provedor()
        crew = MarketingOpsCrew().crew()

        def ao_concluir_tarefa(saida):
            _enviar("task", {"kickoff_id": ex.id, "name": getattr(saida, "name", None), "agent": getattr(saida, "agent", None), "output": getattr(saida, "raw", None) or str(saida)})

        crew.task_callback = ao_concluir_tarefa
        for t in crew.tasks:
            t.callback = ao_concluir_tarefa
        resultado = crew.kickoff(inputs=inputs)
        _enviar("crew", {"kickoff_id": ex.id, "output": getattr(resultado, "raw", None) or str(resultado)})
    except InterruptedError:
        print(f"[runner] {ex.id[:8]} encerrada por reprovação", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[runner] {ex.id[:8]} falhou: {type(e).__name__}: {str(e)[:300]}", flush=True)
        _enviar("crew", {"kickoff_id": ex.id, "output": f"FALHA DO RUNNER: {type(e).__name__}", "erro": True})
    finally:
        with _TRAVA:
            if _ATUAL is ex:
                _ATUAL = None


def iniciar(inputs: dict) -> str | None:
    global _ATUAL
    with _TRAVA:
        if _ATUAL is not None:
            return None
        ex = _Execucao(uuid.uuid4().hex)
        _ATUAL = ex
    threading.Thread(target=_executar, args=(ex, inputs), daemon=True, name=f"run-{ex.id[:8]}").start()
    return ex.id


def retomar(execucao_id: str, task_id: str, feedback: str) -> bool:
    ex = _ATUAL
    if ex is None or ex.id != execucao_id:
        return False
    with ex.lock:
        sinal = ex.sinais.get(task_id)
        if sinal is None or ex.aguardando != task_id:
            return False
        ex.decisao[task_id] = feedback
    sinal.set()
    return True


def cancelar(execucao_id: str) -> bool:
    ex = _ATUAL
    if ex is None or ex.id != execucao_id:
        return False
    with ex.lock:
        ex.cancelada = True
        for s in ex.sinais.values():
            s.set()
    return True


class _Handler(BaseHTTPRequestHandler):
    server_version = "runner"

    def _responder(self, status: int, corpo: dict) -> None:
        dados = json.dumps(corpo).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def _autorizado(self) -> bool:
        token = os.getenv("RUNNER_TOKEN", "")
        enviado = (self.headers.get("Authorization") or "").removeprefix("Bearer ").strip()
        return bool(token) and hmac.compare_digest(enviado.encode(), token.encode())

    def _corpo(self) -> dict | None:
        n = int(self.headers.get("Content-Length") or 0)
        if n > LIMITE_CORPO:
            return None
        try:
            v = json.loads(self.rfile.read(n) or b"{}")
            return v if isinstance(v, dict) else None
        except ValueError:
            return None

    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            return self._responder(200, {"ok": True, "ocupado": _ATUAL is not None})
        self._responder(404, {"erro": "não encontrado"})

    def do_POST(self):  # noqa: N802
        if not self._autorizado():
            return self._responder(401, {"erro": "não autorizado"})
        corpo = self._corpo()
        if corpo is None:
            return self._responder(400, {"erro": "pedido inválido"})
        if self.path == "/kickoff":
            inputs = corpo.get("inputs")
            if not isinstance(inputs, dict):
                return self._responder(400, {"erro": "inputs ausentes"})
            rid = iniciar({str(k): str(v) for k, v in inputs.items()})
            if rid is None:
                return self._responder(409, {"erro": "já existe uma campanha em execução"})
            return self._responder(200, {"kickoff_id": rid})
        if self.path == "/resume":
            ok = retomar(str(corpo.get("executionId", "")), str(corpo.get("taskId", "")), str(corpo.get("humanFeedback", "")))
            return self._responder(200 if ok else 404, {"ok": ok} if ok else {"erro": "execução não está mais ativa no runner (reiniciada ou encerrada)"})
        if self.path == "/cancel":
            ok = cancelar(str(corpo.get("executionId", "")))
            return self._responder(200 if ok else 404, {"ok": ok})
        self._responder(404, {"erro": "não encontrado"})

    def log_message(self, *a):  # silencia o log por requisição (não registrar dados)
        return


def servir() -> None:
    porta = int(os.getenv("PORT", "10000"))
    if not os.getenv("RUNNER_TOKEN"):
        raise SystemExit("RUNNER_TOKEN não definido")
    print(f"[runner] escutando na porta {porta}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", porta), _Handler).serve_forever()


if __name__ == "__main__":
    servir()
