# Runner da Equipe de Operação de Marketing (Render). Dependências travadas pelo uv.lock.
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 UV_LINK_MODE=copy
RUN pip install --no-cache-dir uv==0.5.* && useradd -m -u 10001 app
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY . .
RUN uv sync --frozen --no-dev && mkdir -p /app/output && chown -R app:app /app
USER app
ENV PATH="/app/.venv/bin:$PATH" CREW_OUTPUT_DIR=/app/output
EXPOSE 10000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request,os;urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','10000')+'/health')" || exit 1
CMD ["python", "-m", "marketing_ops.runner"]
