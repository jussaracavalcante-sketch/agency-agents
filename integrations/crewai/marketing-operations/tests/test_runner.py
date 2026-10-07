"""Testes do runner: portão humano (aprovar, devolver, cancelar), autenticação e uma campanha por vez. Sem LLM e sem rede."""
import sys
import threading
import time
import types
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))
from marketing_ops import runner as R  # noqa: E402


class _Saida:
    def __init__(self, output): self.output = output


class _Ctx:
    def __init__(self):
        self.task = types.SimpleNamespace(id="task-1")
        self.ask_for_human_input = True
        self.messages = []
        self.rodadas = 0

    def _format_feedback_message(self, fb): return {"role": "user", "content": fb}

    def _invoke_loop(self):
        self.rodadas += 1
        return _Saida(f"versão {self.rodadas + 1}")


def _preparar():
    enviados = []
    R._enviar = lambda tipo, payload: enviados.append((tipo, payload))
    R._ATUAL = R._Execucao("exec-1")
    return enviados


def _esperar(cond, s=3):
    fim = time.time() + s
    while time.time() < fim:
        if cond(): return True
        time.sleep(0.01)
    return False


def test_aprovado_libera_sem_reexecutar():
    enviados = _preparar()
    ctx, saida = _Ctx(), {}
    t = threading.Thread(target=lambda: saida.update(r=R.ProvedorPortao().handle_feedback(_Saida("versão 1"), ctx)))
    t.start()
    assert _esperar(lambda: R._ATUAL.aguardando == "task-1")
    assert enviados[0][0] == "human_input" and enviados[0][1]["task_id"] == "task-1" and enviados[0][1]["output"] == "versão 1"
    assert R.retomar("exec-1", "task-1", "Aprovado.")
    t.join(3)
    assert saida["r"].output == "versão 1" and ctx.rodadas == 0 and ctx.ask_for_human_input is False


def test_devolver_reexecuta_e_abre_novo_pedido_ate_aprovar():
    enviados = _preparar()
    ctx, saida = _Ctx(), {}
    t = threading.Thread(target=lambda: saida.update(r=R.ProvedorPortao().handle_feedback(_Saida("versão 1"), ctx)))
    t.start()
    assert _esperar(lambda: R._ATUAL.aguardando == "task-1")
    assert R.retomar("exec-1", "task-1", "DECISÃO G1: DEVOLVIDO COM FEEDBACK. Ajustes pedidos: trocar X")
    assert _esperar(lambda: len(enviados) == 2)           # novo pedido com a versão reescrita
    assert enviados[1][1]["output"] == "versão 2"
    assert _esperar(lambda: R._ATUAL.aguardando == "task-1")
    assert R.retomar("exec-1", "task-1", "Aprovado.")
    t.join(3)
    assert saida["r"].output == "versão 2" and ctx.rodadas == 1 and "trocar X" in ctx.messages[0]["content"]


def test_cancelar_encerra_a_espera():
    _preparar()
    ctx, erro = _Ctx(), {}

    def rodar():
        try:
            R.ProvedorPortao().handle_feedback(_Saida("v1"), ctx)
        except InterruptedError as e:
            erro["e"] = e

    t = threading.Thread(target=rodar); t.start()
    assert _esperar(lambda: R._ATUAL.aguardando == "task-1")
    assert R.cancelar("exec-1")
    t.join(3)
    assert "e" in erro


def test_retomar_de_execucao_inexistente_ou_portao_errado_falha():
    _preparar()
    assert R.retomar("outra", "task-1", "Aprovado.") is False
    assert R.retomar("exec-1", "task-x", "Aprovado.") is False
    R._ATUAL = None
    assert R.retomar("exec-1", "task-1", "Aprovado.") is False


def test_so_uma_campanha_por_vez():
    _preparar()
    assert R.iniciar({"cliente": "x"}) is None   # já há execução ativa
    R._ATUAL = None
