FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --extra api
COPY . .
RUN uv sync --frozen --no-dev --extra api
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "pycricinfo.api.server:app", "--host", "0.0.0.0", "--port", "8000"]